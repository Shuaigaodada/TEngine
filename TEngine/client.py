import os
import time
import json
import pickle
import socket
import struct
import ssl as SSL
from typing import *
from .converter import Converter

__all__ = ['SocketClient']


class SocketClient:
    def __init__( self,
                 host_address   : str       = "localhost", 
                 port           : int       = 8000,
                 family         : int | str = "IPv4",
                 protocol       : int | str = "TCP",
                 ) -> None:
        self.host_address = host_address
        self.port = port
        
        family_info = self.__family_info( family )
        proto_info = self.__proto_info( protocol )
        
        self.family = family_info[0]
        self.protocol = proto_info[0]
        
        socket_family = family_info[1]
        socket_protocol = proto_info[1]
        
        self.socket = socket.socket( socket_family, socket_protocol )
        self.__size_buffer: int = -1

    def create_SSL( self, certfile: str, context_kwargs: Dict = {}, locations_kwargs: Dict = {}, wrap_kwargs: Dict = {} ) -> None:
        context = SSL.create_default_context( **context_kwargs )
        context.load_verify_locations( certfile, **locations_kwargs )
        self.socket = context.wrap_socket( self.socket, **wrap_kwargs )
    
    def connect( self, __timeout: Optional[int] = None, retry: int = 3 ) -> None:
        """连接服务器"""
        
        self.socket.settimeout( __timeout )
        
        for i in range( retry ):
            try:
                self.socket.connect( (self.host_address, self.port) )
                break
            except Exception as e:
                if i == retry - 1:
                    raise e
                else:
                    time.sleep( 1 )
                    continue
        self.socket.settimeout( None )
    
    def send( 
             self, 
             __data: Any, 
             __flags: int = 0, 
             __timeout: Optional[int] = None, 
             convert: bool = True, 
             encoding: str = "utf-8" 
             ) -> None:
        """发送数据"""
        if convert:
            __data = self.encode( __data, encoding )
        
        send: Callable = self.socket.sendall if self.protocol == "TCP" else self.socket.sendto
        
        self.socket.settimeout( __timeout )
        send( self.encode( len( __data ) ), __flags )
        send( __data, __flags )
        self.socket.settimeout( None )
    
    def recv( self, 
             __size: int = -1, 
             __flags: int = 0, 
             __timeout: Optional[int] = None 
             ) -> Optional[Converter]:
        
        recv: Callable = self.socket.recv if self.protocol == "TCP" else self.socket.recvfrom
        
        self.socket.settimeout( __timeout )
        if __size == -1:
            if self.__size_buffer == -1:
                try:
                    bsize: int = struct.unpack( ">L", recv( struct.calcsize( ">L" ), __flags ) )[ 0 ]
                    self.__size_buffer = bsize
                except struct.error:
                    return None # TODO: 处理struct.unpack异常
                except socket.timeout:
                    return None # TODO: 处理超时
                except BlockingIOError:
                    return None # TODO: 处理阻塞
            data: bytes = b""
            while len(data) < self.__size_buffer:
                try:
                    chunk: bytes = recv( self.__size_buffer - len(data), __flags )
                    if not chunk:
                        break # connection closed
                    data += chunk
                except socket.timeout:
                    return None # TODO: 处理超时
                except BlockingIOError:
                    return None # TODO: 处理阻塞
            self.__size_buffer = -1
            return Converter( data )
        else:
            return recv( __size, __flags )
        
    def __enter__( self ) -> "SocketClient":
        return self
    def __exit__( self, exc_type, exc_value, traceback ) -> None:
        self.close()
    
    def disconnect( self, read: bool = True, write: bool = True ) -> None:
        """断开连接"""
        if read:
            self.socket.shutdown( socket.SHUT_RD )
        if write:
            self.socket.shutdown( socket.SHUT_WR )
    
    def close( self ) -> None:
        """关闭连接"""
        try:
            self.disconnect( )
            self.socket.close()
        except OSError:
            return
    
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


if __name__ == "__main__":
    from threading import Thread
    
    def server( ) -> None:
        from server import SocketServer
        with SocketServer( ) as server:
            server.listen( )
            
            server.accept_for( 1 )
            
            server.send( b"Hello Client" )
            
            data = server.recv( )[ 0 ]
            print( data.as_json( ) )
    
    Thread( target = server ).start( )
    
    with SocketClient( ) as client:
        time.sleep( 1 )
        client.connect( )
        
        client.send( [1, 2, 3, 4] )
        
        data = client.recv( )
        print( data.decode( ) )
        
    
