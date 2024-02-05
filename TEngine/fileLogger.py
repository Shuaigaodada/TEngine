# 这是一个用于debug的日志记录器
import time
import typing as T

__all__ = ["DebugLogger"]

class DebugLogger:
    def __init__(self, logFile: str) -> None:
        """初始化日志记录器

        参数:
            logFile (str): 日志文件路径
        """
        
        self.logFile = logFile
        self.logFileHandler = self.open(self.logFile)
        
        return
    
    def open(self, filePath: str) -> None:
        """打开日志文件"""
        self.logFile = filePath
        self.logFileHandler = open(self.logFile, 'w')
        return
    def close(self) -> None:
        """关闭日志文件"""
        self.logFileHandler.close()
        return
    
    def info(self, *messages: T.Tuple[str], sep: str = ' ') -> None:
        """记录信息

        参数:
            message (str): 信息
            sep (str): 分隔符
        """
        
        message = sep.join(messages)
        
        self.logFileHandler.write(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] INFO: {message}\n')
        return
    def warning(self, *messages: T.Tuple[str], sep: str = ' ') -> None:
        """记录警告

        参数:
            message (str): 信息
            sep (str): 分隔符
        """
        
        message = sep.join(messages)
        
        self.logFileHandler.write(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] WARNING: {message}\n')
        return
    
    def error(self, *messages: T.Tuple[str], sep: str = ' ') -> None:
        """记录错误

        参数:
            message (str): 信息
            sep (str): 分隔符
        """
        
        message = sep.join(messages)
        
        self.logFileHandler.write(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] ERROR: {message}\n')
        return
        
    
    


