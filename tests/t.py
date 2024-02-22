import curses
import typing as T

scr = curses.initscr()

scr.addstr(chr(0x2588) * 3)
scr.getch()

curses.endwin()