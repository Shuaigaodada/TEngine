import json
import curses
from typing import *
from typing import Tuple

from .engine_component import EngineComponent
from ..interfaces import Renderer as IRenderer

class Renderer( IRenderer, EngineComponent ):
    __instance: Optional["Renderer"] = None
    def __new__( cls, *args, **kwargs ) -> "Renderer":
        if cls.__instance is None:
            cls.__instance = super().__new__( cls )
            cls.__instance.__init( )
        return cls.__instance
    
    def __init(self) -> None:
        super( ).__init__( )
        
        self.cache_color        : Dict[str, int]    = {}
        self.pairs              : Dict[str, int]    = {}
        self.index              : int               = 1
        self.oncolor            : List[int]         = []
    
    def create(self, name: str, fg: str, bg: str = "#000000") -> None:
        fgcolor = self.push_cache( fg )
        bgcolor = self.push_cache( bg )
        
        self.pairs[name] = self.index
        curses.init_pair( self.index, fgcolor, bgcolor )
        self.index += 1
        return
    
    def start(self, *__name: Tuple[Union[str, int]]) -> None:
        for pair_name in __name:
            if isinstance( pair_name, int ):
                self.stdscr.attron( pair_name )
                self.oncolor.append( pair_name )
            else:
                pair = self.pairs.get( pair_name )
                cpair = curses.color_pair( pair )
                self.stdscr.attron( cpair )
                self.oncolor.append( pair_name )

    def stop(self, *__name: Tuple[str, int]) -> None:
        if not __name:
            __name = self.oncolor
        
        for pair_name in __name:
            if isinstance(pair_name, int):
                self.stdscr.attroff( pair_name )
                self.oncolor.remove( pair_name )
            else:
                pair = self.pairs.get( pair_name )
                cpair = curses.color_pair( pair )
                self.stdscr.attroff( cpair )
                self.oncolor.remove( pair_name )
    
    def save(self, __path: str) -> None:
        with open( __path, "w" ) as fp:
            json.dump( {
                "cache_color": self.cache_color,
                "pairs": self.pairs,
                "index": self.index
                }, fp, indent=4 )
    
    def load(self, __path: str) -> None:
        with open( __path, "r" ) as fp:
            data: Dict = json.load( fp )
            self.cache_color = data.get( "cache_color" )
            self.pairs = data.get( "pairs" )
            self.index = data.get( "index" )

    def push_cache(self, __name: str) -> int:
        if __name in self.cache_color:
            return self.cache_color.get( __name )
        self.cache_color[__name] = self.index
        curses.init_color( self.index, *self.convert(__name))
        self.index += 1
        return self.index - 1

    def convert(self, __hex: str) -> int:
        R, G, B = int(__hex[1:3], 16), int(__hex[3:5], 16), int(__hex[5:7], 16)
        R = int(R * 1000 / 255)
        G = int(G * 1000 / 255)
        B = int(B * 1000 / 255)
        return R, G, B

    BOLD = curses.A_BOLD
    DIM = curses.A_DIM
    REVERSE = curses.A_REVERSE
    BLINK = curses.A_BLINK
    UNDERLINE = curses.A_UNDERLINE
    STANDOUT = curses.A_STANDOUT
    NORMAL = curses.A_NORMAL