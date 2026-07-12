from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from models.position import Position
from realtime.motion import CELL_SIZE


@dataclass(frozen=True)
class PieceSnapshot:
    kind: str
    color: str
    pixel_x: int
    pixel_y: int
    state: str


@dataclass(frozen=True)
class GameSnapshot:
    board_width: int
    board_height: int
    pieces: tuple[PieceSnapshot, ...]
    selected_cell: Position | None
    game_over: bool


class Renderer(ABC):

    @abstractmethod
    def render(self, snapshot: GameSnapshot) -> None: ...
