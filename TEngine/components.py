from typing import *
from .interfaces import FileLogger
from curses import window as cwindow

class EngineComponent:
    def __init__( self, stdscr: Optional[cwindow] = None, logger: Optional[FileLogger] = None ) -> None:
        self.logger: Optional[FileLogger] = logger
        self.stdscr: Optional[cwindow] = stdscr
        return
    
    def set_logger( self, logger: FileLogger ) -> None:
        self.logger = logger
        return
    
    def set_screen( self, stdscr: cwindow ) -> None: 
        self.stdscr = stdscr
