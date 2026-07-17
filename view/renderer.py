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
    motion_progress: float = 1.0
    is_jumping: bool = False
    legal_moves: tuple[Position, ...] = ()

@dataclass(frozen=True)
class MoveRecord:
    piece_kind: str
    piece_color: str
    from_col: int
    from_row: int
    to_col: int
    to_row: int
    time_ms: int


@dataclass(frozen=True)
class CooldownInfo:
    col: int
    row: int
    progress: float


@dataclass(frozen=True)
class GameSnapshot:
    board_width: int
    board_height: int
    pieces: tuple[PieceSnapshot, ...]
    selected_cell: Position | None
    game_over: bool
    current_time: int = 0
    legal_moves: tuple[Position, ...] = ()
    cooldowns: tuple[CooldownInfo, ...] = ()
    move_history: tuple[MoveRecord, ...] = ()



class Renderer(ABC):

    @abstractmethod
    def render(self, snapshot: GameSnapshot) -> None: ...
