import curses
from typing import *
from typing import Iterator

from ..components import EngineComponent
from ..interfaces import Mouse as MouseInterface
from ..Engine.clickbox import ClickBox as ClickBoxInterface
from ..Engine.clickbox import ClickedBox as ClickedBoxInterface

__all__ = ["Mouse"]

class Mouse( MouseInterface, EngineComponent ):
    """鼠标接口，用于管理鼠标事件，点击框等。引擎实例化后，会自动实例化一个鼠标对象。"""
    __instance: Optional["Mouse"] = None
    def __new__(cls, *args, **kwargs) -> "Mouse":
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self) -> None:
        super().__init__()
        self.clickbox: Dict[str, ClickBoxInterface] = {}
        return
    
    def init(self, interval: int = 0, drag: bool = False) -> None:
        """启用鼠标事件，设置鼠标事件的间隔，是否启用拖拽。"""
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        curses.mouseinterval(interval)
        if drag: print("\033[?1003h", end="", flush=True)
    
    def clear_cb(self) -> None:
        """清除所有点击框"""
        self.clickbox.clear()
    
    def pop_cb(self, name: str) -> ClickBoxInterface:
        """删除点击框并返回点击框对象"""
        return self.clickbox.pop(name)
    
    def set_cb(self, name: str, x: int, y: int, w: int, h: int) -> None:
        """设置点击框"""
        self.clickbox[name] = ClickBoxInterface(x, y, w, h)
    
    def check(self, x: int, y: int) -> Iterator[str]:
        """检查点击框是否被点击，返回点击的名字"""
        for name, box in self.clickbox.items():
            if box.check(x, y):
                yield name
    
    def get(self) -> ClickedBoxInterface:
        """获取鼠标点击的点击框对象"""
        _, mx, my, _, bstate = curses.getmouse()
        return ClickedBoxInterface(mx, my, bstate, self.check(mx, my))
