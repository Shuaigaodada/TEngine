import typing as T
import unicodedata as ucd

class ClickBox:
    def __init__(self, startX: int, startY: int, endX: int | str, endY: int = None, offset: bool = False) -> None:
        self.box = None
        if isinstance(endX, str):
            length = sum(2 if ucd.east_asian_width(c) in 'FW' else 1 for c in endX)
            self.box = (startX, startY, startX + length, startY)
        else:
            self.box = (startX, startY, endX, endY)
        
        self.offset = offset
        
        self.clickBox: T.List[T.Tuple[int, int]] = []
        if offset:
            for y in range(self.box[1], self.box[3]):
                for x in range(self.box[0], self.box[2]):
                    self.clickBox.append((x, y))
            
