import time

from models.game_state import GameState
from models.position import Position
from engine.game_engine import GameEngine
from input.board_mapper import BoardMapper

DOUBLE_CLICK_MS = 400


class Controller:

    def __init__(self, engine: GameEngine, mapper: BoardMapper):
        self._engine = engine
        self._mapper = mapper
        self._last_click_time: float | None = None
        self._last_click_position: Position | None = None

    def on_left_button(self, state: GameState, x: int, y: int) -> None:
        """Single click selects/moves; double-click on a piece triggers jump."""
        position = self._mapper.to_position(x, y)
        now = time.time()

        is_double_click = (
            self._last_click_time is not None
            and (now - self._last_click_time) * 1000 < DOUBLE_CLICK_MS
            and position is not None
            and position == self._last_click_position
        )

        if is_double_click:
            self._last_click_time = None
            self._last_click_position = None
            state.deselect()
            self.on_jump(state, x, y)
            return

        self._last_click_time = now
        self._last_click_position = position
        self.on_click(state, x, y)

    def on_click(self, state: GameState, x: int, y: int) -> None:
        position = self._mapper.to_position(x, y)

        if state.has_selection():
            if position is None:
                state.deselect()
                return
            source = state.selected
            state.deselect()
            self._engine.request_move(state, source, position)
        else:
            if position is None:
                return
            piece = state.board.get_piece(position)
            if piece is None:
                return
            state.select(position)

    def on_jump(self, state: GameState, x: int, y: int) -> None:
        """Handle jump command (double-click on a piece)."""
        position = self._mapper.to_position(x, y)
        if position is None:
            return
        self._engine.request_jump(state, position)
