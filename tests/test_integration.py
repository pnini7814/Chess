import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from io import StringIO
from board.board_parser import BoardParser
from moves.move_validator import StandardMoveValidator
from moves.move_factory import MoveFactory
from moves.move_scheduler import MoveScheduler
from commands.command_factory import CommandFactory
from game.game_engine import GameEngine


def run_game(input_text: str) -> str:
    lines = input_text.strip().splitlines()
    board = BoardParser().parse(lines)
    engine = GameEngine(CommandFactory(
        StandardMoveValidator(), MoveFactory(), MoveScheduler()
    ))
    captured = StringIO()
    sys.stdout = captured
    engine.run(lines, board)
    sys.stdout = sys.__stdout__
    return captured.getvalue()


class TestGameEngineIntegration(unittest.TestCase):

    def test_rook_moves_horizontally(self):
        output = run_game("""
Board:
wR . . .
. . . .
. . . .
. . . wK
Commands:
click 0 0
click 200 0
wait 1000
print board
""")
        lines = output.strip().splitlines()
        self.assertEqual(lines[0], ". . wR .")

    def test_pawn_promotion_white(self):
        output = run_game("""
Board:
. . . .
wP . . .
. . . .
. . . wK
Commands:
click 0 100
click 0 0
wait 250
print board
""")
        lines = output.strip().splitlines()
        self.assertEqual(lines[0].split()[0], "wQ")

    def test_pawn_promotion_black(self):
        output = run_game("""
Board:
. . . bK
. . . .
bP . . .
. . . .
Commands:
click 0 200
click 0 300
wait 250
print board
""")
        lines = output.strip().splitlines()
        self.assertEqual(lines[3].split()[0], "bQ")

    def test_game_over_stops_moves(self):
        output = run_game("""
Board:
wR . bK .
. . . .
. . . .
. . . wK
Commands:
click 0 0
click 200 0
wait 1000
click 300 0
click 300 100
wait 500
print board
""")
        lines = output.strip().splitlines()
        self.assertEqual(lines[0], ". . wR .")
        self.assertEqual(lines[1], ". . . .")

    def test_print_board_after_game_over(self):
        output = run_game("""
Board:
wR bK . .
. . . .
. . . .
. . . wK
Commands:
click 0 0
click 100 0
wait 1000
print board
""")
        self.assertIn("wR", output)

    def test_click_on_empty_does_nothing(self):
        output = run_game("""
Board:
. . . .
. wR . .
. . . .
. . . wK
Commands:
click 0 0
click 100 100
wait 1000
print board
""")
        lines = output.strip().splitlines()
        self.assertEqual(lines[1].split()[1], "wR")

    def test_invalid_board_returns_no_output(self):
        lines = ["Board:", "wR xX wK", "Commands:", "print board"]
        board = BoardParser().parse(lines)
        self.assertIsNone(board)

    def test_multiple_pieces_move_simultaneously(self):
        output = run_game("""
Board:
wR . . .
. . . .
. . . .
wB . . wK
Commands:
click 0 0
click 300 0
wait 1000
print board
""")
        lines = output.strip().splitlines()
        # הרוק זז ל-col 3 בשורה 0
        self.assertEqual(lines[0], ". . . wR")
        # הרץ נשאר במקומו בשורה 3
        self.assertIn("wB", lines[3])

    def test_jump_prevents_airborne_capture(self):
        output = run_game("""
Board:
. . . .
. . . .
. . . .
wR . bR .
Commands:
jump 0 300
click 200 300
click 0 300
wait 1000
print board
""")
        lines = output.strip().splitlines()
        self.assertEqual(lines[3].split()[0], "wR")


if __name__ == "__main__":
    unittest.main()
