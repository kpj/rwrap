"""Implement opinionated Py<->R conversion functions."""

import datetime

from loguru import logger

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely import geometry

import rpy2.robjects as ro
import rpy2.rinterface as ri

from rpy2.robjects import numpy2ri, pandas2ri

from rpy2.robjects.conversion import converter as template_converter, Converter


# setup converter
template_converter += numpy2ri.converter
template_converter += pandas2ri.converter
converter = Converter("rwrap", template=template_converter)


# None type
@converter.py2rpy.register(type(None))
def _(obj):
    logger.trace(f"py2rpy::None")
    return ri.NULLType


@converter.rpy2py.register(ri.NULLType)
def _(obj):
    logger.trace(f"rpy2py::ri.NULLType")
    return None


# special classes
def convert_dates(obj):
    days2date = lambda days_since_epoch: datetime.datetime.fromtimestamp(
        days_since_epoch * 24 * 60 * 60
    ).replace(hour=0, minute=0, second=0)
    return [days2date(days_since_epoch) for days_since_epoch in obj]


def convert_geometry(obj):
    """Convert an sfg (simple feature geometry) object.

    Can have one of these dimensionalities:
    * 2D: single point
    * 3D: set of points (each row containing one point)
    * 4D: list

    Polygons consist of a hull (set of points) and optionally a set of holes (each hole is yet again a set of points)

    More details: https://r-spatial.github.io/sf/articles/sf1.html#how-simple-features-in-r-are-organized-1
    """
    # determine object properties
    rlcass = list(obj.rclass)
    assert len(rlcass) == 3, rlcass
    assert rlcass[-1] == "sfg", rlcass

    dimension = rlcass[0]
    type_ = rlcass[1]

    assert dimension == "XY", "Other dimensions not yet implemented"

    # convert object
    if type_ == "POINT":
        return geometry.Point(obj)
    elif type_ == "POLYGON":
        hole_list = []
        if obj.typeof == ri.RTYPES.VECSXP:
            hull = np.asarray(obj[0])

            if len(obj) > 1:
                for o in obj[1:]:
                    hole_list.append(np.asarray(o))
        elif obj.typeof == ri.RTYPES.REALSXP:
            hull = np.asarray(obj)

        return geometry.Polygon(hull, hole_list)
    elif type_ == "MULTIPOLYGON":
        poly_list = []
        for entry in obj:
            # entry class is `list` otherwise
            entry.rclass = ri.StrSexpVector([dimension, "POLYGON", "sfg"])

            p = convert_geometry(entry)
            poly_list.append(p)

        return geometry.MultiPolygon(poly_list)
    else:
        raise TypeError(f"Invalid geometry type: {type_}")


# TODO: make use of `NameClassMap`
CLASS_CONVERTERS = {
    "Date": convert_dates,
    "sf": lambda obj: gpd.GeoDataFrame(
        pd.DataFrame(
            {column: converter.rpy2py(data) for column, data in zip(obj.names, obj)}
        )
    ),
    "sfc": lambda obj: gpd.GeoSeries([convert_geometry(o) for o in obj]),
    "POINT": lambda obj: [convert_geometry(obj)],
    "POLYGON": lambda obj: [convert_geometry(obj)],
    "MULTIPOLYGON": lambda obj: [convert_geometry(obj)],
    "data.frame": lambda obj: converter.rpy2py(ro.DataFrame(obj)),
    "matrix": lambda obj: np.array(obj),
}


@converter.py2rpy.register(datetime.datetime)
def _(obj):
    logger.trace(f"py2rpy::datetime.datetime")

    return ro.r(
        f"lubridate::make_date(year={obj.year}, month={obj.month}, day={obj.day})"
    )


# vectors
@converter.py2rpy.register(list)
def _(obj):
    logger.trace("py2rpy::list")

    if len({type(e) for e in obj}) == 1:
        # has no mixed types

        vector_type_map = {
            bool: ro.BoolVector,
            int: ro.IntVector,
            float: ro.FloatVector,
            str: ro.StrVector,
        }

        for type_, VectorClass in vector_type_map.items():
            if isinstance(obj[0], type_):
                return VectorClass([converter.py2rpy(x) for x in obj])

        raise NotImplementedError(
            f"No list conversion implemented for type {type(obj[0])}"
        )

    # heterogeneous types, use R list
    return ro.ListVector({i + 1: converter.py2rpy(v) for i, v in enumerate(obj)})


@converter.rpy2py.register(ro.Vector)
@converter.rpy2py.register(ro.ListVector)
@converter.rpy2py.register(ri.BoolSexpVector)
@converter.rpy2py.register(ri.IntSexpVector)
@converter.rpy2py.register(ri.FloatSexpVector)
@converter.rpy2py.register(ri.StrSexpVector)
@converter.rpy2py.register(ri.ListSexpVector)
def _(obj):
    logger.trace(f"rpy2py::ro.Vector[{list(obj.rclass)}]")
    rclass = set(obj.rclass)
    is_atomic = True

    # handle special classes
    for class_, conv_func in CLASS_CONVERTERS.items():
        if class_ in rclass:
            logger.trace(f"Using custom class converter for {class_}")
            obj = conv_func(obj)
            break
    else:
        # if not special class was detected, we try primitives
        if {"numeric", "character", "logical", "list"} & rclass:
            logger.trace("Using default class converter")

            keys = converter.rpy2py(obj.names)
            values = [converter.rpy2py(x) for x in obj]

            if keys is not None:
                # could accidentally be atomic
                if not isinstance(keys, list):
                    keys = [keys]

                obj = dict(zip(keys, values))
            else:
                obj = values

            if "list" in rclass:
                is_atomic = False
        else:
            # if no converter was found, we just return the raw object
            logger.trace(f"Skipping conversion for class {rclass}")

    # vector of length 1 in R should be atomic type in Python
    if not isinstance(obj, dict) and len(obj) == 1 and is_atomic:
        return obj[0]
    return obj


# dicts
@converter.py2rpy.register(dict)
def _(obj):
    logger.trace("py2rpy::dict")

    return ro.ListVector({k: converter.py2rpy(v) for k, v in obj.items()})
