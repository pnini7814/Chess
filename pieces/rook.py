from pieces.piece import Piece


class Rook(Piece):

    @property
    def piece_type(self) -> str:
        return "R"

    @property
    def move_duration_ms(self) -> int:
        return 1000

    @property
    def blocks_path(self) -> bool:
        return True

    def is_legal_shape(self, from_row, from_col, to_row, to_col, board) -> bool:
        return from_row == to_row or from_col == to_col
