"""Implement opinionated Py<->R conversion functions."""

import datetime

import numpy as np
import pandas as pd

from loguru import logger

import rpy2.rinterface as ri
from rpy2.rinterface import RTYPES

import rpy2.robjects as ro
from rpy2.robjects import numpy2ri, pandas2ri

from rpy2.robjects.conversion import (
    converter as template_converter,
    Converter)


# setup converter
template_converter += numpy2ri.converter
template_converter += pandas2ri.converter
converter = Converter('r_wrapper', template=template_converter)


@converter.py2rpy.register(list)
def _(obj):
    logger.debug('py2rpy: list -> <type>Vector')
    # TODO: handle mixed types better

    if len({type(e) for e in obj}) != 1:
        raise TypeError(f'Mixed types in {obj}')

    vector_type_map = {
        float: ro.FloatVector,
        int: ro.IntVector,
        bool: ro.BoolVector,
        str: ro.StrVector
    }

    for type_, VectorClass in vector_type_map.items():
        if isinstance(obj[0], type_):
            logger.trace(f'Detected: {type_}')
            return VectorClass([converter.py2rpy(x) for x in obj])

    raise TypeError(f'No vector class found for {obj}')


@converter.py2rpy.register(dict)
def _(obj):
    logger.debug('py2rpy: dict -> ro.ListVector')
    logger.trace(f' object: {obj}')
    logger.trace(f' member types: {[type(o) for o in obj.values()]}')

    return ro.vectors.ListVector(
        {k: converter.py2rpy(v) for k, v in obj.items()})


@converter.py2rpy.register(datetime.datetime)
def _(obj):
    logger.debug('py2rpy: datetime.datetime -> lubridate::Date')
    logger.trace(f' object: {obj}')

    return ro.r(f'lubridate::make_date(year={obj.year}, month={obj.month}, day={obj.day})')


@converter.rpy2py.register(ro.vectors.ListVector)
def _(obj):
    logger.debug('rpy2py: ro.ListVector -> dict/list')
    logger.trace(f' object: {obj}')

    keys = obj.names
    values = [converter.rpy2py(x) for x in obj]

    if isinstance(keys, np.ndarray) or keys.typeof != RTYPES.NILSXP:
        return dict(zip(keys, values))
    else:
        return values


@converter.rpy2py.register(ri.FloatSexpVector)
def rpy2py_sexp(obj):
    """Convert named arrays while keeping the names.

    This function is adapted from 'rpy2/robjects/numpy2ri.py'.
    """
    logger.debug('rpy2py: ri.FloatSexpVector -> np.array/pd.Series')
    logger.trace(f' object: {obj}')

    if 'Date' in obj.rclass:
        days2date = lambda days_since_epoch: \
            datetime.datetime.fromtimestamp(days_since_epoch * 24 * 60 * 60).replace(hour=0, minute=0, second=0)
        dates = [days2date(days_since_epoch) for days_since_epoch in obj]

        res = dates
    else:
        # TODO: implement this for other SexpVector types
        _vectortypes = (RTYPES.LGLSXP,
                        RTYPES.INTSXP,
                        RTYPES.REALSXP,
                        RTYPES.CPLXSXP,
                        RTYPES.STRSXP)

        if (obj.typeof in _vectortypes) and (obj.typeof != RTYPES.VECSXP):
            if obj.names.typeof == RTYPES.NILSXP:
                # no names associated
                res = np.array(obj)
            else:
                res = pd.Series(obj, index=obj.names)
        else:
            res = ro.default_converter.rpy2py(obj)

    return res if len(res) > 1 else res[0]
