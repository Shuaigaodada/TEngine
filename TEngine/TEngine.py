# 引擎主文件
__all__ = ["TEngine"]

import sys
import atexit
import unicurses as curses
from .fileLogger import DebugLogger

class TEngine:
    def __init__(self) -> None:
        self.mainWin = curses.stdscr
        self.logger: DebugLogger = None
        return
    
    def init(self, registerExit: bool = True) -> None:
        """
        初始化引擎, 进入cbreak和noecho模式, 设置光标不可见, 初始化颜色。
        
        参数:
            registExit: bool = True, 是否注册退出事件
        """
        curses.initscr()
        curses.cbreak()
        curses.noecho()
        curses.curs_set(0)
        curses.start_color()
        
        if registerExit:
            # 注册退出事件
            atexit.register(self.exit)

        self.mainWin = curses.stdscr
        
        return
        
    def exit(self) -> None:
        """
        卸载引擎, 退出cbreak和noecho模式, 显示光标。
        """
        curses.curs_set(1)
        curses.nocbreak()
        curses.echo()
        curses.endwin()
        
        excType, excValue, excTraceback = sys.exc_info()
        if self.logger is not None:
            if excType is not None:
                self.logger.error("An error occurred:", excType, excValue, excTraceback)
            else:
                self.logger.info("Exited successfully.")
            self.logger.close()
        
        return
    
    def nodelayMode(self, mode: bool) -> None:
        """
        设置是否阻塞输入。
        
        参数:
            mode: bool, 是否阻塞输入
        """
        curses.nodelay(self.mainWin, mode)
        return
        
    

