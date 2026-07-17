from __future__ import annotations
from models.board import Board
from models.piece import Piece, PieceColor
from models.position import Position
from models.queen import Queen
from realtime.motion import Motion
from realtime.real_time_arbiter import RealTimeArbiter, KingCapturedError
from realtime.real_time_arbiter import RealTimeArbiter, KingCapturedError, COOLDOWN_MS



class KungFuArbiter(RealTimeArbiter):
    """
    Extended arbiter with extra features (Iteration 10):
    - Jump movements
    - Pawn promotion
    - Airborne capture collision
    
    This class extends RealTimeArbiter to add kung fu chess specific rules
    without polluting the common route implementation.
    """

    def start_jump(self, piece: Piece, pos: Position, current_time: int) -> None:
        """Start a jump motion (EXTRA FEATURE - Iteration 10)"""
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
        """Check if piece at position is in motion (EXTRA FEATURE - Iteration 10)"""
        return any(m.from_pos == pos and not m.is_jump for m in self._active_motions)

    def has_active_non_jump_motion(self) -> bool:
        """Check if there's active regular motion (EXTRA FEATURE - Iteration 10)"""
        return any(not m.is_jump for m in self._active_motions)

    def advance(self, current_time: int, board: Board) -> None:
        """Override to handle both regular and jump motions"""
        motions = list(self._active_motions)
        arrived = [m for m in motions if current_time >= m.arrival_time]
        self._active_motions = [m for m in motions if current_time < m.arrival_time]

        # Process regular motions first, then jumps
        # This ensures enemy reaches physically to square before king lands
        arrived.sort(key=lambda m: m.is_jump)

        for motion in arrived:
            if motion.is_jump:
                self._resolve_jump_arrival(motion, board, arrived)
            else:
                self._resolve_regular_arrival_with_airborne(motion, board, arrived)

    def _resolve_jump_arrival(self, motion: Motion, board: Board, arrived_in_tick: list[Motion]) -> None:
        """Handle jump arrival (EXTRA FEATURE - Iteration 10)"""
        target = board.get_piece(motion.to_pos)
        
        if target is not None and target.color != motion.piece.color:
            board.remove_piece(motion.to_pos)
            motion.piece.cell = motion.to_pos
            board.add_piece(motion.piece)
            
            if target.kind == "king":
                raise KingCapturedError(f"{target.color.value} king was captured")
        self._cooldowns[motion.piece.id] = motion.arrival_time + COOLDOWN_MS

        

    def _resolve_regular_arrival_with_airborne(self, motion: Motion, board: Board, arrived_in_tick: list[Motion]) -> None:
        """
        Handle regular arrival with airborne collision check (EXTRA FEATURE - Iteration 10)
        If enemy jumped to same destination in this tick, capture the moving piece
        """
        # Check for airborne enemy
        airborne_enemy = None
        
        # Check 1: Arrived in this tick
        for other in arrived_in_tick:
            if other.is_jump and other.to_pos == motion.to_pos and other.piece.color != motion.piece.color:
                airborne_enemy = other.piece
                break
                
        # Check 2: Still in air, arriving in future
        if airborne_enemy is None:
            for active in self._active_motions:
                if active.is_jump and active.to_pos == motion.to_pos and active.piece.color != motion.piece.color:
                    airborne_enemy = active.piece
                    break

        if airborne_enemy is not None:
            # Airborne collision - moving piece gets captured
            if board.get_piece(motion.from_pos) == motion.piece:
                board.remove_piece(motion.from_pos)
            
            if board.get_piece(motion.to_pos) == airborne_enemy:
                board.remove_piece(motion.to_pos)
                
            airborne_enemy.cell = motion.to_pos
            board.add_piece(airborne_enemy)
            
            if motion.piece.kind == "king":
                raise KingCapturedError(f"{motion.piece.color.value} king was captured")
            return

        # Regular arrival with promotion support
        if board.get_piece(motion.from_pos) == motion.piece:
            board.remove_piece(motion.from_pos)

        target = board.get_piece(motion.to_pos)
        if target is not None and target.color != motion.piece.color:
            board.remove_piece(motion.to_pos)
            
            if target.kind == "king":
                # Handle promotion before raising
                if self._should_promote(motion.piece, motion.to_pos, board):
                    promoted = Queen(color=motion.piece.color, cell=motion.to_pos, piece_id=motion.piece.id)
                    board.add_piece(promoted)
                else:
                    motion.piece.cell = motion.to_pos
                    board.add_piece(motion.piece)
                raise KingCapturedError(f"{target.color.value} king was captured")

        # Handle promotion
        if self._should_promote(motion.piece, motion.to_pos, board):
            promoted = Queen(color=motion.piece.color, cell=motion.to_pos, piece_id=motion.piece.id)
            board.add_piece(promoted)
        else:
            motion.piece.cell = motion.to_pos
            board.add_piece(motion.piece)
        self._cooldowns[motion.piece.id] = motion.arrival_time + COOLDOWN_MS


    def _should_promote(self, piece: Piece, to_pos: Position, board: Board) -> bool:
        """Check if pawn should be promoted (EXTRA FEATURE - Iteration 10)"""
        if piece.kind != "pawn":
            return False
        if piece.color == PieceColor.WHITE and to_pos.row == 0:
            return True
        if piece.color == PieceColor.BLACK and to_pos.row == board.rows - 1:
            return True
        return False