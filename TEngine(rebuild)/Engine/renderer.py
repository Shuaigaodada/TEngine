import json
from typing import *

from ..components import EngineComponent
from ..interfaces import Renderer as RendererInterfaces

class Renderer( RendererInterfaces ):
    __instance: "Renderer" = None
    def __new__( cls, *args, **kwargs ) -> "Renderer":
        if cls.__instance is None:
            cls.__instance = super().__new__( cls )
        return cls.__instance
    
    def __init__(self) -> None:
        super( ).__init__( )
        
        self.cache_color: Dict[str, int]
        self.pair       : Dict[str, int]
        self.index      : int
        self.oncolor    : List[int]
        
        if self.cache_color is None:
            self.cache_color = {}
        if self.pair is None:
            self.pair = {}
        if self.index is None:
            self.index = 1
        if self.oncolor is None:
            self.oncolor = []
    
    def create(self, name: str, fg: str, bg: str = "#000000") -> None:
        return super().create(name, fg, bg)
