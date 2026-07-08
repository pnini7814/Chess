from abc import ABC, abstractmethod
from pieces.piece_factory import PieceFactory


class MoveValidator(ABC):

    @abstractmethod
    def is_valid(self, piece: str, from_row: int, from_col: int,
                 to_row: int, to_col: int, board: list[list[str]]) -> bool: ...


class StandardMoveValidator(MoveValidator):

    def is_valid(self, piece: str, from_row: int, from_col: int,
                 to_row: int, to_col: int, board: list[list[str]]) -> bool:
        if from_row == to_row and from_col == to_col:
            return False

        piece_obj = PieceFactory.from_token(piece)

        if not piece_obj.is_legal_shape(from_row, from_col, to_row, to_col, board):
            return False

        if piece_obj.blocks_path and not self._is_path_clear(from_row, from_col, to_row, to_col, board):
            return False

        return True

    def _is_path_clear(self, from_row: int, from_col: int,
                       to_row: int, to_col: int, board: list[list[str]]) -> bool:
        step_row = self._step(from_row, to_row)
        step_col = self._step(from_col, to_col)

        current_row = from_row + step_row
        current_col = from_col + step_col

        while current_row != to_row or current_col != to_col:
            if board[current_row][current_col] != ".":
                return False
            current_row += step_row
            current_col += step_col

        return True

    @staticmethod
    def _step(frm: int, to: int) -> int:
        if to > frm:
            return 1
        if to < frm:
            return -1
        return 0
