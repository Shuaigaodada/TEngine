import os
import json
import pickle
import socket
import struct
from typing import *

__all__ = ['Client']

class Client:
    def __init__( self, 
                 host_address   : str       = "localhost", 
                 port           : int       = 8000,
                 family         : int | str = "IPv4",
                 protocol       : int | str = "TCP"
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
        self.__buffers: Dict[ int, bytes ] = { }

    def connect( self, __timeout: Optional[int] = None, __retry: int = 3 ) -> None:
        """连接服务器"""
        
        self.socket.settimeout( __timeout )
        
        for i in range( __retry ):
            try:
                self.socket.connect( (self.host_address, self.port) )
                break
            except Exception as e:
                if i == __retry - 1:
                    raise e
                else:
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
             ) -> Any:
        
        recv: Callable = self.socket.recv if self.protocol == "TCP" else self.socket.recvfrom
        
        self.socket.settimeout( __timeout )
        if not __size:
            bsize: float = struct.unpack( ">L", recv( struct.calcsize( ">L" ), __flags ) )[ 0 ]
            return recv( bsize, __flags )
        else:
            return recv( __size, __flags )
    
    def encode( self, __data: Any, encoding: str = "utf-8" ) -> bytes:
        """编码数据"""
        if isinstance( __data, bytes ):
            return __data
        elif isinstance( __data, str ):
            return __data.encode( encoding )
        elif isinstance( __data, (list, dict) ):
            return json.dumps( __data ).encode( encoding )
        elif isinstance( __data, (int, float) ):
            return struct.pack( ">L", __data )[ 0 ]
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
   