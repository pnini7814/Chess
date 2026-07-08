from game.game_state import GameState
from commands.command_factory import CommandFactory
from commands.print_command import PrintCommand


class GameEngine:

    def __init__(self, command_factory: CommandFactory):
        self._command_factory = command_factory

    def run(self, lines: list[str], board: list[list[str]]) -> None:
        state = GameState(board=board)
        inside_commands = False

        for line in lines:
            if line.startswith("Commands:"):
                inside_commands = True
                continue
            if not inside_commands:
                continue

            command = self._command_factory.parse(line)
            if command is None:
                continue

            if state.game_over and not isinstance(command, PrintCommand):
                continue

            command.execute(state)
