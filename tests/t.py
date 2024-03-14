class TestP:
    __instance: "TestP" = None
    def __new__(cls) -> "TestP":
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance
    
    def __init__(self) -> None:
        self.x = 15
        
class TestC(TestP):
    def __init__(self) -> None:
        super().__init__()
        self.y = 20

f = TestC()
print(f.x, f.y)
    