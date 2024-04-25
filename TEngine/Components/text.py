import unicodedata
from typing import List, Union, Optional
from ..Engine.clickbox import ClickBox
from ..interfaces import Text as IText
from ..Engine.mouse import Mouse as IMouse
from ..Engine.renderer import Renderer as IRenderer

__all__ = [ "Text" ]

class Text( IText ):
    """更好的管理文本"""
    __list: List["Text"] = []
    
    def __new__( cls, *args, **kwargs ) -> "Text":
        cls.__list.append( cls )
        return super().__new__( cls )
    
    def __init__(self, string: str) -> None:
        self.__str = string
        self.__x   = -1
        self.__y   = -1
        self.__attr= []
        self._id   = len(Text.__list)
        self.__bn  = "text"
        return
    
    @property
    def click_box( self ) -> ClickBox:
        return ClickBox( self.__x, self.__y, self.__x + len( self ) - 1, self.__y )

    def set_clickbox(self, __name: str) -> None:
        """给文本设置点击框"""
        mouse = IMouse()
        box = self.click_box
        mouse.set_cb( __name, box.x, box.y, box.w, box.h )
        self.__bn = __name
    
    def replace( self, new_x: int, new_y: int ) -> None:
        from ..Engine.screen import Screen as IScreens

        screen = IScreens( )
        renderer = IRenderer( )
        
        screen._write( " ", self.__x, self.__y )
        if self.__attr:
            renderer.start( self.__attr )
        screen.write( self, new_x, new_y ).set_clickbox( self.__bn )
        if self.__attr:
            renderer.stop( self.__attr )
    
    def set_position(self, __x: int, __y: int) -> None:
        """设置文本位置"""
        self.__x = __x
        self.__y = __y
    
    def _set_attr(self, __attr: List[int]) -> None:
        """设置文本属性"""
        self.__attr = __attr
    
    def __str__( self ) -> str:
        return self.__str
    def __repr__(self) -> str:
        return self.__str
    def __iter__( self ) -> iter:
        return iter(self.__str)
        
    def __len__( self ) -> int:
        return sum(2 if unicodedata.east_asian_width(c) in 'FW' else 1 for c in self.__str)
    
    def find(self, __item: Union[str, int]) -> Union["Text", List["Text"]]:
        """查找文本，可以使用索引或者字符串查找"""
        if isinstance( __item, int ):
            try:
                return Text.__list[__item]
            except IndexError as e:
                raise e
        elif isinstance( __item, str ):
            return [i for i in Text.__list if __item in str(i)]
        else:
            raise ValueError("item must be str or int")
    
    def findid(self, __id: int) -> Optional["Text"]:
        """使用id查找文本"""
        for text in Text.__list:
            if text._id == __id:
                return text
        return None
