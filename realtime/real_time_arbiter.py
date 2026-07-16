from __future__ import annotations
from models.board import Board
from models.piece import Piece
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
        self._active_motions.append(motion)

    def advance(self, current_time: int, board: Board) -> None:
        motions = list(self._active_motions)
        arrived = [m for m in motions if current_time >= m.arrival_time]
        self._active_motions = [m for m in motions if current_time < m.arrival_time]

        for motion in arrived:
            self._resolve_arrival(motion, board)

    def _resolve_arrival(self, motion: Motion, board: Board) -> None:
        """
        Atomic arrival resolution:
        1. Remove piece from source
        2. Capture enemy at destination (if any)
        3. Place piece at destination
        4. Report king capture if applicable
        """
        # 1. Remove from source
        if board.get_piece(motion.from_pos) == motion.piece:
            board.remove_piece(motion.from_pos)

        # 2. Handle capture and place
        target = board.get_piece(motion.to_pos)
        if target is not None and target.color != motion.piece.color:
            board.remove_piece(motion.to_pos)
            
            # Place moving piece
            motion.piece.cell = motion.to_pos
            board.add_piece(motion.piece)
            
            # 4. Report king capture
            if target.kind == "king":
                raise KingCapturedError(f"{target.color.value} king was captured")
        else:
            # 3. No capture, just place
            motion.piece.cell = motion.to_pos
            board.add_piece(motion.piece)

    def get_active_motions(self) -> list[Motion]:
        return list(self._active_motions)