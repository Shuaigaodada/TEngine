import ssl
import socket
from typing import *
from TEngine.interfaces import SSClient
from .ssclient import SSClient
from ..interfaces import SocketServer as SocketServerInterface


class SocketServer( SocketServerInterface ):
    __instance: Optional["SocketServer"] = None
    
    def __new__( cls, *args, **kwargs ) -> "SocketServer":
        if cls.__instance is None:
            cls.__instance = super().__new__( cls )
        return cls.__instance
    
    def __init__(self, 
                 __addr: str, 
                 __port: int, 
                 *, 
                 family: Union[str, int] = "IPv4", 
                 proto: Union[str, int] = "TCP") -> None:
        self.address        : str               = __addr
        self.port           : int               = __port
        
        self.family         : Optional[str]     = None
        self.proto          : Optional[str]     = None
        self.__fam          : Optional[int]     = None
        self.__proto        : Optional[int]     = None
        
        self.clients        : List[SSClient] = {}
        
        self.__family__( family )
        self.__proto__( proto )
        
        self.socket         : socket.socket     = socket.socket( self.__fam, self.__proto )
        self.ssl            : bool              = False
        self.context        : Optional[ssl.SSLContext] = None
        
        self.__wrap_kwargs  : Dict[str, Any]    = {}

    def find(self, __noc: Union[SSClient, str, int, socket.socket]) -> SSClient:
        if isinstance( __noc, str ):
            for client in self.clients:
                if client.name == __noc:
                    return client
            raise ValueError( f"Client not found: {__noc}" )
        elif isinstance( __noc, int ):
            return self.clients[__noc]
        elif isinstance( __noc, SSClient ):
            return __noc
        elif isinstance( __noc, socket.socket ):
            for client in self.clients:
                if client.socket == __noc:
                    return client
            raise ValueError( f"Client not found: {__noc}" )
        else:
            raise TypeError( f"Unknow type: {type(__noc).__name__}" )
    
    def rm_client(self, __noc: Union[SSClient, str, socket.socket]) -> None:
        client = self.find( __noc )
        client.disconnect()
        self.clients.remove( client )
    
    def rename(self, __noc: Union[SSClient, str, socket.socket], __name: str) -> None:
        client = self.find( __noc )
        client.name = __name
    
    def set_opt( self, __lvl: int, __opt: int, __val: bool ) -> None:
        self.socket.setsockopt( __lvl, __opt, __val )
    
    def createSSL( self, __cf: str, __kf: str, *, checkhost: bool = False, **context_kwargs) -> None:
        if not context_kwargs:
            context_kwargs = { "purpose": ssl.Purpose.CLIENT_AUTH }
        self.context = ssl.create_default_context( **context_kwargs )

    def __family__(self, __f: Union[str, int]) -> None:
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
        
