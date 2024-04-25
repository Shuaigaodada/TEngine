import time
import curses
import wcwidth
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
                clear: Optional[Callable[..., None]] = None,
                command: Optional[Dict[Union[Tuple[int], int], Callable[..., Tuple[int, int]]]] = None
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
        注释: 此函数不为不兼容unicode的终端提供支持
        """
        if __msg: self.stdscr.addstr(__msg)
        if clear is None: 
            clear = lambda stdscr, _s, _i: self.stdscr.clrtoeol( )
        if not command: command = {}
        else:
            for key, cmd in command.items():
                if isinstance(key, list):
                    command.pop(key)
                    command[tuple(key)] = cmd
        
        istring: List[str] = list()
        ibuffer: List[str] = list()
        y, x    = self.stdscr.getyx()
        curpos  = 0
        index   = 0
        curses.curs_set( cursor )
        
        quitkey = quitkey if isinstance(quitkey, int) else ord(quitkey)
        arrow_key = (
            curses.KEY_LEFT,
            curses.KEY_RIGHT,
            curses.KEY_UP,
            curses.KEY_DOWN
        )
        
        while True:
            key = self.stdscr.getch()
            if key == quitkey:
                break
            elif key == curses.KEY_BACKSPACE and istring and curpos:
                curpos, index = self.__handle_delete_char( istring, curpos, index )
            elif key >= 32 and key <= 126:
                curpos, index = self.__handle_key( istring, key, curpos, index )
            else:
                curpos, index = self.__handle_command( istring, key, index, curpos, command, arrow_key, coding )
            
            self.stdscr.move(y, x)
            clear( self.stdscr, istring, curpos )
            
            if mask is not None:
                # write mask
                self.stdscr.addstr(mask * len(istring))
            else:
                # write string
                self.stdscr.addstr("".join(istring))
            
            if istring != ibuffer:
                self.stdscr.refresh()
                ibuffer = istring.copy()
            # move back cursor to the right position
            self.stdscr.move(y, x + curpos)
            
        return "".join(istring)

    def __handle_delete_char( self, istring: List[str], curpos: int, index: int ) -> Tuple[int, int]:
        if index - 1 >= 0:
            ksize = istring.pop(index - 1)
            curpos -= wcwidth.wcswidth(ksize)
            index -= 1
        return curpos, index
    
    def __handle_key( self, istring: List[str], key: int, curpos: int, index: int ) -> Tuple[int, int]:
        istring.insert(index, chr(key))
        key_size = wcwidth.wcwidth(chr(key))
        return curpos + key_size, index + 1

    def __handle_command( self, 
                         istring: List[str], 
                         key: int, 
                         index: int, 
                         curpos: int, 
                         command: Dict[Union[Tuple[int], int], Callable[..., Tuple[int, int]]], 
                         arrow_key: List[int],
                         coding: str) -> Tuple[int, int]:
        if key in arrow_key:
            if key == curses.KEY_LEFT:
                if index - 1 < 0:
                    return curpos, index
                curpos -= wcwidth.wcswidth(istring[index - 1])
                index -= 1
            elif key == curses.KEY_RIGHT:
                if index + 1 > len(istring):
                    return curpos, index
                curpos += wcwidth.wcswidth(istring[index])
                index += 1
            elif key == curses.KEY_UP:
                curpos = 0
            elif key == curses.KEY_DOWN:
                curpos = 0
                for c in istring:
                    curpos += wcwidth.wcwidth(c)
                index = len(istring)
            return curpos, index
        else:
            buffer = self.__get_buffer( key )
            # chech command
            for key, cmd in command.items():
                if key in buffer:
                    curpos, index = cmd(istring, curpos, index)
                    return curpos, index
            
            # try decode keys buffer
            try:
                unistr = bytearray( buffer ).decode( coding )
                for uni_char in unistr:
                    istring.insert(index, uni_char)
                    curpos += wcwidth.wcswidth(uni_char)
                    index += 1
                
            # 不处理错误, 代表用户输入的不是utf-8编码
            except UnicodeDecodeError:  pass
            except ValueError:          pass
            return curpos, index
                    
    
    def __get_buffer( self, key: int ) -> Tuple[int]:
        # get keys buffer
        self.delay = False
        keys = [key]
        while True:
            key = self.stdscr.getch()
            if key == -1: break
            keys.append(key)
        self.delay = True
        return tuple(keys)
          
    @property
    def delay( self ) -> bool:
        return self.__delay
    @delay.setter
    def delay( self, delay: bool ) -> None:
        self.__delay = delay
        self.stdscr.nodelay( not delay )
    
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

