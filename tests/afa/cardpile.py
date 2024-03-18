import env
import const
import random
from roles import *
from typing import *
from TEngine.components import Resource


__all__ = ['CardPile']



class Stack:
    def __init__(self) -> None:
        self.__backStack:   List[Role]                = []
        
    @property
    def size(self) -> int:
        return len(self.__backStack)
    
    def push(self, *roles: Tuple[Role]) -> None:
        self.__backStack.extend(roles)
        return
    
    def pop(self) -> Role:
        return self.__backStack.pop()

class CardPile:
    def __init__(self) -> None:
        self.__pile:        List[List[Role]]        = []
        self.__prob:        Dict[str, List[int]]    = {}
        self.stack:         Stack                       = Stack()
        
        
        self.init()
        
    def init(self) -> None:
        resource = Resource()
        self.__prob             = resource.load( const.file_prob ).as_json   (  )
        roles                   = resource.load( const.file_role ).as_lines  (  )
        counts                  = resource.load( const.file_count ).as_string(  )
        
        
        counts = list(map(int, counts.split(",")))
        
        self.__pile = [list() for _ in range(5)]

        for role in roles:
            role = role.strip("\n")
            if role == "": continue
            
            name, cost = role.split(" ")
            cost = int(cost)
            self.__pile[cost - 1].extend([Role.createOfName(name)] * counts[cost - 1])
        return
    
    def drawOnce(self, level: int) -> Role:
        cost = None
        while cost is None or len(self.__pile[cost]) == 0:
            for index, prob in enumerate(self.__prob[str(level)][::-1]):
                if random.random() * 100 <= prob:
                    cost = (len(self.__pile) - 1) - index
                    break
        
        roleIndex: int = random.randint(0, len(self.__pile[cost]) - 1)
        role = self.__pile[cost][roleIndex]
        del self.__pile[cost][roleIndex]
        return role

    def draw(self, level: int) -> List[Role]:
        return [self.drawOnce(level) for _ in range(5)]
    
    def push(self, *roles: Tuple[Role]) -> None:
        self.stack.push(*roles)
        for _ in range( self.stack.size ):
            role: Role = self.stack.pop()
            self.__pile[role.cost - 1].append(role)
        return
            
            