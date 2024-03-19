import json
import pickle
import struct
from typing import *
from ..interfaces import SSClient as ISSClient
from ..interfaces import Converter as IConveter
__all__ = ["Converter"]

class Converter(IConveter):
    def __init__(self, __d: bytes, __c: Optional[ISSClient] = None) -> None:
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
        if type(__t) is str:        return self.as_string(coding)
        elif type(__t) is int:      return self.as_int()
        elif type(__t) is float:    return self.as_float()
        elif type(__t) is bool:     return self.as_bool()
        elif type(__t) is bytes:    return self.as_bytes()
        elif type(__t) is list:     return self.as_list(coding)
        elif type(__t) is tuple:    return self.as_tuple(coding)
        elif type(__t) is dict:     return self.as_json(coding)
        elif type(__t) is object:   return self.as_object(__t)
        else:                       return self.as_pickle()
    
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
        if type(data) == str:       return data.encode(coding)
        elif type(data) == bytes:   return data
        elif type(data) == int:     return struct.pack(">L", data)
        elif type(data) == float:   return struct.pack(">f", data)
        elif type(data) == bool:    return struct.pack(">?", data)
        elif type(data) in (list, tuple, dict): return json.dumps(data, **kwargs).encode(coding)
        
        if isinstance(data, object):return pickle.dumps(data)
        if data is None:            return b""
