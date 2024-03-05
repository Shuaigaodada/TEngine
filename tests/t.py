import curses

scr = curses.initscr()
curses.noecho()
curses.cbreak()
curses.start_color( )
scr.keypad( False )

# key = scr.getch()
# scr.addstr( f"key: {key}" )
while scr.getch() != 27: pass

curses.nocbreak()
scr.keypad( False )
curses.echo()
curses.endwin()

