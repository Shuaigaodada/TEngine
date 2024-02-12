# 这是一个用于debug的日志记录器
import os
import time
import typing as T

__all__ = ["DebugLogger"]

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
        self.Open(self.logFile)
        self.instance.append(self)
        return
    
    def Update(self) -> None:
        """更新日志记录器"""
        self.Close()
        self.Open(self.logFile, "a")
        return
    
    def Open(self, filePath: str, mode = "w") -> None:
        """打开日志文件"""
        self.logFile = filePath
        self.logFileHandler = open(self.logFile, mode)
        return
    def Close(self) -> None:
        """关闭日志文件"""
        try:
            self.logFileHandler.close()
        except ValueError:
            pass
        return
    
    def Info(self, *messages: T.Tuple[str], sep: str = ' ') -> None:
        """记录信息

        参数:
            message (str): 信息
            sep (str): 分隔符
        """
        
        message = sep.join(messages)
        
        self.logFileHandler.write(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] INFO: {message}\n')
        return
    def Warning(self, *messages: T.Tuple[str], sep: str = ' ') -> None:
        """记录警告

        参数:
            message (str): 信息
            sep (str): 分隔符
        """
        
        message = sep.join(messages)
        
        self.logFileHandler.write(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] WARNING: {message}\n')
        return
    
    def Error(self, *messages: T.Tuple[str], sep: str = ' ') -> None:
        """记录错误

        参数:
            message (str): 信息
            sep (str): 分隔符
        """
        
        message = sep.join(messages)
        
        self.logFileHandler.write(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] ERROR: {message}\n')
        return
        
    def Clear(self) -> None:
        """清空日志文件"""
        self.logFileHandler.close()
        self.logFileHandler = open(self.logFile, 'w')
        return


