from __future__ import annotations
from dataclasses import dataclass
from models.board import Board
from models.position import Position


@dataclass
class GameState:
    board: Board
    current_time: int = 0
    selected: Position | None = None
    game_over: bool = False

    def select(self, position: Position) -> None:
        self.selected = position

    def deselect(self) -> None:
        self.selected = None

    def has_selection(self) -> bool:
        return self.selected is not None
