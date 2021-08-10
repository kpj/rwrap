"""Implement opinionated Py<->R conversion functions."""

import datetime

from loguru import logger

import rpy2.robjects as ro
import rpy2.rinterface as ri

from rpy2.robjects import numpy2ri, pandas2ri

from rpy2.robjects.conversion import converter as template_converter, Converter


# setup converter
template_converter += numpy2ri.converter
template_converter += pandas2ri.converter
converter = Converter("r_wrapper", template=template_converter)


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


CLASS_CONVERTERS = {
    "Date": convert_dates,
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
@converter.rpy2py.register(ri.BoolSexpVector)
@converter.rpy2py.register(ri.IntSexpVector)
@converter.rpy2py.register(ri.FloatSexpVector)
@converter.rpy2py.register(ri.StrSexpVector)
def _(obj):
    logger.trace(f"rpy2py::ro.Vector[{list(obj.rclass)}]")

    # handle special classes
    for class_, conv_func in CLASS_CONVERTERS.items():
        if class_ in obj.rclass:
            logger.trace(f"Using custom class converter for {class_}")
            obj = conv_func(obj)
            break
    else:
        # if not special class was detected, we try primitives
        if {"numeric", "character", "logical"} & set(obj.rclass):
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
        else:
            # if no converter was found, we just return the raw object
            logger.trace(f"Skipping conversion for class {list(obj.rclass)}")

    # vector of length 1 in R should be atomic type in Python
    if not isinstance(obj, dict) and len(obj) == 1:
        return obj[0]
    return obj


# dicts
@converter.py2rpy.register(dict)
def _(obj):
    logger.trace("py2rpy::dict")

    return ro.ListVector({k: converter.py2rpy(v) for k, v in obj.items()})


@converter.rpy2py.register(ro.ListVector)
def _(obj):
    logger.trace(f"rpy2py::ro.ListVector[{list(obj.rclass)}]")

    # do not convert complicated objects
    if not {"list"} & set(obj.rclass):
        logger.trace("Skipping conversion")
        return obj

    keys = converter.rpy2py(obj.names)
    values = [converter.rpy2py(x) for x in obj]

    if keys is not None:
        # could accidentally be atomic
        if not isinstance(keys, list):
            keys = [keys]

        return dict(zip(keys, values))
    else:
        return values
