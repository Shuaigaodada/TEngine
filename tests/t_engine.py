import env
from TEngine import TEngine

class MainTester( TEngine ):
    def __init__(self) -> None:
        super().__init__()
        self._init()
    
    def main( self ) -> None:
        string = self.input.getline( "输入你的手机号: " )
        self.screen.write( "\n" )
        # string = string[:3] + "-" + string[3:6] + "-" + string[6:]
        self.screen.write( "你的手机号是: " + string )
        self.input.getch( )

    def phone_number_checker( self, key: str, all_key: list[ str ] ) -> bool:
        try:
            num = int( key )
        except ValueError:
            return False
        
        return len( all_key ) <= 9


MainTester( ).main( )
