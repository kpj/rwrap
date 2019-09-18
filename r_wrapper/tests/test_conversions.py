import numpy as np
import pandas as pd

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
