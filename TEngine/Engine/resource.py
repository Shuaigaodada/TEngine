import os
import json
import pickle
import typing as T
from .component import Component
__all__ = ["Resource", "FileLoader", "resource"]


class FileLoader(Component):
    def __init__(self, filePath: str, encoding: str = None) -> None:
        super().__init__()
        self.filePath = filePath
        self.encoding = encoding if encoding is not None else "utf-8"
        return

    def asString(self) -> str:
        with open(self.filePath, "r", encoding=self.encoding) as file:
            return file.read()
    
    def asFile(self) -> T.IO:
        return open(self.filePath, "r")
    
    def asLines(self) -> T.List[str]:
        with open(self.filePath, "r", encoding=self.encoding) as file:
            return file.readlines()
    
    def asJson(self) -> T.Dict:
        with open(self.filePath, "r", encoding=self.encoding) as file:
            return json.load(file)
    
    def asObject(self) -> object:
        with open(self.filePath, "rb", encoding=self.encoding) as file:
            return pickle.load(file)
        
    def write(self, data: str | T.Dict | object) -> None:
        if type(data) is str:
            with open(self.filePath, "w", encoding=self.encoding) as file:
                file.write(data)
        elif type(data) is dict:
            with open(self.filePath, "w", encoding=self.encoding) as file:
                json.dump(data, file)
        else:
            with open(self.filePath, "wb", encoding=self.encoding) as file:
                pickle.dump(data, file)
        return

    @property
    def path(self) -> str:
        return self.filePath

class Resource:
    def __init__(self, srcPath: str) -> None:
        global resource
        basePath = os.getcwd()
        srcPath = srcPath.replace("/", os.sep)
        if srcPath.startswith(os.sep):
            self.srcPath = srcPath
        else:
            self.srcPath = os.path.join(basePath, srcPath)
        
        resource = self
        return
    
    def load(self, name: str, existOk: bool = False) -> FileLoader:
        # 分割文件路径
        dirs = name.split("/")
        
        # 如果文件路径中有多个文件夹，那么需要逐个检查文件夹是否存在，如果不存在则创建
        if len(dirs) > 1:
            path = self.srcPath
            # 逐个检查文件夹是否存在
            for dir in dirs[:-1]:
                # 链接文件夹
                path = os.path.join(path, dir)
                # 检查文件夹是否存在
                if not os.path.exists(path):
                    # 如果文件夹不存在，检查是否允许创建文件夹并创建
                    if existOk: os.mkdir(path)
                    # 如果不允许创建文件夹，抛出异常
                    else: raise FileNotFoundError(f"Directory {path} not found.")
            
            # 检查文件是否存在，不存在则创建
            if existOk: open(os.path.join(path, dirs[-1]), "a").close()
            # 返回文件加载器
            return FileLoader(os.path.join(path, dirs[-1]))
        else:
            # 检查文件是否存在，不存在则创建
            if existOk: open(os.path.join(self.srcPath, dirs[-1]), "a").close()
            # 返回文件加载器
            return FileLoader(os.path.join(self.srcPath, name))


resource: Resource = None
