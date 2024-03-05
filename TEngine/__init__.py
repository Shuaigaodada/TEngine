try:
    import curses
except ModuleNotFoundError:
    raise ModuleNotFoundError( "can't import curses module, maybe your OS is `Windows`, try install `windows-curses` and run again." )

from .Engine.fileLogger import DebugLogger
from .Engine.engine import TEngine
from .Engine.resource import Resource, FileLoader

version = "0.0.0beta"
__all__ = [
    "version",
    "DebugLogger",
    "TEngine",
    "Resource", "FileLoader"
]