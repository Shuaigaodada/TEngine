from typing import Iterator, Tuple
from .clickstatus import ClickStatus
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
        
        self.pressed                : Tuple[str] = ( )
        self.clicked                : Tuple[str] = ( )
        self.released               : Tuple[str] = ( )
        self.doubleClicked          : Tuple[str] = ( )
        self.tripleClicked          : Tuple[str] = ( )
        self.rightPressed           : Tuple[str] = ( )
        self.rightClicked           : Tuple[str] = ( )
        self.rightDoubleClicked     : Tuple[str] = ( )
        self.rightTripleClicked     : Tuple[str] = ( )
        self.middlePressed          : Tuple[str] = ( )
        self.middleClicked          : Tuple[str] = ( )
        self.middleDoubleClicked    : Tuple[str] = ( )
        self.middleTripleClicked    : Tuple[str] = ( )
        
        self.draging                : Tuple[str] = ( )
        
        self.init()
    
    def init(self) -> None:
        for name in self.clicked:
            if self.bstate & ClickStatus.PRESSED:
                self.pressed += (name, )
            if self.bstate & ClickStatus.CLICKED:
                self.clicked += (name, )
            if self.bstate & ClickStatus.RELEASED:
                self.released += (name, )
            if self.bstate & ClickStatus.DOUBLE_CLICKED:
                self.doubleClicked += (name, )
            if self.bstate & ClickStatus.TRIPLE_CLICKED:
                self.tripleClicked += (name, )
            if self.bstate & ClickStatus.RIGHT_PRESSED:
                self.rightPressed += (name, )
            if self.bstate & ClickStatus.RIGHT_CLICKED:
                self.rightClicked += (name, )
            if self.bstate & ClickStatus.RIGHT_DOUBLE_CLICKED:
                self.rightDoubleClicked += (name, )
            if self.bstate & ClickStatus.RIGHT_TRIPLE_CLICKED:
                self.rightTripleClicked += (name, )
            if self.bstate & ClickStatus.MIDDLE_PRESSED:
                self.middlePressed += (name, )
            if self.bstate & ClickStatus.MIDDLE_CLICKED:
                self.middleClicked += (name, )
            if self.bstate & ClickStatus.MIDDLE_DOUBLE_CLICKED:
                self.middleDoubleClicked += (name, )
            if self.bstate & ClickStatus.MIDDLE_TRIPLE_CLICKED:
                self.middleTripleClicked += (name, )
            
            if self.bstate & ClickStatus.DRAGING:
                self.draging += (name, )
        return

