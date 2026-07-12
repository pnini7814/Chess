import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from models.king import King
from models.queen import Queen
from models.rook import Rook
from models.bishop import Bishop
from models.knight import Knight
from models.pawn import Pawn
from models.piece import PieceColor
from models.piece_factory import PieceFactory
from models.position import Position
from models.board import Board
from rules.rule_engine import RuleEngine


W = PieceColor.WHITE
B = PieceColor.BLACK
ORIGIN = Position(4, 4)


def make_board(pieces: dict, rows=8, cols=8) -> Board:
    board = Board(rows=rows, cols=cols)
    for (r, c), token in pieces.items():
        piece = PieceFactory.from_token(token, Position(r, c))
        board.add_piece(piece)
    return board


class TestKing(unittest.TestCase):

    def setUp(self):
        self.engine = RuleEngine()

    def test_kind(self):
        self.assertEqual(King(color=W, cell=ORIGIN).kind, "king")

    def test_str(self):
        self.assertEqual(str(King(color=W, cell=ORIGIN)), "wK")

    def test_legal_one_step_horizontal(self):
        board = make_board({(4, 4): "wK"})
        self.assertTrue(self.engine.validate(board, Position(4, 4), Position(4, 5)).is_valid)

    def test_legal_one_step_diagonal(self):
        board = make_board({(4, 4): "wK"})
        self.assertTrue(self.engine.validate(board, Position(4, 4), Position(5, 5)).is_valid)

    def test_illegal_two_steps(self):
        board = make_board({(4, 4): "wK"})
        self.assertFalse(self.engine.validate(board, Position(4, 4), Position(4, 6)).is_valid)


class TestQueen(unittest.TestCase):

    def setUp(self):
        self.engine = RuleEngine()

    def test_kind(self):
        self.assertEqual(Queen(color=W, cell=ORIGIN).kind, "queen")

    def test_legal_horizontal(self):
        board = make_board({(4, 4): "wQ"})
        self.assertTrue(self.engine.validate(board, Position(4, 4), Position(4, 7)).is_valid)

    def test_legal_diagonal(self):
        board = make_board({(4, 4): "wQ"})
        self.assertTrue(self.engine.validate(board, Position(4, 4), Position(7, 7)).is_valid)

    def test_illegal_l_shape(self):
        board = make_board({(4, 4): "wQ"})
        self.assertFalse(self.engine.validate(board, Position(4, 4), Position(6, 5)).is_valid)


class TestRook(unittest.TestCase):

    def setUp(self):
        self.engine = RuleEngine()

    def test_kind(self):
        self.assertEqual(Rook(color=W, cell=ORIGIN).kind, "rook")

    def test_legal_horizontal(self):
        board = make_board({(0, 0): "wR"})
        self.assertTrue(self.engine.validate(board, Position(0, 0), Position(0, 7)).is_valid)

    def test_legal_vertical(self):
        board = make_board({(0, 0): "wR"})
        self.assertTrue(self.engine.validate(board, Position(0, 0), Position(7, 0)).is_valid)

    def test_illegal_diagonal(self):
        board = make_board({(0, 0): "wR"})
        self.assertFalse(self.engine.validate(board, Position(0, 0), Position(3, 3)).is_valid)


class TestBishop(unittest.TestCase):

    def setUp(self):
        self.engine = RuleEngine()

    def test_kind(self):
        self.assertEqual(Bishop(color=B, cell=ORIGIN).kind, "bishop")

    def test_legal_diagonal(self):
        board = make_board({(0, 0): "wB"})
        self.assertTrue(self.engine.validate(board, Position(0, 0), Position(5, 5)).is_valid)

    def test_illegal_horizontal(self):
        board = make_board({(0, 0): "wB"})
        self.assertFalse(self.engine.validate(board, Position(0, 0), Position(0, 5)).is_valid)


class TestKnight(unittest.TestCase):

    def setUp(self):
        self.engine = RuleEngine()

    def test_kind(self):
        self.assertEqual(Knight(color=W, cell=ORIGIN).kind, "knight")

    def test_legal_2_1(self):
        board = make_board({(4, 4): "wN"})
        self.assertTrue(self.engine.validate(board, Position(4, 4), Position(6, 5)).is_valid)

    def test_legal_1_2(self):
        board = make_board({(4, 4): "wN"})
        self.assertTrue(self.engine.validate(board, Position(4, 4), Position(5, 6)).is_valid)

    def test_illegal_straight(self):
        board = make_board({(4, 4): "wN"})
        self.assertFalse(self.engine.validate(board, Position(4, 4), Position(4, 6)).is_valid)

    def test_jumps_over_pieces(self):
        board = make_board({(4, 4): "wN", (4, 5): "bP", (5, 4): "bP"})
        self.assertTrue(self.engine.validate(board, Position(4, 4), Position(6, 5)).is_valid)


class TestPawn(unittest.TestCase):

    def setUp(self):
        self.engine = RuleEngine()

    def test_kind(self):
        self.assertEqual(Pawn(color=W, cell=ORIGIN).kind, "pawn")

    def test_white_one_step_forward(self):
        board = make_board({(4, 4): "wP"})
        self.assertTrue(self.engine.validate(board, Position(4, 4), Position(3, 4)).is_valid)

    def test_white_cannot_move_backward(self):
        board = make_board({(4, 4): "wP"})
        self.assertFalse(self.engine.validate(board, Position(4, 4), Position(5, 4)).is_valid)

    def test_white_capture_diagonal(self):
        board = make_board({(4, 4): "wP", (3, 5): "bP"})
        self.assertTrue(self.engine.validate(board, Position(4, 4), Position(3, 5)).is_valid)

    def test_white_cannot_capture_empty(self):
        board = make_board({(4, 4): "wP"})
        self.assertFalse(self.engine.validate(board, Position(4, 4), Position(3, 5)).is_valid)

    def test_black_one_step_forward(self):
        board = make_board({(4, 4): "bP"})
        self.assertTrue(self.engine.validate(board, Position(4, 4), Position(5, 4)).is_valid)

    def test_black_capture_diagonal(self):
        board = make_board({(4, 4): "bP", (5, 5): "wP"})
        self.assertTrue(self.engine.validate(board, Position(4, 4), Position(5, 5)).is_valid)


class TestPieceFactory(unittest.TestCase):

    def test_create_king(self):
        piece = PieceFactory.create("K", W, Position(0, 0))
        self.assertIsInstance(piece, King)
        self.assertEqual(piece.color, W)

    def test_create_all_pieces(self):
        for symbol, expected in [("K", King), ("Q", Queen), ("R", Rook),
                                  ("B", Bishop), ("N", Knight), ("P", Pawn)]:
            with self.subTest(symbol=symbol):
                self.assertIsInstance(PieceFactory.create(symbol, W, Position(0, 0)), expected)

    def test_from_token(self):
        piece = PieceFactory.from_token("bQ", Position(0, 0))
        self.assertIsInstance(piece, Queen)
        self.assertEqual(piece.color, B)

    def test_unknown_symbol_raises(self):
        with self.assertRaises(ValueError):
            PieceFactory.create("X", W, Position(0, 0))

    def test_register_new_piece(self):
        class TestPiece(King):
            @property
            def kind(self): return "test"

        PieceFactory.register("T", TestPiece)
        self.assertIn("T", PieceFactory.known_symbols())
        PieceFactory._registry.pop("T")

    def test_known_symbols_contains_all(self):
        for s in ("K", "Q", "R", "B", "N", "P"):
            self.assertIn(s, PieceFactory.known_symbols())


if __name__ == "__main__":
    unittest.main()
