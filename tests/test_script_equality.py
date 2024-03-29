import os
import contextlib
import subprocess

import pandas as pd
from pandas.util.testing import assert_frame_equal

import pytest


@contextlib.contextmanager
def chdir(dir_: str):
    """Temporarily switch directories."""
    curdir = os.getcwd()
    os.chdir(dir_)
    try:
        yield
    finally:
        os.chdir(curdir)


@pytest.fixture
def empty_dir(tmp_path):
    with chdir(tmp_path):
        yield


def gather_test_scripts(script_dir="./tests/scripts"):
    script_list = []
    for entry in os.scandir(script_dir):
        if entry.name.startswith("__") or entry.name == "DESCRIPTION":
            continue

        script_list.append((entry.name, os.path.realpath(entry.path)))
    return script_list


def assert_file_equality(fname_r, fname_py):
    fname, ext = os.path.splitext(fname_r)

    if ext == ".csv":
        df_r = pd.read_csv(fname_r, dtype={"geometry": "str"})
        df_py = pd.read_csv(fname_py)

        assert_frame_equal(df_r.sort_index(axis=1), df_py.sort_index(axis=1))
    else:
        with open(fname_r) as fd1, open(fname_py) as fd2:
            assert fd1.read() == fd2.read()


@pytest.mark.parametrize("name,path", gather_test_scripts())
def test_execution(empty_dir, name, path):
    # TODO: remove once upstream is fixed
    if name in ["biomaRt", "DEA_workflow"]:
        pytest.skip("Skip biomaRt's 'SSL certificate problem' error")

    # assemble paths
    py_script = os.path.join(path, f"{name}.py")
    r_script = os.path.join(path, f"{name}.R")

    setup_script = os.path.join(path, "setup.py")

    # execute Python script
    os.makedirs("cwd_py")
    with chdir("cwd_py"):
        # execute setup script if given
        if os.path.exists(setup_script):
            print("Calling setup")
            subprocess.call(["python3", setup_script])

        # execute script
        print("Calling Python")
        proc_py = subprocess.run(
            ["python3", py_script], stdin=subprocess.PIPE, check=True
        )

    # execute R script
    os.makedirs("cwd_r")
    with chdir("cwd_r"):
        # execute setup script if given
        if os.path.exists(setup_script):
            print("Calling setup")
            subprocess.call(["python3", setup_script])

        # execute script
        print("Calling R")
        proc_r = subprocess.run(
            ["Rscript", r_script], stdin=subprocess.PIPE, check=True
        )

    # assert that scripts had same output
    assert proc_r.stdout == proc_py.stdout

    # assert that both scripts created same files
    assert os.listdir("cwd_r") == os.listdir("cwd_py")

    # assert that files have same content
    for fname in os.listdir("cwd_r"):
        fname_r = os.path.join("cwd_r", fname)
        fname_py = os.path.join("cwd_py", fname)

        assert_file_equality(fname_r, fname_py)
