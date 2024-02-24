import curses
import typing as T
from .. import dataTypes
import unicodedata as ucd
from .fileLogger import DebugLogger
__all__ = ["Component"]

class Component:
    def __init__(self) -> None:
        self.logger: T.Optional[DebugLogger] = None if not DebugLogger.instance else DebugLogger.instance[0]
        self.stdscr: T.Optional[curses.window] = None
        return

    def setLogger(self, logger: DebugLogger) -> None:
        """设置日志记录器"""
        self.logger = logger
        return
    
    def setScreen(self, stdscr: curses.window) -> None:
        """重置绘制的屏幕"""
        self.stdscr = stdscr
        
class Text:
    class Controller:
        def __init__(self) -> None:
            self.textList: T.List[Text] = list()
            
        def find(self, string: str) -> T.List["Text"]:
            match_text = list()
            for text in self.textList:
                if string in text.__str:
                    match_text.append(text)
            return match_text
        
        def findByIndex(self, index: int) -> "Text":
            return self.textList[index]
        
        def findById(self, id: int) -> T.Optional["Text"]:
            for text in self.textList:
                if text._id == id:
                    return text
            return None
    
    controller: Controller = Controller()
    
    @staticmethod
    def find( string: str ) -> T.List["Text"]:
        return Text.controller.find(string)
    
    @staticmethod
    def findByIndex( index: int ) -> "Text":
        return Text.controller.findByIndex(index)
    
    @staticmethod
    def findById( id: int ) -> T.Optional["Text"]:
        return Text.controller.findById(id)
    
    def __init__(self, string: str) -> None:
        self.__str = string
        self.__x   = -1
        self.__y   = -1
        self.__len = sum(2 if ucd.east_asian_width(c) in 'FW' else 1 for c in self.__str)
        self._id   = -1
        
        Text.controller.textList.append( self )
        return
    
    @property
    def click_box( self ) -> dataTypes.BoxSize:
        return dataTypes.BoxSize( self.__x, self.__y, self.__x + self.__len - 1, self.__y)
    
    def set_clickbox( self, name: str, call: T.Callable = None, *args, **kwargs ) -> None:
        from .TEngine import TEngine
        noneArgs = (None, None, None)
        TEngine.instance.input.mouse.set_clickbox( name, self, *noneArgs, call, *args, **kwargs )
        return self

    def merge_clickbox( self, name: str ) -> None:
        from .TEngine import TEngine
        TEngine.instance.input.mouse.merge_clickbox( name, self )
        return self
    
    def __str__(self) -> str:
        return self.__str
    def __repr__(self) -> str:
        return self.__str__()
    def __iter__( self ) -> T.Iterator[ str ]:
        return iter( self.__str )
    
    
    
    def set_position(self, x: int, y: int) -> None:
        self.__x = x
        self.__y = y
        return self
    
    
    