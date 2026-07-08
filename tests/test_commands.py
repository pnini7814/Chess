import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from unittest.mock import MagicMock
from io import StringIO
from game.game_state import GameState
from commands.click_command import ClickCommand
from commands.jump_command import JumpCommand
from commands.wait_command import WaitCommand
from commands.print_command import PrintCommand
from commands.command_factory import CommandFactory


def make_board(pieces: dict, rows=4, cols=4):
    b = [["." for _ in range(cols)] for _ in range(rows)]
    for (r, c), token in pieces.items():
        b[r][c] = token
    return b


def make_state(pieces: dict, rows=4, cols=4, **kwargs):
    return GameState(board=make_board(pieces, rows, cols), **kwargs)


class TestClickCommandSelection(unittest.TestCase):

    def setUp(self):
        self.validator = MagicMock()
        self.factory = MagicMock()

    def _click(self, x, y):
        return ClickCommand(["click", str(x), str(y)], self.validator, self.factory)

    def test_selects_piece(self):
        state = make_state({(0, 0): "wR"})
        self._click(0, 0).execute(state)
        self.assertEqual(state.selected_row, 0)
        self.assertEqual(state.selected_col, 0)

    def test_does_not_select_empty_cell(self):
        state = make_state({})
        self._click(0, 0).execute(state)
        self.assertFalse(state.has_selection())

    def test_does_not_select_moving_piece(self):
        state = make_state({(0, 0): "wR"})
        state.pending_moves.append({"from_row": 0, "from_col": 0, "arrival_time": 999, "is_jump": False})
        self._click(0, 0).execute(state)
        self.assertFalse(state.has_selection())

    def test_out_of_bounds_ignored(self):
        state = make_state({})
        self._click(900, 900).execute(state)
        self.assertFalse(state.has_selection())

    def test_switch_selection_to_ally(self):
        state = make_state({(0, 0): "wR", (0, 1): "wB"})
        state.select(0, 0)
        self._click(100, 0).execute(state)
        self.assertEqual(state.selected_col, 1)

    def test_does_not_switch_to_moving_ally(self):
        state = make_state({(0, 0): "wR", (0, 1): "wB"})
        state.select(0, 0)
        state.pending_moves.append({"from_row": 0, "from_col": 1, "arrival_time": 999, "is_jump": False})
        self._click(100, 0).execute(state)
        self.assertEqual(state.selected_col, 0)


class TestClickCommandMove(unittest.TestCase):

    def setUp(self):
        self.validator = MagicMock(return_value=True)
        self.validator.is_valid = MagicMock(return_value=True)
        self.factory = MagicMock()
        self.factory.create = MagicMock(return_value={
            "piece": "wR", "from_row": 0, "from_col": 0,
            "to_row": 0, "to_col": 2, "arrival_time": 1000, "is_jump": False
        })

    def _click(self, x, y):
        return ClickCommand(["click", str(x), str(y)], self.validator, self.factory)

    def test_valid_move_added_to_pending(self):
        state = make_state({(0, 0): "wR"})
        state.select(0, 0)
        self._click(200, 0).execute(state)
        self.assertEqual(len(state.pending_moves), 1)
        self.assertFalse(state.has_selection())

    def test_invalid_move_not_added(self):
        self.validator.is_valid = MagicMock(return_value=False)
        state = make_state({(0, 0): "wR"})
        state.select(0, 0)
        self._click(200, 0).execute(state)
        self.assertEqual(len(state.pending_moves), 0)

    def test_valid_capture_added_to_pending(self):
        state = make_state({(0, 0): "wR", (0, 2): "bP"})
        state.select(0, 0)
        self._click(200, 0).execute(state)
        self.assertEqual(len(state.pending_moves), 1)
        self.assertFalse(state.has_selection())

    def test_deselects_after_move(self):
        state = make_state({(0, 0): "wR"})
        state.select(0, 0)
        self._click(200, 0).execute(state)
        self.assertFalse(state.has_selection())


class TestJumpCommand(unittest.TestCase):

    def _jump(self, x, y):
        return JumpCommand(["jump", str(x), str(y)])

    def test_adds_jump_move(self):
        state = make_state({(0, 0): "wR"})
        self._jump(0, 0).execute(state)
        self.assertEqual(len(state.pending_moves), 1)
        self.assertTrue(state.pending_moves[0]["is_jump"])

    def test_jump_on_empty_cell_ignored(self):
        state = make_state({})
        self._jump(0, 0).execute(state)
        self.assertEqual(len(state.pending_moves), 0)

    def test_jump_out_of_bounds_ignored(self):
        state = make_state({})
        self._jump(900, 900).execute(state)
        self.assertEqual(len(state.pending_moves), 0)

    def test_jump_on_already_moving_piece_ignored(self):
        state = make_state({(0, 0): "wR"})
        state.pending_moves.append({"from_row": 0, "from_col": 0, "arrival_time": 999, "is_jump": False})
        self._jump(0, 0).execute(state)
        self.assertEqual(len(state.pending_moves), 1)

    def test_jump_arrival_time(self):
        state = make_state({(0, 0): "wR"})
        state.current_time = 500
        self._jump(0, 0).execute(state)
        self.assertEqual(state.pending_moves[0]["arrival_time"], 1500)


class TestWaitCommand(unittest.TestCase):

    def test_advances_time(self):
        scheduler = MagicMock()
        scheduler.resolve = MagicMock(return_value=([], False))
        state = make_state({})
        WaitCommand(["wait", "500"], scheduler).execute(state)
        self.assertEqual(state.current_time, 500)

    def test_calls_scheduler(self):
        scheduler = MagicMock()
        scheduler.resolve = MagicMock(return_value=([], False))
        state = make_state({})
        WaitCommand(["wait", "1000"], scheduler).execute(state)
        scheduler.resolve.assert_called_once_with(1000, [], state.board, False)

    def test_updates_game_over(self):
        scheduler = MagicMock()
        scheduler.resolve = MagicMock(return_value=([], True))
        state = make_state({})
        WaitCommand(["wait", "1000"], scheduler).execute(state)
        self.assertTrue(state.game_over)


class TestPrintCommand(unittest.TestCase):

    def test_prints_board(self):
        state = make_state({(0, 0): "wR"}, rows=2, cols=2)
        state.board = [["wR", "."], [".", "bK"]]
        captured = StringIO()
        sys.stdout = captured
        PrintCommand().execute(state)
        sys.stdout = sys.__stdout__
        self.assertEqual(captured.getvalue(), "wR .\n. bK\n")


class TestCommandFactory(unittest.TestCase):

    def setUp(self):
        self.validator = MagicMock()
        self.factory = MagicMock()
        self.scheduler = MagicMock()
        self.cmd_factory = CommandFactory(self.validator, self.factory, self.scheduler)

    def test_parses_click(self):
        cmd = self.cmd_factory.parse("click 100 200")
        self.assertIsInstance(cmd, ClickCommand)

    def test_parses_jump(self):
        cmd = self.cmd_factory.parse("jump 100 200")
        self.assertIsInstance(cmd, JumpCommand)

    def test_parses_wait(self):
        cmd = self.cmd_factory.parse("wait 500")
        self.assertIsInstance(cmd, WaitCommand)

    def test_parses_print_board(self):
        cmd = self.cmd_factory.parse("print board")
        self.assertIsInstance(cmd, PrintCommand)

    def test_unknown_command_returns_none(self):
        cmd = self.cmd_factory.parse("unknown 1 2")
        self.assertIsNone(cmd)

    def test_empty_line_returns_none(self):
        cmd = self.cmd_factory.parse("")
        self.assertIsNone(cmd)

    def test_print_without_board_returns_none(self):
        cmd = self.cmd_factory.parse("print")
        self.assertIsNone(cmd)


if __name__ == "__main__":
    unittest.main()
