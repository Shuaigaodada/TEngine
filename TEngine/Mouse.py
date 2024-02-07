import typing as T
import unicurses as curses
from Component import Component


class ClickStatus(T.NamedTuple):
    PRESSED: int = curses.BUTTON1_PRESSED
    RELEASED: int = curses.BUTTON1_RELEASED
    CLICK: int = curses.BUTTON1_CLICKED
    DOUBLE_CLICK: int = curses.BUTTON1_DOUBLE_CLICKED
    TRIPLE_CLICK: int = curses.BUTTON1_TRIPLE_CLICKED
    RIGHT_PRESSED: int = curses.BUTTON2_PRESSED
    RIGHT_CLICK: int = curses.BUTTON2_CLICKED
    RIGHT_DOUBLE_CLICK: int = curses.BUTTON2_DOUBLE_CLICKED
    RIGHT_TRIPLE_CLICK: int = curses.BUTTON2_TRIPLE_CLICKED
    MIDDLE_PRESSED: int = curses.BUTTON3_PRESSED
    MIDDLE_CLICK: int = curses.BUTTON3_CLICKED
    MIDDLE_DOUBLE_CLICK: int = curses.BUTTON3_DOUBLE_CLICKED
    MIDDLE_TRIPLE_CLICK: int = curses.BUTTON3_TRIPLE_CLICKED
    UNKNOWN: int = -1


class BoxInfo(T.NamedTuple):
    x: int
    y: int
    w: int
    h: int
class MouseClickEvent(T.NamedTuple):
    x: int
    y: int
    bstate: int
    state: int
    clicked: T.Tuple[str, BoxInfo]

class ClickedBoxInfo:
    def __init__(self, datas: T.Tuple[str, BoxInfo]) -> None:
        self.names = [data[0] for data in datas]
        self.boxes = [data[1] for data in datas]
    
    def __contains__(self, name: str) -> bool:
        return name in self.names
        
        

class Mouse(Component):
    def __init__(self) -> None:
        super().__init__()
        self.clickBox: T.Dict[str, BoxInfo] = {}
    
    def SetClickBox(self, name: str, x: int, y: int, w: int, h: int) -> None:
        """设置点击区域"""
        self.clickBox[name] = BoxInfo(x, y, w, h)
        return
    
    def CheckClick(self, mouseEvent: MouseClickEvent) -> MouseClickEvent:
        clickedBox: T.List[T.Tuple[str, BoxInfo]] = []
        for name, box in self.clickBox.items():
            if box.x <= mouseEvent.x <= box.x + box.w and box.y <= mouseEvent.y <= box.y + box.h:
                clickedBox.append((name, box))
        return MouseClickEvent(mouseEvent.x, mouseEvent.y, mouseEvent.bstate, clickedBox)
    
    def GetMouse(self) -> MouseClickEvent:
        _, mx, my, _, bstate = curses.getmouse()
        state = ClickStatus.UNKNOWN
        if   state & ClickStatus.PRESSED:               state = ClickStatus.PRESSED
        elif state & ClickStatus.RELEASED:              state = ClickStatus.RELEASED
        elif state & ClickStatus.CLICK:                 state = ClickStatus.CLICK
        elif state & ClickStatus.DOUBLE_CLICK:          state = ClickStatus.DOUBLE_CLICK
        elif state & ClickStatus.TRIPLE_CLICK:          state = ClickStatus.TRIPLE_CLICK
        elif state & ClickStatus.RIGHT_PRESSED:         state = ClickStatus.RIGHT_PRESSED
        elif state & ClickStatus.RIGHT_CLICK:           state = ClickStatus.RIGHT_CLICK
        elif state & ClickStatus.RIGHT_DOUBLE_CLICK:    state = ClickStatus.RIGHT_DOUBLE_CLICK
        elif state & ClickStatus.RIGHT_TRIPLE_CLICK:    state = ClickStatus.RIGHT_TRIPLE_CLICK
        elif state & ClickStatus.MIDDLE_PRESSED:        state = ClickStatus.MIDDLE_PRESSED
        elif state & ClickStatus.MIDDLE_CLICK:          state = ClickStatus.MIDDLE_CLICK
        elif state & ClickStatus.MIDDLE_DOUBLE_CLICK:   state = ClickStatus.MIDDLE_DOUBLE_CLICK
        elif state & ClickStatus.MIDDLE_TRIPLE_CLICK:   state = ClickStatus.MIDDLE_TRIPLE_CLICK
        
        return self.CheckClick(MouseClickEvent(mx, my, bstate, state, None))
        
