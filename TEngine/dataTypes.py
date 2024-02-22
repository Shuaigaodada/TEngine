import typing as T
import unicurses as curses
from .Engine.clickBox import ClickBox

class ClickStatus:
    PRESSED: int = curses.BUTTON1_PRESSED
    RELEASED: int = curses.BUTTON1_RELEASED
    CLICK: int = curses.BUTTON1_CLICKED
    DOUBLE_CLICK: int = curses.BUTTON1_DOUBLE_CLICKED
    TRIPLE_CLICK: int = curses.BUTTON1_TRIPLE_CLICKED
    RIGHT_PRESSED: int = curses.BUTTON2_PRESSED
    RIGHT_CLICK: int = curses.BUTTON2_CLICKED
    RIGHT_DOUBLE_CLICK: int = curses.BUTTON2_DOUBLE_CLICKED
    RIGHT_TRIPLE_CLICK: int = curses.BUTTON2_TRIPLE_CLICKED
    MIDDLE_PRESSED: int = curses.BUTTON3_PRESSED
    MIDDLE_CLICK: int = curses.BUTTON3_CLICKED
    MIDDLE_DOUBLE_CLICK: int = curses.BUTTON3_DOUBLE_CLICKED
    MIDDLE_TRIPLE_CLICK: int = curses.BUTTON3_TRIPLE_CLICKED
    UNKNOWN: int = -1

class MouseClickEvent(T.NamedTuple):
    x: int
    y: int
    bstate: int
    state: int
    clicked: T.Tuple[str, ClickBox]

class SizeType(T.NamedTuple):
    width: int
    height: int
