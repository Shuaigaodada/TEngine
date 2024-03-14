from typing import List, Tuple
from ..interfaces import FileLogger as FileLoggerInterfaces

import os
import io
import sys
import time
import traceback
from typing import *

__all__ = [ "FileLogger" ]

class FileLogger( FileLoggerInterfaces ):
    """
    这是一个用于记录日志的类，它是一个单例类，所以你只能创建一个实例。
    
    因为在curses中无法将信息输出到控制台, 因此创建FileLogger类来记录日志。 
    """

    __instance: Optional["FileLogger"] = None
    def __new__(cls, *args, **kwargs) -> "FileLogger":
        if cls.__instance is None:
            cls.__instance = super().__new__( cls )
        return cls.__instance

    def __init__(self, path: Optional[str] = None, **open_kwargs: Dict[str, Any]) -> None:
        """
        path为日志文件的路径, 如果不指定则会自动创建一个文件名。 
        open_kwargs为open函数的参数。
        """
        self.handle: TextIO = None
        self.path = None
        self.open_args = open_kwargs
        
        if path is None:
            # auto create file name
            path = os.path.join(os.getcwd(), time.strftime("%Y-%m-%d %H:%M:%S") + ".log")
        self.path = path
        self.open( )
    
    def open(self, mode="a") -> None:
        """打开文件并指定模式"""
        self.handle = open(self.path, mode, **self.open_args)
           
    def read(self) -> str:
        """读取文件中的所有内容并返回。如果无法读取这个方法会关闭handle并重新打开文件。"""
        try:
            return self.handle.read( ) 
        except io.UnsupportedOperation:
            self.close()
            self.open( "r" )
            return self.read( )
        except FileNotFoundError:
            return ""
        except Exception as e:
            raise e
    
    def readlines(self) -> List[str]:
        """读取文件中的所有行并返回。如果无法读取这个方法会关闭handle并重新打开文件。"""
        try:
            return self.handle.readlines( )
        except io.UnsupportedOperation:
            self.close()
            self.open( "r" )
            return self.readlines( )
        except FileNotFoundError:
            return []
        except Exception as e:
            raise e
            
    def update(self) -> None:
        """更新文件,简单来说就是关闭文件并重新打开。"""
        self.close()
        self.open( )

    def close(self) -> None:
        """关闭文件"""
        self.handle.close( )
    
    def __write( self, level: str, msgs: Tuple[str], sep: str ) -> None:
        """内部写入"""
        message = sep.join(map( str, msgs ))
        self.handle.write( f"[{time.strftime( '%Y-%m-%d %H:%M:%S' )}] {level}: {message}\n" )
    
    def info(self, *msg: Tuple[str], sep: str = " ") -> None:
        """记录INFO级别的日志。"""
        self.__write( "INFO", msg, sep )
    
    def warning(self, *msg: Tuple[str], sep: str = " ") -> None:
        """记录WARNING级别的日志。"""
        self.__write( "WARNING", msg, sep )
    
    def error(self, *msg: Tuple[str], sep: str = " ") -> None:
        """记录ERROR级别的日志。"""
        self.__write( "ERROR", msg, sep )
            
    def clear(self) -> None:
        """清理文件中的所有内容。"""
        self.close( )
        self.open( "w" )

    def set_excepthook(self) -> None:
        """将异常处理函数设置为自定义的函数."""
        def exc_handle( type, value, tr ):
            self.error( "".join(traceback.format_exception( type, value, tr )) )
        sys.excepthook = exc_handle