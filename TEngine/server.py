import socket
import struct
import threading
from typing import *

__all__ = [ "Server" ]
class ClientPacket(NamedTuple):
    client: socket.socket
    data: bytes

class Server:
    def __init__( 
                 self, 
                 address    : str = 'localhost', 
                 port       : int = 8000,
                 family     : int | str = "IPv4",
                 protocol   : int | str = "TCP"
                ) -> None:
        """address:服务器地址, port:服务器端口"""
        self.address    : str        = address
        self.port       : int        = port
        
        
        family_info = self.__family_info( family )
        protocol_info = self.__protocol_info( protocol )
        
        self.family = family_info[0]
        self.protocol = protocol_info[0]
        
        socket_family = family_info[1]
        socket_protocol = protocol_info[1]
        
        self.socket = socket.socket( socket_family, socket_protocol )
        self.socket.bind( (self.address, self.port) )
        
        self.clients: List[ socket.socket ] = [ ]
        self.__bsize_buffer: Dict[ socket.socket: int ] = [ ]

    def listen( self, __backlog: int = -1 ) -> None:
        """backlog:最大连接数"""
        self.socket.listen( __backlog )

    def accept( self, __timeout: float = -1 ) -> Tuple[socket.socket, str]:
        """接受客户端连接"""
        socket.setdefaulttimeout( __timeout )
        client, address = self.socket.accept()
        self.clients.append( client )
        return client, address

    def accept_for( self, __count: int, __timeout: float = -1 ) -> List[ socket.socket ]:
        """等待足够数量的客户端"""
        while len( self.clients ) < __count: self.accept( __timeout )
        return self.clients
        
    def recv_from( self, __client: socket.socket, __size: int = -1, __flags: int = 0, __stuck: Optional[Callable] | Optional[str] = "wait_for" ) -> Optional[ bytes ]:
        if __client not in self.clients:
            raise ValueError( "Invalid client" )
        
        recv = __client.recv if self.protocol == "TCP" else __client.recvfrom
        
        if __size == -1:
            try:
                bytes_size = recv( 8, __flags )
                bsize = struct.unpack( "L", bytes_size )[ 0 ]
            except BlockingIOError:
                return None
            except struct.error:
                bytes_size = self.__bsize_buffer.get( __client, 0 )
                if not bytes_size:
                    raise ValueError( "Invalid size" )
            try:
                data = recv( bsize, __flags )
                return data
            except BlockingIOError:
                if __client.getblocking( ):
                    return None
                else:
                    self.__bsize_buffer[ __client ] = bsize
                    if isinstance( __stuck, Callable ):
                        return __stuck( recv, bsize, __flags )
                    else:
                        return self.__stuck_func( __stuck, recv, bsize, __flags )
        else:
            data = recv( __size, __flags )
            return data
    
    
        
    def __stuck_func( self, __name: str, __do: Callable, *args: Tuple[Any], **kwargs: Dict[Any, Any] ) -> Any:
        if __name == "wait_for":
            # __do must is recv or recvfrom
            while True:
                try:
                    data = __do( *args, **kwargs )
                    return data
                except BlockingIOError:
                    continue
        elif __name == "raise":
            raise BlockingIOError( "The socket is blocking and the operation would block" )
        else:
            raise ValueError( f"Invalid stuck function name: {__name}" )
        
    def __family_info( self, __family: str | int ) -> Tuple[ str, int ]:
        """返回family的字符串表示和对应的socket.AF_XXX常量值"""
        family_string = ""
        if isinstance( __family, str ):
            if __family.lower() == "ipv4":
                __family = socket.AF_INET
                family_string = "IPv4"
            elif __family.lower() == "ipv6":
                __family = socket.AF_INET6
                family_string = "IPv6"
            else:
                raise ValueError( f"Invalid family: {__family}" )
        elif isinstance( __family, int ):
            if __family == socket.AF_INET:
                family_string = "IPv4"
            elif __family == socket.AF_INET6:
                family_string = "IPv6"
            else:
                raise ValueError( f"Invalid family: {__family}" )
        else:
            raise ValueError( f"unkown type family: {type( __family ).__name__}" )
        
        if not family_string:
            raise ValueError( f"Invalid family: {__family}" )
        
        return family_string, __family
    
    def __protocol_info( self, __proto: str | int ) -> Tuple[ str, int ]:
        """返回protocol的字符串表示和对应的socket.SOCK_XXX常量值"""
        protocol_string = ""
        if isinstance( property, str ):
            protocol_string = __proto.upper()
            if protocol_string == "TCP":
                __proto = socket.SOCK_STREAM
            elif protocol_string == "UDP":
                __proto = socket.SOCK_DGRAM
            else:
                raise ValueError( f"Invalid protocol: {__proto}" )
        elif isinstance( __proto, int ):
            if __proto == socket.SOCK_STREAM:
                protocol_string = "TCP"
            elif __proto == socket.SOCK_DGRAM:
                protocol_string = "UDP"
            else:
                raise ValueError( f"Invalid protocol: {__proto}" )
        else:
            raise ValueError( f"unkown type protocol: {type( __proto ).__name__}" )
    
        if not protocol_string:
            raise ValueError( f"Invalid protocol: {__proto}" )
        
        return protocol_string, __proto
    