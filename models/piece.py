from __future__ import annotations
from abc import ABC, abstractmethod
from uuid import uuid4
from enum import Enum
from models.position import Position


class PieceColor(Enum):
    WHITE = "white"
    BLACK = "black"


class PieceState(Enum):
    IDLE = "idle"
    MOVING = "moving"
    CAPTURED = "captured"


class Piece(ABC):

    def __init__(self, color: PieceColor, cell: Position, piece_id: str | None = None):
        self._id = piece_id if piece_id is not None else str(uuid4())
        self._color = color
        self._cell = cell
        self._state = PieceState.IDLE

    @property
    @abstractmethod
    def kind(self) -> str: ...

    @property
    def id(self) -> str:
        return self._id

    @property
    def color(self) -> PieceColor:
        return self._color

    @property
    def cell(self) -> Position:
        return self._cell

    @cell.setter
    def cell(self, position: Position) -> None:
        self._cell = position

    @property
    def state(self) -> PieceState:
        return self._state

    @state.setter
    def state(self, new_state: PieceState) -> None:
        self._state = new_state

    def __repr__(self) -> str:
        return f"Piece(id={self._id}, color={self._color.value}, kind={self.kind}, cell={self._cell}, state={self._state.value})"
