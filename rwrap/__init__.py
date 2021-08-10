"""Make using R packages from Python easier."""

import sys
from importlib import metadata

from loguru import logger
import rpy2.rinterface as ri

from .wrapper import RLibraryWrapper


__version__ = metadata.version('rwrap')

logger.remove()
logger.add(sys.stderr, level='WARNING')


def __getattr__(name: str) -> RLibraryWrapper:
    try:
        return RLibraryWrapper(name)
    except ri.RRuntimeError:
        # TODO: use ModuleNotFoundError, ImportError
        raise AttributeError(f'Error while importing "{name}"')
