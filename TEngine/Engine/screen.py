import curses
from typing import *

from ..components import EngineComponent
from ..Components.text import Text as TextInterface
from ..interfaces import Screen as ScreenInterface

__all__ = ["Screen"]

class Screen( ScreenInterface, EngineComponent ):
    __instance: Optional["Screen"] = None
    def __new__(cls, *args, **kwargs) -> "Screen":
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance
    
    def __init__(self) -> None:
        super().__init__()

    @property
    def size(self) -> Tuple[int, int]:
        return self.stdscr.getmaxyx()[::-1]
    
    @property
    def width(self) -> int:
        return self.size[0]
    
    @property
    def height(self) -> int:
        return self.size[1]
    
    def write(self, 
              msg: Union[str, TextInterface], 
              x: Optional[int] = None, 
              y: Optional[int] = None) -> TextInterface:
        msg = msg if isinstance(msg, TextInterface) else TextInterface(msg)
        
        if x is None and y is None:
            y, x = self.stdscr.getyx()
            
        msg.set_position(x, y)    
        try:
            self.stdscr.addstr( y, x, msg.__str__() )
        except curses.error as e:
            if self.logger is not None:
                self.logger.error(e.__str__())
            else:
                raise e    
        return msg
            
    def clear(self) -> None:
        self.stdscr.clear()
    
    def clear_line(self, y: int) -> None:
        self.stdscr.move(y, 0)
        self.stdscr.clrtoeol()
        
    def clrtobot(self) -> None:
        self.stdscr.clrtobot()
    
    def clrtoeol(self) -> None:
        self.stdscr.clrtoeol()
    
    def update(self) -> None:
        self.stdscr.refresh( )
    