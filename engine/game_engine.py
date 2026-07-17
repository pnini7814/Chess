from __future__ import annotations
from dataclasses import dataclass
from models.board import Board
from models.game_state import GameState
from models.position import Position
from rules.rule_engine import RuleEngine
from realtime.real_time_arbiter import RealTimeArbiter, KingCapturedError
from realtime.motion import CELL_SIZE
from view.renderer import GameSnapshot, PieceSnapshot
from view.renderer import GameSnapshot, PieceSnapshot, CooldownInfo



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

        piece = state.board.get_piece(from_pos)
        if piece is None:
            return MoveResult(is_accepted=False, reason="empty_source")

        if self._arbiter.is_on_cooldown(piece, state.current_time):
            return MoveResult(is_accepted=False, reason="on_cooldown")

        validation = self._rule_engine.validate(state.board, from_pos, to_pos)
        if not validation.is_valid:
            return MoveResult(is_accepted=False, reason=validation.reason)

        self._arbiter.start_motion(piece, from_pos, to_pos, state.current_time)
        return MoveResult(is_accepted=True, reason="ok")


    def request_jump(self, state: GameState, pos: Position) -> MoveResult:
        if state.game_over:
            return MoveResult(is_accepted=False, reason="game_over")

        piece = state.board.get_piece(pos)
        if piece is None:
            return MoveResult(is_accepted=False, reason="empty_source")

        if self._arbiter.is_on_cooldown(piece, state.current_time):
            return MoveResult(is_accepted=False, reason="on_cooldown")

        if self._arbiter.has_active_motion_for_piece(piece):
            return MoveResult(is_accepted=False, reason="piece_in_motion")

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

    def _piece_motion_info(self, piece, state: GameState, motion_by_piece):
        """Return (pixel_x, pixel_y, motion_progress, is_jumping) for a piece."""
        m = motion_by_piece.get(piece)
        if m is not None:
            px, py = m.pixel_position(state.current_time, CELL_SIZE)
            return px, py, m.progress(state.current_time), m.is_jump
        return None

    def _build_pieces(self, state: GameState, motion_by_piece) -> list[PieceSnapshot]:
        pieces: list[PieceSnapshot] = []
        for row in range(state.board.rows):
            for col in range(state.board.cols):
                piece = state.board.get_piece(Position(row, col))
                if piece is None:
                    continue
                motion_info = self._piece_motion_info(piece, state, motion_by_piece)
                if motion_info is not None:
                    px, py, progress, is_jumping = motion_info
                else:
                    px, py = col * CELL_SIZE, row * CELL_SIZE
                    progress, is_jumping = 1.0, False

                if is_jumping:
                    visual_state = "jump"
                elif motion_info is not None:
                    visual_state = "moving"
                elif self._arbiter.is_on_cooldown(piece, state.current_time):
                    progress = self._arbiter.get_cooldown_progress(piece, state.current_time)
                    visual_state = "long_rest" if progress < 0.5 else "short_rest"
                else:
                    visual_state = piece.state.value

                pieces.append(PieceSnapshot(
                    kind=piece.kind,
                    color=piece.color.value,
                    pixel_x=px,
                    pixel_y=py,
                    state=visual_state,
                    motion_progress=progress,
                    is_jumping=is_jumping,
                ))
        return pieces


    def snapshot(self, state: GameState) -> GameSnapshot:
        motion_by_piece = self._active_motions_map()
        pieces = tuple(self._build_pieces(state, motion_by_piece))

        legal_moves = ()
        if state.selected is not None:
            piece = state.board.get_piece(state.selected)
            if piece is not None:
                legal_moves = tuple(self._rule_engine.legal_moves(state.board, state.selected))

        cooldowns = []
        for row in range(state.board.rows):
            for col in range(state.board.cols):
                piece = state.board.get_piece(Position(row, col))
                if piece is not None and self._arbiter.is_on_cooldown(piece, state.current_time):
                    progress = self._arbiter.get_cooldown_progress(piece, state.current_time)
                    cooldowns.append(CooldownInfo(col=col, row=row, progress=progress))

        return GameSnapshot(
            board_width=state.board.cols * CELL_SIZE,
            board_height=state.board.rows * CELL_SIZE,
            pieces=pieces,
            selected_cell=state.selected,
            game_over=state.game_over,
            current_time=state.current_time,
            legal_moves=legal_moves,
            cooldowns=tuple(cooldowns),
        )



