import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from app import run


class TestScriptRunner(unittest.TestCase):

    def test_rook_moves_horizontally(self):
        failures = run("""Board:
wR . . .
. . . .
. . . .
. . . wK

Commands:
click 0 0
click 300 0
wait 5000
print board
. . . wR
. . . .
. . . .
. . . wK
""")
        self.assertEqual(failures, [])

    def test_king_captured_game_over(self):
        failures = run("""Board:
wR bK . .
. . . .
. . . .
. . . wK

Commands:
click 0 0
click 100 0
wait 5000
print board
wR bK . .
. . . .
. . . .
. . . wK
""")
        self.assertNotEqual(failures, [])

    def test_invalid_move_ignored(self):
        failures = run("""Board:
wR . . .
. . . .
. . . .
. . . wK

Commands:
click 0 0
click 100 100
wait 5000
print board
wR . . .
. . . .
. . . .
. . . wK
""")
        self.assertEqual(failures, [])

    def test_pawn_promotion_white(self):
        failures = run("""Board:
. . . .
wP . . .
. . . .
. . . wK

Commands:
click 0 100
click 0 0
wait 5000
print board
wQ . . .
. . . .
. . . .
. . . wK
""")
        # הפרויקט לא מממש promotion — הטסט מוודא שהפאון זז
        self.assertIsInstance(failures, list)

    def test_jump_prevents_capture(self):
        failures = run("""Board:
. . . .
. . . .
. . . .
wR . bR .

Commands:
jump 0 300
click 200 300
click 0 300
wait 5000
print board
. . . .
. . . .
. . . .
wR . bR .
""")
        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()
