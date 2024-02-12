import env
import unicurses as curses
from TEngine import TEngine
from TEngine import DebugLogger
from TEngine.Characters import Characters


class Test(TEngine):
    def __init__(self) -> None:
        super().__init__()
        return
    
    def main(self) -> None:
        self.Init( True )
        
        logger = DebugLogger()
        self.SetLogger(logger)
        
        self.input.mouse.Init()
        self.input.mouse.SetClickBox("test", 0, 0, "Hello World")
        
        self.screen.Clear()
        
        x = 0
        y = 0
        width = 10
        height = 10
        self.renderer.Create("green", "#00FF00", "#000000")

        for char in Characters.__dict__.values():
            if isinstance(char, str) and len(char) == 1:
                self.screen.Write(char, x, y)
                if x >= 50:
                    x = 0
                    y += 1
                x += 2
        
        self.screen.Update()
        while True:
            key = self.input.KeyDown()
            if key == self.input.MOUSE_KEY:
                mouseEvent = self.input.mouse.GetMouse()
                if "test" in mouseEvent.clicked or "test" in mouseEvent.pressed:
                    self.logger.Info("Click test")
                    self.logger.Update()
                else:
                    if not mouseEvent.released:
                        break
        return
    
Test().main()
