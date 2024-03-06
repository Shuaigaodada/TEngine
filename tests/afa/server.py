import os
import env
from typing import *
from player import *
from cardPile import *
from socket import socket
from TEngine import Resource
from TEngine.server import SocketServer

__base__ = \
os.path.join(
    os.path.dirname(
        os.path.abspath(
            __file__
        )    
    ),
    "src"
)

address = "localhost"
port = 9999
resource = Resource( __base__ )


def find_player( client: socket, players: List[ Player ] ) -> Player:
    for player in players:
        if player.client == client:
            return player
    raise ValueError( "undefine player" )

def main( *args, **kwargs ):
    server = SocketServer( address, port )
    
    server.listen( )
    clients = \
    server.accept_for( 2 ) # test for 2 clients
    
    # init game
    cardpile = CardPile( )
    players: List[ Player ] = [
        Player( c, cardpile ) for c in clients
    ]
    
    for data in server.recv( len( players ) ):
        if not data.as_boolen( ):
            raise Exception( "client not ready" )
    
    # start game
    for player in players:
        player.refreshPile( True )
    
    while players:
        poster = server.recv( 1 )[ 0 ]
        post = poster.as_json( )
        """
        post数据:
        {
            "refresh"   : bool,
            "upgrade"   : bool,
            "sort_card" : bool,
            "exit"      : bool,
            "buy"       : int,
            "sell"      : int
        }
        """
        if post is None or post.get( "exit", False ):
            players.remove( poster.client )
            continue
        
        player = find_player( poster.client, players )
        if post.get( "refresh", False ):
            player.refreshPile( )
        if post.get( "upgrade", False ):
            player.upgrade( )
        if post.get( "sort_card", False ):
            player.sortCard( )
        if post.get( "buy", -1 ) != -1:
            player.buyCard( post[ "buy" ] )
        if post.get( "sell", -1 ) != -1:
            player.sellCard( post[ "sell" ] )
        
        
        server.send_to( player.client, player.as_json( ) )
        
        
    
    
    
    
    server.close( )
    

if __name__ == "__main__":
    main( )
    
