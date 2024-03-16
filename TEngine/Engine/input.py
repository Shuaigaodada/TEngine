import curses
from typing import *
from ..engine_component import EngineComponent
from .mouse import Mouse as IMouse
from ..interfaces import Input as IInput

__all__ = ["Input"]

class Input(IInput, EngineComponent):
    __instance: Optional["Input"] = None
    def __new__(cls, *args, **kwargs) -> "Input":
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__init( )
        return cls.__instance
    
    def __init(self) -> None:
        super().__init__()
        self.mouse      : IMouse = IMouse()
        self._buffer    : bytearray     = bytearray()
        self.__delay    : bool          = False
    
    def getch(self, __timeout: float = -1) -> int:
        self.stdscr.timeout( __timeout )
        key = self.stdscr.getch()
        self.stdscr.timeout(-1)
        return key
    
    def getwch(self, __timeout: float = -1) -> str:
        self.stdscr.timeout( __timeout )
        key = self.stdscr.get_wch()
        self.stdscr.timeout(-1)
        return key if not isinstance(key, int) else chr( key )
    
    def getline(self, 
                __msg: str = "", 
                *, 
                quitkey: str = '\n', 
                coding: str = "utf-8", 
                cursor: int = 1, 
                mask: Optional[str] = None, 
                clreol: Optional[bool] = True, 
                check: Callable[..., Any] | None = None) -> str:
        """
        获取一行输入, 类似input函数
        
        参数:
            __msg: str = ""     - 提示信息
            exitkey: str|int = "\\n" - 退出键
            encode: str = 'utf-8' - 编码
            cursor: int = 1     - 光标
            mask: Optional[str] = None - 掩码
            clreol: Optional[bool] = True - 是否清除行( False将为尝试使用空格覆盖, 若不想覆盖任何字符, 请使用None )
            check: Optional[Callable] = None - 检查函数
        """
        if __msg:
            self.stdscr.addstr(__msg)
        if not check:
            check = lambda k, s: True
        
        string: List[str] = []
        bytes_buffer = bytearray()
        y, x = self.stdscr.getyx()
        index = 0
        curses.curs_set( cursor )
        
        quitkey = quitkey if isinstance(quitkey, int) else ord(quitkey)
        arrow_key = [
            curses.KEY_LEFT,
            curses.KEY_RIGHT,
            curses.KEY_UP,
            curses.KEY_DOWN
        ]
        
        while True:
            key = self.stdscr.getch()
            if key == quitkey:
                break
            elif key == curses.KEY_BACKSPACE and string and index:
                if not clreol:
                    self.stdscr.addstr(y, x + index, " ")
                string.pop(index)
                index -= 1
            elif key >= 32 and key <= 126:
                key = chr(key)
                if not check(key, string):
                    continue
                string.insert(index, key)
                index += 1
            elif key in arrow_key:
                if key == curses.KEY_LEFT and index:
                    index -= 1
                elif key == curses.KEY_RIGHT and index < len(string):
                    index += 1
                elif key == curses.KEY_UP:
                    index = 0
                else:
                    index = len(string)
            else:
                try:
                    bytes_buffer += bytes([key])
                    key = bytes_buffer.decode(coding)
                    if not check(key, string):
                        continue
                    string.insert(index, key)
                    index += 1
                    bytes_buffer.clear()
                except UnicodeDecodeError:
                    continue
                except ValueError:
                    continue
            
            self.stdscr.move(y, x)
            if clreol:
                self.stdscr.clrtoeol()
            if mask is not None:
                self.stdscr.addstr(mask * len(string))
            else:
                self.stdscr.addstr("".join(string))
            self.stdscr.refresh()
        return "".join(string)
                
    @property
    def delay( self ) -> bool:
        return self.__delay
    @delay.setter
    def delay( self, delay: bool ) -> None:
        self.__delay = delay
        curses.curs_set( delay )
    
    A = ord("a")
    B = ord("b")
    C = ord("c")
    D = ord("d")
    E = ord("e")
    F = ord("f")
    G = ord("g")
    H = ord("h")
    I = ord("i")
    J = ord("j")
    K = ord("k")
    L = ord("l")
    M = ord("m")
    N = ord("n")
    O = ord("o")
    P = ord("p")
    Q = ord("q")
    R = ord("r")
    S = ord("s")
    T = ord("t")
    U = ord("u")
    V = ord("v")
    W = ord("w")
    X = ord("x")
    Y = ord("y")
    Z = ord("z")
    SPACE = ord(" ")
    ENTER = ord("\n")
    ESC = 27
    
    def init(self) -> None:
        """初始化按键"""
        setattr(self, "UP", curses.KEY_UP)
        setattr(self, "DOWN", curses.KEY_DOWN)
        setattr(self, "LEFT", curses.KEY_LEFT)
        setattr(self, "RIGHT", curses.KEY_RIGHT)
        setattr(self, "BACKSPACE", curses.KEY_BACKSPACE)
        setattr(self, "DELETE", curses.KEY_DC)
        setattr(self, "INSERT", curses.KEY_IC)
        setattr(self, "HOME", curses.KEY_HOME)
        setattr(self, "END", curses.KEY_END)
        setattr(self, "PAGE_UP", curses.KEY_PPAGE)
        setattr(self, "PAGE_DOWN", curses.KEY_NPAGE)
        setattr(self, "MOUSE_KEY", curses.KEY_MOUSE)
    
    UP          = None
    DOWN        = None
    LEFT        = None
    RIGHT       = None
    BACKSPACE   = None
    DELETE      = None
    INSERT      = None
    HOME        = None
    END         = None
    PAGE_UP     = None
    PAGE_DOWN   = None
    MOUSE_KEY   = None
    SHIFT_A = ord("A")
    SHIFT_B = ord("B")
    SHIFT_C = ord("C")
    SHIFT_D = ord("D")
    SHIFT_E = ord("E")
    SHIFT_F = ord("F")
    SHIFT_G = ord("G")
    SHIFT_H = ord("H")
    SHIFT_I = ord("I")
    SHIFT_J = ord("J")
    SHIFT_K = ord("K")
    SHIFT_L = ord("L")
    SHIFT_M = ord("M")
    SHIFT_N = ord("N")
    SHIFT_O = ord("O")
    SHIFT_P = ord("P")
    SHIFT_Q = ord("Q")
    SHIFT_R = ord("R")
    SHIFT_S = ord("S")
    SHIFT_T = ord("T")
    SHIFT_U = ord("U")
    SHIFT_V = ord("V")
    SHIFT_W = ord("W")
    SHIFT_X = ord("X")
    SHIFT_Y = ord("Y")
    SHIFT_Z = ord("Z")

    SCROLL_UP = 257
    SCROLL_DOWN = 258

