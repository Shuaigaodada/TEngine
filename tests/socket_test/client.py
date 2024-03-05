SERVER_IP = "localhost"
SERVER_PORT = 9113
SERVER_ADDRESS = (SERVER_IP, SERVER_PORT)

# Path: tests/socket_test/client.py
import os
import time
import socket
import curses
import locale
import typing as T
from threading import Thread

# AF_INET: 互联网
# SOCK_STREAM: TCP协议
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
message_limit: int = 10240 # 10KB message
all_message: T.List[ str ] = []
input_text = "Input message: "

def get_input_pos( message: T.List ) -> int:
    return len( input_text ) + len( message )

def input_message( stdscr: curses.window ) -> str:
    byte_buffer = bytearray()
    message = []

    height, width = stdscr.getmaxyx()
    input_pos_y = height - 1
    stdscr.move(input_pos_y, len(input_text))
    stdscr.clrtoeol( )

    while True:
        stdscr.refresh()
        c = stdscr.getch()

        if c == 10:  # Enter 键
            break
        elif c == curses.KEY_BACKSPACE or c == 127:  # 退格键
            if message:
                message.pop()  # 删除最后一个字符
                stdscr.move(input_pos_y, len(input_text) + len(''.join(message)))
                stdscr.clrtoeol()  # 清除从光标到行尾的内容
                stdscr.addstr(input_pos_y, len(input_text), ''.join(message))  # 重新显示文本
        elif c >= 32 and c <= 126:  # 可打印的ASCII字符
            # 处理单字节字符
            char = chr(c)
            message.append(char)
            stdscr.addstr(char)
        else:
            # 尝试处理多字节字符（如UTF-8中文字符）
            try:
                byte_buffer += bytes([c])
                char = byte_buffer.decode('utf-8')
                message.append(char)
                stdscr.addstr(char)
                byte_buffer.clear()  # 清空缓冲区，等待下一个字符
            except UnicodeDecodeError:
                # 如果解码失败，继续累积字节
                continue
            except ValueError:
                continue

    return ''.join(message)

def recv_message( stdscr: curses.window, message_pad: curses.window ) -> None:
    message_index = 1
    while True:
        message: str = client.recv( message_limit ).decode( 'utf-8' )
        if not message:
            break
        
        cursor_y, cursor_x = stdscr.getyx( )
        
        if message_index < curses.LINES - 2:
            message_pad.addstr( message_index, 1, message )
        else:
            message_pad.addstr( message_index, 1, message )
        
        message_pad.box( )
        message_pad.refresh( 0, 0, 0, 0, curses.LINES - 2, curses.COLS - 2 )
        stdscr.move( cursor_y, cursor_x )
        stdscr.refresh( )
        message_index += 1
        
        
        

def main( *args, **kwargs ) -> T.NoReturn:
    name = input( "Input your name: " )
    while True:
        try:
            client.connect( SERVER_ADDRESS )
        except ConnectionRefusedError:
            print( "Unable to connect to the server, try again after ten seconds, press `ctrl + c` to exit the program" )
            time.sleep( 10 )
            continue
        break
    client.sendall( name.encode( 'utf-8' ) )
    
    stdscr: curses.window = curses.initscr( )
    curses.cbreak( )
    curses.noecho( )
    locale.setlocale( locale.LC_ALL, "" )
    
    stdscr.keypad( True )
    stdscr.clear( )
    
    message_pad = curses.newpad( 10000, curses.COLS - 1 )
    message_pad.scrollok( True )
    message_pad.box( )
    message_pad.refresh( 0, 0, 0, 0, curses.LINES - 2, curses.COLS - 2 )
    
    stdscr.move( stdscr.getmaxyx()[0] - 1, 0 )
    stdscr.addstr( input_text )
    
    Thread( target=recv_message, args=(stdscr, message_pad), daemon=True ).start( )
    while True:
        message: str = input_message( stdscr )
        if message == "exit":
            break
        
        if len( message ) < message_limit:
            client.sendall( message.encode( 'utf-8' ) )
    
    curses.nocbreak( )
    curses.endwin( )
    client.shutdown( socket.SHUT_RDWR )
    client.close( )


if __name__ == "__main__":
    main( )
