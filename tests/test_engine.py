import env
from typing import *
from TEngine import Engine

class Test( Engine ):
    def __init__( self ) -> None:
        self.test_init_attrs( )
        self.test_screen( )
        self.test_input( )
    
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
        text = self.input.getline( "input your message: ", command={23: self.__clear} )
        self.screen.write( "you typed: " + text, 0, 6 )
        self.screen.update()
        self.input.getch()
        self.screen.clear()
    
    def test_renderer( self ) -> None:
        pass
        
    def __clear( self, string: List[str], index: int ) -> int:
        sstring = "".join(string)
        lsstring = sstring.split( " " )
        if lsstring.pop() == " ":
            lsstring.pop( )
        
        string.clear()
        string.extend( list( " ".join(lsstring) ) )
        return len(string)
            
        

if __name__ == "__main__":
    Test( )
