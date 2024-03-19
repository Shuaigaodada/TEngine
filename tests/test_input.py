import env
from TEngine import Engine

class Test(Engine):
    def __init__(self) -> None:
        self.init_engine( )
    
    def run(self) -> None:
        while True:
            self.input.wait( 100, 1 )
            key = self.input.getch()
            if key == -1:
                continue
            if key == ord("q"):
                break
            self.screen.write( chr(key) )

Test().run()    
        
            
            
