import typing as T
import curses

class ClickStatus:
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

class RawClickData(T.NamedTuple):
    x: int
    y: int
    bstate: int
    clicked: T.Tuple[str, T.Tuple]

class ClickBox:
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        self.box = (x, y, width, height)
    
    def checkbox( self, mouse: RawClickData | T.Tuple ) -> bool:
        """ 检查点击是否在盒子内 """
        x, y, width, height = self.box
        # box.box[0] <= mouseEvent.x <= box.box[2] and box.box[1] <= mouseEvent.y <= box.box[3]
        if isinstance( mouse, RawClickData ):
            return x <= mouse.x <= width and y <= mouse.y <= height
        else:
            return x <= mouse[0] <= width and y <= mouse[1] <= height

class BoxSize(T.NamedTuple):
    x: int
    y: int
    width: int
    height: int
    
    def __add__( self, other: "BoxSize" ) -> "BoxSize":
        new_x = min( self.x, other.x )
        new_y = min( self.y, other.y )
        new_w = max( self.width, other.width )
        new_h = max( self.height, other.height )
        return BoxSize( new_x, new_y, new_w, new_h )
        

    def unpack( self ) -> T.Tuple[int, int, int, int]:
        return self.x, self.y, self.width, self.height

class ScreenSize(T.NamedTuple):
    width: int
    height: int
