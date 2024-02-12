from .Mouse import Mouse
import unicurses as curses
from .Component import Component


class Input(Component):
    def __init__(self, stdscr: int) -> None:
        super().__init__()
        self.stdscr: int = stdscr
        self.logKeys: bool = False
        self.mouse: Mouse = Mouse()
        return
    
    def KeyDown(self) -> int:
        """获取输入"""
        key = curses.wgetch(self.stdscr)
        if self.logger and self.logKeys:
            self.logger.Info(f"Input: {key}")
        return key

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
    
    def InitKeys(self) -> None:
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
