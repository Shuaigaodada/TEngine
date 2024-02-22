import typing as T
import random
from roles import *
from TEngine import Resource

__all__ = ['CardPile']

from main import resource

class Stack:
    def __init__(self) -> None:
        self.__backStack:   T.List[Role]                = []
        
    @property
    def size(self) -> int:
        return len(self.__backStack)
    
    def push(self, role: Role) -> None:
        self.__backStack.append(role)
        return
    
    def pop(self) -> Role:
        return self.__backStack.pop()

class CardPile:
    def __init__(self) -> None:
        self.__pile:        T.List[T.List[Role]]        = []
        self.__prob:        T.Dict[str, T.List[int]]    = {}
        self.stack:       Stack                       = Stack()
        
        
        self.init()
        
    def init(self) -> None:
        self.__prob = resource.Load("roleProbs.json").AsJson()
        
        roles = resource.Load("rolesInfo.data").AsLines()
        
        counts = resource.Load("cardCounts.count").AsString()
        counts = list(map(int, counts.split(",")))
        
        self.__pile = [list() for _ in range(5)]

        for role in roles:
            role = role.strip("\n")
            if role == "": continue
            
            name, cost = role.split(",")
            cost = int(cost)
            self.__pile[cost - 1].append([Role.createOfName(name)] * counts[cost - 1])
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

    def draw(self, level: int) -> T.List[Role]:
        return [self.drawOnce(level) for _ in range(5)]
    
    def push(self) -> None:
        for _ in self.stack.size:
            role: Role = self.stack.pop()
            self.__pile[role.cost - 1].append(role)
        return
            
            