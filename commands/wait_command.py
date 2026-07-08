from commands.command import Command
from game.game_state import GameState


class WaitCommand(Command):

    def __init__(self, parts: list[str], move_scheduler):
        self._ms = int(parts[1])
        self._scheduler = move_scheduler

    def execute(self, state: GameState) -> None:
        state.current_time += self._ms
        state.pending_moves, state.game_over = self._scheduler.resolve(
            state.current_time, state.pending_moves, state.board, state.game_over
        )
