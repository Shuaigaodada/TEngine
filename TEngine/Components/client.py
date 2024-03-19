import ssl
import time
import socket
import struct
from typing import *

from .converter import Converter as IConverter
from ..interfaces import SocketClient as ISocketClient

__all__ = ['SocketClient']

class SocketClient(ISocketClient):
    def __init__(self, 
                 __host: str, 
                 __port: int, 
                 *, 
                 family: Union[str, int] = "IPv4", 
                 proto: Union[str, int] = "TCP") -> None:
        self.host       : str                   = __host
        self.port       : int                   = __port
        self.__fam      : int                   = -1
        self.__proto    : int                   = -1
        self.family     : str                   = ""
        self.proto      : str                   = ""
        
        self.__family__(family)
        self.__proto__ (proto)
        
        self.socket     : socket.socket         = socket.socket(self.__fam, self.__proto)
        self.__size_buffer: int                 = -1
        self.bsize_fmt  : str                   = ">L"
    
    def createSSL( 
                  self, 
                  __cf: str, 
                  *, 
                  context_kwargs: Optional[Dict[str, Any]] = None,
                  locations_kwargs: Optional[Dict[str, Any]] = None,
                  wrap_kwargs: Optional[Dict[str, Any]] = None
                  ) -> None:
        if not context_kwargs:      context_kwargs      = {"purpose": ssl.Purpose.SERVER_AUTH}
        if not locations_kwargs:    locations_kwargs    = {}
        if not wrap_kwargs:         wrap_kwargs         = {}
        
        context = ssl.create_default_context( **context_kwargs )
        context.load_verify_locations( __cf, **locations_kwargs )
        self.socket = context.wrap_socket( self.socket, **wrap_kwargs )
    
    def connect(self, __retry: Optional[int] = None, *, timeout: Optional[int] = None) -> None:
        self.socket.settimeout( timeout )
        try_count = 0
        while True:
            try:
                self.socket.connect( (self.host, self.port) )
                break
            except Exception as e:
                if __retry is None:
                    time.sleep( 1 )
                else:
                    try_count += 1
                    if try_count >= __retry:
                        raise e
                    time.sleep( 1 )
        self.socket.settimeout( None )
    
    def send(self, 
             __d: Any, 
             __flags: int = 0, 
             *, 
             timeout: Optional[float] = None, 
             convert: bool = True) -> None:
        if convert: __d = IConverter.encode( __d )
        send: Callable = self.socket.send if self.proto == "TCP" else self.socket.sendto

        self.socket.settimeout( timeout )
        bsize = struct.pack( self.bsize_fmt, len( __d ) )
        send( bsize, __flags )
        send( __d, __flags )
        self.socket.settimeout( None )
    
    def recv( self, __size: Optional[int] = None, __flags: int = 0, *, timeout: Optional[float] = None ) -> Optional[IConverter]:
        recv: Callable = self.socket.recv if self.proto == "TCP" else self.socket.recvfrom
        self.socket.settimeout( timeout )
        if __size is None:
            if self.__size_buffer == -1:
                try:
                    self.__size_buffer = struct.unpack( self.bsize_fmt, recv( struct.calcsize( self.bsize_fmt ), __flags ) )[ 0 ]
                except struct.error:
                    return None # TODO: 处理struct.unpack异常
                except socket.timeout:
                    return None # TODO: 处理socket.timeout异常
                except BlockingIOError:
                    return None # TODO: 处理BlockingIOError异常
                except Exception as e:
                    raise e
            data: bytes = b""
            while len(data) < self.__size_buffer:
                try:
                    chunk = recv( self.__size_buffer - len(data), __flags )
                    if not chunk: break
                    data += chunk
                except socket.timeout:
                    return None # TODO: 处理socket.timeout异常
                except BlockingIOError:
                    return None # TODO: 处理BlockingIOError异常
                except Exception as e:
                    raise e
            self.__size_buffer = -1
            return IConverter(data)
        else:
            return IConverter(recv( __size, __flags ))
    
    def __family__(self, __f: Union[str, int]) -> None:
        """内部方法，用于设置套接字族。
        
        参数:
            __f: 套接字族（字符串或整数形式）。
        """

        fam_str = ""
        if isinstance( __f, str ):
            if __f.lower() == "ipv4":
                __f = socket.AF_INET
                fam_str = "IPv4"
            elif __f.lower() == "ipv6":
                __f = socket.AF_INET6
                fam_str = "IPv6"
            else:
                raise ValueError( f"Invalid family: {__f}" )
        elif isinstance( __f, int ):
            if __f == socket.AF_INET:
                fam_str = "IPv4"
            elif __f == socket.AF_INET6:
                fam_str = "IPv6"
            else:
                raise ValueError( f"Invalid family: {__f}" )
        else:
            raise TypeError( f"Invalid family type: {type(__f)}" )
        self.family = fam_str
        self.__fam  = __f
    
    def __proto__(self, __p: Union[str, int]) -> None:
        """内部方法，用于设置协议类型。
        
        参数:
            __p: 协议类型（字符串或整数形式）。
        """
        proto_str = ""
        if isinstance( __p, str ):
            if __p.lower() == "tcp":
                __p = socket.SOCK_STREAM
                proto_str = "TCP"
            elif __p.lower() == "udp":
                __p = socket.SOCK_DGRAM
                proto_str = "UDP"
            else:
                raise ValueError( f"Invalid protocol: {__p}" )
        elif isinstance( __p, int ):
            if __p == socket.SOCK_STREAM:
                proto_str = "TCP"
            elif __p == socket.SOCK_DGRAM:
                proto_str = "UDP"
            else:
                raise ValueError( f"Invalid protocol: {__p}" )
        else:
            raise TypeError( f"Invalid protocol type: {type(__p)}" )
        self.proto = proto_str
        self.__proto = __p

