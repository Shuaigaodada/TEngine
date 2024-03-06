__all__ = ["Game"]
import env
import const
import typing as T
from tests.afa.player import *
from TEngine import *
from tests.afa.cardPile import *
from TEngine.Engine import component



class Game( TEngine ):
    def __init__( self ) -> None:
        super( ).__init__( )
        
        self.round          : str                 = "1-1"
        
        self.client         : Player              = None
        self.players        : T.List[Player | AI] = list( )
        self.globalCardPile : CardPile            = CardPile( )
        
        
        self.init                                   ( )
        
    def init( self ) -> None:
        self._init                          (  )
        self.logger                         = DebugLogger( "logs/game.log" )
        self.setLogger                      ( self.logger )
        self.input.mouse.init               ( ) # 启用鼠标支持
        self.logger.auto_update             = True
        
        self.client                         = Player( self.globalCardPile )
        
        
        
        self.players.append( self.client )
        
        self.buyCardKeys                    = [ '1', '2', '3', '4', '5' ]

        self.uiString                         =  lambda : [
            const.refreshCard, const.upgradeCard,
            "当前经验: "    + str( self.client.exp if self.client.levelExp[ self.client.level ] != -1 else "max" ) \
                + "/" + str( self.client.levelExp[ self.client.level ] if self.client.levelExp[ self.client.level ] != -1 else "max" )  + \
            ", 当前等级: "  + str( self.client.level ),
            "当前金币: "    + str( self.client.coin ),
            "战力: 0",
            "当前血量: 0"
        ]
        self.createColor                    ( )
        
    def createColor( self ) -> None:
        """ 初始化着色器 """
        
        # card color
        self.renderer.create( "cost-1", "#FFFFFF" )
        self.renderer.create( "cost-2", "#00FF00" )
        self.renderer.create( "cost-3", "#0000FF" )
        self.renderer.create( "cost-4", "#FF00FF" )
        self.renderer.create( "cost-5", "#FFFF00" )
        
        # star color
        self.renderer.create( "star-1", "#5E331F" )
        self.renderer.create( "star-2", "#96A8AB" )
        self.renderer.create( "star-3", "#E2C258" )
    
    def start( self ) -> None:
        self.logger.clear( )
        
        for player in self.players:
            player.refreshPile( True )
            
        running: bool = True
        
        while running:
            self.screen.clear( False )
            self.draw( )
            
            key = self.input.getch( )
            
            if key == self.input.Q:
                running = False
                break
            
            elif chr( key ) in self.buyCardKeys:
                self.client.buyCard( int( chr( key ) ) )
            elif key == self.input.D:
                if self.client.refreshPile( ):
                    self.logger.info( "Refresh card pile" )
            elif key == self.input.F:
                if self.client.upgrade( ):
                    self.logger.info( "buy exp" )
            
            elif key == self.input.MOUSE_KEY:
                mouse = self.input.mouse.get(  )
                for click_name in mouse.clicked + mouse.pressed:
                    if "role" in click_name.split( "-" ):
                        self.logger.info( f"click buy {click_name}" )
                        idx = int( click_name.split( "-" )[ 1 ] )
                        self.client.buyCard( idx )
                    
                    elif "player" in click_name.split( "-" ):
                        self.logger.info( f"click sell {click_name}" )
                        idx = int( click_name.split( "-" )[ 1 ] )
                        self.client.sellCard( idx )
                        
                    self.input.mouse.remove_clickbox( click_name )
            
            self.client.synthesisCard( )
            self.screen.update( )
            self.input.mouse.clear_clickbox( )
                        
        
    def draw( self ) -> None:
        self.screen.clear()

        self.screen.write( const.title )
        
        # draw ui
        for i, ui in enumerate( self.uiString( ) ):
            self.screen.write( ui, 0, self.height - 2 - i )
        
        for player in self.players:
            player.sortCard( )
        
        # draw client cardpile
        self.draw_clientCardPile( )
        
        # draw cardpile tips
        self.draw_clientTip( )
        
        # draw client cards
        self.draw_clientCards( )
        
        self.screen.update( )
        
    
    def draw_clientCardPile( self ) -> None:
        self.screen.write( const.currentPlayerPile, 0, self.height )

        drawpos = self.client.get_drawpos( )
        
        for idx, card in self.client.cardPile.items( ):
            if card is None:
                continue
            
            if self.client.checkCard( card ):
                self.renderer.start( "cost-" + str( card.cost ), self.renderer.STANDOUT )
            else:
                self.renderer.start( "cost-" + str( card.cost ) )
            
            text = \
            self.screen.write( card.name, drawpos[ idx - 1 ], self.height )
            x, y, w, h = text.click_box.unpack( )
            self.input.mouse.set_clickbox( "role-" + str( idx ), x, y, w, h )
            
            self.renderer.end( )
        
        
            
    def draw_clientCards( self ) -> None:
        self.screen.write( const.currentPlayerCards, 3, 0 )
        offset: int = len( const.currentPlayerCards ) + 6 # 6 space
        drawline: int = 3
        
        for idx, card in enumerate( self.client.cards ):
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
            
            self.input.mouse.set_clickbox( "player-" + str(idx), *(click_box1 + click_box2).unpack() )
            
            offset += card.name_lenght + 2
            
    def draw_clientTip( self ) -> None:
        counter     = self.client.cardCount( )
        cardpile    = list( self.client.cardPile.values( ) )
        drawpos     = self.client.get_drawpos( )
        
        pile_count: T.Dict[ str, int ] = { } # role_name: count
        
        # 将卡牌堆中的卡牌数量统计
        for card in cardpile:
            if card is not None:
                pile_count[ card.name ] = pile_count.get( card.name, 0 ) + 1
        
        for card_name, count in pile_count.items( ):
            if self.client.checkCard( card_name ):
                if counter[ card_name ].get( 1, 0 ) + count >= 3:
                    star_pos = [ ]
                    for idx, card in enumerate( cardpile ):
                        if card is None: continue
                        if card.name == card_name:
                            star_pos.append( idx )
                    
                    level: int
                    # 3 star
                    if counter[ card_name ].get( 2, 0 ) * 3 + counter[ card_name ].get( 1, 0 ) + count >= 9:
                        level: int = 3
                    # 2 star
                    else:
                        level: int = 2
                        
                    self.renderer.start( "star-" + str( level ) )
                    
                    for idx, pos in enumerate(star_pos):
                        position = drawpos[ pos ] + len( card_name ) - (level - 1)
                        self.screen.write( const.star * level, position, self.height - 1 )
                    
                    self.renderer.end( "star-" + str( level ) )