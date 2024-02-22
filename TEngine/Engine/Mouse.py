import typing as T
from .Component import Component, Text
from .clickBox import ClickBox
from ..dataTypes import ClickStatus, MouseClickEvent

__all__ = ["Mouse", "ClickData"]   

class ClickData:
    def __init__(self, mouseClickEvent: MouseClickEvent) -> None:
        self.info: MouseClickEvent  = mouseClickEvent
        self.pressed                : T.List[str]=[]
        self.clicked                : T.List[str]=[]
        self.released               : T.List[str]=[]
        self.doubleClicked          : T.List[str]=[]
        self.tripleClicked          : T.List[str]=[]
        self.rightPressed           : T.List[str]=[]
        self.rightClicked           : T.List[str]=[]
        self.rightDoubleClicked     : T.List[str]=[]
        self.rightTripleClicked     : T.List[str]=[]
        self.middlePressed          : T.List[str]=[]
        self.middleClicked          : T.List[str]=[]
        self.middleDoubleClicked    : T.List[str]=[]
        self.middleTripleClicked    : T.List[str]=[]
        self.unknown                : T.List[str]=[]
        self.init()
        return
    
    def init(self) -> None:
        if self.info.state & ClickStatus.PRESSED:
            self.pressed.extend([name for name, box in self.info.clicked])
        elif self.info.state & ClickStatus.RELEASED:
            self.released.extend([name for name, box in self.info.clicked])
        elif self.info.state & ClickStatus.CLICK:
            self.clicked.extend([name for name, box in self.info.clicked])
        elif self.info.state & ClickStatus.DOUBLE_CLICK:
            self.doubleClicked.extend([name for name, box in self.info.clicked])
        elif self.info.state & ClickStatus.TRIPLE_CLICK:
            self.tripleClicked.extend([name for name, box in self.info.clicked])
        elif self.info.state & ClickStatus.RIGHT_PRESSED:
            self.rightPressed.extend([name for name, box in self.info.clicked])
        elif self.info.state & ClickStatus.RIGHT_CLICK:
            self.rightClicked.extend([name for name, box in self.info.clicked])
        elif self.info.state & ClickStatus.RIGHT_DOUBLE_CLICK:
            self.rightDoubleClicked.extend([name for name, box in self.info.clicked])
        elif self.info.state & ClickStatus.RIGHT_TRIPLE_CLICK:
            self.rightTripleClicked.extend([name for name, box in self.info.clicked])
        elif self.info.state & ClickStatus.MIDDLE_PRESSED:
            self.middlePressed.extend([name for name, box in self.info.clicked])
        elif self.info.state & ClickStatus.MIDDLE_CLICK:
            self.middleClicked.extend([name for name, box in self.info.clicked])
        elif self.info.state & ClickStatus.MIDDLE_DOUBLE_CLICK:
            self.middleDoubleClicked.extend([name for name, box in self.info.clicked])
        elif self.info.state & ClickStatus.MIDDLE_TRIPLE_CLICK:
            self.middleTripleClicked.extend([name for name, box in self.info.clicked])
        else:
            self.unknown.extend([name for name, box in self.info.clicked])
        return
        
        

class Mouse(Component):
    def __init__(self) -> None:
        super().__init__()
        self.clickBox: T.Dict[str, ClickBox] = {}
        return
    
    def init(self, interval: int = 50) -> None:
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        curses.mouseinterval(interval)
    
    def set_clickBox(self, name: str, x: int | Text, y: int = None, w: int | str = None, h: int = None) -> None:
        """设置点击区域"""
        if isinstance(x, Text):
            text = x
            self.clickBox[name] = ClickBox( *text.click_box )
        else:
            h = h if h is not None else 1
            if y is None or w is None:
                self.logger.error("Invalid click box")
                return
            self.clickBox[name] = ClickBox(x, y, w, h)
        return
    
    def checkClick(self, mouseEvent: MouseClickEvent) -> MouseClickEvent:
        """检查点击事件是否在点击区域内，内部调用"""
        clickedBox: T.List[T.Tuple[str, ClickBox]] = []
        for name, box in self.clickBox.items():
            if box.offset:
                clickedX, clickedY = mouseEvent.x, mouseEvent.y
                for bx, by in box.clickBox:
                    if bx == clickedX and by == clickedY:
                        clickedBox.append((name, box))
                        break
            else:
                if box.box[0] <= mouseEvent.x <= box.box[2] and box.box[1] <= mouseEvent.y <= box.box[3]:
                    clickedBox.append((name, box))
        mouseEvent = MouseClickEvent(mouseEvent.x, mouseEvent.y, mouseEvent.bstate, mouseEvent.state, clickedBox)
        return mouseEvent
    
    def get(self) -> ClickData:
        """获取鼠标点击， 返回对象，包含点击位置，点击状态，点击区域名称"""
        _, mx, my, _, bstate = curses.getmouse()
        state = ClickStatus.UNKNOWN
        if   bstate & ClickStatus.PRESSED:               state = ClickStatus.PRESSED
        elif bstate & ClickStatus.RELEASED:              state = ClickStatus.RELEASED
        elif bstate & ClickStatus.CLICK:                 state = ClickStatus.CLICK
        elif bstate & ClickStatus.DOUBLE_CLICK:          state = ClickStatus.DOUBLE_CLICK
        elif bstate & ClickStatus.TRIPLE_CLICK:          state = ClickStatus.TRIPLE_CLICK
        elif bstate & ClickStatus.RIGHT_PRESSED:         state = ClickStatus.RIGHT_PRESSED
        elif bstate & ClickStatus.RIGHT_CLICK:           state = ClickStatus.RIGHT_CLICK
        elif bstate & ClickStatus.RIGHT_DOUBLE_CLICK:    state = ClickStatus.RIGHT_DOUBLE_CLICK
        elif bstate & ClickStatus.RIGHT_TRIPLE_CLICK:    state = ClickStatus.RIGHT_TRIPLE_CLICK
        elif bstate & ClickStatus.MIDDLE_PRESSED:        state = ClickStatus.MIDDLE_PRESSED
        elif bstate & ClickStatus.MIDDLE_CLICK:          state = ClickStatus.MIDDLE_CLICK
        elif bstate & ClickStatus.MIDDLE_DOUBLE_CLICK:   state = ClickStatus.MIDDLE_DOUBLE_CLICK
        elif bstate & ClickStatus.MIDDLE_TRIPLE_CLICK:   state = ClickStatus.MIDDLE_TRIPLE_CLICK
        
        mouseClickEvent = self.checkClick(MouseClickEvent(mx, my, bstate, state, None))
        return ClickData(mouseClickEvent)
        
