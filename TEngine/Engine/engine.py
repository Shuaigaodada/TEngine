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
    def __new__(cls, *args, **kwargs):
        instance = super().__new__( cls )
        instance.__init()
        return instance
    
    def __init(self) -> None:
        self.stdscr: Optional[curses.window] = None
        self.logger: Optional[IFileLogger] = None
        
        self.renderer: IRenderer =      IRenderer   ( )
        self.screen: IScreen =          IScreen     ( )
        self.input: IInput =            IInput      ( )
    
    def set_logger(self, path: Optional[str] = None) -> None:
        self.logger = IFileLogger       ( path )
        self.renderer.set_logger        ( self.logger )
        self.screen.set_logger          ( self.logger )
        self.input.set_logger           ( self.logger )
        self.input.mouse.set_logger     ( self.logger )
        
    def set_screen( self, stdscr: curses.window ) -> None:
        self.stdscr = stdscr
        self.renderer.set_screen        ( stdscr )
        self.screen.set_screen          ( stdscr )
        self.input.set_screen           ( stdscr )
        self.input.mouse.set_screen     ( stdscr )
        
    def init_engine(self, __reg: bool = True) -> None:
        self.set_screen( curses.initscr() )
        curses.noecho           ( )
        curses.cbreak           ( )
        curses.curs_set         ( 0 )
        curses.start_color      ( )
        self.stdscr.keypad      ( True )
        if __reg:
            atexit.register     ( self.quit )
    
    def quit(self) -> None:
        self.stdscr.keypad      ( False )
        self.screen.clear       ( )
        curses.echo             ( )
        curses.nocbreak         ( )
        curses.endwin           ( )
        print("\033[?1003l", end="", flush=True) # close mouse tracking
        
        if self.logger is not None:
            try: self.logger.info("Engine quit")
            except ValueError: pass # ValueError: I/O operation on closed file
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


