import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from moves.move_validator import StandardMoveValidator
from moves.move_factory import MoveFactory
from moves.move_scheduler import MoveScheduler


def empty_board(rows=8, cols=8):
    return [["." for _ in range(cols)] for _ in range(rows)]


def board_with(pieces: dict, rows=8, cols=8):
    b = empty_board(rows, cols)
    for (r, c), token in pieces.items():
        b[r][c] = token
    return b


class TestMoveValidator(unittest.TestCase):

    def setUp(self):
        self.validator = StandardMoveValidator()

    def test_same_cell_invalid(self):
        self.assertFalse(self.validator.is_valid("wR", 0, 0, 0, 0, empty_board()))

    def test_rook_horizontal_clear(self):
        self.assertTrue(self.validator.is_valid("wR", 0, 0, 0, 5, empty_board()))

    def test_rook_blocked_by_piece(self):
        board = board_with({(0, 3): "wP"})
        self.assertFalse(self.validator.is_valid("wR", 0, 0, 0, 5, board))

    def test_rook_illegal_diagonal(self):
        self.assertFalse(self.validator.is_valid("wR", 0, 0, 3, 3, empty_board()))

    def test_bishop_diagonal_clear(self):
        self.assertTrue(self.validator.is_valid("wB", 0, 0, 5, 5, empty_board()))

    def test_bishop_blocked(self):
        board = board_with({(2, 2): "bP"})
        self.assertFalse(self.validator.is_valid("wB", 0, 0, 5, 5, board))

    def test_queen_horizontal(self):
        self.assertTrue(self.validator.is_valid("wQ", 4, 0, 4, 7, empty_board()))

    def test_queen_diagonal(self):
        self.assertTrue(self.validator.is_valid("wQ", 0, 0, 7, 7, empty_board()))

    def test_queen_blocked(self):
        board = board_with({(0, 3): "bP"})
        self.assertFalse(self.validator.is_valid("wQ", 0, 0, 0, 7, board))

    def test_knight_jumps_over_pieces(self):
        board = board_with({(1, 0): "bP", (0, 1): "bP", (1, 1): "bP"})
        self.assertTrue(self.validator.is_valid("wN", 0, 0, 2, 1, board))

    def test_knight_illegal_move(self):
        self.assertFalse(self.validator.is_valid("wN", 0, 0, 0, 3, empty_board()))

    def test_king_one_step(self):
        self.assertTrue(self.validator.is_valid("wK", 4, 4, 4, 5, empty_board()))

    def test_king_two_steps_invalid(self):
        self.assertFalse(self.validator.is_valid("wK", 4, 4, 4, 6, empty_board()))

    def test_pawn_forward(self):
        self.assertTrue(self.validator.is_valid("wP", 6, 1, 5, 1, empty_board()))

    def test_pawn_capture(self):
        board = board_with({(5, 2): "bP"})
        self.assertTrue(self.validator.is_valid("wP", 6, 1, 5, 2, board))


class TestMoveFactory(unittest.TestCase):

    def setUp(self):
        self.factory = MoveFactory()

    def test_creates_correct_fields(self):
        move = self.factory.create("wR", 0, 0, 0, 5, 0)
        self.assertEqual(move["piece"], "wR")
        self.assertEqual(move["from_row"], 0)
        self.assertEqual(move["from_col"], 0)
        self.assertEqual(move["to_row"], 0)
        self.assertEqual(move["to_col"], 5)
        self.assertFalse(move["is_jump"])

    def test_arrival_time_rook(self):
        move = self.factory.create("wR", 0, 0, 0, 5, 500)
        self.assertEqual(move["arrival_time"], 1500)

    def test_arrival_time_pawn(self):
        move = self.factory.create("wP", 6, 0, 5, 0, 0)
        self.assertEqual(move["arrival_time"], 250)

    def test_arrival_time_knight(self):
        move = self.factory.create("wN", 0, 0, 2, 1, 1000)
        self.assertEqual(move["arrival_time"], 2500)

    def test_arrival_time_king(self):
        move = self.factory.create("wK", 4, 4, 4, 5, 0)
        self.assertEqual(move["arrival_time"], 500)


class TestMoveScheduler(unittest.TestCase):

    def setUp(self):
        self.scheduler = MoveScheduler()

    def _move(self, piece, fr, fc, tr, tc, arrival, is_jump=False):
        return {
            "piece": piece, "from_row": fr, "from_col": fc,
            "to_row": tr, "to_col": tc,
            "arrival_time": arrival, "is_jump": is_jump,
        }

    def test_empty_pending_returns_empty(self):
        remaining, game_over = self.scheduler.resolve(1000, [], empty_board(), False)
        self.assertEqual(remaining, [])
        self.assertFalse(game_over)

    def test_move_not_yet_arrived_stays_pending(self):
        board = board_with({(0, 0): "wR"})
        move = self._move("wR", 0, 0, 0, 5, 1000)
        remaining, _ = self.scheduler.resolve(500, [move], board, False)
        self.assertEqual(len(remaining), 1)
        self.assertEqual(board[0][0], "wR")

    def test_move_arrived_updates_board(self):
        board = board_with({(0, 0): "wR"})
        move = self._move("wR", 0, 0, 0, 5, 1000)
        remaining, _ = self.scheduler.resolve(1000, [move], board, False)
        self.assertEqual(remaining, [])
        self.assertEqual(board[0][5], "wR")
        self.assertEqual(board[0][0], ".")

    def test_capture_king_sets_game_over(self):
        board = board_with({(0, 0): "wR", (0, 5): "bK"})
        move = self._move("wR", 0, 0, 0, 5, 1000)
        _, game_over = self.scheduler.resolve(1000, [move], board, False)
        self.assertTrue(game_over)

    def test_pawn_promotion_white(self):
        board = board_with({(1, 0): "wP"})
        move = self._move("wP", 1, 0, 0, 0, 1000)
        self.scheduler.resolve(1000, [move], board, False)
        self.assertEqual(board[0][0], "wQ")

    def test_pawn_promotion_black(self):
        board = board_with({(6, 0): "bP"}, rows=8)
        move = self._move("bP", 6, 0, 7, 0, 1000)
        self.scheduler.resolve(1000, [move], board, False)
        self.assertEqual(board[7][0], "bQ")

    def test_jump_move_is_ignored(self):
        board = board_with({(0, 0): "wR"})
        move = self._move("wR", 0, 0, 0, 0, 1000, is_jump=True)
        self.scheduler.resolve(1000, [move], board, False)
        self.assertEqual(board[0][0], "wR")

    def test_airborne_capture(self):
        board = board_with({(0, 5): "wR"})
        arriving = self._move("bR", 0, 0, 0, 5, 1000)
        jump = self._move("wR", 0, 5, 0, 5, 2000, is_jump=True)
        pending = [arriving, jump]
        self.scheduler.resolve(1000, pending, board, False)
        self.assertEqual(board[0][5], "wR")

    def test_piece_moved_away_before_arrival(self):
        board = board_with({(0, 3): "bP"})
        move = self._move("wR", 0, 0, 0, 5, 1000)
        board[0][0] = "."
        remaining, _ = self.scheduler.resolve(1000, [move], board, False)
        self.assertEqual(board[0][5], ".")

    def test_game_over_skips_remaining_moves(self):
        board = board_with({(0, 0): "wR", (1, 0): "wB"})
        move1 = self._move("wR", 0, 0, 0, 5, 500)
        move2 = self._move("wB", 1, 0, 3, 2, 1000)
        _, game_over = self.scheduler.resolve(1000, [move1, move2], board, True)
        self.assertEqual(board[0][5], ".")
        self.assertEqual(board[3][2], ".")


if __name__ == "__main__":
    unittest.main()
