from game.game_logic import GameLogic
from server.connection_pool import ConnectionPool

if __name__ == '__main__':
    game_logic = GameLogic()
    pool = ConnectionPool(game_logic, 10)
    pool.start_pool()
