import env
import re
import curses
from TEngine import TEngine
from TEngine import DebugLogger
from TEngine.dataTypes import ClickStatus
from TEngine.Engine.Component import Text


class Test(TEngine):
    def __init__(self) -> None:
        super().__init__()
        return
    
    def main(self) -> None:
        self._init( True )
        
        logger = DebugLogger( "logs/test.log" )
        self.setLogger(logger)
        
        self.logger.clear( )
        
        self.input.mouse.init( 0, True )
        
        drawing = False
        running = True
        
        while running:
            key = self.input.get( )
            
            if key == self.input.MOUSE_KEY:
                mouse = self.input.mouse.get( )
                
                if mouse.bstate & ClickStatus.PRESSED or mouse.bstate & ClickStatus.CLICKED:
                    drawing = True

                elif drawing and mouse.bstate & ClickStatus.DRAGING:
                    self.screen.write( "X", mouse.x, mouse.y )
                
                elif mouse.bstate & ClickStatus.RELEASED:
                    drawing = False
            
            elif key == self.input.Q:
                running = False
            
            self.screen.update( )
        
        
Test().main()
