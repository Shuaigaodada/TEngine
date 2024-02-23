# 这是一个用于debug的日志记录器
import os
import sys
import time
import typing as T

__all__ = ["DebugLogger"]

class ExceptionInfo:
    type: T.Type[BaseException]
    value: BaseException
    traceback: T.Any

class DebugLogger:
    instance = []
    
    def __init__(self, logFile: str = None) -> None:
        """初始化日志记录器

        参数:
            logFile (str): 日志文件路径
        """
        if logFile is None:
            logFile = os.path.join(os.getcwd(), "logs", time.strftime("%Y-%m-%d %H:%M:%S") + ".log")
            os.makedirs(os.path.dirname(logFile), exist_ok=True)
            open(logFile, "w").close()
        
        self.logFile = logFile
        self.open(self.logFile)
        self.instance.append(self)
        
        self.auto_update: bool = False
        
        return
    
    def update(self) -> None:
        """更新日志记录器"""
        self.close()
        self.open(self.logFile, "a")
        return
    
    def open(self, filePath: str, mode = "w") -> None:
        """打开日志文件"""
        self.logFile = filePath
        self.logFileHandler = open(self.logFile, mode)
        return
    def close(self) -> None:
        """关闭日志文件"""
        try:
            self.logFileHandler.close()
        except ValueError:
            pass
        return
    
    def info(self, *messages: T.Tuple[str], sep: str = ' ') -> None:
        """记录信息

        参数:
            message (str): 信息
            sep (str): 分隔符
        """
        messages = map(str, messages)
        message = sep.join(messages)
        
        self.logFileHandler.write(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] INFO: {message}\n')
        
        if self.auto_update:
            self.update( )
        return
    def warning(self, *messages: T.Tuple[str], sep: str = ' ') -> None:
        """记录警告

        参数:
            message (str): 信息
            sep (str): 分隔符
        """
        messages = map(str, messages)
        message = sep.join(messages)
        
        self.logFileHandler.write(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] WARNING: {message}\n')
        if self.auto_update:
            self.update( )
        return
    
    def error(self, *messages: T.Tuple[str], sep: str = ' ') -> None:
        """记录错误

        参数:
            message (str): 信息
            sep (str): 分隔符
        """
        messages = map(str, messages)
        message = sep.join(messages)
        
        self.logFileHandler.write(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] ERROR: {message}\n')
        if self.auto_update:
            self.update( )
        return
        
    def clear(self) -> None:
        """清空日志文件"""
        self.logFileHandler.close()
        self.logFileHandler = open(self.logFile, 'w')
        return

    exceptions: T.List[ExceptionInfo] = []


def handle_exception(exc_type, exc_value, exc_traceback):
    DebugLogger.exceptions.append(ExceptionInfo(exc_type, exc_value, exc_traceback))
    
sys.excepthook = handle_exception
