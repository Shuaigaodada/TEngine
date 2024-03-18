class TestA:
    def __new__(cls):
        instance = super().__new__(cls)
        instance.__init()
        return instance
    def __init(self):
        self.a = 15

    def __init__(self) -> None:
        pass

class TestB(TestA):
    def run(self):
        print(self.a)

TestB().run()
