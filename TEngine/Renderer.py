import typing as T
import unicurses as curses
from Component import Component

# 用于绘制颜色色块
class Renderer(Component):
    def __init__(self) -> None:
        super().__init__()
        # 所有颜色的index将会缓存在这个dict，而这个dict的key是颜色的hex值，value是颜色的index
        self.cacheColor: T.Dict[str, int] = {}
        # pairs是一个dict，key是颜色对的名字，value是颜色对的index
        self.pairs: T.Dict[str, int] = {}
        # index会自动分配，因此不需要手动设置
        self.index = 1
        # 设置是否记录警告和错误
        self.warning = True
        self.error = True
        return
    
    def Create(self, name: str, fg: str, bg: str | int = -1) -> None:
        """创建颜色渲染"""
        # 使用PushToCache来获取颜色的index
        fgColor = self.PushToCache(fg)
        bgColor = self.PushToCache(bg)
        
        # 判断条件 and 是否记录等级 and 是否有日志记录器
        if name in self.pairs and self.warning and self.logger is not None:
            self.logger.Warning(f"Color pair '{name}' already exists, will be overwritten.")
        
        self.pairs[name] = self.index
        curses.init_pair(self.index, fgColor, bgColor)
        self.index += 1
        return
    
    def GetIndex(self, name: str) -> int:
        """获取颜色对的index"""
        index = self.pairs.get(name, "N/A")
        if index == "N/A" and self.error and self.logger is not None:
            self.logger.Error(f"Color pair '{name}' not found.")
        return index

    def GetByIndex(self, index: int) -> int:
        """使用index获取颜色对"""
        keys = list(self.pairs.keys())
        key = keys[index]
        index = self.pairs.get(key, "N/A")
        if index == "N/A" and self.error and self.logger is not None:
            self.logger.Error(f"Color pair '{key}' not found.")
        return index
        
    def PushToCache(self, name: str) -> int:
        """将颜色推入缓存，如果存在返回颜色的index，否则创建颜色并返回index"""
        # 如果颜色已经在缓存中，直接返回index
        if name in self.cacheColor:
            return self.cacheColor[name]
        # 创建颜色并返回index
        self.cacheColor[name] = self.index
        self.index += 1
        curses.init_color(self.index, *self.HexToColor(name))
        return self.index - 1
        
    def HexToColor(self, hex: str) -> int:
        """将十六进制颜色转换为curses的颜色值"""
        R, G, B = int(hex[1:3], 16), int(hex[3:5], 16), int(hex[5:7], 16)
        R = int(R * 1000 / 255)
        G = int(G * 1000 / 255)
        B = int(B * 1000 / 255)
        return R, G, B