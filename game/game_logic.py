import socket
from typing import List, Callable

from game.board import Board
from game.event import GameEvent
from model.client import Client


class GameLogic:
    def __init__(self) -> None:
        self.players: List = []
        self.update_callbacks: List[Callable] = []
        self.socket_count = 0
        self.board = Board()

    def add_update_callback(self, callback: Callable) -> None:
        self.update_callbacks.append(callback)

    def process_action(self, event: GameEvent, conn: socket.socket, data=None) -> None:
        try:
            if event == GameEvent.NEW_PLAYER:
                client = Client(self.socket_count, "", "", conn)
                self.socket_count += 1
                msg = f"El jugador {client.name} se ha unido al juego :) "
                self.players.append(client)
                self.send_game_update(event, msg)
                print(msg)
            elif event == GameEvent.DISCONNECTED_PLAYER:
                client = Client(self.socket_count, "", "", conn)
                self.players = [player for player in self.players if player != conn]
                msg = f"El jugador {client.name} ha abandonado el juego :( "
                self.send_game_update(event, msg)
                print(msg)
            elif event == GameEvent.MSG_RECEIVED_PLAYER:
                data = data.decode("utf-8")
                action, _ = data.split()
                if action == "FLIP":
                    self.process_action(GameEvent.FLIP_BOARD_POS, conn, data)
                    return
                client = Client(self.socket_count, "", "", conn)
                msg = f"El jugador {client.name} dice {data}"
                self.send_game_update(event, msg)
                print(msg)
            elif event == GameEvent.FLIP_BOARD_POS:
                client = Client(self.socket_count, "", "", conn)
                _, coords = data.split()
                x, y = coords.split(',')
                if not self.board.check_finalized_status():
                    cell = self.board.discover_cell(x, y)
                    if cell:
                        print(f"Se volteo la carta {x},{y} con valor {cell}")
                        self.send_game_update(event, f"FLIP de la carta {x},{y} {cell}")
                    else:
                        self.send_game_update(event, "Lo siento, esa no era una celda valida")
                else:
                    self.send_game_update(event, "Juego finalizado")
        except Exception as e:
            print(f"Ha ocurrido un error al procesar una accion {e}")

    def send_game_update(self, event: GameEvent, update_msg: str):
        for callback in self.update_callbacks:
            callback(event, update_msg)
