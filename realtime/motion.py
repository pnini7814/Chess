from dataclasses import dataclass
from models.piece import Piece
from models.position import Position

CELL_SIZE = 100
PIECE_SPEED = 100


@dataclass
class Motion:
    piece: Piece
    from_pos: Position
    to_pos: Position
    start_time: int
    arrival_time: int
    is_jump: bool = False

    @staticmethod
    def compute_duration(from_pos: Position, to_pos: Position) -> int:
        steps = max(abs(to_pos.row - from_pos.row), abs(to_pos.col - from_pos.col))
        return steps * 1000

    @staticmethod
    def create(piece: Piece, from_pos: Position, to_pos: Position, start_time: int) -> "Motion":
        duration = Motion.compute_duration(from_pos, to_pos)
        return Motion(
            piece=piece,
            from_pos=from_pos,
            to_pos=to_pos,
            start_time=start_time,
            arrival_time=start_time + duration,
        )
