import json
import pickle
import struct
from typing import *
from ..interfaces import SSClient as SSClientInterface
from ..interfaces import Converter as ConveterInterface
__all__ = ["Converter"]

class Converter(ConveterInterface):
    def __init__(self, __d: bytes, __c: Optional[SSClientInterface] = None) -> None:
        self.client = __c
        self.__data = __d
    
    @property
    def size(self) -> int:
        return len(self.__data)
    
    def __len__(self) -> int:
        return self.size
    
    def as_json(self, coding: str = "utf-8", *args, **kwargs) -> Dict[str, Any]:
        try:
            return json.loads(self.__data.decode(coding), *args, **kwargs)
        except json.JSONDecodeError:
            return {}
    
    def as_list(self, coding: str = "utf-8", *args, **kwargs) -> List[Any]:
        return list(json.loads(self.__data.decode(coding), *args, **kwargs))
    
    def as_tuple(self, coding: str = "utf-8", *args, **kwargs) -> Tuple[Any]:
        return tuple(json.loads(self.__data.decode(coding), *args, **kwargs))
    
    def as_bytes(self) -> bytes:
        return Converter.encode( self.__data )
    
    def as_string(self, coding: str = "utf-8") -> str:
        return self.__data.decode(coding)
    
    def as_int(self, __format: Optional[str] = ">L") -> int:
        __format = ("L", "i")
        __bit = ("<", ">")
        
        for format, bit in zip(__format, __bit):
            try:
                return struct.unpack(bit + format, self.__data)[0]
            except struct.error:
                continue
            
    def as_float(self, __format: str = ">f") -> float:
        __format = ("f", "d")
        __bit = ("<", ">")
        
        for format, bit in zip(__format, __bit):
            try:
                return struct.unpack(bit + format, self.__data)[0]
            except struct.error:
                continue
            
    def as_bool(self, __format: str = ">?") -> bool:
        return struct.unpack(__format, self.__data)[0]
    
    def As(self, __t: type, coding: str = "utf-8") -> Union[int, float]:
        if isinstance(__t, str):
            return self.as_string(coding)
        elif isinstance(__t, int):
            return self.as_int()
        elif isinstance(__t, float):
            return self.as_float()
        elif isinstance(__t, bool):
            return self.as_bool()
        elif isinstance(__t, bytes):
            return self.as_bytes()
        elif isinstance(__t, list):
            return self.as_list(coding)
        elif isinstance(__t, tuple):
            return self.as_tuple(coding)
        elif isinstance(__t, dict):
            return self.as_json(coding)
        elif isinstance(__t, object):
            return self.as_object(__t)
        else:
            return self.as_pickle()
    
    def as_pickle(self, *args, **kwargs) -> Any:
        return pickle.loads(self.__data, *args, **kwargs)
    
    def as_object(self, __obj: object, *args, **kwargs) -> object:
        try:
            return pickle.loads(self.__data, *args, **kwargs)
        except pickle.PickleError:
            return __obj
        
    def decode(self, coding: str = "utf-8") -> str:
        return self.__data.decode(coding)
    
    @staticmethod
    def encode(data: Any, coding: str = "utf-8", **kwargs) -> bytes:
        if isinstance(data, str):   return data.encode(coding)
        if isinstance(data, bytes):  return data
        if isinstance(data, int):    return struct.pack(">L", data)
        if isinstance(data, float):  return struct.pack(">f", data)
        if isinstance(data, bool):   return struct.pack(">?", data)
        if isinstance(data, list):   return json.dumps(data, **kwargs).encode(coding)
        if isinstance(data, tuple):  return json.dumps(data, **kwargs).encode(coding)
        if isinstance(data, dict):   return json.dumps(data, **kwargs).encode(coding)
        if isinstance(data, object): return pickle.dumps(data)
        if isinstance(data, None):   return b""
