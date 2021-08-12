"""Wrap R package with Python class to facilitate method access."""

from typing import Callable

from loguru import logger

import rpy2.robjects as ro
from rpy2.robjects.packages import importr
from rpy2.robjects.conversion import localconverter

from .converter import converter


class RLibraryWrapper:
    """Shallow wrapper of R package."""

    def __init__(self, lib_name: str) -> None:
        """Import R package."""
        self.__lib = importr(lib_name.replace("_", "."))

    def __getattr__(self, name: str) -> Callable:
        """Access method of R package."""

        def wrapper(*args, **kwargs):
            logger.trace("Calling {name}", name=name)
            with localconverter(converter) as cv:
                res = getattr(self.__lib, name)(*args, **kwargs)
                return cv.rpy2py(res)

        return wrapper

    def __repr__(self) -> str:
        lib_path = ro.r(f"find.package('{self.__lib.__rname__}')")[0]
        return f"<module '{self.__lib.__rname__}' from '{lib_path}'>"
