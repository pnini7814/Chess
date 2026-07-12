from models.position import Position
from realtime.motion import CELL_SIZE


class BoardMapper:

    def __init__(self, rows: int, cols: int):
        self._rows = rows
        self._cols = cols

    def to_position(self, x: int, y: int) -> Position | None:
        row = y // CELL_SIZE
        col = x // CELL_SIZE
        if 0 <= row < self._rows and 0 <= col < self._cols:
            return Position(row, col)
        return None
