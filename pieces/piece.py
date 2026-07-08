from abc import ABC, abstractmethod


class Piece(ABC):

    def __init__(self, color: str):
        self._color = color

    @property
    def color(self) -> str:
        return self._color

    @property
    @abstractmethod
    def piece_type(self) -> str: ...

    @property
    @abstractmethod
    def move_duration_ms(self) -> int: ...

    @property
    def blocks_path(self) -> bool:
        return False

    @abstractmethod
    def is_legal_shape(self, from_row: int, from_col: int,
                       to_row: int, to_col: int, board: list[list[str]]) -> bool: ...

    def __str__(self) -> str:
        return self._color + self.piece_type
