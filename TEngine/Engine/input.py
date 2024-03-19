import time
import curses
from typing import *
from .engine_component import EngineComponent
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
        self.key_buffer : List[int]     = []
        self.__allow    : bool          = True
        self.__timer    : float         = -1
        self.__clrbuffer: bool          = True
        self.init()        
    
    def wait( self, __ms: int, __kc: int, *, without: Optional[List[int]] = None, clrbuffer: bool = True ) -> None:
        """
        简单的输入控制器，防止用户长按键盘导致的输入过快
        
        参数:
            __ms: int - 毫秒
            __kc: int - 允许的按键数量
            without: Optional[List[int]] = None - 排除的按键
        """
        self.__clrbuffer = clrbuffer
        if self.__timer == -1:
            self.__timer = time.time()
        
        for key in without or []:
            if key in self.key_buffer:
                self.key_buffer.remove( key )
        
        curtime = time.time()
        total_time = curtime - self.__timer
        if curtime - self.__timer >= __ms / 1000:
            self.__allow = True
            self.__timer = -1
            self.key_buffer.clear()
            return
        
        if len(self.key_buffer) >= __kc:
            self.__allow = False
        
    
    def getch(self, __timeout: float = -1) -> int:
        if not self.__allow:
            if self.__clrbuffer:
                self.stdscr.nodelay(1)
                while self.stdscr.getch() != -1: pass
                return -1
            return -1
        self.stdscr.timeout( __timeout )
        key = self.stdscr.getch()
        self.stdscr.timeout(-1)
        self.key_buffer.append( key )
        
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
                command: Optional[Dict[Union[Tuple[int], int], Callable[..., int]]] = None
                ) -> str:
        """
        获取一行输入, 类似input函数
        
        参数:
            __msg: str = ""     - 提示信息
            exitkey: str|int = "\\n" - 退出键
            encode: str = 'utf-8' - 编码
            cursor: int = 1     - 光标
            mask: Optional[str] = None - 掩码
            clreol: Optional[bool] = True - 是否清除行( False将为尝试使用空格覆盖, 若不想覆盖任何字符, 请使用None )
            command: Optional[Dict[Union[Tuple[int], int], Callable[..., int]]] = None - 指令集，键为按键，值为函数，允许为tuple为键，会读取所有缓冲区的按键然后对比key
        """
        if __msg:
            self.stdscr.addstr(__msg)
        if not command: command = {}
        else:
            for key, cmd in command.items():
                if isinstance(key, list):
                    command.pop(key)
                    command[tuple(key)] = cmd
        
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
                string.pop(index - 1)
                index -= 1
            elif key >= 32 and key <= 126:
                key = chr(key)
                string.insert(index, key)
                index += 1
            elif key in arrow_key:
                if key == curses.KEY_LEFT and index - 1 >= 0:
                    index -= 1
                elif key == curses.KEY_RIGHT and index < len(string):
                    index += 1
                elif key == curses.KEY_UP:
                    index = 0
                elif key == curses.KEY_DOWN:
                    index = len(string)
            else:
                # get keys buffer
                self.stdscr.nodelay(1)
                keys = [key]
                while True:
                    key = self.stdscr.getch()
                    if key == -1: break
                    keys.append(key)
                self.stdscr.nodelay(0)
                for key, cmd in command.items():
                    if key in keys:
                        index = cmd(string, index)
                
                # try decode keys buffer
                try:
                    bytes_buffer += bytes(keys)
                    key = bytes_buffer.decode(coding)
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
            self.stdscr.move(y, x + index)
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
    RESIZE      = curses.KEY_RESIZE
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

