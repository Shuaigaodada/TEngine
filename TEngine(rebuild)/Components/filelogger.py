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
    __instance: "FileLogger" = None
    def __new__(cls, *args, **kwargs) -> "FileLogger":
        if cls.__instance is None:
            cls.__instance = super().__new__( cls )
        return cls.__instance

    def __init__(self, path: Optional[str] = None, **open_kwargs: Dict[str, Any]) -> None:
        self.handle: TextIO = None
        self.path = None
        self.open_args = open_kwargs
        
        if path is None:
            # auto create file name
            path = os.path.join(os.getcwd(), time.strftime("%Y-%m-%d %H:%M:%S") + ".log")
        self.path = path
        self.open( )
    
    def open(self, mode="a") -> None:
        self.handle = open(self.path, mode, **self.open_args)
           
    def read(self) -> str:
        try:
            return self.handle.read( ) 
        except io.UnsupportedOperation:
            self.close()
            with open( self.path, "r", **self.open_args ) as file:
                file: TextIO
                text = file.read( )
            self.open( )
            return text
        except FileNotFoundError:
            return ""
        except Exception as e:
            raise e
    
    def readlines(self) -> List[str]:
        try:
            return self.handle.readlines( )
        except io.UnsupportedOperation:
            self.close()
            with open( self.path, "r", **self.open_args ) as file:
                file: TextIO
                lines = file.readlines( )
            self.open( )
            return lines
        except FileNotFoundError:
            return []
        except Exception as e:
            raise e
            
    def update(self) -> None:
        self.close()
        self.open( )

    def close(self) -> None:
        self.handle.close( )
    
    def __write( self, level: str, msgs: Tuple[str], sep: str ) -> None:
        message = sep.join(map( str, msgs ))
        self.handle.write( f"[{time.strftime( '%Y-%m-%d %H:%M:%S' )}] {level}: {message}\n" )
    
    def info(self, *msg: Tuple[str], sep: str = " ") -> None:
        self.__write( "INFO", msg, sep )
    
    def warning(self, *msg: Tuple[str], sep: str = " ") -> None:
        self.__write( "WARNING", msg, sep )
    
    def error(self, *msg: Tuple[str], sep: str = " ") -> None:
        self.__write( "ERROR", msg, sep )
            
    def clear(self) -> None:
        self.close( )
        with open( self.path, "w" ) as file:
            pass
        self.open( )

    def set_excepthook(self) -> None:
        def exc_handle( type, value, tr ):
            self.error( "".join(traceback.format_exception( type, value, tr )) )
        sys.excepthook = exc_handle