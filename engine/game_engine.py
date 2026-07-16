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
        if piece is None:
            return MoveResult(is_accepted=False, reason="empty_source")

        self._arbiter.start_motion(piece, from_pos, to_pos, state.current_time)
        return MoveResult(is_accepted=True, reason="ok")
    def request_jump(self, state: GameState, pos: Position) -> MoveResult:
        if state.game_over:
            return MoveResult(is_accepted=False, reason="game_over")

        if self._arbiter.has_active_motion():
            return MoveResult(is_accepted=False, reason="motion_in_progress")

        piece = state.board.get_piece(pos)
        if piece is None:
            return MoveResult(is_accepted=False, reason="empty_source")

        if not hasattr(self._arbiter, 'start_jump'):
            return MoveResult(is_accepted=False, reason="jump_not_supported")

        self._arbiter.start_jump(piece, pos, state.current_time)
        return MoveResult(is_accepted=True, reason="ok")

    def wait(self, state: GameState, ms: int) -> None:
        state.current_time += ms
        try:
            self._arbiter.advance(state.current_time, state.board)
        except KingCapturedError:
            state.game_over = True

    def _active_motions_map(self):
        """Return a dict mapping piece -> Motion for active motions."""
        active = []
        if hasattr(self._arbiter, "get_active_motions"):
            active = self._arbiter.get_active_motions()
        return {m.piece: m for m in active}

    def _piece_pixel(self, piece, row: int, col: int, state: GameState, motion_by_piece):
        """Return (pixel_x, pixel_y) for a piece, using motion if present."""
        m = motion_by_piece.get(piece)
        if m is not None:
            return m.pixel_position(state.current_time, CELL_SIZE)
        return col * CELL_SIZE, row * CELL_SIZE

    def _build_pieces(self, state: GameState, motion_by_piece) -> list[PieceSnapshot]:
        pieces: list[PieceSnapshot] = []
        for row in range(state.board.rows):
            for col in range(state.board.cols):
                piece = state.board.get_piece(Position(row, col))
                if piece is None:
                    continue
                px, py = self._piece_pixel(piece, row, col, state, motion_by_piece)
                pieces.append(PieceSnapshot(
                    kind=piece.kind,
                    color=piece.color.value,
                    pixel_x=px,
                    pixel_y=py,
                    state=piece.state.value,
                ))
        return pieces

    def snapshot(self, state: GameState) -> GameSnapshot:
        motion_by_piece = self._active_motions_map()
        pieces = tuple(self._build_pieces(state, motion_by_piece))
        return GameSnapshot(
            board_width=state.board.cols * CELL_SIZE,
            board_height=state.board.rows * CELL_SIZE,
            pieces=pieces,
            selected_cell=state.selected,
            game_over=state.game_over,
        )
