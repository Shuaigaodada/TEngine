__all__ = ["Player", "AI"]
import env
import const
import typing as T
from roles import *
from cardPile import *
from main import resource

class Player:
    def __init__(self, globalCardPile: CardPile) -> None:
        self.level          : int               = 2
        self.exp            : int               = 0
        self.coin           : int               = 0
        self.cards          : T.List[Role]      = list()
        self.items          : T.List[str]       = list()
        
        self.health         : int               = 100
        self.maxHealth      : int               = 100
        
        self.levelUpCost    : int               = 4
        self.refreshCost    : int               = 2
        
        self.levelUpExp     : int               = 4
        self.roundExp       : int               = 2
        
        self.hextech        : T.List[str]       = list()
        
        self.maxInterest    : int               = 5
        self.WLCounts       : int               = 0 # 负数表示连败次数, 正数表示连胜次数
        self.WLInterest     : T.Dict[int, int]  = { 3 : 1, 4 : 1, 5 : 2, 6 : 3 }
        
        self.cardPile       : T.Dict[int, Role] = { 1: None, 2: None, 3: None, 4: None, 5: None }
        self.globalCardPile : CardPile          = globalCardPile
        self.levelExp       : T.Dict[str, int]  = resource.load( const.file_levelexp ).asJson()
        
        # int level exp keys
        self.levelExp = { int(k): v for k, v in self.levelExp.items() }
        
        self.__offset_list: T.List[ int ] = [ ]
        
    def get_drawpos( self ) -> T.List[ int ]:
        if self.__offset_list:
            return self.__offset_list
        
        offset = len( const.currentPlayerPile ) + 4 # 4 space
        space = 2
        for card in self.cardPile.values( ):            
            self.__offset_list.append( offset )
            offset += card.name_lenght + space
        return self.__offset_list
        
    def sellCard(self, index: int) -> None:
        """出售卡牌"""
        sell_card = self.cards.pop( index )
        
        price, count = sell_card.sell_price, sell_card.sell_count
        self.coin += price
        self.globalCardPile.push( *count )
        
        
        
    
    def buyCard(self, index: int, free: bool = False) -> None:
        """购买卡牌"""
        if self.cardPile[ index ] is None:
            return
        
        card_cost = self.cardPile[ index ].cost if not free else 0
        
        if self.coin >= card_cost:
            self.coin -= card_cost
            self.cards.append( self.cardPile[ index ] )
            self.cardPile[ index ] = None
    
    def upgrade( self, free: bool = False, __checkgrade: bool = False ) -> bool:
        """升级角色"""
        # max level
        if self.levelExp[ self.level ] == -1: return False
        
        if self.exp >= self.levelExp[ self.level ]:
            self.exp -= self.levelExp[ self.level ]
            self.level += 1
            self.upgrade( free, True )
            
        if __checkgrade: return
        
        if free or self.coin >= self.levelUpCost:
            self.coin -= self.levelUpCost
            self.exp += self.levelUpExp
        self.upgrade( free, True )
        
    def refreshPile( self, free: bool = False ) -> bool:
        """刷新卡池"""
        if free or self.coin >= self.refreshCost:
            self.coin -= self.refreshCost if not free else 0
            
            self.globalCardPile.push( *[ role for role in self.cardPile.values( ) if role is not None ] )
            
            for idx, card in enumerate( self.globalCardPile.draw( self.level ) ):
                self.cardPile[ idx + 1 ] = card
            
            self.__offset_list.clear( )
            self.get_drawpos( )
            return True
        
        self.__offset_list.clear( )
        self.get_drawpos( )
        return False
    
    def synthesisCard( self ) -> None:
        """ 合成卡牌 """
        counter = self.cardCount( )
        
        for card in self.cards:
            count = counter[ card.name ][ card.level ]
            if count == 3 and card.level <= 3:
                for _ in range( 3 ):
                    self.cards.remove( card )
                new_card = type( card )( )
                new_card.level = card.level + 1
                self.cards.append( new_card )
                self.synthesisCard( )
                break
        return 
                
    
    @property
    def interest( self ) -> int:
        clamp = lambda num, min_value, max_value: max(min(num, max_value), min_value)
        inrst = clamp( self.coin // 10, 0, self.maxInterest )
        
        for key, val in dict( reversed( list( self.WLInterest.items() ) ) ).items( ):
            if abs( self.WLCounts ) >= key:
                inrst += val
                break
        
        return inrst
    
    def sortCard( self ) -> None:
        """排序卡牌"""
        sortKey = lambda card: ( -card.cost, card.name, -card.level )
        self.cards.sort( key = sortKey )
    
    def cardCount( self ) -> T.Dict[ str, T.Dict[ int, int ] ]:
        """获取卡牌数量"""
        counter: T.Dict[ str, T.Dict[ int, int ] ] = {}
        for card in self.cards:
            counter[ card.name ] = counter.get( card.name, { card.level: 0 } )
            counter[ card.name ][ card.level ] = counter[ card.name ].get( card.level, 0 ) + 1
        return counter
    
    def checkCard( self, other: Role | str ) -> bool:
        """ 检查卡牌是是否在玩家手牌中 """
        if isinstance( other, Role ):
            for card in self.cards:
                if card.name == other.name and card.level < 3:
                    return True
            return False
        else:
            for card in self.cards:
                if card.name == other and card.level < 3:
                    return True
            return False
    
    
    
    
class AI(Player):
    pass
    