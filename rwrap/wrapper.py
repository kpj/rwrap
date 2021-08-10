"""Wrap R package with Python class to facilitate method access."""

from typing import Callable

from loguru import logger

from rpy2.robjects.packages import importr
from rpy2.robjects.conversion import localconverter

from .converter import converter


class RLibraryWrapper:
    """Shallow wrapper of R package."""

    def __init__(self, lib_name: str) -> None:
        """Import R package."""
        self.lib_name = lib_name.replace("_", ".")
        self.lib = importr(self.lib_name)

    def __getattr__(self, name: str) -> Callable:
        """Access method of R package."""
        def wrapper(*args, **kwargs):
            logger.debug("Calling {name}", name=name)
            with localconverter(converter) as cv:
                res = getattr(self.lib, name)(*args, **kwargs)
                return cv.rpy2py(res)

        return wrapper

    def __repr__(self) -> str:
        return f"<module '{self.lib_name}' from R>"
