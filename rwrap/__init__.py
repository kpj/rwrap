"""Make using R packages from Python easier."""

from importlib import metadata

import rpy2.rinterface as ri

from .wrapper import RLibraryWrapper


__version__ = metadata.version("rwrap")


def __getattr__(name: str) -> RLibraryWrapper:
    try:
        return RLibraryWrapper(name)
    except ri.RRuntimeError:
        # TODO: use ModuleNotFoundError, ImportError
        raise AttributeError(f'Error while importing "{name}"')
