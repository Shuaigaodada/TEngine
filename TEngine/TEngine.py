# 引擎主文件
__all__ = ["TEngine"]

import sys
import atexit
import typing as T
import unicurses as curses
from Input import Input
from Screen import Screen
from Renderer import Renderer
from fileLogger import DebugLogger

"""
TEngine应当有几个类实例
    screen对象: 用于绘制字符
    renderer对象: 用于绘制颜色色块
    input对象: 用于获取输入
    mouse对象: 用于获取鼠标输入
    logger对象: 用于记录日志
"""

class TEngine:
    def __init__(self) -> None:
        self.stdscr  :  int          = curses.stdscr
        self.logger  :  DebugLogger  = None if not DebugLogger.instance else DebugLogger.instance[0]
        self.renderer:  Renderer     = Renderer()
        self.screen  :  Screen       = Screen(self.stdscr)
        self.input   :  Input        = Input(self.stdscr)
        return
    
    def SetLogger(self, logger: DebugLogger) -> None:
        """设置日志记录器"""
        self.logger = logger
        self.renderer.SetLogger(logger)
        self.screen.SetLogger(logger)
        self.input.SetLogger(logger)
        self.input.mouse.SetLogger(logger) 
        return
    
    def SetScreen(self, stdscr: int) -> None:
        """设置新的屏幕为绘制屏幕"""
        self.renderer.SetScreen(stdscr)
        self.screen.SetScreen(stdscr)
        self.input.SetScreen(stdscr)
        self.stdscr = stdscr
        return 
    
    def Init(self, registerExit: bool = True) -> None:
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
        curses.keypad(self.stdscr, True)
        
        if registerExit:
            # 注册退出事件
            atexit.register(self.Exit)
        return
        
    def Exit(self) -> None:
        """
        卸载引擎, 退出cbreak和noecho模式, 显示光标。
        """
        curses.curs_set(1)
        curses.nocbreak()
        curses.echo()
        curses.endwin()
        
        # 获取异常信息
        excType, excValue, excTraceback = sys.exc_info()
        
        # 关闭日志并且判断是否有异常并输出
        if self.logger is not None:
            if excType is not None:
                self.logger.Error("An error occurred:", excType, excValue, excTraceback)
            else:
                self.logger.Info("Exited successfully.")
            self.logger.Close()
        return
    
    def NoDelayMode(self, mode: bool) -> None:
        """
        设置是否阻塞输入。
        
        参数:
            mode: bool, 是否阻塞输入
        """
        curses.nodelay(self.stdscr, mode)
        return
    


    

