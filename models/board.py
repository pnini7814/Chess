from models.piece import Piece
from models.position import Position


class Board:

    def __init__(self, rows: int, cols: int):
        self._rows = rows
        self._cols = cols
        self._cells: dict[Position, Piece] = {}

    @property
    def rows(self) -> int:
        return self._rows

    @property
    def cols(self) -> int:
        return self._cols

    def is_within_bounds(self, position: Position) -> bool:
        return 0 <= position.row < self._rows and 0 <= position.col < self._cols

    def get_piece(self, position: Position) -> Piece | None:
        return self._cells.get(position)

    def add_piece(self, piece: Piece) -> None:
        if not self.is_within_bounds(piece.cell):
            raise ValueError(f"Position {piece.cell} is out of bounds")
        if piece.cell in self._cells:
            raise ValueError(f"Position {piece.cell} is already occupied")
        self._cells[piece.cell] = piece

    def remove_piece(self, position: Position) -> Piece:
        if position not in self._cells:
            raise ValueError(f"No piece at {position}")
        return self._cells.pop(position)

    def move_piece(self, from_pos: Position, to_pos: Position) -> None:
        if not self.is_within_bounds(to_pos):
            raise ValueError(f"Position {to_pos} is out of bounds")
        piece = self.remove_piece(from_pos)
        if to_pos in self._cells:
            raise ValueError(f"Position {to_pos} is already occupied")
        piece.cell = to_pos
        self._cells[to_pos] = piece

    def __repr__(self) -> str:
        return f"Board(rows={self._rows}, cols={self._cols}, pieces={len(self._cells)})"
