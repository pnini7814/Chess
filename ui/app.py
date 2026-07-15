from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ui.rendering.board_view import BoardView


if __name__ == "__main__":
    board_view = BoardView()
    board = board_view.render()
    board.show("Chess Board")