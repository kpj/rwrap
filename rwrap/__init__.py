"""Make using R packages from Python easier."""

import sys

from loguru import logger
import rpy2.rinterface as ri

from .wrapper import RLibraryWrapper


logger.remove()
logger.add(sys.stderr, level='WARNING')


def __getattr__(name: str) -> RLibraryWrapper:
    try:
        return RLibraryWrapper(name)
    except ri.RRuntimeError:
        # TODO: use ModuleNotFoundError, ImportError
        raise AttributeError(f'Error while importing "{name}"')
