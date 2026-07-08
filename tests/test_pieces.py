import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from pieces.king import King
from pieces.queen import Queen
from pieces.rook import Rook
from pieces.bishop import Bishop
from pieces.knight import Knight
from pieces.pawn import Pawn
from pieces.piece_factory import PieceFactory


EMPTY_BOARD = [["." for _ in range(8)] for _ in range(8)]


class TestKing(unittest.TestCase):

    def setUp(self):
        self.king = King("w")

    def test_piece_type(self):
        self.assertEqual(self.king.piece_type, "K")

    def test_move_duration(self):
        self.assertEqual(self.king.move_duration_ms, 500)

    def test_blocks_path_false(self):
        self.assertFalse(self.king.blocks_path)

    def test_legal_one_step_horizontal(self):
        self.assertTrue(self.king.is_legal_shape(4, 4, 4, 5, EMPTY_BOARD))

    def test_legal_one_step_vertical(self):
        self.assertTrue(self.king.is_legal_shape(4, 4, 5, 4, EMPTY_BOARD))

    def test_legal_one_step_diagonal(self):
        self.assertTrue(self.king.is_legal_shape(4, 4, 5, 5, EMPTY_BOARD))

    def test_illegal_two_steps(self):
        self.assertFalse(self.king.is_legal_shape(4, 4, 4, 6, EMPTY_BOARD))

    def test_illegal_same_cell(self):
        # same-cell נבדק ב-MoveValidator ולא בכלי עצמו
        self.assertFalse(self.king.is_legal_shape(4, 4, 4, 6, EMPTY_BOARD))

    def test_str(self):
        self.assertEqual(str(self.king), "wK")


class TestQueen(unittest.TestCase):

    def setUp(self):
        self.queen = Queen("b")

    def test_piece_type(self):
        self.assertEqual(self.queen.piece_type, "Q")

    def test_move_duration(self):
        self.assertEqual(self.queen.move_duration_ms, 1000)

    def test_blocks_path_true(self):
        self.assertTrue(self.queen.blocks_path)

    def test_legal_horizontal(self):
        self.assertTrue(self.queen.is_legal_shape(4, 4, 4, 7, EMPTY_BOARD))

    def test_legal_vertical(self):
        self.assertTrue(self.queen.is_legal_shape(4, 4, 0, 4, EMPTY_BOARD))

    def test_legal_diagonal(self):
        self.assertTrue(self.queen.is_legal_shape(4, 4, 7, 7, EMPTY_BOARD))

    def test_illegal_l_shape(self):
        self.assertFalse(self.queen.is_legal_shape(4, 4, 6, 5, EMPTY_BOARD))


class TestRook(unittest.TestCase):

    def setUp(self):
        self.rook = Rook("w")

    def test_piece_type(self):
        self.assertEqual(self.rook.piece_type, "R")

    def test_blocks_path_true(self):
        self.assertTrue(self.rook.blocks_path)

    def test_legal_horizontal(self):
        self.assertTrue(self.rook.is_legal_shape(0, 0, 0, 7, EMPTY_BOARD))

    def test_legal_vertical(self):
        self.assertTrue(self.rook.is_legal_shape(0, 0, 7, 0, EMPTY_BOARD))

    def test_illegal_diagonal(self):
        self.assertFalse(self.rook.is_legal_shape(0, 0, 3, 3, EMPTY_BOARD))


class TestBishop(unittest.TestCase):

    def setUp(self):
        self.bishop = Bishop("b")

    def test_piece_type(self):
        self.assertEqual(self.bishop.piece_type, "B")

    def test_blocks_path_true(self):
        self.assertTrue(self.bishop.blocks_path)

    def test_legal_diagonal(self):
        self.assertTrue(self.bishop.is_legal_shape(0, 0, 5, 5, EMPTY_BOARD))

    def test_illegal_horizontal(self):
        self.assertFalse(self.bishop.is_legal_shape(0, 0, 0, 5, EMPTY_BOARD))

    def test_illegal_vertical(self):
        self.assertFalse(self.bishop.is_legal_shape(0, 0, 5, 0, EMPTY_BOARD))


class TestKnight(unittest.TestCase):

    def setUp(self):
        self.knight = Knight("w")

    def test_piece_type(self):
        self.assertEqual(self.knight.piece_type, "N")

    def test_move_duration(self):
        self.assertEqual(self.knight.move_duration_ms, 1500)

    def test_blocks_path_false(self):
        self.assertFalse(self.knight.blocks_path)

    def test_legal_2_1(self):
        self.assertTrue(self.knight.is_legal_shape(4, 4, 6, 5, EMPTY_BOARD))

    def test_legal_1_2(self):
        self.assertTrue(self.knight.is_legal_shape(4, 4, 5, 6, EMPTY_BOARD))

    def test_illegal_straight(self):
        self.assertFalse(self.knight.is_legal_shape(4, 4, 4, 6, EMPTY_BOARD))

    def test_illegal_diagonal(self):
        self.assertFalse(self.knight.is_legal_shape(4, 4, 6, 6, EMPTY_BOARD))


class TestPawn(unittest.TestCase):

    def _board(self, rows):
        return [list(r) for r in rows]

    def test_piece_type(self):
        self.assertEqual(Pawn("w").piece_type, "P")

    def test_move_duration(self):
        self.assertEqual(Pawn("w").move_duration_ms, 250)

    def test_white_one_step_forward(self):
        board = self._board([
            ["."] * 4,
            ["."] * 4,
            ["."] * 4,
            ["."] * 4,
        ])
        self.assertTrue(Pawn("w").is_legal_shape(2, 1, 1, 1, board))

    def test_white_two_steps_from_start(self):
        board = self._board([
            ["."] * 4,
            ["."] * 4,
            ["."] * 4,
            ["."] * 4,
        ])
        self.assertTrue(Pawn("w").is_legal_shape(3, 1, 1, 1, board))

    def test_white_two_steps_blocked_middle(self):
        board = self._board([
            ["."] * 4,
            ["."] * 4,
            [".", "bP", ".", "."],
            ["."] * 4,
        ])
        self.assertFalse(Pawn("w").is_legal_shape(3, 1, 1, 1, board))

    def test_white_capture_diagonal(self):
        board = self._board([
            ["."] * 4,
            [".", "bP", ".", "."],
            ["."] * 4,
            ["."] * 4,
        ])
        self.assertTrue(Pawn("w").is_legal_shape(2, 0, 1, 1, board))

    def test_white_cannot_capture_empty(self):
        board = self._board([
            ["."] * 4,
            ["."] * 4,
            ["."] * 4,
            ["."] * 4,
        ])
        self.assertFalse(Pawn("w").is_legal_shape(2, 0, 1, 1, board))

    def test_white_cannot_move_backward(self):
        board = self._board([["."] * 4] * 4)
        self.assertFalse(Pawn("w").is_legal_shape(1, 1, 2, 1, board))

    def test_black_one_step_forward(self):
        board = self._board([["."] * 4] * 4)
        self.assertTrue(Pawn("b").is_legal_shape(1, 1, 2, 1, board))

    def test_black_two_steps_from_start(self):
        board = self._board([["."] * 4] * 4)
        self.assertTrue(Pawn("b").is_legal_shape(0, 1, 2, 1, board))

    def test_black_capture_diagonal(self):
        board = self._board([
            ["."] * 4,
            ["."] * 4,
            [".", "wP", ".", "."],
            ["."] * 4,
        ])
        self.assertTrue(Pawn("b").is_legal_shape(1, 0, 2, 1, board))


class TestPieceFactory(unittest.TestCase):

    def test_create_king(self):
        piece = PieceFactory.create("w", "K")
        self.assertIsInstance(piece, King)
        self.assertEqual(piece.color, "w")

    def test_create_all_pieces(self):
        for symbol, expected in [("K", King), ("Q", Queen), ("R", Rook),
                                  ("B", Bishop), ("N", Knight), ("P", Pawn)]:
            with self.subTest(symbol=symbol):
                self.assertIsInstance(PieceFactory.create("w", symbol), expected)

    def test_from_token(self):
        piece = PieceFactory.from_token("bQ")
        self.assertIsInstance(piece, Queen)
        self.assertEqual(piece.color, "b")

    def test_unknown_symbol_raises(self):
        with self.assertRaises(ValueError):
            PieceFactory.create("w", "X")

    def test_register_new_piece(self):
        class TestPiece(King):
            @property
            def piece_type(self): return "T"

        PieceFactory.register("T", TestPiece)
        self.assertIn("T", PieceFactory.known_symbols())
        PieceFactory._registry.pop("T")

    def test_known_symbols_contains_all(self):
        symbols = PieceFactory.known_symbols()
        for s in ("K", "Q", "R", "B", "N", "P"):
            self.assertIn(s, symbols)


if __name__ == "__main__":
    unittest.main()
