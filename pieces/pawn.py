from pieces.piece import Piece


class Pawn(Piece):

    @property
    def piece_type(self) -> str:
        return "P"

    @property
    def move_duration_ms(self) -> int:
        return 250

    def is_legal_shape(self, from_row, from_col, to_row, to_col, board) -> bool:
        delta_col = abs(to_col - from_col)
        target_cell = board[to_row][to_col]

        if self._color == "w":
            row_diff = from_row - to_row
            start_row = len(board) - 1
            step = -1
        else:
            row_diff = to_row - from_row
            start_row = 0
            step = 1

        if delta_col == 0 and row_diff == 1:
            return target_cell == "."

        if delta_col == 0 and row_diff == 2 and from_row == start_row:
            middle_row = from_row + step
            return board[middle_row][from_col] == "." and target_cell == "."

        if delta_col == 1 and row_diff == 1:
            return target_cell != "."

        return False
