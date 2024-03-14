import socket
from ssl import SSLContext
from typing import *
from typing import Dict, Tuple
from ..interfaces import SSClient as SSClientInterface
from ..interfaces import Converter as ConverterInterface
from ..interfaces import SocketServer as SocketServerInterface

class SSClient( SSClientInterface ):
    def __init__(self, __client: socket.socket, __addr: Tuple[str, int], __serv: SocketServerInterface, __ssl: bool = False, /, context: SSLContext | None = None, **warp_kwargs: Dict[str, Any]) -> None:
        self.socket = __client
        self.address = __addr
        self.__server = __serv
        self.name = ""
        self.id = id( self )
        
        if __ssl:
            self.socket = context.wrap_socket( self.socket, server_side = True, **warp_kwargs )
    
    @property
    def connected(self) -> SocketServerInterface:
        return self.__server

    def send(self, data: Any, __flag: int = 0, *, convert: bool = True) -> None:
        self.__server.send_to( self.socket, data, __flag, convert = convert )

    def recv(self, __size: int | None = None, __flag: int = 0) -> ConverterInterface | None:
        return self.__server.recv_from( self.socket, __size, __flag )
    
    def disconnect(self) -> None:
        self.__server.rm_client( self )
        self.socket.close()
    
    def __hash__(self) -> int:
        return hash( self.socket )
    
    def __eq__(self, other: Union["SSClient", socket.socket, str]) -> bool:
        other = self.__server.find( other )
        return self.socket == other.socket
    
    def peername(self) -> Tuple[Union[str, int]]:
        return self.socket.getpeername()
    