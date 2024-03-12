import json
import struct
import pickle
from typing import *

if __name__ == "__main__":
    # import ScoketClient for annotations
    from .server import SSClient

__all__ = ["Converter"]

class Converter:
    def __init__( self, __data: bytes, __c: Optional["SSClient"] = None ) -> None:
        self.client     = __c
        self.__data     = __data
    
    @property
    def size( self ) -> int:
        return len( self.__data )
    def __len__( self ) -> int:
        return self.size
    
    def as_json( self, coding: str = "utf-8", *args, **kwargs ) -> Dict[ str, Any ]:
        try:
            return json.loads( self.__data.decode( coding ), *args, **kwargs )
        except json.JSONDecoder:
            return {}
    def as_list( self, coding: str = "utf-8", *args, **kwargs ) -> List[ Any ]:
        return list( json.loads( self.__data.decode( coding ), *args, **kwargs ) )
    def as_tuple( self, coding: str = "utf-8", *args, **kwargs ) -> Tuple[ Any ]:
        return tuple( json.loads( self.__data.decode( coding ), *args, **kwargs ) )
    def as_bytes( self ) -> bytes:
        return self.__data
    def as_string( self, coding: str = "utf-8" ) -> str:
        return self.__data.decode( coding )
    def as_int( self, __format: Optional[str] = ">L" ) -> int:
        __format = ("L", "i")
        __bit = ("<", ">")
        
        for format, bit in zip( __format, __bit ):
            try:
                return struct.unpack( bit + format, self.__data )[0]
            except struct.error:
                continue
        
    def as_float( self, __format: str = ">f" ) -> float:
        __format = ("f", "d")
        __bit = ("<", ">")
        
        for format, bit in zip( __format, __bit ):
            try:
                return struct.unpack( bit + format, self.__data )[0]
            except struct.error:
                continue
        
    def as_bool( self, __format: str = ">?" ) -> bool:
        return struct.unpack( __format, self.__data )[0]
    
    def As( self, __t: Type, coding: str = "utf-8" ) -> Union[ int, float ]:
        if isinstance( __t, str ):
            return self.as_string( coding )
        elif isinstance( __t, int ):
            return self.as_int()
        elif isinstance( __t, float ):
            return self.as_float()
        elif isinstance( __t, bool ):
            return self.as_bool()
        elif isinstance( __t, bytes ):
            return self.as_bytes()
        elif isinstance( __t, dict ):
            return self.as_json( coding )
        elif isinstance( __t, list ):
            return self.as_list( coding )
        elif isinstance( __t, tuple ):
            return self.as_tuple( coding )
        elif isinstance( __t, pickle.Pickler ):
            return self.as_pickle( )
        else:
            return self.as_object( __t )
            
    
    def as_pickle( self, *args, **kwargs ) -> Any:
        return pickle.loads( self.__data, *args, **kwargs )
    
    def as_object( self, __obj: object, *args, **kwargs ) -> object:
        try:
            cls = __obj( *args, **kwargs )
        except TypeError as e:
            raise e
        
        data = self.as_json()
        for key, value in data.items():
            if hasattr( cls, key ): setattr( cls, key, value )
            # 抛弃无效数据
    
    def decode( self, coding: str = "utf-8" ) -> str:
        return self.__data.decode( coding )

