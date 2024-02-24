import curses

def main(stdscr):
    # 初始化 curses 环境设置
    curses.curs_set(0)  # 隐藏光标
    stdscr.clear()  # 清屏
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    curses.mouseinterval(0)  # 设置鼠标事件的最小间隔

    # 启用鼠标移动事件的报告
    print("\033[?1003h\n")  # 对于 xterm 和类似终端

    drawing = False  # 跟踪是否正在绘制
    while True:
        key = stdscr.getch()

        if key == curses.KEY_MOUSE:
            _, mx, my, _, bstate = curses.getmouse()

            # 按下鼠标左键开始绘制
            if bstate & curses.BUTTON1_PRESSED or bstate & curses.BUTTON1_CLICKED:
                drawing = True
                stdscr.addstr(my, mx, 'X')  # 在按下的位置打印 'X'
                stdscr.refresh()

            # 鼠标移动时绘制 'Y'
            elif drawing and bstate & curses.REPORT_MOUSE_POSITION:
                stdscr.addstr(my, mx, 'Y')  # 在移动的位置打印 'Y'
                stdscr.refresh()

            # 鼠标释放时结束绘制
            elif bstate & curses.BUTTON1_RELEASED:
                drawing = False

        elif key == ord('q'):  # 按 'q' 键退出
            break

    # 禁用鼠标移动事件的报告
    print("\033[?1003l\n")  # 对于 xterm 和类似终端

curses.wrapper(main)
