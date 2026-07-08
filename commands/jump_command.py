from commands.command import Command
from game.game_state import GameState


class JumpCommand(Command):

    def __init__(self, parts: list[str]):
        self._row, self._col = self.parse_coords(parts)

    def execute(self, state: GameState) -> None:
        if not state.is_within_bounds(self._row, self._col):
            return

        cell = state.board[self._row][self._col]
        if cell == ".":
            return

        if state.is_piece_moving(self._row, self._col, include_jumps=False):
            return

        state.pending_moves.append({
            "piece": cell,
            "from_row": self._row, "from_col": self._col,
            "to_row": self._row, "to_col": self._col,
            "arrival_time": state.current_time + 1000,
            "is_jump": True,
        })
