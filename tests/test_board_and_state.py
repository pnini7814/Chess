import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from board.board_parser import BoardParser
from game.game_state import GameState


class TestBoardParser(unittest.TestCase):

    def setUp(self):
        self.parser = BoardParser()

    def _lines(self, board_rows, commands=None):
        lines = ["Board:"] + board_rows
        if commands:
            lines += ["Commands:"] + commands
        return lines

    def test_valid_board_parsed(self):
        lines = self._lines(["wR . wK", ". . .", "bR . bK"])
        board = self.parser.parse(lines)
        self.assertIsNotNone(board)
        self.assertEqual(board[0][0], "wR")
        self.assertEqual(board[0][1], ".")
        self.assertEqual(board[0][2], "wK")

    def test_empty_input_returns_none(self):
        self.assertIsNone(self.parser.parse([]))

    def test_no_board_section_returns_none(self):
        self.assertIsNone(self.parser.parse(["Commands:", "click 0 0"]))

    def test_row_width_mismatch_returns_none(self):
        lines = self._lines(["wR . wK", ". ."])
        self.assertIsNone(self.parser.parse(lines))

    def test_unknown_token_returns_none(self):
        lines = self._lines(["wR xX wK"])
        self.assertIsNone(self.parser.parse(lines))

    def test_invalid_color_returns_none(self):
        lines = self._lines(["xR . wK"])
        self.assertIsNone(self.parser.parse(lines))

    def test_stops_at_commands_section(self):
        lines = self._lines(["wR . wK"], ["click 0 0"])
        board = self.parser.parse(lines)
        self.assertEqual(len(board), 1)

    def test_dots_are_valid(self):
        lines = self._lines([". . .", ". . ."])
        board = self.parser.parse(lines)
        self.assertIsNotNone(board)

    def test_all_piece_types_valid(self):
        lines = self._lines(["wK wQ wR wB wN wP"])
        board = self.parser.parse(lines)
        self.assertIsNotNone(board)


class TestGameState(unittest.TestCase):

    def _state(self, pieces=None, rows=4, cols=4):
        board = [["." for _ in range(cols)] for _ in range(rows)]
        if pieces:
            for (r, c), token in pieces.items():
                board[r][c] = token
        return GameState(board=board)

    def test_initial_state(self):
        state = self._state()
        self.assertEqual(state.current_time, 0)
        self.assertFalse(state.game_over)
        self.assertFalse(state.has_selection())
        self.assertEqual(state.pending_moves, [])

    def test_select_and_deselect(self):
        state = self._state()
        state.select(2, 3)
        self.assertTrue(state.has_selection())
        self.assertEqual(state.selected_row, 2)
        self.assertEqual(state.selected_col, 3)
        state.deselect()
        self.assertFalse(state.has_selection())

    def test_is_within_bounds_true(self):
        state = self._state()
        self.assertTrue(state.is_within_bounds(0, 0))
        self.assertTrue(state.is_within_bounds(3, 3))

    def test_is_within_bounds_false(self):
        state = self._state()
        self.assertFalse(state.is_within_bounds(-1, 0))
        self.assertFalse(state.is_within_bounds(4, 0))
        self.assertFalse(state.is_within_bounds(0, 4))

    def test_is_piece_moving_true(self):
        state = self._state()
        state.pending_moves.append({"from_row": 1, "from_col": 2, "arrival_time": 500, "is_jump": False})
        self.assertTrue(state.is_piece_moving(1, 2))

    def test_is_piece_moving_false(self):
        state = self._state()
        self.assertFalse(state.is_piece_moving(1, 2))

    def test_is_piece_moving_exclude_jumps(self):
        state = self._state()
        state.pending_moves.append({"from_row": 1, "from_col": 2, "arrival_time": 500, "is_jump": True})
        self.assertFalse(state.is_piece_moving(1, 2, include_jumps=False))
        self.assertTrue(state.is_piece_moving(1, 2, include_jumps=True))


if __name__ == "__main__":
    unittest.main()
