from enum import Enum, auto


class GameEvent(Enum):
    NEW_PLAYER = auto()
    DISCONNECTED_PLAYER = auto()
    MSG_RECEIVED_PLAYER = auto()
    FLIP_BOARD_POS = auto()