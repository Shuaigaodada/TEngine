import os
import json
import pickle

from ..components import EngineComponent
from ..interfaces import Resource as ResourceInterfaces
from ..interfaces import FileLoader as FileLoaderInterfaces
from typing import *

__all__ = [ "Resource", "FileLoader" ]

class FileLoader( FileLoaderInterfaces, EngineComponent ):
    """
    这是一个文件加载器, 用于加载常见文件, 快速返回字符。
    
    当然也可以选择只调用`path`属性, 来获取文件的完整路径
    """
    
    def __init__( self, path: str ) -> None:
        super( ).__init__( )
        self.path = path
        self.coding = "utf-8"
        return
    
    def as_string( self ) -> str:
        """加载为str"""
        with open( self.path, "r", encoding=self.coding ) as file:
            return file.read()
    
    def as_file( self, mode: str ) -> TextIO:
        """返回open对象"""
        return open( self.path, mode, encoding=self.coding )

    def as_lines( self ) -> List[str]:
        """返回文件的每一行"""
        with open( self.path, "r", encoding=self.coding ) as file:
            return file.readlines()
        
    def as_json(self) -> Dict[str, Any]:
        """返回json对象"""
        with open( self.path, "r", encoding=self.coding ) as file:
            return json.load( file )
    
    def as_object(self) -> object:
        """返回pickle对象"""
        with open( self.path, "rb", encoding=self.coding ) as file:
            return pickle.load( file )
    
    def write(self, data: Union[str, Dict, List, object]) -> None:
        """写入文件"""
        if isinstance( data, str ):
            with open( self.path, "w", encoding=self.coding ) as file:
                file.write( data )
        elif isinstance( data, (Dict, List) ): 
            with open( self.path, "w", encoding=self.coding ) as file:
                json.dump( data, file )
        else:
            with open( self.path, "wb" ) as file:
                pickle.dump( data, file )

class Resource( ResourceInterfaces, EngineComponent ):
    """资源加载器，快速加载文件，推荐文件在src目录下"""
    __instance: Optional["Resource"] = None
    def __new__(cls, *args, **kwargs) -> "Resource":
        if cls.__instance is None:
            cls.__instance = super( ).__new__( cls )
        return cls.__instance
    
    def __init__(self, srcpath: Optional[str] = None) -> None:
        super( ).__init__( )
        # 获取工作路径
        basepath = os.getcwd()
        # 修正斜杠
        srcpath = srcpath.replace( "/", os.sep )
        # 判断是否是绝对路径
        if srcpath.startswith( os.sep ):
            self.srcpath = srcpath
        else:
            self.srcpath = os.path.join( basepath, srcpath )
        return

    def load(self, path: str, existok: bool = False) -> FileLoader:
        """加载文件，path为文件路径，使用/分割文件夹，existok为True则文件不存在时创建文件"""
        # 分割文件路径
        dirs = path.split( "/" )
        # 如果文件路径中有多个文件夹，那么需要逐个检查文件夹是否存在，如果不存在则创建
        if len( dirs ) > 1:
            path = self.srcpath
            for dir in dirs[:-1]:
                path = os.path.join( path, dir )
                if not os.path.exists( path ):
                    if not existok:
                        raise FileNotFoundError( f"File path {path} not exists" )
                    os.makedirs( path )
            # 恢复文件路径
            path = dirs
        path = os.path.join( self.srcpath, path )
        if existok and not os.path.exists( path ):
            open( path, "a" ).close( )
        return FileLoader( path )
    
        
        

    
            