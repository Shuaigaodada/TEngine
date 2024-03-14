import json
import curses
from typing import *
from typing import Tuple

from ..components import EngineComponent
from ..interfaces import Renderer as RendererInterfaces

class Renderer( RendererInterfaces, EngineComponent ):
    __instance: Optional["Renderer"] = None
    def __new__( cls, *args, **kwargs ) -> "Renderer":
        if cls.__instance is None:
            cls.__instance = super().__new__( cls )
        return cls.__instance
    
    def __init__(self) -> None:
        super( ).__init__( )
        
        self.cache_color: Dict[str, int]
        self.pairs      : Dict[str, int]
        self.index      : int
        self.oncolor    : List[int]
        
        if self.cache_color is None:
            self.cache_color = {}
        if self.pairs is None:
            self.pairs = {}
        if self.index is None:
            self.index = 1
        if self.oncolor is None:
            self.oncolor = []
    
    def create(self, name: str, fg: str, bg: str = "#000000") -> None:
        fgcolor = self.push_cache( fg )
        bgcolor = self.push_cache( bg )
        
        self.pairs[name] = self.index
        curses.init_pair( self.index, fgcolor, bgcolor )
        self.index += 1
        return
    
    def start(self, *__name: Tuple[str]) -> None:
        for pair_name in __name:
            pair = self.pairs.get( pair_name )
            cpair = curses.color_pair( pair )
            self.stdscr.attron( cpair )
            self.oncolor.append( pair_name )

    def stop(self, *__name: Tuple[str]) -> None:
        if not __name:
            __name = self.oncolor
        
        for pair_name in __name:
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