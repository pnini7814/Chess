from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import cv2

from chess_io.board_parser import BoardParser
from engine.game_engine import GameEngine
from input.board_mapper import BoardMapper
from input.controller import Controller
from models.game_state import GameState
from realtime.real_time_arbiter import RealTimeArbiter
from rules.rule_engine import RuleEngine
from ui.rendering.board_view import BoardView
from view.renderer import GameSnapshot


def load_initial_board() -> GameState:
    board_text = [
        "Board:",
        "bR bN bB bQ bK bB bN bR",
        "bP bP bP bP bP bP bP bP",
        ". . . . . . . .",
        ". . . . . . . .",
        ". . . . . . . .",
        ". . . . . . . .",
        "wP wP wP wP wP wP wP wP",
        "wR wN wB wQ wK wB wN wR",
        
    ]
    board = BoardParser().parse(board_text)
    if board is None:
        raise RuntimeError("Failed to load initial board")
    return GameState(board=board)


if __name__ == "__main__":
    rule_engine = RuleEngine()
    arbiter = RealTimeArbiter()
    engine = GameEngine(rule_engine, arbiter)
    state = load_initial_board()
    mapper = BoardMapper(rows=state.board.rows, cols=state.board.cols)
    controller = Controller(engine, mapper)
    board_view = BoardView()

    window_name = "Kung Fu Chess"
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, lambda event, x, y, flags, param: controller.on_click(state, x, y) if event == cv2.EVENT_LBUTTONDOWN else None)

    last_time = time.time()
    while True:
        now = time.time()
        dt_ms = int((now - last_time) * 1000)
        last_time = now

        engine.wait(state, dt_ms)
        snapshot: GameSnapshot = engine.snapshot(state)
        frame = board_view.render(snapshot)

        cv2.imshow(window_name, frame.img)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC יוצא
            break
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            break

    cv2.destroyAllWindows()