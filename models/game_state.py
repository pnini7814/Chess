from __future__ import annotations
from dataclasses import dataclass, field
from models.board import Board
from models.position import Position


@dataclass
class GameState:
    board: Board
    pending_moves: list[dict] = field(default_factory=list)
    current_time: int = 0
    selected: Position | None = None
    game_over: bool = False

    def select(self, position: Position) -> None:
        self.selected = position

    def deselect(self) -> None:
        self.selected = None

    def has_selection(self) -> bool:
        return self.selected is not None

    def is_piece_moving(self, position: Position, include_jumps: bool = True) -> bool:
        return any(
            m["from_row"] == position.row and m["from_col"] == position.col
            and (include_jumps or not m.get("is_jump"))
            for m in self.pending_moves
        )
