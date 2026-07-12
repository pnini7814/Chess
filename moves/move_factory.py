from models.piece_factory import PieceFactory


class MoveFactory:

    def create(self, piece: str, from_row: int, from_col: int,
               to_row: int, to_col: int, current_time: int) -> dict:
        piece_obj = PieceFactory.from_token(piece)
        arrival_time = current_time + piece_obj.move_duration_ms

        return {
            "piece": piece,
            "from_row": from_row,
            "from_col": from_col,
            "to_row": to_row,
            "to_col": to_col,
            "arrival_time": arrival_time,
            "is_jump": False,
        }
