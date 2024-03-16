import ssl
import socket
import struct
from typing import *
from .ssclient import SSClientInterface
from .converter import ConverterInterface
from ..interfaces import SocketServer as SocketServerInterface


class SocketServer( SocketServerInterface ):
    __instance: Optional["SocketServer"] = None
    
    def __new__( cls, *args, **kwargs ) -> "SocketServer":
        """实现SocketServer作为单例类，确保整个应用中只有一个SocketServer实例。
        
        返回:
            SocketServer的单一实例。
        """
        if cls.__instance is None:
            cls.__instance = super().__new__( cls )
        return cls.__instance
    
    def __init__(self, 
                 __addr: str, 
                 __port: int, 
                 *, 
                 family: Union[str, int] = "IPv4", 
                 proto: Union[str, int] = "TCP") -> None:
        """初始化SocketServer实例，设置服务器的地址、端口、协议族和协议类型。
        
        参数:
            __addr: 服务器绑定的IP地址。
            __port: 服务器绑定的端口号。
            family: 套接字族（默认IPv4）。
            proto: 使用的协议（默认TCP）。
        """
        self.address        : str               = __addr
        self.port           : int               = __port
        
        self.family         : Optional[str]     = None
        self.proto          : Optional[str]     = None
        self.__fam          : Optional[int]     = None
        self.__proto        : Optional[int]     = None
        self.__binded       : bool              = False
        
        self.clients        : List[SSClientInterface] = {}
        self.__bsize_buffer : Dict[SSClientInterface, int] = {}
        
        self.__family__( family )
        self.__proto__( proto )
        
        self.socket         : socket.socket     = socket.socket( self.__fam, self.__proto )
        self.ssl            : bool              = False
        self.context        : Optional[ssl.SSLContext] = None
        self.bsize_fmt      : str               = ">L"
        
        self.__wrap_kwargs  : Dict[str, Any]    = {}

    def find(self, __noc: Union[SSClientInterface, str, int, socket.socket]) -> SSClientInterface:
        """根据不同的标识符（名称、索引、SSClient实例或套接字）查找并返回对应的客户端实例。
        
        参数:
            __noc: 客户端的标识符。
            
        返回:
            对应的SSClient实例。
            
        抛出:
            ValueError: 如果无法找到对应的客户端。
            TypeError: 如果__noc的类型不被支持。
        """
        if isinstance( __noc, str ):
            for client in self.clients:
                if client.name == __noc:
                    return client
            raise ValueError( f"Client not found: {__noc}" )
        elif isinstance( __noc, int ):
            return self.clients[__noc]
        elif isinstance( __noc, SSClientInterface ):
            return __noc
        elif isinstance( __noc, socket.socket ):
            for client in self.clients:
                if client.socket == __noc:
                    return client
            raise ValueError( f"Client not found: {__noc}" )
        else:
            raise TypeError( f"Unknow type: {type(__noc).__name__}" )
    
    def rm_client(self, __noc: Union[SSClientInterface, str, socket.socket]) -> None:
        """移除一个指定的客户端。
        
        参数:
            __noc: 要移除的客户端的标识符。
        """
        client = self.find( __noc )
        client.disconnect()
        self.clients.remove( client )
    
    def rename(self, __noc: Union[SSClientInterface, str, socket.socket], __name: str) -> None:
        """给指定的客户端重命名。
        
        参数:
            __noc: 要重命名的客户端的标识符。
            __name: 新的名称。
        """
        client = self.find( __noc )
        client.name = __name
    
    def set_opt( self, __lvl: int, __opt: int, __val: bool ) -> None:
        """设置套接字选项。
        
        参数:
            __lvl: 套接字选项的级别。
            __opt: 要设置的选项。
            __val: 设置的值。
        """
        self.socket.setsockopt( __lvl, __opt, __val )
    def set_wrapper(self, **kwargs) -> None:
        """设置SSL封装的参数。
        
        参数:
            **kwargs: 封装参数的键值对。
        """
        self.__wrap_kwargs = kwargs
    
    def createSSL( self, __cf: str, __kf: str, *, checkhost: bool = False, **context_kwargs) -> None:
        """创建并配置SSL上下文。
        
        参数:
            __cf: 证书文件路径。
            __kf: 私钥文件路径。
            checkhost: 是否检查主机名。
            **context_kwargs: 其他SSL上下文配置选项。
        """
        if not context_kwargs:
            context_kwargs = { "purpose": ssl.Purpose.CLIENT_AUTH }
        self.context = ssl.create_default_context( **context_kwargs )
        self.context.load_cert_chain( certfile = __cf, keyfile = __kf )
        self.context.check_hostname = checkhost
        self.ssl = True
    
    def bind(self, __addr: Optional[str] = None, __port: Optional[int] = None) -> None:
        """绑定套接字到指定的地址和端口。
        
        参数:
            __addr: 绑定的地址。
            __port: 绑定的端口。
        """
        address = __addr if __addr is not None else self.address
        port    = __port if __port is not None else self.port
        self.socket.bind( (address, port) )
        self.__binded = True
    
    def listen( self, __backlog: int ) -> None:
        """开始监听入站连接。
        
        参数:
            __backlog: 连接队列的大小。
        """
        if not self.__binded:
            self.bind()
        self.socket.listen( __backlog )
    
    def accept(self, __name: Optional[str] = None, *, timeout: Optional[float] = None) -> Tuple[SSClientInterface, str, str]:
        """接受一个连接，并返回一个SSClient实例及其地址和分配的名称。
        
        参数:
            __name: 客户端的名称（如果没有提供，则自动生成）。
            timeout: 接受连接的超时时间。
            
        返回:
            一个包含SSClient实例、地址和名称的元组。
        """
        self.socket.settimeout( timeout )
        
        try:                    client, addr = self.socket.accept()
        except socket.timeout:  client, addr = None, None
        
        if __name is None: __name = "client-" + str(len(self.clients))
        
        self.socket.settimeout( None )
        client = SSClientInterface(
            client, addr, self,
            self.ssl, self.context, **self.__wrap_kwargs
        )
        self.clients.append( client )
        return client, addr, __name

    def accept_for(self, __c: int, *, timeout: Optional[float] = None) -> List[SSClientInterface]:
        """接受指定数量的连接。
        
        参数:
            __c: 要接受的连接数。
            timeout: 接受每个连接的超时时间。
            
        返回:
            接受的SSClient实例列表。
        """
        accepted_clients = []
        while len(accepted_clients) < __c: 
            accepted_clients.append(self.accept( timeout = timeout )[0])
        return accepted_clients

    def recv_from(self, __c: SSClientInterface, __size: Optional[int] = None, __flag: int = 0) -> Optional[ConverterInterface]:
        """从指定的客户端接收数据。
        
        参数:
            __c: 从中接收数据的客户端。
            __size: 要接收的数据大小。
            __flag: 接收操作的标志。
            
        返回:
            接收到的数据，封装在Converter对象中。
        """
        if __c not in self.clients:
            raise ValueError( f"Client not found: {__c}" )
        recv: Callable = __c.socket.recv if self.proto == "TCP" else __c.socket.recvfrom
        if __size is None:
            try:
                if __c in self.__bsize_buffer.keys( ):
                    raise struct.error( )
                raw_bsize = recv( struct.calcsize(self.bsize_fmt), __flag )
                bsize = struct.unpack( self.bsize_fmt, raw_bsize )[0]
            except BlockingIOError:         return None
            except ssl.SSLWantReadError:    return None
            except struct.error:
                bsize = self.__bsize_buffer.pop( __c )
                if not bsize: return None
            except Exception as e:          raise e
            
            try:
                return ConverterInterface( recv( bsize, __flag ) )
            except BlockingIOError:         return self.__savebs__( __c, bsize )
            except ssl.SSLWantReadError:    return self.__savebs__( __c, bsize )
            except Exception as e:          raise e
        else:
            try:
                return ConverterInterface( recv( __size, __flag ) )
            except BlockingIOError:         return None
            except ssl.SSLWantReadError:    return None
            except Exception as e:          raise e

    def recv(self, __count: int, __size: Optional[int] = None, __flag: int = 0, *, once: bool = False, without: Optional[List[SSClientInterface]] = None) -> Optional[ConverterInterface]:
        """接收所有client的数据
        
        参数:
            __size: 要接收的数据大小。
            __flag: 接收操作的标志。
            once: 是否只接收一次。
            
        返回:
            接收到的数据，封装在Converter对象中。
        """
        all_data: List[ConverterInterface] = []
        self.set_blocking( False )
        clients = self.clients.copy( )
        
        for wc in without or []:
            clients.remove( wc )
        
        while len( all_data ) < __count:
            for client in clients:
                data = self.recv_from( client, __size, __flag )
                if data is not None:
                    all_data.append( data )
                    if once: clients.remove( client )
        
        self.set_blocking( True )
        return all_data
    
    def send_to(self, __c: SSClientInterface, __d: Any, __flag: int = 0, *, convert: bool = True) -> None:
        if __c not in self.clients:
            raise ValueError( f"Client not found: {__c}" )
        if convert: __d = ConverterInterface.encode( __d )
        
        bsize = struct.pack( self.bsize_fmt, len(__d) )
        try:
            __c.socket.send( bsize, __flag )
            __c.socket.send( __d, __flag )
        except Exception as e: raise e
        return
        
    def send( self, __d: Any, __flag: int = 0, *, convert: bool = True, without: Optional[List[SSClientInterface]] = None ) -> None:
        clients = self.clients.copy( )
        for wc in without or []:
            clients.remove( wc )
        for client in clients:
            self.send_to( client, __d, __flag, convert = convert )
        return
    
    def set_blocking(self, __status: bool) -> None:
        for client in self.clients:
            client.blocking = __status
    
    def close(self) -> None:
        for client in self.clients:
            try:                client.disconnect( )
            except Exception:   continue
        try:                   self.socket.shutdown( )
        except Exception:      pass
        finally:               self.socket.close( )
    
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
        
