import os
import env
from TEngine import Resource

__basePath = os.path.dirname(os.path.abspath(__file__))
srcPath = os.path.join(__basePath, 'src')
resource = Resource( srcPath )


if __name__ == "__main__":
    from game import Game



    game = Game()
    # TODO: 作弊
    game.client.coin                    = 10000
    game.start()


