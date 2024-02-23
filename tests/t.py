import curses
import typing as T

stdscr = \
curses.         initscr             (               )           # init screen
curses.         cbreak              (               )           # start cbreak mode
curses.         noecho              (               )           # start noecho mode
curses.         curs_set            (       0       )           # hide cursor
curses.         start_color         (               )           # start color mode


curses.init_color(11, 0, 0, 0)
curses.init_color(12, 1000, 0, 0)
curses.init_pair(1, 12, 11)

stdscr.attron( curses.color_pair( 1 ) )
stdscr.attron( curses.A_STANDOUT )

stdscr.addstr( 0, 0, "Hello, world!" )

stdscr.attroff( curses.color_pair( 1 ) )
stdscr.attroff( curses.A_STANDOUT )

stdscr.getch()

curses.echo()
curses.nocbreak()
curses.endwin() # end screen
