import socket
from typing import *
from ssl import SSLContext
from ..interfaces import SSClient as SSClientInterface
from ..interfaces import Converter as ConverterInterface
from ..interfaces import SocketServer as SocketServerInterface

class SSClient( SSClientInterface ):
    def __init__(self, 
                 __client: socket.socket, 
                 __addr: Tuple[str, int], 
                 __serv: SocketServerInterface, 
                 __ssl: bool = False, /, 
                 context: Optional[SSLContext] = None, 
                 **warp_kwargs: Dict[str, Any]) -> None:
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

    def recv(self, __size: int | None = None, __flag: int = 0) -> Optional[ConverterInterface]:
        return self.__server.recv_from( self.socket, __size, __flag )
    
    def disconnect(self) -> None:
        self.__server.rm_client( self )
        self.socket.close()
    
    def __hash__(self) -> int:
        return hash( self.socket )
    
    def __eq__(self, other: Union["SSClient", socket.socket, str]) -> bool:
        other = self.__server.find( other )
        return self.socket == other.socket
    
    @property
    def peername(self) -> Tuple[str, int]:
        return self.socket.getpeername()

    @property
    def blocking(self) -> bool:
        return self.socket.getblocking()
    @blocking.setter
    def blocking(self, value: bool) -> None:
        self.socket.setblocking( value )
    