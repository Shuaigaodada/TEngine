import curses
import traceback
import typing as T
from .. import dataTypes
from .component import Component, Text

__all__ = ["Screen"]

# screen
class Screen(Component):
    def __init__(self) -> None:
        super().__init__()
        return
    
    @property
    def size(self) -> dataTypes.ScreenSize:
        """ 获取屏幕大小 """
        return dataTypes.ScreenSize( *list( p - 1 for p in self.stdscr.getmaxyx( ) )[::-1] )
    @property
    def width(self) -> int:
        """ 获取屏幕宽度 """
        return self.size.width
    @property
    def height(self) -> int:
        """ 获取屏幕高度 """
        return self.size.height

    def write(self, string: str | Text, x: int = -1, y: int = -1, color: T.Tuple[int] | int | str = -1) -> Text:
        """绘制字符"""
        # 获取颜色的真正值
        if isinstance(color, tuple) or isinstance(color, list):
            colorAttrs = color[0]
            for attr in color[1:]:
                colorAttrs |= attr
        elif isinstance(color, str):
            from .engine import TEngine
            colorAttrs = TEngine.instance.renderer.getColor(color)
        else:
            colorAttrs = color
        
        string = string if isinstance( string, Text ) else Text( string )
        string._id = len(Text.controller.textList)
        
        # 如果没有指定位置，直接绘制在当前位置，手动实现printw
        if x == -1 and y == -1:
            # 启用颜色
            if colorAttrs != -1:
                self.stdscr.attron(colorAttrs)
            # 获取浮标当前位置
            y, x = self.stdscr.getyx()
            string.set_position( x, y )
            
            try:
                # 绘制字符
                self.stdscr.move( y, x )
                self.stdscr.addstr( string.__str__() )
            except curses.error as e:
            # 如果超出屏幕范围，抛出异常
                if self.logger is not None:
                    # 打印或记录错误信息
                    self.logger.error(e.__str__())

            # 关闭颜色
            if colorAttrs != -1:
                self.stdscr.attroff(colorAttrs)
            return string
        # 如果指定了位置，直接绘制在指定位置
        else:
            # 启用颜色
            if colorAttrs != -1:
                self.stdscr.attron(colorAttrs)
            string.set_position( x, y )
            # 字符绘制，如果超出屏幕范围，抛出异常
            try:
                self.stdscr.addstr( y, x, string.__str__() )
            except curses.error as e:
                if self.logger is not None:
                    # 打印或记录错误信息
                    self.logger.error(e.__str__())
                else:
                    raise e
                    
                    
            # 关闭颜色
            if colorAttrs != -1:
                self.stdscr.attroff(colorAttrs)
            return string
        
    
    def clear(self, __clear_cmpnt: bool = True) -> None:
        """清空屏幕"""
        self.stdscr.clear()
        self.stdscr.clrtobot
        self.stdscr.clrtoeol
        if __clear_cmpnt:
            Text.controller.textList.clear()
        return
    
    def update(self) -> None:
        """更新屏幕"""
        self.stdscr.refresh()
        return
