from commands.command import Command
from game.game_state import GameState


class PrintCommand(Command):

    def execute(self, state: GameState) -> None:
        for row in state.board:
            print(" ".join(row))
