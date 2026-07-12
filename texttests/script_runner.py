from chess_io.board_parser import BoardParser
from chess_io.board_printer import BoardPrinter
from models.game_state import GameState
from engine.game_engine import GameEngine
from input.controller import Controller
from texttests.script_parser import (
    ScriptParser, ParsedScript,
    ClickCommand, WaitCommand, JumpCommand, PrintBoardCommand
)


class ScriptRunner:

    def __init__(self, engine: GameEngine, controller: Controller):
        self._engine = engine
        self._controller = controller
        self._parser = ScriptParser()
        self._board_parser = BoardParser()
        self._board_printer = BoardPrinter()

    def run(self, text: str) -> list[str]:
        script = self._parser.parse(text)

        board = self._board_parser.parse(["Board:"] + list(script.board_lines))
        if board is None:
            return ["ERROR: invalid board"]

        state = GameState(board=board)
        failures = []

        for command in script.commands:
            if isinstance(command, ClickCommand):
                self._controller.on_click(state, command.x, command.y)
            elif isinstance(command, JumpCommand):
                self._controller.on_jump(state, command.x, command.y)
            elif isinstance(command, WaitCommand):
                self._engine.wait(state, command.ms)
            elif isinstance(command, PrintBoardCommand):
                actual = self._capture_print(state)
                if actual != list(command.expected_lines):
                    failures.append(
                        f"FAIL\nexpected:\n" + "\n".join(command.expected_lines) +
                        f"\nactual:\n" + "\n".join(actual)
                    )

        return failures

    def _capture_print(self, state: GameState) -> list[str]:
        import io as _io
        import sys
        captured = _io.StringIO()
        sys.stdout = captured
        self._board_printer.print(state.board)
        sys.stdout = sys.__stdout__
        return [line for line in captured.getvalue().splitlines() if line]
