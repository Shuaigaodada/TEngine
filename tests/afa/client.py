import env
import const
import unicodedata
from typing import *
from TEngine import TEngine
from TEngine.client import SocketClient

host = "localhost"
port = 9999
READY = True

class Player:
    def __init__( self, post_data: Dict[ str, Any ] ) -> None:
        self.level          : int               = post_data.get( "level" )
        self.exp            : int               = post_data.get( "exp" )
        self.coin           : int               = post_data.get( "coin" )
        self.cards          : List[Role]        = post_data.get( "cards" )
        self.items          : List[str]         = post_data.get( "items" )
        
        self.health         : int               = post_data.get( "health" )
        self.maxHealth      : int               = post_data.get( "maxHealth" )
        
        self.levelUpCost    : int               = post_data.get( "levelUpCost" )
        self.refreshCost    : int               = post_data.get( "refreshCost" )
        
        self.levelUpExp     : int               = post_data.get( "levelUpExp" )
        self.roundExp       : int               = post_data.get( "roundExp" )
        
        self.hextech        : List[str]         = post_data.get( "hextech" )
        
        self.maxInterest    : int               = post_data.get( "maxInterest" )
        self.WLCounts       : int               = post_data.get( "WLCounts" )
        self.WLInterest     : Dict[str, int]    = post_data.get( "WLInterest" )
        
        self.cardPile       : Dict[str, Role]   = post_data.get( "cardPile" )
        self.levelExp       : Dict[str, int]    = post_data.get( "levelExp" )
        
        self.draw_pos       : List[ int ]       = post_data.get( "draw_pos" )
        
        self._init( )
    
    def _init( self ) -> None:
        self.cards = [ Role( card ) for card in self.cards ]
        self.cardPile = { int( idx ): Role( card ) for idx, card in self.cardPile.items( ) }
    
    def check_card( self, other: "Role" ) -> bool:
        for card in self.cards:
            if card.name == other.name and card.level < 3:
                return True
        return False

class Role:
    def __init__( self, role_dict: Dict[ str, Union[str, int, bool] ] ) -> None:
        self.name               : str               = role_dict.get( "name" )
        self.cost               : int               = role_dict.get( "cost" )
        self.level              : int               = role_dict.get( "level" )
        
        self.maxHealthPoint     : int               = role_dict.get( "maxHealthPoint" )
        self.healthPoint        : int               = role_dict.get( "healthPoint" )
        self.physicAttackPoint  : int               = role_dict.get( "physicAttackPoint" )
        self.magicAttackPoint   : int               = role_dict.get( "magicAttackPoint" )
        self.maxManaPoint       : int               = role_dict.get( "maxManaPoint" )
        self.manaPoint          : int               = role_dict.get( "manaPoint" )
        self.physicDefensePoint : int               = role_dict.get( "physicDefensePoint" )
        self.magicDefensePoint  : int               = role_dict.get( "magicDefensePoint" )
        self.speed              : int               = role_dict.get( "speed" )
        self.criticalRate       : int               = role_dict.get( "criticalRate" )
        self.criticalDamage     : int               = role_dict.get( "criticalDamage" )
        self.skillCanCritical   : int               = role_dict.get( "skillCanCritical" )
        
        self.score              : int               = role_dict.get( "score" )
    
    @property
    def name_lenght( self ) -> int:
        return sum (
            2 if unicodedata.east_asian_width( char ) in "FW" else 1 \
                for char in self.name
        )
    
class Game( TEngine ):
    def __init__( self, *args, **kwargs ):
        super( ).__init__( *args, **kwargs )
        self.client = SocketClient( host, port )
        self.client.connect( )
        self._init( )
        self.create_color( )
        self.player: Player = None

    def main( self ):
        self.client.send( READY )
        
        while True:
            # sort player's card and get player's information
            self.player = self.post( sort_card=True )
            self.draw( )
            
            
    def draw( self ) -> None:
        if self.player is None:
            raise ValueError( "player info is empty" )
        self.screen.clear( )
        
        self.screen.write( const.title )
        # draw ui
        for idx, UI in enumerate( self.create_ui( self.player ) ):
            self.screen.write( UI, 0, self.height - 2 - idx )
        self.draw_clientCardPile( )
        
    def draw_clientCardPile( self ) -> None:
        self.screen.write( const.currentPlayerPile, 0, self.height )
        draw_pos = self.player.draw_pos
        
        for idx, card in self.player.cardPile.items( ):
            if card is None:
                continue
                
            if self.player.check_card( card ):
                self.renderer.start( "cost-" + str( card.cost) , self.renderer.STANDOUT )
            else:
                self.renderer.start( "cost-" + str( card.cost) )
            
            self.screen.write( card.name, draw_pos[ idx ], self.height + 1 ) \
                .set_clickbox( "role" + str( idx ) )
            
            self.renderer.end( )
        return
    
    def draw_clientCards( self ) -> None:
        self.screen.write( const.currentPlayerCards, 3, 0 )
        offset = len( const.currentPlayerCards ) + 6
        drawline = 3
        
        for idx, card in enumerate( self.player.cards ):
            if offset + card.name_lenght >= self.width - 5:
                offset = len( const.currentPlayerCards ) + 6
                drawline += 2
            
            self.renderer.start( "cost-" + str( card.cost ) )
            
            click_box1 = \
            self.screen.write( card.name, offset, drawline ).click_box
            
            self.renderer.end( )
            
            # draw star
            star_pos = offset + card.name_lenght // 2
            star_pos = star_pos - 1 if card.level < 3 else star_pos - 2
            self.renderer.start( "star-" + str( card.level ) )
            click_box2 = \
            self.screen.write( const.star * card.level, star_pos, drawline - 1 ).click_box
            
            self.renderer.end( )
            self.input.mouse.set_clickbox( "player-" + str( idx ), *(click_box1 + click_box2).unpack( ) )
            offset += card.name_lenght + 2
        return

    def create_ui( self, player: Player ) -> List[ str ]:
        return [
            const.refreshCard, const.upgradeCard,
            "当前经验: "    + str( player.exp if player.levelExp[ str( player.level ) ] != -1 else "max" ) \
                + "/" + str( player.levelExp[ str( player.level ) ] if player.levelExp[ str( player.level ) ] != -1 else "max" )  + \
            ", 当前等级: "  + str( player.level ),
            "当前金币: "    + str( player.coin ),
            "战力: 0",
            "当前血量: 0"
        ]
    def create_color( self ) -> None:
        self.renderer.create( "cost-1", "#FFFFFF" )
        self.renderer.create( "cost-2", "#00FF00" )
        self.renderer.create( "cost-3", "#0000FF" )
        self.renderer.create( "cost-4", "#FF00FF" )
        self.renderer.create( "cost-5", "#FFFF00" )
        
        self.renderer.create( "star-1", "#5E331F" )
        self.renderer.create( "star-2", "#96A8AB" )
        self.renderer.create( "star-3", "#E2C258" )
        
    def post( self, 
            refresh     : bool      = False,
            upgrade     : bool      = False,
            sort_card   : bool      = False,
            exit        : bool      = False,
            buy         : int       = -1,
            sell        : int       = -1
        ) -> Player:
        
        post_data = {
            "refresh"   : refresh   ,
            "upgrade"   : upgrade   ,
            "sort_card" : sort_card ,
            "exit"      : exit      ,
            "buy"       : buy       ,
            "sell"      : sell
        }
        self.client.send( post_data )
        data = self.client.recv( ).as_json( )
        return Player( data )
        
         
