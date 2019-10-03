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
])
def test_rpy2py_lists(r_expr, py_data):
    r_data = converter.rpy2py(ro.r(r_expr))

    if isinstance(r_data, np.ndarray):
        nptest.assert_allclose(r_data, py_data)
    else:
        assert r_data == py_data


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
def test_rpy2py_dates(r_expr, py_data):
    r_data = converter.rpy2py(ro.r(r_expr))
    assert r_data == py_data
