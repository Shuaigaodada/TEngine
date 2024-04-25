import env
from typing import *
from TEngine import Engine
from TEngine.components import CryptCreator

class Test( Engine ):
    def __init__( self ) -> None:
        self.test_init_attrs( )   # work
        self.test_screen( )       # work
        self.test_input( )        # work
        self.test_renderer( )     # work
        self.test_mouse( )        # work
        self.test_cryptcreator( ) # work
        self.test_logger( )       # work
        
        # self.quit()
    
    def test_logger( self ) -> None:
        self.set_logger( "./tests/test.log" )
        self.logger.info( "this file logger was running" )
        self.logger.warning( "test warning" )
        self.logger.error( "test error" )
        
        self.screen.write( "logger write done", 0, 0 )
        self.screen.update()
        self.input.getch()
    
    def test_cryptcreator( self ) -> None:
        crypt = CryptCreator( )
        crypt.sign( )
        crypt.write( "./tests/cert.pem", "./tests/key.pem" )
        self.screen.write( "crypt signed", 0, 0 )
        self.screen.update()
        self.input.getch()
    
    def test_init_attrs( self ) -> None:
        self.init_engine( )
        assert self.screen      != None
        assert self.input       != None
        assert self.renderer    != None
        assert self.stdscr      != None
        assert self.width       != None
        assert self.height      != None
        assert self.size        != None
    
    def test_screen( self ) -> None:
        self.screen.write( "Hello World" )
        self.screen.write( "Hello World", 0, 1 )
        self.screen.move( 0, 2 )
        self.screen.write("need clears characters")
        self.screen.write("\nneed clears characters")
        self.screen.update()
        self.input.getch( )
        self.screen.clrtobot( 0, 2 )
        self.screen.write( "clear to bottom from 0, 2 position" )
        self.screen.update()
        self.input.getch( )
        self.screen.clrtoeol( 0, 2 )
        self.screen.update()
        self.input.getch()
        self.screen.write( f"screen size: {self.screen.size}" )
        self.input.getch()
        self.screen.clear()
    
    def test_input( self ) -> None:
        self.screen.write( "test input.getch -> int", 0, 0 )
        key = self.input.getch( )
        self.screen.write( "you pressed: " + str(key), 0, 1 )
        
        self.screen.write("test input.getwch -> str", 0, 2)
        self.screen.update()
        
        key = self.input.getwch( )
        
        self.screen.write( "you pressed: " + str(key), 0, 3 )
        self.screen.write( "test input.getline -> str", 0, 4 )
        self.screen.update()
        self.screen.move( 0, 5 )
        text = self.input.getline( "input your message: ", command={23: self.__clrcmd} )
        self.screen.write( "you typed: " + text, 0, 6 )
        self.screen.update()
        self.input.getch()
        self.screen.clear()
    
    def test_renderer( self ) -> None:
        self.renderer.create( "1", "#FFFFFF" )
        self.renderer.start("1")
        self.screen.write("white text")
        self.renderer.stop()
        
        self.renderer.start(("#00FF00", "#000000"))
        self.renderer.start(("#00FFFF", "#000000"))
        self.screen.write("cache test", 0, 1)
        self.renderer.stop()
        
        self.screen.update()
        self.input.getch()
        
        self.screen.clear()
        
        self.renderer.save( "./tests/cache.json" )
        self.renderer.load( "./tests/cache.json" )
        
        self.renderer.start("1")
        self.screen.write("white text")
        self.renderer.stop()
        
        self.input.getch()
        self.screen.clear()
    
    def test_mouse( self ) -> None:
        self.input.mouse.init( drag = True )
        
        self.screen.write( "[button]", 0, 0 ).set_clickbox( "button-1" )
        X_txt = self.screen.write( "X", 10, 0 )
        X_txt.set_clickbox( "X" )
        
        draging = False
        
        while True:
            key = self.input.getch()
            if key == self.input.Q:
                break
            if key == self.input.MOUSE_KEY:
                event = self.input.mouse.get( )
                for name in event.pressed + event.clicked:
                    if name == "button-1":
                        self.screen.write( "button clicked", 0, 1 )
                        self.screen.update()
                    if name == "X":
                        draging = True
                
                for name in event.released:
                    if name == "X":
                        draging = False
                
                if draging:
                    X_txt.replace( event.x, event.y )
                    self.screen.update()
        
        self.input.mouse.quit()
                
    def __clrcmd(self, istr: list[str], curpos: int, idx: int) -> tuple[int, int]:
        istr.clear()
        return 0, 0
    
    

if __name__ == "__main__":
    Test( )