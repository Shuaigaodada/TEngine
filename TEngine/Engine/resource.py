import os
import json
import pickle
import typing as T
from .Component import Component
__all__ = ["Resource", "FileLoader"]


class FileLoader(Component):
    def __init__(self, filePath: str) -> None:
        super().__init__()
        self.filePath = filePath
        return

    def AsString(self) -> str:
        with open(self.filePath, "r") as file:
            return file.read()
    
    def AsFile(self) -> T.IO:
        return open(self.filePath, "r")
    def AsLines(self) -> T.List[str]:
        with open(self.filePath, "r") as file:
            return file.readlines()
    
    def AsJson(self) -> T.Dict:
        with open(self.filePath, "r") as file:
            return json.load(file)
    
    def AsObject(self) -> object:
        with open(self.filePath, "rb") as file:
            return pickle.load(file)
        
    def Write(self, data: str | T.Dict | object) -> None:
        if type(data) is str:
            with open(self.filePath, "w") as file:
                file.write(data)
        elif type(data) is dict:
            with open(self.filePath, "w") as file:
                json.dump(data, file)
        else:
            with open(self.filePath, "wb") as file:
                pickle.dump(data, file)
        return

    @property
    def Path(self) -> str:
        return self.filePath

class Resource:
    def __init__(self, srcPath: str) -> None:
        basePath = os.getcwd()
        srcPath = srcPath.replace("/", os.sep)
        if srcPath.startswith(os.sep):
            self.srcPath = srcPath
        else:
            self.srcPath = os.path.join(basePath, srcPath)
        return
    
    def Load(self, name: str, existOk: bool = False) -> FileLoader:
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



