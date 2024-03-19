from typing import List, Tuple
from .clickstatus import ClickStatus
from ..interfaces import ClickBox as IClickBox
from ..interfaces import ClickedBox as IClickedBox

__all__ = [ "ClickBox", "ClickedBox" ]

class ClickBox( IClickBox ):
    def __init__(self, x: int, y: int, w: int, h: int) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h
    
    def check(self, x: int, y: int) -> bool:
        return self.x <= x <= self.w and self.y <= y <= self.h
    
    def __add__(self, other: "ClickBox") -> "ClickBox":
        x = min(self.x, other.x)
        y = min(self.y, other.y)
        w = max(self.x + self.w, other.x + other.w) - x
        h = max(self.y + self.h, other.y + other.h) - y
        return ClickBox(x, y, w, h)
    
    @property
    def tuple(self) -> Tuple[int, int, int, int]:
        return (self.x, self.y, self.w, self.h)
    


class ClickedBox( IClickedBox ):
    def __init__(self, x: int, y: int, bstate: int, clicked_name: List[str]) -> None:
        self.x = x
        self.y = y
        self.bstate = bstate
        self.clicked_names = clicked_name
        
        self.pressed                : List[str] = [ ]
        self.clicked                : List[str] = [ ]
        self.released               : List[str] = [ ]
        self.doubleClicked          : List[str] = [ ]
        self.tripleClicked          : List[str] = [ ]
        self.rightPressed           : List[str] = [ ]
        self.rightClicked           : List[str] = [ ]
        self.rightDoubleClicked     : List[str] = [ ]
        self.rightTripleClicked     : List[str] = [ ]
        self.middlePressed          : List[str] = [ ]
        self.middleClicked          : List[str] = [ ]
        self.middleDoubleClicked    : List[str] = [ ]
        self.middleTripleClicked    : List[str] = [ ]
        
        self.draging                : List[str] = [ ]
        
        self.init()
    
    def init(self) -> None:
        for name in self.clicked_names:
            if self.bstate & ClickStatus.PRESSED:
                self.pressed.append(name)
            if self.bstate & ClickStatus.CLICKED:
                self.clicked.append(name)
            if self.bstate & ClickStatus.RELEASED:
                self.released.append(name)
            if self.bstate & ClickStatus.DOUBLE_CLICKED:
                self.doubleClicked.append(name)
            if self.bstate & ClickStatus.TRIPLE_CLICKED:
                self.tripleClicked.append(name)
            if self.bstate & ClickStatus.RIGHT_PRESSED:
                self.rightPressed.append(name)
            if self.bstate & ClickStatus.RIGHT_CLICKED:
                self.rightClicked.append(name)
            if self.bstate & ClickStatus.RIGHT_DOUBLE_CLICKED:
                self.rightDoubleClicked.append(name)
            if self.bstate & ClickStatus.RIGHT_TRIPLE_CLICKED:
                self.rightTripleClicked.append(name)
            if self.bstate & ClickStatus.MIDDLE_PRESSED:
                self.middlePressed.append(name)
            if self.bstate & ClickStatus.MIDDLE_CLICKED:
                self.middleClicked.append(name)
            if self.bstate & ClickStatus.MIDDLE_DOUBLE_CLICKED:
                self.middleDoubleClicked.append(name)
            if self.bstate & ClickStatus.MIDDLE_TRIPLE_CLICKED:
                self.middleTripleClicked.append(name)
            
            if self.bstate & ClickStatus.DRAGING:
                self.draging.append(name)
        return

