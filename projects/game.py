__all__ = ["Game"]
import typing as T
from player import *
from TEngine import *
from cardPile import *

class Game( TEngine ):
    def __init__( self ) -> None:
        self.round          : str                 = "1-1"
        
        self.client         : Player              = None
        self.players        : T.List[Player | AI] = list( )
        self.globalCardPile : CardPile            = CardPile( )
        
        self.init                                   ( )
        
    def init( self ) -> None:
        self.init                           ( True )
        self.logger = DebugLogger           ( "logs/game.log" )
        self.setLogger                      ( self.logger )
        self.input.mouse.init               ( )
        
        self.globalCardPile.init            ( )
        self.client                         = Player( self.globalCardPile )
        
        
        
