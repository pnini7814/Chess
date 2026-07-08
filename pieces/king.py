from pieces.piece import Piece


class King(Piece):

    @property
    def piece_type(self) -> str:
        return "K"

    @property
    def move_duration_ms(self) -> int:
        return 500

    def is_legal_shape(self, from_row, from_col, to_row, to_col, board) -> bool:
        return abs(to_row - from_row) <= 1 and abs(to_col - from_col) <= 1
