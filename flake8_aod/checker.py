import sys

if sys.version_info < (3, 8):
    import importlib_metadata as metadata
else:
    from importlib import metadata

__version__ = metadata.version("flake8_aod")


class ErrorCode:
    ADO001 = "ADO001 Missing ADO item"
    ADO002 = "ADO002 Todo item already resolved"
    ADO003 = "ADO003 Wrong ADO item ID prefix ('AB')"


class Checker:
    name = __name__
    version = __version__
