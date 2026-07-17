import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from models.board import Board
from models.game_state import GameState
from models.position import Position
from models.piece_factory import PieceFactory
from rules.rule_engine import RuleEngine
from engine.game_engine import GameEngine
from realtime.real_time_arbiter import RealTimeArbiter
from realtime.kung_fu_arbiter import KungFuArbiter
from input.controller import Controller
from input.board_mapper import BoardMapper


def make_board(pieces: dict, rows=8, cols=8) -> Board:
    board = Board(rows=rows, cols=cols)
    for (r, c), token in pieces.items():
        piece = PieceFactory.from_token(token, Position(r, c))
        board.add_piece(piece)
    return board


def make_engine():
    return GameEngine(RuleEngine(), RealTimeArbiter())


def make_kung_fu_engine():
    return GameEngine(RuleEngine(), KungFuArbiter())


class TestRuleEngine(unittest.TestCase):

    def setUp(self):
        self.engine = RuleEngine()

    def test_valid_rook_move(self):
        board = make_board({(0, 0): "wR"})
        result = self.engine.validate(board, Position(0, 0), Position(0, 5))
        self.assertTrue(result.is_valid)

    def test_rook_blocked_by_piece(self):
        board = make_board({(0, 0): "wR", (0, 3): "wP"})
        result = self.engine.validate(board, Position(0, 0), Position(0, 5))
        self.assertFalse(result.is_valid)

    def test_friendly_destination_invalid(self):
        board = make_board({(0, 0): "wR", (0, 5): "wP"})
        result = self.engine.validate(board, Position(0, 0), Position(0, 5))
        self.assertFalse(result.is_valid)
        self.assertEqual(result.reason, "friendly_destination")

    def test_empty_source_invalid(self):
        board = make_board({})
        result = self.engine.validate(board, Position(0, 0), Position(0, 5))
        self.assertFalse(result.is_valid)
        self.assertEqual(result.reason, "empty_source")

    def test_outside_board_invalid(self):
        board = make_board({(0, 0): "wR"})
        result = self.engine.validate(board, Position(0, 0), Position(0, 9))
        self.assertFalse(result.is_valid)
        self.assertEqual(result.reason, "outside_board")

    def test_illegal_piece_move(self):
        board = make_board({(0, 0): "wR"})
        result = self.engine.validate(board, Position(0, 0), Position(3, 3))
        self.assertFalse(result.is_valid)
        self.assertEqual(result.reason, "illegal_piece_move")

    def test_capture_enemy(self):
        board = make_board({(0, 0): "wR", (0, 5): "bP"})
        result = self.engine.validate(board, Position(0, 0), Position(0, 5))
        self.assertTrue(result.is_valid)

    def test_knight_jumps_over_pieces(self):
        board = make_board({(0, 0): "wN", (0, 1): "bP", (1, 0): "bP"})
        result = self.engine.validate(board, Position(0, 0), Position(2, 1))
        self.assertTrue(result.is_valid)


class TestGameEngineRequestMove(unittest.TestCase):

    def test_valid_move_accepted(self):
        board = make_board({(0, 0): "wR"})
        state = GameState(board=board)
        engine = make_engine()
        result = engine.request_move(state, Position(0, 0), Position(0, 5))
        self.assertTrue(result.is_accepted)

    def test_game_over_rejects_move(self):
        board = make_board({(0, 0): "wR"})
        state = GameState(board=board, game_over=True)
        engine = make_engine()
        result = engine.request_move(state, Position(0, 0), Position(0, 5))
        self.assertFalse(result.is_accepted)
        self.assertEqual(result.reason, "game_over")

    def test_invalid_move_rejected(self):
        board = make_board({(0, 0): "wR"})
        state = GameState(board=board)
        engine = make_engine()
        result = engine.request_move(state, Position(0, 0), Position(3, 3))
        self.assertFalse(result.is_accepted)

    def test_wait_advances_time(self):
        board = make_board({(0, 0): "wR"})
        state = GameState(board=board)
        engine = make_engine()
        engine.wait(state, 500)
        self.assertEqual(state.current_time, 500)

    def test_king_captured_sets_game_over(self):
        board = make_board({(0, 0): "wR", (0, 5): "bK"})
        state = GameState(board=board)
        engine = make_engine()
        engine.request_move(state, Position(0, 0), Position(0, 5))
        engine.wait(state, 10000)
        self.assertTrue(state.game_over)

    def test_request_jump_accepted(self):
        board = make_board({(0, 0): "wR"})
        state = GameState(board=board)
        engine = make_kung_fu_engine()
        result = engine.request_jump(state, Position(0, 0))
        self.assertTrue(result.is_accepted)

    def test_request_jump_empty_cell_rejected(self):
        board = make_board({})
        state = GameState(board=board)
        engine = make_kung_fu_engine()
        result = engine.request_jump(state, Position(0, 0))
        self.assertFalse(result.is_accepted)
        self.assertEqual(result.reason, "empty_source")

    def test_request_jump_allowed_while_other_piece_moves(self):
        board = make_board({(0, 0): "wR", (0, 7): "wN"})
        state = GameState(board=board)
        engine = make_kung_fu_engine()
        engine.request_move(state, Position(0, 0), Position(0, 5))
        result = engine.request_jump(state, Position(0, 7))
        self.assertTrue(result.is_accepted)

    def test_request_jump_rejected_when_same_piece_in_motion(self):
        board = make_board({(0, 0): "wR"})
        state = GameState(board=board)
        engine = make_kung_fu_engine()
        engine.request_move(state, Position(0, 0), Position(0, 5))
        result = engine.request_jump(state, Position(0, 0))
        self.assertFalse(result.is_accepted)
        self.assertEqual(result.reason, "piece_in_motion")


class TestController(unittest.TestCase):

    def setUp(self):
        self.board = make_board({(0, 0): "wR"}, rows=4, cols=4)
        self.state = GameState(board=self.board)
        self.engine = make_kung_fu_engine()
        self.mapper = BoardMapper(rows=4, cols=4)
        self.controller = Controller(self.engine, self.mapper)

    def test_click_selects_piece(self):
        self.controller.on_click(self.state, 0, 0)
        self.assertTrue(self.state.has_selection())
        self.assertEqual(self.state.selected, Position(0, 0))

    def test_click_empty_cell_no_selection(self):
        self.controller.on_click(self.state, 100, 0)
        self.assertFalse(self.state.has_selection())

    def test_click_out_of_bounds_deselects(self):
        self.controller.on_click(self.state, 0, 0)
        self.controller.on_click(self.state, 9999, 9999)
        self.assertFalse(self.state.has_selection())

    def test_click_move_deselects(self):
        self.controller.on_click(self.state, 0, 0)
        self.controller.on_click(self.state, 300, 0)
        self.assertFalse(self.state.has_selection())

    def test_on_jump_accepted(self):
        result_holder = []
        original = self.engine.request_jump
        def mock_jump(state, pos):
            r = original(state, pos)
            result_holder.append(r)
            return r
        self.engine.request_jump = mock_jump
        self.controller.on_jump(self.state, 0, 0)
        self.assertTrue(result_holder[0].is_accepted)


if __name__ == "__main__":
    unittest.main()
