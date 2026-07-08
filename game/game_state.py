from dataclasses import dataclass, field
from typing import Optional


@dataclass
class GameState:
    board: list[list[str]]
    pending_moves: list[dict] = field(default_factory=list)
    current_time: int = 0
    selected_row: Optional[int] = None
    selected_col: Optional[int] = None
    game_over: bool = False

    def select(self, row: int, col: int) -> None:
        self.selected_row = row
        self.selected_col = col

    def deselect(self) -> None:
        self.selected_row = None
        self.selected_col = None

    def has_selection(self) -> bool:
        return self.selected_row is not None

    def is_within_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < len(self.board) and 0 <= col < len(self.board[0])

    def is_piece_moving(self, row: int, col: int, include_jumps: bool = True) -> bool:
        return any(
            m["from_row"] == row and m["from_col"] == col
            and (include_jumps or not m.get("is_jump"))
            for m in self.pending_moves
        )
