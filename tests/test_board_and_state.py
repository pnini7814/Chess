import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from models.board import Board
from models.game_state import GameState
from models.position import Position
from models.piece import PieceColor
from models.piece_factory import PieceFactory
from chess_io.board_parser import BoardParser


def make_board(pieces: dict, rows=4, cols=4) -> Board:
    board = Board(rows=rows, cols=cols)
    for (r, c), token in pieces.items():
        piece = PieceFactory.from_token(token, Position(r, c))
        board.add_piece(piece)
    return board


class TestBoard(unittest.TestCase):

    def test_add_and_get_piece(self):
        board = make_board({(0, 0): "wR"})
        piece = board.get_piece(Position(0, 0))
        self.assertIsNotNone(piece)
        self.assertEqual(piece.kind, "rook")

    def test_get_empty_cell_returns_none(self):
        board = Board(rows=4, cols=4)
        self.assertIsNone(board.get_piece(Position(0, 0)))

    def test_remove_piece(self):
        board = make_board({(0, 0): "wR"})
        board.remove_piece(Position(0, 0))
        self.assertIsNone(board.get_piece(Position(0, 0)))

    def test_is_within_bounds_true(self):
        board = Board(rows=4, cols=4)
        self.assertTrue(board.is_within_bounds(Position(0, 0)))
        self.assertTrue(board.is_within_bounds(Position(3, 3)))

    def test_is_within_bounds_false(self):
        board = Board(rows=4, cols=4)
        self.assertFalse(board.is_within_bounds(Position(-1, 0)))
        self.assertFalse(board.is_within_bounds(Position(4, 0)))
        self.assertFalse(board.is_within_bounds(Position(0, 4)))

    def test_add_piece_out_of_bounds_raises(self):
        board = Board(rows=4, cols=4)
        piece = PieceFactory.from_token("wR", Position(5, 5))
        with self.assertRaises(ValueError):
            board.add_piece(piece)

    def test_add_piece_occupied_raises(self):
        board = make_board({(0, 0): "wR"})
        piece = PieceFactory.from_token("bR", Position(0, 0))
        with self.assertRaises(ValueError):
            board.add_piece(piece)

    def test_remove_nonexistent_raises(self):
        board = Board(rows=4, cols=4)
        with self.assertRaises(ValueError):
            board.remove_piece(Position(0, 0))


class TestBoardParser(unittest.TestCase):

    def setUp(self):
        self.parser = BoardParser()

    def _parse(self, rows):
        return self.parser.parse(["Board:"] + rows)

    def test_valid_board_parsed(self):
        board = self._parse(["wR . wK", ". . .", "bR . bK"])
        self.assertIsNotNone(board)
        self.assertEqual(board.get_piece(Position(0, 0)).kind, "rook")
        self.assertIsNone(board.get_piece(Position(0, 1)))

    def test_empty_input_returns_none(self):
        self.assertIsNone(self.parser.parse([]))

    def test_no_board_section_returns_none(self):
        self.assertIsNone(self.parser.parse(["Commands:", "click 0 0"]))

    def test_row_width_mismatch_returns_none(self):
        self.assertIsNone(self._parse(["wR . wK", ". ."]))

    def test_unknown_token_returns_none(self):
        self.assertIsNone(self._parse(["wR xX wK"]))

    def test_all_piece_types_valid(self):
        board = self._parse(["wK wQ wR wB wN wP"])
        self.assertIsNotNone(board)

    def test_dots_are_empty(self):
        board = self._parse([". . .", ". . ."])
        self.assertIsNotNone(board)
        self.assertIsNone(board.get_piece(Position(0, 0)))


class TestGameState(unittest.TestCase):

    def test_initial_state(self):
        board = Board(rows=4, cols=4)
        state = GameState(board=board)
        self.assertEqual(state.current_time, 0)
        self.assertFalse(state.game_over)
        self.assertFalse(state.has_selection())

    def test_select_and_deselect(self):
        board = Board(rows=4, cols=4)
        state = GameState(board=board)
        pos = Position(2, 3)
        state.select(pos)
        self.assertTrue(state.has_selection())
        self.assertEqual(state.selected, pos)
        state.deselect()
        self.assertFalse(state.has_selection())

    def test_game_over_default_false(self):
        board = Board(rows=4, cols=4)
        state = GameState(board=board)
        self.assertFalse(state.game_over)


if __name__ == "__main__":
    unittest.main()
