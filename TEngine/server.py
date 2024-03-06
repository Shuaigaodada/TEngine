import os
import json
import pickle
import socket
import struct
from typing import *
from loguru import logger
from threading import Thread

__all__ = [ "SocketServer", "INFO", "WARNING", "ERROR", "ReturnedData", "LoggerTuple" ]
class Logger:
    def info( self, __msg: str ) -> None: ...
    def warning( self, __msg: str ) -> None: ...
    def error( self, __msg: str ) -> None: ...

class ReturnedData(NamedTuple):
    client: socket.socket
    data: bytes
    
    
    def as_json( self, encoding: str = "utf-8", *args, **kwargs ) -> Optional[Dict[str, Any]]:
        try:
            return json.loads( self.data.decode( encoding ), *args, **kwargs )
        except json.JSONDecodeError:
            return None
    def as_list( self, encoding: str = "utf-8", *args, **kwargs ) -> List[Any]:
        return self.as_json( encoding, *args, **kwargs )
    def as_dict( self, encoding: str = "utf-8", *args, **kwargs ) -> Dict[str, Any]:
        return self.as_json( encoding, *args, **kwargs )
    
    def as_number( self, __type: Type, encoding: str = "utf-8", *args, **kwargs ) -> Union[int, float]:
        if isinstance( __type, str ):
            return struct.unpack( __type, self.data.decode( encoding, *args, **kwargs ) )[ 0 ]
        else:
            if isinstance( __type, int ):
                return self.__deint( 'L' )
            elif isinstance( __type, float ):
                return self.__deint( 'f' )
            else:
                return self.__deint( 'i' )
    def as_boolen( self ) -> bool:
        return struct.unpack( "?", self.data )[ 0 ]
            
    
    def __deint( self, key: str ) -> str:
        fmt = [ "<", ">" ]
        keys = [ fmt[ 0 ] + key, key, fmt[ 1 ] + key ]
        for k in keys:
            try:
                return struct.unpack( k, self.data )[ 0 ]
            except struct.error:
                continue
        raise struct.error( f"Invalid key: {key}" )    
            
    
    def decode( self, encoding: str = "utf-8", __error: str = "strict" ) -> str:
        return self.data.decode( encoding, __error )
    
    def as_object( self, *args, **kwargs ) -> Any:
        return pickle.loads( self.data, *args, **kwargs )
    
    @property
    def bytes( self ) -> bytes:
        return self.data
    @property
    def size( self ) -> int:
        return len( self.data )

class LoggerTuple(NamedTuple):
    message: str
    level: int

INFO: int = 0
WARNING: int = 1
ERROR: int = 2

class SocketServer:
    def __init__(
                 self, 
                 address    : str = 'localhost', 
                 port       : int = 8000,
                 family     : int | str = "IPv4",
                 protocol   : int | str = "TCP",
                 logging    : bool = True,
                 log_cfg    : Dict[str, str] = None
                ) -> None:
        self.address    : str        = address
        self.port       : int        = port
        self.logging    : bool       = logging
        self.lcfg       : Dict[str, Dict | str | object] = {}
        
        if logging:
            self.__config_logger( log_cfg )
        family_info = self.__family_info( family )
        proto_info = self.__proto_info( protocol )
        
        self.family = family_info[0]
        self.protocol = proto_info[0]
        
        socket_family = family_info[1]
        socket_protocol = proto_info[1]
        
        self.socket = socket.socket( socket_family, socket_protocol )
        
        self.clients: Dict[ int | str, socket.socket ]  = { }
        self.__bsize_buffer: Dict[ socket.socket: int ] = { }
        
        self.__binded: bool = False
        self.set_option( socket.SOL_SOCKET, socket.SO_REUSEADDR, True )
        
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
        
        self.log( "listen", INFO, __backlog if __backlog != -1 else "unlimited")
        self.socket.listen( __backlog )
        self.log( "show_link", INFO, f"http://{self.address}:{self.port}")

    def accept( self, __name: Optional[str | int] = None, __timeout: Optional[float] = None ) -> Tuple[socket.socket, str]:
        """接受客户端连接"""
        self.socket.settimeout( __timeout )
        
        try:                    client, address = self.socket.accept( )
        except socket.timeout:  return None, None
        
        if __name is None:
            __name = len( self.clients )
        
        self.socket.settimeout( None )
        self.clients[ __name ] = client
        self.log( "accept", INFO, address )
        return client, address

    def accept_for( self, __count: int, __timeout: Optional[float] = None ) -> List[ socket.socket ]:
        """等待足够数量的客户端"""
        self.log( "accept_for", INFO, __count )
        while len( self.clients ) < __count: self.accept( __timeout )
        self.log( "all_accept", INFO )
        return self.clients
        
    def recv_from( self, __client: socket.socket, __size: int = -1, __flags: int = 0, __stuck: Callable | str = "none" ) -> Optional[ bytes ]:
        if __client not in self.clients.values( ):
            raise ValueError( "Invalid client" )
        
        recv = __client.recv if self.protocol == "TCP" else __client.recvfrom
        if __size == -1:
            try:
                if __client in self.__bsize_buffer:
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
                self.log( "recv_from", INFO, __client.getsockname( ) )
                return data
            except BlockingIOError:
                if __client.getblocking( ):
                    self.log( "timeout_block", ERROR )
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
    
    def recv( self, __count: int = 1, __size: int = -1, __flags: int = 0, __stuck: Optional[Callable] | Optional[str] = "none", callback: Optional[Callable] = None ) -> List[ReturnedData]:
        """接收数据"""
        datas: List[ ReturnedData ] = [ ]
        self.set_clients_blocking( False )
        
        while len( datas ) < __count:
            for client in self.clients.values( ):
                data = self.recv_from( client, __size, __flags, __stuck )
                if data:
                    datas.append( ReturnedData( client, data ) )
                    if callback is not None:
                        callback( data )
        
        self.set_clients_blocking( True )
        return datas
    
    def send_to( self, __client: socket.socket, __data: bytes, __flags: int = 0 ) -> None:
        """发送数据"""
        if __client not in self.clients.values( ):
            raise ValueError( "Invalid client" )
        
        bsize = struct.pack( ">L", len( __data ) )
        # send data size
        try:
            __client.sendall( bsize, __flags )
            __client.sendall( __data, __flags )
        except Exception as e:
            self.log( e )
        
        return
    
    def send( self, __data: bytes, __flags: int = 0 ) -> None:
        """发送数据"""
        for client in self.clients.values( ):
            self.send_to( client, __data, __flags )
        return
    
    def set_clients_blocking( self, __blocking: bool ) -> None:
        for client in self.clients.values( ):
            client.setblocking( __blocking )
    
    def close( self ) -> None:
        for client in self.clients.values( ):
            try:                client.close( )
            except Exception:   continue
        try:
            self.socket.shutdown( socket.SHUT_RDWR )
        except OSError: pass
        finally:
            self.socket.close( )
        self.log( "close", INFO )
    
    def log( self, __name: str, __level: int = INFO, *__format: Tuple[str] ) -> None:
        __tuple = LoggerTuple( self.lcfg.get( "msg" ).get( __name ), __level )
        # 如果没有消息或者不需要记录日志
        if not self.logging: return
        if not __tuple.message:
            __tuple = LoggerTuple( __name, __level )
        logger: Logger = self.lcfg.get( "logger" )
        if __tuple.level == 0:
            logger.info( __tuple.message.format( *__format ) )
        elif __tuple.level == 1:
            logger.warning( __tuple.message.format( *__format ) )
        elif __tuple.level == 2:
            logger.error( __tuple.message.format( *__format ) )
        else:
            raise ValueError( f"Invalid level: {__tuple.level}" )
        
        if self.lcfg.get( "file", None ) is not None:
            if self.lcfg.get( "path", None ) is not None:
                with open( os.path.join(self.lcfg.get( "path" ), self.lcfg.get( "file" )), "a" ) as fp:
                    fp.write( f"{__tuple.message.format( *__format )}\n" )
            else:
                with open( self.lcfg.get( "file" ), "a" ) as fp:
                    fp.write( f"{__tuple.message.format( *__format )}\n" )
    
    def encode( self, __data: Any, encoding: str = "utf-8" ) -> bytes:
        """编码数据"""
        if isinstance( __data, bytes ):
            return __data
        elif isinstance( __data, str ):
            return __data.encode( encoding )
        elif isinstance( __data, (list, dict) ):
            return json.dumps( __data ).encode( encoding )
        elif isinstance( __data, (int, float) ):
            return struct.pack( ">L", __data )
        else:
            return pickle.dumps( __data )
    
    def __config_logger( self, __cfg: Optional[ Dict[str, object] ] ) -> None:
        if __cfg is None:
            self.lcfg = {
                "file": None,
                "path": None,
                "logger": logger,
                "msg": {
                    "listen": "start listening for {0} clients",
                    "accept": "accept connection from {0}",
                    "accept_for": "waiting accept {0} clients",
                    "all_accept": "all clients are accepted",
                    "timeout_block": "time was out but didn't not get any data",
                    "recv_from": "recv data from {0}",
                    "close": "server closed",
            
                    "show_link": "you can see the link: {0}",
                }
            }
        else:
            self.lcfg = __cfg
        
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
    
    def __proto_info( self, __proto: str | int ) -> Tuple[ str, int ]:
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
        if exc_type is not None:
            self.log( f"exit_with_error: {exc_type.__name__}", ERROR )
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
        
        callback = lambda bstr: server.log( bstr.decode( ), INFO )
        
        server.recv( 2, callback=callback )
        
        
        
              
    