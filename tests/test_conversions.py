import datetime

import numpy as np
import pandas as pd

import rpy2.robjects as ro

import pytest
import numpy.testing as npt
import pandas.testing as pdt

import igraph
from shapely import geometry

from rwrap.converter import converter


@pytest.mark.parametrize(
    "r_expr,py_data",
    [
        # lists/vectors
        ("c(42)", 42),
        ("list(42)", [42]),
        ("c(TRUE, FALSE)", [True, False]),
        ("c(1, 2, 3)", [1, 2, 3]),
        ("list(1, 2, 3)", [1, 2, 3]),
        ("list(1:2, 1:3)", [[1, 2], [1, 2, 3]]),
        ("list(list(), list('a', 'b'))", [[], ["a", "b"]]),
        ('c(1, "a")', ["1", "a"]),  # adjust for R's type coercion
        # dicts
        ("c(a = 1, beta = 2, c = 3)", {"a": 1, "beta": 2, "c": 3}),
        (
            "list(a = 1, beta = c(2, 42), c = FALSE)",
            {"a": 1, "beta": [2, 42], "c": False},
        ),
        # pandas
        (
            'data.frame(x = 1, y = "A")',
            pd.DataFrame({"x": [1], "y": ["A"]}, index=["1"]),
        ),
        (
            'data.frame(x = c(1), y = c("A"))',
            pd.DataFrame({"x": [1], "y": ["A"]}, index=["1"]),
        ),
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
        # geometry
        ("sf::st_point(c(1, 2))", geometry.Point(1, 2)),
        (
            "sf::st_polygon(list(matrix(c(0, 0, 10, 0, 10, 10, 0, 10, 0, 0), ncol = 2, byrow = TRUE)))",
            geometry.Polygon([(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]),
        ),
        (
            "sf::st_multipolygon(list(sf::st_polygon(list(matrix(c(0, 0, 10, 0, 10, 10, 0, 10, 0, 0), ncol = 2, byrow = TRUE))), sf::st_polygon(list(matrix(c(1, 2, 3, 4, 5, 6, 1, 2), ncol = 2, byrow = TRUE)))))",
            geometry.MultiPolygon(
                [
                    geometry.Polygon([(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]),
                    geometry.Polygon([(1, 2), (3, 4), (5, 6), (1, 2)]),
                ]
            ),
        ),
        # networks
        (
            "igraph::graph_from_data_frame(data.frame(from = c('A', 'B'), to = c('B', 'C')), directed = FALSE)",
            igraph.Graph(
                n=3,
                edges=[(0, 1), (1, 2)],
                directed=False,
                vertex_attrs={"name": ["A", "B", "C"], "id": ["n0", "n1", "n2"]},
            ),
        ),
        (
            "igraph::make_(igraph::ring(4), igraph::with_vertex_(name = letters[1:4], color = 'red'), igraph::with_edge_(weight = 1:4, color = 'green'))",
            igraph.Graph(
                n=4,
                edges=[(0, 1), (1, 2), (2, 3), (3, 0)],
                directed=False,
                graph_attrs={"name": "Ring graph", "mutual": False, "circular": True},
                vertex_attrs={
                    "name": ["a", "b", "c", "d"],
                    "color": ["red", "red", "red", "red"],
                    "id": ["n0", "n1", "n2", "n3"],
                },
                edge_attrs={
                    "weight": [1, 2, 3, 4],
                    "color": ["green", "green", "green", "green"],
                },
            ),
        ),
    ],
)
def test_equality(tmp_path, r_expr, py_data):
    r_data = ro.r(r_expr)

    # rpy2py
    r_data_conv = converter.rpy2py(r_data)

    if isinstance(py_data, pd.DataFrame):
        pdt.assert_frame_equal(r_data_conv, py_data, check_dtype=False)
    elif isinstance(py_data, igraph.Graph):
        fname_py = tmp_path / "py.gml"
        py_data.write_graphml(str(fname_py))

        fname_r = tmp_path / "r.gml"
        r_data_conv.write_graphml(str(fname_r))

        assert fname_py.read_text() == fname_r.read_text()
    else:
        assert r_data_conv == py_data

    # py2rpy
    # py_data_conv = converter.py2rpy(py_data)
    # assert r_data.r_repr() == py_data_conv.r_repr()
