import env
import os
import json
import const
import unicodedata
from typing import *
from TEngine import Engine
from TEngine.components import Resource
from TEngine.components import SocketClient

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
        self.cardPile = { int( idx ): (Role( card ) if card is not None else None) for idx, card in self.cardPile.items( ) }
    
    def check_card( self, other: Union[str, "Role"] ) -> bool:
        for card in self.cards:
            if isinstance( other, Role ):
                if card.name == other.name and card.level < 3:
                    return True
            else:
                if card.name == other and card.level < 3:
                    return True
        return False

    def counter( self ) -> Dict[ str, Dict[ int, int ] ]:
        counter: Dict[ str, Dict[ int, int ] ] = { }
        for card in self.cards:
            counter[ card.name ] = counter.get( card.name, { card.level: 0 } )
            counter[ card.name ][ card.level ] = counter[ card.name ].get( card.level, 0 ) + 1
        return counter

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
    
class Game( Engine ):
    def __init__( self, *args, **kwargs ):
        self.client = SocketClient( host, port )
        self.resource = Resource(
            os.path.join(
                os.path.dirname(
                    os.path.abspath(
                        __file__
                    )
                ),
                "src"
            )
        )
        cert = self.resource.load( "ssl_cert/cert.pem" ).path
        self.client.createSSL( cert, wrap_kwargs={"server_hostname": host} )
        self.client.connect( )
        self.init_engine( )
        self.create_color( )
        self.player: Player = None
        self.buyCardKeys = [ str( idx ) for idx in range( 1, 6 ) ]

    def run( self ):
        self.client.send( READY )
        
        if not self.client.recv( ).as_bool( ):
            raise Exception( "server not ready" )
            
        self.input.mouse.init( )
        self.post( )
        while True:
            # sort player's card and get player's information
            self.draw( )
            
            key = self.input.getch( )
            
            if key == self.input.Q:
                self.post( exit=True )
                break
            
            elif chr( key ) in self.buyCardKeys:
                self.post( buy=int( chr( key ) ) )
                continue
            
            elif key == self.input.D:
                self.post( refresh=True )
                continue
            
            elif key == self.input.F:
                self.post( upgrade=True )
                continue
            
            elif key == self.input.MOUSE_KEY:
                mouse = self.input.mouse.get(  )
                for click_name in mouse.clicked + mouse.pressed:
                    if "role" in click_name.split( "-" ):
                        idx = int( click_name.split( "-" )[ 1 ] )
                        self.post( buy=idx )
                    
                    elif "player" in click_name.split( "-" ):
                        idx = int( click_name.split( "-" )[ 1 ] )
                        self.post( sell=idx )
                        self.input.mouse.clear_cb( )
                continue
            
            
        self.client.close( )
        self.quit( )
            
    def draw( self ) -> None:
        if self.player is None:
            raise ValueError( "player info is empty" )
        self.screen.clear( )
        self.screen.write( const.title )
        # draw ui
        for idx, UI in enumerate( self.create_ui( self.player ) ):
            self.screen.write( UI, 0, self.height - 2 - idx )

        self.draw_clientCardPile( )
        self.draw_cardTip( )
        self.draw_clientCards( )
        
        self.screen.update( )
        
    def draw_clientCardPile( self ) -> None:
        self.screen.write( const.currentPlayerPile, 0, self.height )
        draw_pos = self.player.draw_pos
        
        for idx, card in self.player.cardPile.items( ):
            if card is None:
                continue
                
            if self.player.check_card( card ):
                self.renderer.start( "cost-" + str( card.cost ) , self.renderer.STANDOUT )
            else:
                self.renderer.start( "cost-" + str( card.cost ) )
            
            self.screen.write( card.name, draw_pos[ idx - 1 ], self.height ) \
                .set_clickbox( "role-" + str( idx ) )
            
            self.renderer.stop( )
            
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
            
            self.renderer.stop( )
            
            # draw star
            star_pos = offset + card.name_lenght // 2
            star_pos = star_pos - 1 if card.level < 3 else star_pos - 2
            self.renderer.start( "star-" + str( card.level ) )
            click_box2 = \
            self.screen.write( const.star * card.level, star_pos, drawline - 1 ).click_box
            
            self.renderer.stop( )
            self.input.mouse.set_cb( "player-" + str( idx ), *(click_box1 + click_box2).unpack( ) )
            offset += card.name_lenght + 2
        return
    
    def draw_cardTip( self ) -> None:
        counter     = self.player.counter( )
        cardpile    = list( self.player.cardPile.values( ) )
        draw_pos    = self.player.draw_pos
        
        pile_count: Dict[ str, int ] = { } # role_name: count
        
        # 将卡牌对中的卡牌数量统计
        for card in cardpile:
            if card is not None:
                pile_count[ card.name ] = pile_count.get( card.name, 0 ) + 1
        
        for name, count in pile_count.items( ):
            if self.player.check_card( name ):
                if counter[ name ].get( 1, 0 ) + count >= 3:
                    star_pos = [ ]
                    for idx, card in enumerate( cardpile ):
                        if card is None: continue
                        if card.name == name:
                            star_pos.append( idx )
                    
                    level: int
                    # 3 star
                    if counter[ name ].get( 2, 0 ) * 3 + counter[ name ].get( 1, 0 ) + count >= 9:
                        level = 3
                    else:
                        level = 2
                    
                    self.renderer.start( "star-" + str( level ) )
                    
                    for idx, pos in enumerate( star_pos ):
                        position = draw_pos[ pos ] + len( name ) - ( level - 1 )
                        self.screen.write( const.star * level, position, self.height - 1 )
                    
                    self.renderer.stop( "star-" + str( level ) )
                        

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
            exit        : bool      = False,
            buy         : int       = -1,
            sell        : int       = -1
        ) -> Player:
        
        post_data = {
            "refresh"   : refresh   ,
            "upgrade"   : upgrade   ,
            "exit"      : exit      ,
            "buy"       : buy       ,
            "sell"      : sell
        }
        self.client.send( post_data )
        data = self.client.recv( ).as_json( )
        self.player = Player( data )
        
         
if __name__ == "__main__":
    Game( ).run( )
    