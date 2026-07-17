from dataclasses import dataclass
from models.piece import Piece
from models.position import Position
from typing import Tuple

CELL_SIZE = 75
PIECE_SPEED = 100
TIME_STEP=1000


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
        # מספר צעדים (מקסימום של שורות/עמודות)
        steps = max(abs(to_pos.row - from_pos.row), abs(to_pos.col - from_pos.col))
        # הנחת ברירת מחדל: 1000ms לכל צעד (שמרנו התנהגות נוכחית)
        return steps * TIME_STEP

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

    def duration_ms(self) -> int:
        return max(1, self.arrival_time - self.start_time)

    def progress(self, current_time: int) -> float:
        """Return progress in [0.0, 1.0]."""
        if current_time <= self.start_time:
            return 0.0
        if current_time >= self.arrival_time:
            return 1.0
        return (current_time - self.start_time) / self.duration_ms()

    def jump_height_offset(self, current_time: int, cell_size: int = CELL_SIZE) -> int:
        """Vertical lift during in-place jump: peaks at half a cell at progress 0.5."""
        if not self.is_jump:
            return 0
        p = self.progress(current_time)
        half_cell = cell_size / 2
        return -int(round(half_cell * 4 * p * (1 - p)))

    def pixel_position(self, current_time: int, cell_size: int = CELL_SIZE) -> Tuple[int, int]:
        """
        Linear interpolate between from_pos and to_pos and return pixel coordinates (x, y).
        x = col * cell_size, y = row * cell_size.
        Jump motions add a vertical arc (up half a cell and back down).
        """
        p = self.progress(current_time)
        start_x = self.from_pos.col * cell_size
        start_y = self.from_pos.row * cell_size
        end_x = self.to_pos.col * cell_size
        end_y = self.to_pos.row * cell_size

        cur_x = int(round(start_x + (end_x - start_x) * p))
        cur_y = int(round(start_y + (end_y - start_y) * p))
        cur_y += self.jump_height_offset(current_time, cell_size)
        return cur_x, cur_y