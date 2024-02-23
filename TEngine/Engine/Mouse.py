import curses
import typing as T
from .Component import Component, Text
from ..dataTypes import ClickStatus, RawClickData, ClickBox

__all__ = ["Mouse", "ClickData"]

class ClickInfoList:
    def __init__( self ) -> None:
        self.names: T.List[str] = []
        self.boxs: T.List[ClickBox] = []
        self.boxDict: T.Dict[str, ClickBox] = {}
    
    def add( self, click_data: T.List[ T.Tuple[str, ClickBox] ] ) -> None:
        for name, box in click_data:
            self.names.append(name)
            self.boxs.append(box)
            self.boxDict[name] = box
        return

    def __contains__(self, name: str) -> bool:
        return name in self.names
    def __add__( self, other: "ClickInfoList" ) -> "ClickInfoList":
        self.names.extend( other.names )
        self.boxs.extend( other.boxs )
        self.boxDict.update( other.boxDict )
        return self
    def __iter__( self ) -> T.Iterator[ str ]:
        return self.names.__iter__()
    
class ClickData:
    def __init__(self, mouseClickEvent: RawClickData) -> None:
        self.x = mouseClickEvent.x
        self.y = mouseClickEvent.y
        self.bstate = mouseClickEvent.bstate
        self.clicked_data = mouseClickEvent.clicked
        
        self.pressed                : ClickInfoList = ClickInfoList( )
        self.clicked                : ClickInfoList = ClickInfoList( )
        self.released               : ClickInfoList = ClickInfoList( )
        self.doubleClicked          : ClickInfoList = ClickInfoList( )
        self.tripleClicked          : ClickInfoList = ClickInfoList( )
        self.rightPressed           : ClickInfoList = ClickInfoList( )
        self.rightClicked           : ClickInfoList = ClickInfoList( )
        self.rightDoubleClicked     : ClickInfoList = ClickInfoList( )
        self.rightTripleClicked     : ClickInfoList = ClickInfoList( )
        self.middlePressed          : ClickInfoList = ClickInfoList( )
        self.middleClicked          : ClickInfoList = ClickInfoList( )
        self.middleDoubleClicked    : ClickInfoList = ClickInfoList( )
        self.middleTripleClicked    : ClickInfoList = ClickInfoList( )
        self.unknown                : ClickInfoList = ClickInfoList( )
        self.init()
        return
    
    def init(self) -> None:
        if self.bstate & ClickStatus.PRESSED:
            self.pressed.add( self.clicked_data )
        elif self.bstate & ClickStatus.RELEASED:
            self.released.add( self.clicked_data )
        elif self.bstate & ClickStatus.CLICK:
            self.clicked.add( self.clicked_data )
        elif self.bstate & ClickStatus.DOUBLE_CLICK:
            self.doubleClicked.add( self.clicked_data )
        elif self.bstate & ClickStatus.TRIPLE_CLICK:
            self.tripleClicked.add( self.clicked_data )
        elif self.bstate & ClickStatus.RIGHT_PRESSED:
            self.rightPressed.add( self.clicked_data )
        elif self.bstate & ClickStatus.RIGHT_CLICK:
            self.rightClicked.add( self.clicked_data )
        elif self.bstate & ClickStatus.RIGHT_DOUBLE_CLICK:
            self.rightDoubleClicked.add( self.clicked_data )
        elif self.bstate & ClickStatus.RIGHT_TRIPLE_CLICK:
            self.rightTripleClicked.add( self.clicked_data )
        elif self.bstate & ClickStatus.MIDDLE_PRESSED:
            self.middlePressed.add( self.clicked_data )
        elif self.bstate & ClickStatus.MIDDLE_CLICK:
            self.middleClicked.add( self.clicked_data )
        elif self.bstate & ClickStatus.MIDDLE_DOUBLE_CLICK:
            self.middleDoubleClicked.add( self.clicked_data )
        elif self.bstate & ClickStatus.MIDDLE_TRIPLE_CLICK:
            self.middleTripleClicked.add( self.clicked_data )
        else:
            self.unknown.add( self.clicked_data )
        return
        
        

class Mouse(Component):
    def __init__(self) -> None:
        super().__init__()
        self.clickBox: T.Dict[str, ClickBox] = {}
        return
    
    def init(self, interval: int = 50) -> None:
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        curses.mouseinterval(interval)
    
    def clear_clickbox( self ) -> None:
        self.clickBox.clear()
    def remove_clickbox( self, name: str ) -> None:
        self.clickBox.pop( name )
    
    def set_clickbox(self, name: str, x: int | Text, y: int = None, w: int | str = None, h: int = None) -> None:
        """设置点击区域"""
        if isinstance(x, Text):
            text = x
            box = text.click_box
            self.clickBox[name] = ClickBox( box.x, box.y, box.width, box.height)
        else:
            h = h if h is not None else 1
            if y is None or w is None:
                self.logger.error("Invalid click box")
                return
            self.clickBox[name] = ClickBox(x, y, w, h)
        return
    
    def checkClick(self, x: int, y: int, bstate: int) -> RawClickData:
        """检查点击事件是否在点击区域内，内部调用"""
        clickedBox: T.List[ T.Tuple[ str, ClickBox ] ] = [ ]
        for name, box in self.clickBox.items( ):
            if box.checkbox( ( x, y, bstate ) ):
                clickedBox.append((name, box))
                
        return RawClickData( x, y, bstate, clickedBox )
    
    def get(self) -> ClickData:
        """获取鼠标点击， 返回对象，包含点击位置，点击状态，点击区域名称"""
        _, mx, my, _, bstate = curses.getmouse()

        mouse = self.checkClick(mx, my, bstate)
        return ClickData( mouse )
        
