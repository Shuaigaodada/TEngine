from .fileLogger import DebugLogger


class Component:
    def __init__(self) -> None:
        self.logger: DebugLogger = None if not DebugLogger.instance else DebugLogger.instance[0]
        return

    def SetLogger(self, logger: DebugLogger) -> None:
        """设置日志记录器"""
        self.logger = logger
        return
    
    def SetScreen(self, stdscr: int) -> None:
        """重置绘制的屏幕"""
        self.stdscr = stdscr
    