import env
from TEngine import TEngine
from TEngine import DebugLogger
from TEngine.Characters import Characters
from TEngine.Engine.Component import Text


class Test(TEngine):
    def __init__(self) -> None:
        super().__init__()
        return
    
    def main(self) -> None:
        self.init( True )
        
        logger = DebugLogger( "logs/test.log" )
        self.setLogger(logger)
        
        self.input.mouse.init()
        
        self.renderer.create("green", "#00FF00", "#000000")
        
        self.screen.clear()
        self.screen.write("Hello World", color="green").set_clickBox( "test" )
        self.screen.write("Other Text")
        
        self.screen.update()
        while True:
            key = self.input.get()
            if key == self.input.MOUSE_KEY:
                mouseEvent = self.input.mouse.get()
                if "test" in mouseEvent.clicked or "test" in mouseEvent.pressed:
                    self.logger.info("Click test")
                    self.logger.update()
            if key == self.input.Q:
                break
        return
    
Test().main()
