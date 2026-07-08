from pieces.piece import Piece


class Bishop(Piece):

    @property
    def piece_type(self) -> str:
        return "B"

    @property
    def move_duration_ms(self) -> int:
        return 1000

    @property
    def blocks_path(self) -> bool:
        return True

    def is_legal_shape(self, from_row, from_col, to_row, to_col, board) -> bool:
        return abs(to_row - from_row) == abs(to_col - from_col)
