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

    def start_jump(self, piece: Piece, pos: Position, current_time: int) -> None:
        # הוסר ה-import המקומי המיותר מכאן
        motion = Motion(
            piece=piece, 
            from_pos=pos, 
            to_pos=pos,
            start_time=current_time, 
            arrival_time=current_time + 1000,
            is_jump=True
        )
        self._active_motions.append(motion)

    def is_piece_in_motion(self, pos: Position) -> bool:
        return any(m.from_pos == pos and not m.is_jump for m in self._active_motions)

    def advance(self, current_time: int, board: Board) -> None:
        # כאן כבר נעשה שימוש מעולה ב-List Comprehension כפי שה-Linter ביקש
        arrived = [m for m in self._active_motions if current_time >= m.arrival_time]
        self._active_motions = [m for m in self._active_motions if current_time < m.arrival_time]
        
        for motion in arrived:
            self._resolve_arrival(motion, board)

    def _is_airborne_capture(self, arriving: Motion) -> bool:
        for jump in self._active_motions:
            if not jump.is_jump:
                continue
            if jump.from_pos != arriving.to_pos:
                continue
            if jump.piece.color != arriving.piece.color:
                return True
        return False

    def _resolve_arrival(self, motion: Motion, board: Board) -> None:
        if motion.is_jump:
            return

        if self._is_airborne_capture(motion):
            board.remove_piece(motion.from_pos)
            motion.piece.state = PieceState.IDLE
            return

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