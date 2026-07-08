from pieces.piece import Piece


class Queen(Piece):

    @property
    def piece_type(self) -> str:
        return "Q"

    @property
    def move_duration_ms(self) -> int:
        return 1000

    @property
    def blocks_path(self) -> bool:
        return True

    def is_legal_shape(self, from_row, from_col, to_row, to_col, board) -> bool:
        delta_row = abs(to_row - from_row)
        delta_col = abs(to_col - from_col)
        return delta_row == 0 or delta_col == 0 or delta_row == delta_col
