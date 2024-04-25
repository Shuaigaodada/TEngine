import curses
from typing import *

from .engine_component import EngineComponent
from ..Components.text import Text as IText
from ..interfaces import Screen as IScreen
from .renderer import Renderer as IRenderer

__all__ = ["Screen"]

class Screen( IScreen, EngineComponent ):
    __instance: Optional["Screen"] = None
    def __new__(cls, *args, **kwargs) -> "Screen":
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__init( )
        return cls.__instance
    
    def __init(self) -> None:
        super().__init__()
        self._renderer = IRenderer( )

    @property
    def size(self) -> Tuple[int, int]:
        return tuple(
            map(
                lambda n: n - 1,
                self.stdscr.getmaxyx()[::-1]
                )
            )
    
    @property
    def width(self) -> int:
        return self.size[0]
    
    @property
    def height(self) -> int:
        return self.size[1]
    
    def write(self, 
              msg: Union[str, IText], 
              x: Optional[int] = None, 
              y: Optional[int] = None) -> IText:
        msg = msg if isinstance(msg, IText) else IText(msg)
        
        if x is None and y is None:
            y, x = self.stdscr.getyx()
            
        msg.set_position(x, y)
        try:
            self.stdscr.move(y, x)
            self.stdscr.addstr( msg.__str__() )
        except curses.error as e:
            if self.logger is not None:
                self.logger.error(e.__str__())
            else:
                raise e    
        return msg
            
    def clear(self) -> None:
        self.stdscr.clear()
    
    def _write( self, msg: str, x: int, y: int ) -> None:
        self.stdscr.move(y, x)
        self.stdscr.addstr(msg)
    
    def move(self, __x: int, __y: int) -> None:
        self.stdscr.move(__y, __x)
        
    def clrtobot(self, __x: Optional[int] = None, __y: Optional[int] = None) -> None:
        """`clear to bottom`清除从光标当前位置到屏幕底部的所有行。"""
        if __x is not None and __y is not None:
            self.stdscr.move(__y, __x)
        self.stdscr.clrtobot()
        
    
    def clrtoeol(self, __x: Optional[int] = None, __y: Optional[int] = None) -> None:
        """`clear to end of line`清除从光标当前位置到行尾的所有字符。"""
        if __x is not None and __y is not None:
            self.stdscr.move(__y, __x)
        self.stdscr.clrtoeol()
    
    def update(self) -> None:
        self.stdscr.refresh( )
    