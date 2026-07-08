from abc import ABC, abstractmethod
from game.game_state import GameState


class Command(ABC):

    @abstractmethod
    def execute(self, state: GameState) -> None: ...

    @staticmethod
    def parse_coords(parts: list[str]) -> tuple[int, int]:
        x = int(parts[1])
        y = int(parts[2])
        return y // 100, x // 100  # row, col
