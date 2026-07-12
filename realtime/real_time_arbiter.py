from models.board import Board
from models.piece import Piece, PieceState
from models.position import Position
from realtime.motion import Motion


class KingCapturedError(Exception):
    pass


class RealTimeArbiter:

    def __init__(self) -> None:
        self._active_motions: list[Motion] = []

    def has_active_motion(self) -> bool:
        return len(self._active_motions) > 0

    def start_motion(self, piece: Piece, from_pos: Position, to_pos: Position, current_time: int) -> None:
        motion = Motion.create(piece, from_pos, to_pos, current_time)
        piece.state = PieceState.MOVING
        self._active_motions.append(motion)

    def advance(self, current_time: int, board: Board) -> None:
        remaining = []
        for motion in self._active_motions:
            if current_time >= motion.arrival_time:
                self._resolve_arrival(motion, board)
            else:
                remaining.append(motion)
        self._active_motions = remaining

    def _resolve_arrival(self, motion: Motion, board: Board) -> None:
        board.remove_piece(motion.from_pos)

        target = board.get_piece(motion.to_pos)
        if target is not None:
            board.remove_piece(motion.to_pos)
            target.state = PieceState.CAPTURED
            if target.kind == "king":
                motion.piece.state = PieceState.IDLE
                motion.piece.cell = motion.to_pos
                board.add_piece(motion.piece)
                raise KingCapturedError(f"{target.color.value} king was captured")

        motion.piece.cell = motion.to_pos
        board.add_piece(motion.piece)
        motion.piece.state = PieceState.IDLE
