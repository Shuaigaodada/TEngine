SERVER_IP = "localhost"
SERVER_PORT = 9113
SERVER_ADDRESS = (SERVER_IP, SERVER_PORT)

# Path: tests/socket_test/server.py
import env
import typing as T
from TEngine.server import socket
from threading import Thread

# AF_INET: 互联网
# SOCK_STREAM: TCP协议
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind( SERVER_ADDRESS )
message_limit: int = 10240 # 10KB message

clients: T.Dict[ str, socket.socket ] = {}

def recv_message( name: str, client: socket.socket ) -> None:
    global clients
    while True:
        message: bytes = client.recv( message_limit )
        if not message:
            print( f"{name} is disconnected." )
            for _client in clients.values( ):
                _client.sendall( bytes( f"{name} is disconnected.", 'utf-8' ) )
            clients.pop( name )
            client.close( )
            break
        
        print( f"recv message from {name}: {message.decode( 'utf-8' )}" )
        for _client in clients.values( ):
            _client.sendall( b": ".join( ( bytes( name, 'utf-8' ), message ) ) )

def main( *args, **kwargs ) -> T.NoReturn:
    first_connection: bool = True
    server.listen( -1 )
    server.settimeout( 10 )
    print( f"server is start, listening port: {SERVER_PORT}" )
    while True:
        try:
            client, address = server.accept( )
            client_name = client.recv( 1024 ).decode( 'utf-8' )
        except socket.timeout:
            if not first_connection and not clients:
                print( "all client is disconnected, start close server." )
                break
            else:
                continue
        
        first_connection = False
        print( f"{client_name} is connected." )
        clients[client_name] = client
        Thread( target=recv_message, args=(client_name, client), daemon=True ).start( )

    server.shutdown( socket.SHUT_RDWR )
    server.close()
    exit( 0 )

if __name__ == "__main__":
    main( )
