from dataclasses import dataclass
from models.board import Board
from models.piece import Piece, PieceColor
from models.position import Position
from rules.piece_rules import (
    PieceRule, RookRule, BishopRule, QueenRule, KnightRule, KingRule, PawnRule
)


@dataclass(frozen=True)
class MoveValidation:
    is_valid: bool
    reason: str


_RULE_MAP: dict[str, PieceRule] = {
    "rook": RookRule(),
    "bishop": BishopRule(),
    "queen": QueenRule(),
    "knight": KnightRule(),
    "king": KingRule(),
    "pawn": PawnRule(),
}


class RuleEngine:

    def validate(self, board: Board, from_pos: Position, to_pos: Position) -> MoveValidation:
        if not board.is_within_bounds(from_pos) or not board.is_within_bounds(to_pos):
            return MoveValidation(is_valid=False, reason="outside_board")

        piece = board.get_piece(from_pos)
        if piece is None:
            return MoveValidation(is_valid=False, reason="empty_source")

        target = board.get_piece(to_pos)
        if target is not None and target.color == piece.color:
            return MoveValidation(is_valid=False, reason="friendly_destination")

        rule = _RULE_MAP.get(piece.kind)
        if to_pos not in rule.legal_destinations(board, piece):
            return MoveValidation(is_valid=False, reason="illegal_piece_move")

        return MoveValidation(is_valid=True, reason="ok")
