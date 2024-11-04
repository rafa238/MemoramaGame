import random
from enum import Enum, auto


class Difficulty(Enum):
    EASY = auto()
    HARD = auto()


class Board:

    def __init__(self, difficulty: Difficulty = Difficulty.EASY):
        self.words = ["Perro", "Arbol"]
        self.side = 2
        self.board = self._create_board()
        self.discovered_cells = [[0, 0], [0, 0]]
        if difficulty == Difficulty.HARD:
            self.words_advanced = ["Perro", "Arbol", "Libro", "Lapiz", "Microfono", "Celular", "Agua", "Tortuga"]
            self.side_advance = 4
            self.board_words = self._create_board()

    def discover_cell(self, x: int,  y: int) -> str:
        try:
            x, y = (int(x), int(y))
        except Exception as e:
            print("Error coordenadas no validas")
        if x < 1 or x > self.side or y < 1 or y > self.side:
            print("Posicion invalida para descubrir")
            return ""
        self.discovered_cells[x-1][y-1] = 1
        return self.board[x-1][y-1]

    def check_finalized_status(self) -> bool:
        finalized = True
        for row in self.discovered_cells:
            for elem in row:
                if elem == 0:
                    finalized = False
        return finalized

    def get_board(self):
        return self.board

    def _create_board(self) -> list[list[str]]:
        matrix = []
        words_duplicated = self.words * 2
        random.shuffle(words_duplicated)
        for i in range(self.side):
            matrix_row = []
            for j in range(self.side):
                matrix_row.append(words_duplicated[j + i * self.side])
            matrix.append(matrix_row)
        return matrix
