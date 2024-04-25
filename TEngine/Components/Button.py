from ..interfaces import Screen as IScreen
from ..interfaces import Renderer as IRenderer

class Button:
    def __init__(self,x: int, y: int, w: int, h: int) -> None:
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        
        self._screen = IScreen( )
        self._renderer = IRenderer( )
        

    
        

