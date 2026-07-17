from __future__ import annotations
from models.board import Board
from models.piece import Piece
from models.position import Position
from realtime.motion import Motion

COOLDOWN_MS = 2000

class KingCapturedError(Exception):
    pass


class RealTimeArbiter:

    def __init__(self) -> None:
        self._active_motions: list[Motion] = []
        self._cooldowns: dict[str, int] = {}

    def has_active_motion(self) -> bool:
        return len(self._active_motions) > 0

    def has_active_motion_for_piece(self, piece: Piece) -> bool:
        return any(m.piece is piece for m in self._active_motions)
    
    def is_on_cooldown(self, piece: Piece, current_time: int) -> bool:
        return self._cooldowns.get(piece.id, 0) > current_time

    def get_cooldown_progress(self, piece: Piece, current_time: int) -> float:
        end = self._cooldowns.get(piece.id, 0)
        if end <= current_time:
            return 1.0
        return 1.0 - (end - current_time) / COOLDOWN_MS


    def start_motion(self, piece: Piece, from_pos: Position, to_pos: Position, current_time: int) -> None:
        motion = Motion.create(piece, from_pos, to_pos, current_time)
        self._active_motions.append(motion)

    def advance(self, current_time: int, board: Board) -> None:
        motions = list(self._active_motions)
        arrived = [m for m in motions if current_time >= m.arrival_time]
        self._active_motions = [m for m in motions if current_time < m.arrival_time]

        for motion in arrived:
            self._resolve_arrival(motion, board)

    def _resolve_arrival(self, motion: Motion, board: Board) -> None:
        if board.get_piece(motion.from_pos) == motion.piece:
            board.remove_piece(motion.from_pos)

        target = board.get_piece(motion.to_pos)
        if target is not None and target.color != motion.piece.color:
            board.remove_piece(motion.to_pos)
            motion.piece.cell = motion.to_pos
            board.add_piece(motion.piece)
            if target.kind == "king":
                raise KingCapturedError(f"{target.color.value} king was captured")
        else:
            motion.piece.cell = motion.to_pos
            board.add_piece(motion.piece)

        self._cooldowns[motion.piece.id] = motion.arrival_time + COOLDOWN_MS

    def get_active_motions(self) -> list[Motion]:
        return list(self._active_motions)