from pieces.piece import Piece


class Knight(Piece):

    @property
    def piece_type(self) -> str:
        return "N"

    @property
    def move_duration_ms(self) -> int:
        return 1500

    def is_legal_shape(self, from_row, from_col, to_row, to_col, board) -> bool:
        delta_row = abs(to_row - from_row)
        delta_col = abs(to_col - from_col)
        return (delta_row == 2 and delta_col == 1) or (delta_row == 1 and delta_col == 2)
