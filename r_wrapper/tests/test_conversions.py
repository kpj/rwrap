import datetime

import numpy as np

import rpy2.robjects as ro

import pytest
import numpy.testing as nptest

from ..converter import converter


@pytest.mark.parametrize('r_expr,py_data', [
    (
        'c(1, 2, 3)',
        [1, 2, 3]
    ),
    (
        'list(1, 2, 3)',
        [[1], [2], [3]]
    ),
    (
        'list(a=1, b=2, c=3)',
        {'a': [1], 'b': [2], 'c': [3]}
    ),
    (
        'c(1, "a")',
        ['1', 'a']  # adjust for R's type coercion
    ),
])
def test_lists(r_expr, py_data):
    r_data = ro.r(r_expr)

    # rpy2py
    r_data_conv = converter.rpy2py(r_data)
    if isinstance(r_data_conv, np.ndarray):
        r_data_conv = r_data_conv.tolist()
    assert r_data_conv == py_data

    # py2rpy
    py_data_conv = converter.py2rpy(py_data)
    # TODO: fix this
    # assert r_data.r_repr() == py_data_conv.r_repr()


@pytest.mark.parametrize('r_expr,py_data', [
    (
        'lubridate::ymd("2017-01-31")',
        datetime.datetime(2017, 1, 31)
    ),
    (
        'c(lubridate::ymd("1982-06-25"), lubridate::dmy("03-Oct-2017"))',
        [datetime.datetime(1982, 6, 25), datetime.datetime(2017, 10, 3)]
    ),
    (
        'list(foo=lubridate::ymd("2000-01-01"))',
        {'foo': datetime.datetime(2000, 1, 1)}
    ),
])
def test_dates(r_expr, py_data):
    r_data = ro.r(r_expr)

    # rpy2py
    r_data_conv = converter.rpy2py(r_data)
    assert r_data_conv == py_data

    # py2rpy
    py_data_conv = converter.py2rpy(py_data)
    assert r_data.r_repr() == py_data_conv.r_repr()
