import datetime

import numpy as np
import pandas as pd

import rpy2.robjects as ro

import pytest
import numpy.testing as npt
import pandas.testing as pdt

from rwrap.converter import converter


@pytest.mark.parametrize(
    "r_expr,py_data",
    [
        # lists/vectors
        ("c(TRUE, FALSE)", [True, False]),
        ("c(1, 2, 3)", [1, 2, 3]),
        ("list(1, 2, 3)", [1, 2, 3]),
        ('c(1, "a")', ["1", "a"]),  # adjust for R's type coercion
        # dicts
        ("c(a = 1, beta = 2, c = 3)", {"a": 1, "beta": 2, "c": 3}),
        (
            "list(a = 1, beta = c(2, 42), c = FALSE)",
            {"a": 1, "beta": [2, 42], "c": False},
        ),
        # pandas
        (
            'data.frame(x = c(1, 2, 3), y = c("A", "B", "C"))',
            pd.DataFrame({"x": [1, 2, 3], "y": ["A", "B", "C"]}, index=["1", "2", "3"]),
        ),
        # dates/times
        ('lubridate::ymd("2017-01-31")', datetime.datetime(2017, 1, 31)),
        (
            'c(lubridate::ymd("1982-06-25"), lubridate::dmy("03-Oct-2017"))',
            [datetime.datetime(1982, 6, 25), datetime.datetime(2017, 10, 3)],
        ),
        (
            'list(foo = lubridate::ymd("2000-01-01"))',
            {"foo": datetime.datetime(2000, 1, 1)},
        ),
    ],
)
def test_equality(r_expr, py_data):
    r_data = ro.r(r_expr)

    # rpy2py
    r_data_conv = converter.rpy2py(r_data)

    if isinstance(py_data, pd.DataFrame):
        pdt.assert_frame_equal(r_data_conv, py_data, check_dtype=False)
    else:
        assert r_data_conv == py_data

    # py2rpy
    py_data_conv = converter.py2rpy(py_data)
    assert r_data.r_repr() == py_data_conv.r_repr()
