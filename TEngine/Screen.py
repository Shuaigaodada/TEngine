import traceback
import typing as T
import unicurses as curses
from Component import Component

# screen
class Screen(Component):
    def __init__(self, stdscr: int) -> None:
        super().__init__()
        # 用于绘制字符的窗口
        self.stdscr: int = stdscr
        return

    def Write(self, string: str, x: int = -1, y: int = -1, color: T.Tuple[int] | int = 0) -> None:
        """绘制字符"""
        # 获取颜色的真正值
        if type(color) is tuple:
            colorAttrs = color[0]
            for attr in color[1:]:
                colorAttrs |= attr
        else:
            colorAttrs = color
        
        # 如果没有指定位置，直接绘制在当前位置，手动实现printw
        if x == -1 and y == -1:
            # 启用颜色
            curses.attron(colorAttrs)
            # 获取浮标当前位置
            y, x = curses.getyx(self.stdscr)
            # 获取屏幕的的大小
            height, width = curses.getmaxyx(self.stdscr)
            # 逐字符绘制
            for char in string:
                # 检查是否需要换行
                if x >= width:
                    x = 0
                    y += 1
                # 如果超出屏幕范围，抛出异常
                if y >= height and self.logger is not None:
                    # 获取当前的堆栈信息
                    stack_info = traceback.extract_stack()
                    # 获取调用这个函数的上一级调用信息
                    last_call = stack_info[-2]
                    # 打印或记录错误信息
                    self.logger.Error(f"Out of screen range in {last_call.name} at {last_call.filename}:{last_call.lineno}")
                    return
                curses.mvaddwstr(y, x, char)
                x += 1
            # 关闭颜色
            curses.attroff(colorAttrs)
            return
        # 如果指定了位置，直接绘制在指定位置
        else:
            # 启用颜色
            curses.attron(colorAttrs)
            # 字符绘制，如果超出屏幕范围，抛出异常
            if curses.mvaddwstr(y, x, string) == curses.ERR and self.logger is not None:
                # 获取当前的堆栈信息
                stack_info = traceback.extract_stack()
                # 获取调用这个函数的上一级调用信息
                last_call = stack_info[-2]
                # 打印或记录错误信息
                self.logger.Error(f"Out of screen range in {last_call.name} at {last_call.filename}:{last_call.lineno}")
            # 关闭颜色
            curses.attroff(colorAttrs)
            return
        
    
    def Clear(self) -> None:
        """清空屏幕"""
        curses.wclear(self.stdscr)
        return
    
