from models.game_state import GameState
from models.position import Position
from engine.game_engine import GameEngine
from input.board_mapper import BoardMapper


class Controller:

    def __init__(self, engine: GameEngine, mapper: BoardMapper):
        self._engine = engine
        self._mapper = mapper

    def on_jump(self, state: GameState, x: int, y: int) -> None:
        position = self._mapper.to_position(x, y)
        if position is None:
            return
        self._engine.request_jump(state, position)

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
