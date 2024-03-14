import curses
import typing as T
from .component import Component, Text
from ..dataTypes import ClickStatus, RawClickData, ClickBox

__all__ = ["Mouse", "ClickData"]

class ClickInfoList:
    def __init__( self ) -> None:
        self.names: T.List[str] = []
        self.boxs: T.List[ClickBox] = []
        self.dict: T.Dict[str, ClickBox] = {}
    
    def add( self, mouse: RawClickData ) -> None:
        for box_data in mouse.clicked:
            name, box = box_data
            self.names.append(name)
            self.boxs.append(box)
            self.dict[name] = box
            if isinstance( box._func, T.Callable ):
                if box._when == -1:
                    box._func( *box._args, **box._kwargs )
                else:
                    if mouse.bstate & box._when:
                        box._func( *box._args, **box._kwargs )
        return

    def __contains__(self, name: str) -> bool:
        return name in self.names
    def __add__( self, other: "ClickInfoList" ) -> "ClickInfoList":
        self.names.extend( other.names )
        self.boxs.extend( other.boxs )
        self.dict.update( other.dict )
        return self
    def __iter__( self ) -> T.Iterator[ str ]:
        return self.names.__iter__()
    
class ClickData:
    def __init__(self, mouseClickEvent: RawClickData) -> None:
        self.x = mouseClickEvent.x
        self.y = mouseClickEvent.y
        self.bstate = mouseClickEvent.bstate
        self.clicked_data = mouseClickEvent.clicked
        self._raw = mouseClickEvent
        
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
        
        self.draging                : ClickInfoList = ClickInfoList( )
        self.unknown                : ClickInfoList = ClickInfoList( )
        self.init()
        return
    
    def init(self) -> None:
        if self.bstate & ClickStatus.PRESSED:
            self.pressed.add( self._raw )
        elif self.bstate & ClickStatus.RELEASED:
            self.released.add( self._raw )
        elif self.bstate & ClickStatus.CLICKED:
            self.clicked.add( self._raw )
        elif self.bstate & ClickStatus.DOUBLE_CLICKED:
            self.doubleClicked.add( self._raw )
        elif self.bstate & ClickStatus.TRIPLE_CLICKED:
            self.tripleClicked.add( self._raw )
        elif self.bstate & ClickStatus.RIGHT_PRESSED:
            self.rightPressed.add( self._raw )
        elif self.bstate & ClickStatus.RIGHT_CLICKED:
            self.rightClicked.add( self._raw )
        elif self.bstate & ClickStatus.RIGHT_DOUBLE_CLICKED:
            self.rightDoubleClicked.add( self._raw )
        elif self.bstate & ClickStatus.RIGHT_TRIPLE_CLICK:
            self.rightTripleClicked.add( self._raw )
        elif self.bstate & ClickStatus.MIDDLE_PRESSED:
            self.middlePressed.add( self._raw )
        elif self.bstate & ClickStatus.MIDDLE_CLICK:
            self.middleClicked.add( self._raw )
        elif self.bstate & ClickStatus.MIDDLE_DOUBLE_CLICK:
            self.middleDoubleClicked.add( self._raw )
        elif self.bstate & ClickStatus.MIDDLE_TRIPLE_CLICK:
            self.middleTripleClicked.add( self._raw )
        elif self.bstate & ClickStatus.DRAGING:
            self.draging.add( self._raw )
        else:
            self.unknown.add( self._raw )
        return
        
        

class Mouse(Component):
    def __init__(self) -> None:
        super().__init__()
        self.clickbox: T.Dict[str, ClickBox] = {}
        return
    
    def init(self, interval: int = 0, drag: bool = False) -> None:
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        curses.mouseinterval(interval)
        if drag:
            print("\033[?1003h")
    
    def clear_clickbox( self ) -> None:
        self.clickbox.clear()
    def remove_clickbox( self, name: str ) -> None:
        self.clickbox.pop( name )
    
    def set_clickbox(self, name: str, x: int | Text, y: int = None, w: int | str = None, h: int = None, call: T.Callable = None, *call_args, **call_kwargs) -> None:
        """设置点击区域"""
        if isinstance(x, Text):
            text = x
            box = text.click_box
            self.clickbox[name] = ClickBox( box.x, box.y, box.width, box.height, call, *call_args, **call_kwargs )
        else:
            h = h if h is not None else 1
            if y is None or w is None:
                self.logger.error("Invalid click box")
                return
            self.clickbox[name] = ClickBox( x, y, w, h, call, *call_args, **call_kwargs )
        return
    
    def checkClick(self, x: int, y: int, bstate: int) -> RawClickData:
        """检查点击事件是否在点击区域内，内部调用"""
        clickedbox: T.List[ T.Tuple[ str, ClickBox ] ] = [ ]
        for name, box in self.clickbox.items( ):
            if box.checkbox( ( x, y, bstate ) ):
                clickedbox.append((name, box))
                
        return RawClickData( x, y, bstate, clickedbox )
    
    def get(self) -> ClickData:
        """获取鼠标点击， 返回对象，包含点击位置，点击状态，点击区域名称"""
        _, mx, my, _, bstate = curses.getmouse()

        mouse = self.checkClick(mx, my, bstate)
        return ClickData( mouse )
        
