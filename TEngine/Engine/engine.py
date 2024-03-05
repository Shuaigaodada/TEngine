# 引擎主文件
__all__ = ["TEngine"]

import sys
import atexit
import curses
import traceback
import typing as T
from .. import dataTypes
from .input import Input
from .screen import Screen
from .renderer import Renderer
from .fileLogger import DebugLogger

"""
TEngine应当有几个类实例
    screen对象: 用于绘制字符
    renderer对象: 用于绘制颜色色块
    input对象: 用于获取输入
    mouse对象: 用于获取鼠标输入
    logger对象: 用于记录日志
"""

class TEngine:
    instance: "TEngine" = None
    def __init__(self) -> None:
        self.stdscr  :  T.Optional[curses.window]   = None
        self.logger  :  DebugLogger  = None if not DebugLogger.instance else DebugLogger.instance[0]
        
        self.renderer:  Renderer     = Renderer    (      )
        self.screen  :  Screen       = Screen      (      )
        self.input   :  Input        = Input       (      )
        
        TEngine.instance             = self
        return
    
    def setLogger(self, logger: DebugLogger) -> None:
        """设置日志记录器"""
        self.logger                 = logger    # self      logger
        self.renderer.setLogger     ( logger )  # renderer  logger
        self.screen.setLogger       ( logger )  # screen    logger
        self.input.setLogger        ( logger )  # input     logger
        self.input.mouse.setLogger  ( logger )  # mouse     logger
        return
    
    def SetScreen(self, stdscr: curses.window) -> None:
        """设置新的屏幕为绘制屏幕"""
        self.stdscr                 = stdscr    # self      stdscr
        self.renderer.setScreen     ( stdscr )  # renderer  stdscr
        self.screen.setScreen       ( stdscr )  # screen    stdscr
        self.input.setScreen        ( stdscr )  # input     stdscr
        self.input.mouse.setScreen  ( stdscr )  # mouse     stdscr
        return 
    
    def _init(self, registerExit: bool = True) -> None:
        """
        初始化引擎, 进入cbreak和noecho模式, 设置光标不可见, 初始化颜色。
        
        参数:
            registExit: bool = True, 是否注册退出事件
        """
        self.stdscr = \
        curses.         initscr             (               )           # init screen
        curses.         cbreak              (               )           # start cbreak mode
        curses.         noecho              (               )           # start noecho mode
        curses.         curs_set            (       0       )           # hide cursor
        curses.         start_color         (               )           # start color mode
        self.           SetScreen           (  self.stdscr  )           # set stdscr
        self.input.     init                (               )           # init keys
        self.stdscr.    keypad              (      True     )           # enable keypad
        if registerExit:
            # 注册退出事件
            atexit.     register            (   self.exit   )           # register exit event
            
        return
        
    def exit(self) -> None:
        """
        卸载引擎, 退出cbreak和noecho模式, 显示光标。
        """
        curses.curs_set(1)
        curses.nocbreak()
        curses.echo()
        curses.endwin()
        print("\033[?1003l")
        
        try:
            exc_type, exc_value, exc_traceback = sys.last_type, sys.last_value, sys.last_traceback
        except AttributeError:
            exc_type, exc_value, exc_traceback = None, None, None
        
        # 关闭日志并且判断是否有异常并输出
        if self.logger is not None:
            if DebugLogger.exceptions:
                for exception in DebugLogger.exceptions:
                    exception_string = traceback.format_exception(exception.type, exception.value, exception.traceback)
                    self.logger.error( ''.join( exception_string ) )
            elif exc_type is not None:
                self.logger.error( ''.join( traceback.format_exception( exc_type, exc_value, exc_traceback ) ) )
            else:
                self.logger.info("Exited successfully.")
            self.logger.close()
        return
    

    @property
    def size( self ) -> dataTypes.ScreenSize:
        """获取屏幕大小"""
        return self.screen.size
    @property
    def width( self ) -> int:
        """获取屏幕宽度"""
        return self.screen.width
    @property
    def height( self ) -> int:
        """获取屏幕高度"""
        return self.screen.height
    
    
    
