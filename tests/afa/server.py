import os
import env
import json
from typing import *
from player import *
from cardpile import *
from loguru import logger
from socket import socket
from TEngine.engine_component import Resource, SSClient, SocketServer

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


def find_player( client: SSClient, players: List[ Player ] ) -> Player:
    for player in players:
        if player.client == client:
            return player
    raise ValueError( "undefine player" )

def main( *args, **kwargs ):
    server = SocketServer( address, port )
    
    cert = resource.load( "ssl_cert/cert.pem" ).path
    key  = resource.load( "ssl_cert/key.pem" ) .path
    server.create_SSL( cert, key )
    
    logger.info( "start afa server" )
    server.listen( )
    
    logger.info( "waiting for clients" )
    server.accept_for( 1 ) # test for 1 clients
    
    logger.info( "init game" )
    # init game
    cardpile = CardPile( )
    players: List[ Player ] = [
        Player( c, cardpile ) for c in server.clients
    ]
    # TODO: delete below code when done test
    # -------start-----------
    for player in players:
        player.coin = 9999
    # --------end------------
    
    
    logger.info( "waiting for clients ready" )
    for data in server.recv( len( players ), client_once=True ):
        if not data.as_bool( ):
            raise Exception( "client not ready" )
    
    server.send( True )
    
    logger.info( "game started" )
    # start game
    for player in players:
        player.refreshPile( True )
    
    while players:
        poster = server.recv( 1 )[ 0 ]        
        post = poster.as_json( )
        logger.info( f"post: {post}" )
        """
        post数据:
        {
            "refresh"   : bool,
            "upgrade"   : bool,
            "exit"      : bool,
            "buy"       : int,
            "sell"      : int
        }
        """

                    
        player = find_player( poster.client, players )
        
        if post.get( "exit", False ):
            logger.info( f"{poster.client.peername} was disconnect and exit" )
            server.send_to( player.client, json.dumps(player.as_json( ), indent=4) )
            players.remove( poster.client )
            continue
        # api check
        if post.get( "refresh", False ):
            logger.info( f"{poster.client.peername} refresh card" )
            player.refreshPile( )
        if post.get( "upgrade", False ):
            logger.info( f"{poster.client.peername} upgrade" )
            player.upgrade( )
        if post.get( "buy", -1 ) != -1:
            logger.info( f"{poster.client.peername} buy card-{post.get( 'buy' )}" )
            player.buyCard( post[ "buy" ] )
            player.synthesisCard( )
            player.sortCard( )
        if post.get( "sell", -1 ) != -1:
            logger.info( f"{poster.client.peername} sell card-{post.get( 'sell' )}" )
            try:
                player.sellCard( post[ "sell" ] )
            except IndexError:
                logger.error( f"card-{post.get( 'sell' )} not found" )
            player.synthesisCard( )
            player.sortCard( )
        
        # logger.info( f"send back player information to {poster.client.peername}" )
        server.send_to( player.client, json.dumps(player.as_json( ), indent=4) )
        # logger.info( f"data: {json.dumps( player.as_json(), indent=4 )}" )
        
    logger.info( "server closing" )
    server.close( )
    logger.info( "server closed" )
    

if __name__ == "__main__":
    main( )
    
