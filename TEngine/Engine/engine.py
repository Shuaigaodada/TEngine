import sys
import atexit
import curses
from typing import *
from .input import Input as IInput
from .screen import Screen as IScreen
from .renderer import Renderer as IRenderer
from ..Components.filelogger import FileLogger as IFileLogger
from ..interfaces import Engine as IEngine

class Engine(IEngine):
    __instance: Optional["Engine"] = None
    def __new__(cls, *args, **kwargs) -> "Engine":
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__init( )
        return cls
    
    def __init(self) -> None:
        self.stdscr: Optional[curses.window] = None
        self.logger: Optional[IFileLogger] = None
        
        self.renderer: IRenderer = IRenderer()
        self.screen: IScreen = IScreen()
        self.input: IInput = IInput()
    
    def set_logger(self) -> None:
        self.logger = IFileLogger( )
        self.renderer.set_logger(self.logger)
        self.screen.set_logger(self.logger)
        self.input.set_logger(self.logger)
        self.input.mouse.set_logger(self.logger)
        
    def set_screen( self, stdscr: curses.window ) -> None:
        self.stdscr = stdscr
        self.renderer.set_screen(stdscr)
        self.screen.set_screen(stdscr)
        self.input.set_screen(stdscr)
        self.input.mouse.set_screen(stdscr)
        
    def init_engine(self, __reg: bool = True) -> None:
        self.set_screen( curses.initscr() )
        curses.noecho           ( )
        curses.cbreak           ( )
        curses.curs_set         ( 0 )
        self.stdscr.keypad      ( True )
        if __reg:
            atexit.register     ( self.quit )
    
    def quit(self) -> None:
        self.stdscr.keypad      ( False )
        self.screen.clear       ( )
        curses.echo             ( )
        curses.nocbreak         ( )
        curses.endwin           ( )
        print("\033[?1003l", end="", flush=True)
        
        if self.logger is not None:
            try: self.logger.info("Engine quit")
            finally:
                try:                self.logger.close()
                except Exception:   pass
        return

    @property
    def size( self ) -> Tuple[int, int]:
        return self.screen.size
    
    @property
    def width( self ) -> int:
        return self.screen.width
    
    @property
    def height( self ) -> int:
        return self.screen.height


