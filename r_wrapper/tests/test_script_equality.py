import os
import contextlib
import subprocess

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


def gather_test_scripts(script_dir='./r_wrapper/tests/scripts'):
    script_list = []
    for entry in os.scandir(script_dir):
        if entry.name.startswith('__'):
            continue

        test_name = entry.name
        script_list.append((
            os.path.realpath(f'{entry.path}/{test_name}.R'),
            os.path.realpath(f'{entry.path}/{test_name}.py')))
    return script_list


def assert_file_equality(fname1, fname2):
    with open(fname1) as fd1, open(fname2) as fd2:
        assert fd1.read() == fd2.read()


@pytest.mark.parametrize('r_script,py_script', gather_test_scripts())
def test_execution(empty_dir, r_script, py_script):
    # execute Python script
    os.makedirs('cwd_py')
    with chdir('cwd_py'):
        print('Calling Python')
        subprocess.call(['python3', py_script])

    # execute R script
    os.makedirs('cwd_r')
    with chdir('cwd_r'):
        print('Calling R')
        subprocess.call(['Rscript', r_script])

    # assert that both scripts created same files
    assert os.listdir('cwd_r') == os.listdir('cwd_py')

    # assert that files have same content
    for fname in os.listdir('cwd_r'):
        fname_r = os.path.join('cwd_r', fname)
        fname_py = os.path.join('cwd_py', fname)

        assert_file_equality(fname_r, fname_py)
