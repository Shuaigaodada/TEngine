import json
import pickle
import socket
import struct
import ssl as SSL
from typing import *
from threading import Thread
from .converter import Converter

__all__ = [ "SocketServer", "SSClient" ]

# SSClient -> Socket Server Client( just allow to send, recv, and more server's client's operations )
class SSClient:
    def __init__( self, __client: socket.socket, address: str, __server: "SocketServer", ssl: bool = False, **wrap_kwargs ) -> None:
        self.socket = __client
        self.__server = __server
        self.address = address
        self.name = ""
        
        if ssl:
            self.socket = SSL.wrap_socket( __client, server_side=True, **wrap_kwargs if wrap_kwargs else {"ssl_version": SSL.PROTOCOL_TLS} )
    
    @property
    def connected( self ) -> "SocketServer":
        return self.__server
    
    def send( self, __data: Any, __flags: int = 0, convert: bool = True ) -> None:
        self.__server.send_to( self.socket, __data, __flags, convert )
    
    def recv( self, __size: int = -1, __flags: int = 0, __stuck: Union[str, Callable] = "none" ) -> Optional[ Converter ]:
        return self.__server.recv_from( self.socket, __size, __flags, __stuck )

    def close( self ) -> None:
        self.__server.remove_client( self.socket )
        self.socket.close( )
    
    def __eq__( self, other: Union[str, "SSClient", socket.socket] ) -> bool:
        other = self.__server.find( other )
        return self.socket == other.socket and other.name == self.name
    
    
    @property
    def blocking( self ) -> bool:
        return self.socket.getblocking( )
    @blocking.setter
    def blocking( self, __blocking: bool ) -> None:
        self.socket.setblocking( __blocking )
        
    @property
    def timeout( self ) -> float:
        return self.socket.gettimeout( )
    @timeout.setter
    def timeout( self, __timeout: float ) -> None:
        self.socket.settimeout( __timeout )
    
    @property
    def peername( self ) -> Tuple[str, int]:
        return self.socket.getpeername( )
    

class SocketServer:
    def __init__(
                 self, 
                 address    : str             = 'localhost', 
                 port       : int             = 8000,
                 family     : Union[str, int] = "IPv4",
                 protocol   : Union[str, int] = "TCP"
                ) -> None:
        self.address    : str        = address
        self.port       : int        = port
        
        family_info = self.__family_info( family )
        proto_info = self.__proto_info( protocol )
        
        self.family = family_info[0]
        self.protocol = proto_info[0]
        
        socket_family = family_info[1]
        socket_protocol = proto_info[1]
        
        self.socket = socket.socket( socket_family, socket_protocol )
        
        self.clients: List[ SSClient ]  = []
        self.__bsize_buffer: Dict[ SSClient: int ] = { }
        
        self.__binded: bool = False
        self.__SSL   : bool = False
        
        self.__SSL_wrap_kwarg = { }
        self.set_option( socket.SOL_SOCKET, socket.SO_REUSEADDR, True )
    
    def find( self, __name_or_client: Union[str, socket.socket, SSClient] ) -> Optional[SSClient]:
        if isinstance( __name_or_client, str ):
            for client in self.clients:
                if client.name == __name_or_client:
                    return client
            return None
        elif isinstance( __name_or_client, SSClient ):
            return __name_or_client
        elif isinstance( __name_or_client, socket.socket ):
            for client in self.clients:
                if client.socket == __name_or_client:
                    return client
        else:
            return None
        
    def remove_client( self, client: Union[str, socket.socket, SSClient] ) -> SSClient:
        return self.clients.pop( self.clients.index( self.find( client ) ) )

    def rename( self, __c: SSClient, __n: str ) -> str:
        """client, name"""
        __c.name = __n
        return __n
    
    def set_option( self, __level: int, __option: int, __value: bool ) -> None:
        self.socket.setsockopt( __level, __option, __value )

    def bind( self, address: Optional[ str ] = None, port: Optional[ int ] = None ) -> None:
        address = address if address is not None else self.address
        port = port if port is not None else self.port
        
        self.socket.bind( (address, port) )
        self.__binded = True
        
    def listen( self, __backlog: int = -1 ) -> None:
        """backlog:最大连接数"""
        if not self.__binded:
            self.bind( )
        self.socket.listen( __backlog )
    
    def create_SSL( self, certfile: Optional[str], keyfile: Optional[str], **context_kwargs ) -> None:
        context: SSL.SSLContext = SSL.create_default_context( **context_kwargs if context_kwargs else SSL.Purpose.CLIENT_AUTH )
        context.load_cert_chain( certfile=certfile, keyfile=keyfile )
        self.__SSL = True

    def set_wrapper( self, **wrap_kwargs ) -> None:
        if self.__SSL:
            self.__SSL_wrap_kwarg = wrap_kwargs
        else:
            raise ValueError( "SSL is not create" )
    
    def accept( self, __name: Optional[str] = None, __timeout: Optional[float] = None ) -> Tuple[SSClient, str, str]:
        """接受客户端连接"""
        self.socket.settimeout( __timeout )
        
        try:                    client, address = self.socket.accept( )
        except socket.timeout:  return None, None
        
        if __name is None:
            __name = "client-" + str(len( self.clients ))
        
        self.socket.settimeout( None )
        client = SSClient( client, address, self, self.__SSL, self.__SSL_wrap_kwarg )
        self.clients.append( client )
        return client, address, __name

    def accept_for( self, __count: int, __timeout: Optional[float] = None ) -> List[ SSClient ]:
        """等待足够数量的客户端"""
        while len( self.clients ) < __count: self.accept( __timeout )
        return self.clients
        
    def recv_from( self, __client: SSClient, __size: int = -1, __flags: int = 0, __stuck: Union[str, Callable] = "none" ) -> Optional[ Converter ]:
        if __client not in self.clients:
            raise ValueError( "Invalid client" )
        
        recv = __client.socket.recv if self.protocol == "TCP" else __client.socket.recvfrom
        if __size == -1:
            try:
                if __client in self.__bsize_buffer.items():
                    raise struct.error( )
                bytes_size = recv( struct.calcsize( ">L" ), __flags )
                bsize = struct.unpack( ">L", bytes_size )[ 0 ]
            except BlockingIOError:
                return None
            except struct.error:
                bytes_size = self.__bsize_buffer.pop( __client, 0 )
                if not bytes_size:                        
                    return
                bsize = bytes_size
            try:
                data = recv( bsize, __flags )
                return Converter( data )
            except BlockingIOError:
                if __client.blocking:
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
    
    def recv( self, __count: int = 1, 
             __size: int = -1, 
             __flags: int = 0, 
             callback: Optional[Callable] = None,
             client_once: bool = False
             ) -> List[Converter]:
        """接收数据"""
        datas: List[ Converter ] = [ ]
        self.set_clients_blocking( False )
        
        clients = self.clients.copy( )
        while len( datas ) < __count:
            for client in clients:
                if len( datas ) >= __count: break
                data = self.recv_from( client, __size, __flags )
                if data:
                    data.client = client
                    datas.append( data )
                    if callback is not None:
                        callback( data )
                    if client_once:
                        clients.remove( client )
        
        self.set_clients_blocking( True )
        return datas
    
    def send_to( self, 
                __client: SSClient, 
                __data: bytes, 
                __flags: int = 0, 
                convert: bool = True,
                ) -> None:
        """发送数据"""
        if __client not in self.clients:
            raise ValueError( "Invalid client" )
        if convert:
            __data = self.encode( __data )
        
        bsize = struct.pack( ">L", len( __data ) )
        # send data size
        try:
            __client.socket.sendall( bsize, __flags )
            __client.socket.sendall( __data, __flags )
        except Exception as e:
            raise e
        
        return
    
    def send( self, 
             __data: bytes, 
             __flags: int = 0, 
             convert: bool = True,
             without: List[SSClient] = []
             ) -> None:
        """发送数据"""
        for client in self.clients:
            if client not in without:
                try:
                    self.send_to( client, __data, __flags, convert )
                except BrokenPipeError:
                    continue
        return
    
    def set_clients_blocking( self, __blocking: bool ) -> None:
        for client in self.clients:
            client.socket.setblocking( __blocking )
    
    def close( self ) -> None:
        for client in self.clients:
            try:                client.close( )
            except Exception:   continue
        try:
            self.socket.shutdown( socket.SHUT_RDWR )
        except OSError: pass
        finally:
            self.socket.close( )
    
    def encode( self, __data: Any, encoding: str = "utf-8" ) -> bytes:
        """编码数据"""
        if isinstance( __data, bytes ):
            return __data
        elif isinstance( __data, str ):
            return __data.encode( encoding )
        elif isinstance( __data, (list, dict) ):
            return json.dumps( __data ).encode( encoding )
        elif isinstance( __data, bool ):
            return struct.pack( "?", __data )
        elif isinstance( __data, (int, float) ):
            return struct.pack( ">L", __data )
        else:
            return pickle.dumps( __data )
        
    def __stuck_func( self, __name: str, __do: Callable, *args: Tuple[ Any ], **kwargs: Dict[ Any, Any ] ) -> Any:
        __name = __name.lower( )
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
        elif __name == "none":
            return None
        else:
            raise ValueError( f"Invalid stuck function name: {__name}" )
        
    def __family_info( self, __family: Union[str, int] ) -> Tuple[ str, int ]:
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
    
    def __proto_info( self, __proto: Union[str, int] ) -> Tuple[ str, int ]:
        """返回protocol的字符串表示和对应的socket.SOCK_XXX常量值"""
        proto_str = ""
        if isinstance( __proto, str ):
            proto_str = __proto.upper()
            if proto_str == "TCP":
                __proto = socket.SOCK_STREAM
            elif proto_str == "UDP":
                __proto = socket.SOCK_DGRAM
            else:
                raise ValueError( f"Invalid protocol: {__proto}" )
        elif isinstance( __proto, int ):
            if __proto == socket.SOCK_STREAM:
                proto_str = "TCP"
            elif __proto == socket.SOCK_DGRAM:
                proto_str = "UDP"
            else:
                raise ValueError( f"Invalid protocol: {__proto}" )
        else:
            raise ValueError( f"unkown type protocol: {type( __proto ).__name__}" )
    
        if not proto_str:
            raise ValueError( f"Invalid protocol: {__proto}" )
        
        return proto_str, __proto
        
    def __enter__( self ) -> "SocketServer":
        return self
    def __exit__( self, exc_type, exc_val, exc_tb ) -> None:
        self.close( )
        return False


if __name__ == "__main__":
    client1 = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    client2 = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    
    import time, random
    def connect( __client: socket.socket ) -> None:
        time.sleep( random.randint( 1, 3 ) )
        __client.connect( ("localhost", 8000) )
    def recv( __client: socket.socket ) -> None:
        time.sleep( random.randint( 3, 4 ) )
        size = struct.unpack( ">L", __client.recv( struct.calcsize('>L') ) )[ 0 ]
        print( __client.recv( size ).decode( ) )
    def send( __client: socket.socket ) -> None:
        time.sleep( random.randint( 2, 3 ) )
        
        raw_string = str( __client.getsockname( ) ) # convert tuple to string
        raw_string = raw_string[ 1: -1 ].encode( ) # remove parentheses and encode
        
        bsize = struct.pack( ">L", len( raw_string ) )
        
        __client.sendall( bsize )
        __client.sendall( raw_string )
    
    with SocketServer( ) as server:
        server.set_option( socket.SOL_SOCKET, socket.SO_REUSEADDR, True )
        server.listen( )
        
        Thread( target=connect, args=(client1,) ).start( )
        Thread( target=connect, args=(client2,) ).start( )
        
        server.accept_for( 2 )
        
        # Thread( target=recv, args=(client1,) ).start( )
        # Thread( target=recv, args=(client2,) ).start( )
        
        Thread( target=send, args=(client1,) ).start( )
        Thread( target=send, args=(client2,) ).start( )
