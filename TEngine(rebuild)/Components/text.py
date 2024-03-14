import unicodedata
from typing import List, Union, Optional
from ..Engine.clickbox import ClickBox
from ..interfaces import Text as TextInterfaces

__all__ = [ "Text" ]

class Text( TextInterfaces ):
    __list: List["Text"] = []
    
    def __new__( cls, *args, **kwargs ) -> "Text":
        cls.__list.append( cls )
        return super().__new__( cls )
    
    def __init__(self, string: str) -> None:
        self.__str = string
        self.__x   = -1
        self.__y   = -1
        self._id   = len(Text.__list)
        return
    
    @property
    def click_box( self ) -> ClickBox:
        return ClickBox( self.__x, self.__y, self.__x + len( self ), self.__y )

    def set_clickbox(self, name: str) -> None:
        # TODO: 实现鼠标接口，然后实例鼠标并设置点击框
        # mouse = Mouse( )
        # box = self.click_box
        # mouse.set_cb( name, box.x, box.y, box.w, box.h )
        pass
    
    def set_position(self, x: int, y: int) -> None:
        self.__x = x
        self.__y = y
    
    def __str__( self ) -> str:
        return self.__str
    def __repr__(self) -> str:
        return self.__str
    def __iter__( self ) -> iter:
        return iter(self.__str)
        
    def __len__( self ) -> int:
        return sum(2 if unicodedata.east_asian_width(c) in 'FW' else 1 for c in self.__str)
    
    def find(self, item: Union[str, int]) -> Union["Text", List["Text"]]:
        if isinstance( item, int ):
            try:
                return Text.__list[item]
            except IndexError as e:
                raise e
        elif isinstance( item, str ):
            return [i for i in Text.__list if item in str(i)]
        else:
            raise ValueError("item must be str or int")
    
    def findid(self, id: int) -> Optional["Text"]:
        for text in Text.__list:
            if text._id == id:
                return text
        return None
