from typing import Iterator
from ..interfaces import ClickBox as ClickBoxInterfaces
from ..interfaces import ClickedBox as ClickedBoxInterfaces

__all__ = [ "ClickBox", "ClickedBox" ]

class ClickBox( ClickBoxInterfaces ):
    def __init__(self, x: int, y: int, w: int, h: int) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h
    
    def check(self, x: int, y: int) -> bool:
        return self.x <= x <= self.x + self.w and self.y <= y <= self.y + self.h


class ClickedBox( ClickedBoxInterfaces ):
    def __init__(self, x: int, y: int, bstate: int, clicked: Iterator[str]) -> None:
        self.x = x
        self.y = y
        self.bstate = bstate
        self.clicked = clicked

