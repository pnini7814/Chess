from __future__ import annotations
from dataclasses import dataclass
from models.board import Board
from models.game_state import GameState
from models.position import Position
from rules.rule_engine import RuleEngine
from realtime.real_time_arbiter import RealTimeArbiter, KingCapturedError
from realtime.motion import CELL_SIZE
from view.renderer import GameSnapshot, PieceSnapshot


@dataclass(frozen=True)
class MoveResult:
    is_accepted: bool
    reason: str


class GameEngine:

    def __init__(self, rule_engine: RuleEngine, arbiter: RealTimeArbiter):
        self._rule_engine = rule_engine
        self._arbiter = arbiter

    def request_move(self, state: GameState, from_pos: Position, to_pos: Position) -> MoveResult:
        if state.game_over:
            return MoveResult(is_accepted=False, reason="game_over")

        if self._arbiter.has_active_motion():
            return MoveResult(is_accepted=False, reason="motion_in_progress")

        validation = self._rule_engine.validate(state.board, from_pos, to_pos)
        if not validation.is_valid:
            return MoveResult(is_accepted=False, reason=validation.reason)

        piece = state.board.get_piece(from_pos)
        self._arbiter.start_motion(piece, from_pos, to_pos, state.current_time)
        return MoveResult(is_accepted=True, reason="ok")

    def wait(self, state: GameState, ms: int) -> None:
        state.current_time += ms
        try:
            self._arbiter.advance(state.current_time, state.board)
        except KingCapturedError:
            state.game_over = True

    def snapshot(self, state: GameState) -> GameSnapshot:
        pieces = []
        for row in range(state.board.rows):
            for col in range(state.board.cols):
                piece = state.board.get_piece(Position(row, col))
                if piece is not None:
                    pieces.append(PieceSnapshot(
                        kind=piece.kind,
                        color=piece.color.value,
                        pixel_x=col * CELL_SIZE,
                        pixel_y=row * CELL_SIZE,
                        state=piece.state.value,
                    ))
        return GameSnapshot(
            board_width=state.board.cols * CELL_SIZE,
            board_height=state.board.rows * CELL_SIZE,
            pieces=tuple(pieces),
            selected_cell=state.selected,
            game_over=state.game_over,
        )