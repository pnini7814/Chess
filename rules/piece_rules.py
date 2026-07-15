from abc import ABC, abstractmethod
from models.board import Board
from models.piece import Piece
from models.position import Position


class PieceRule(ABC):

    @abstractmethod
    def legal_destinations(self, board: Board, piece: Piece) -> set[Position]: ...

    def _slide(self, board: Board, piece: Piece, directions: list[tuple[int, int]]) -> set[Position]:
        destinations = set()
        for dr, dc in directions:
            row, col = piece.cell.row + dr, piece.cell.col + dc
            while True:
                pos = Position(row, col)
                if not board.is_within_bounds(pos):
                    break
                occupant = board.get_piece(pos)
                if occupant is not None:
                    if occupant.color != piece.color:
                        destinations.add(pos)
                    break
                destinations.add(pos)
                row += dr
                col += dc
        return destinations


class RookRule(PieceRule):

    def legal_destinations(self, board: Board, piece: Piece) -> set[Position]:
        return self._slide(board, piece, [(0, 1), (0, -1), (1, 0), (-1, 0)])


class BishopRule(PieceRule):

    def legal_destinations(self, board: Board, piece: Piece) -> set[Position]:
        return self._slide(board, piece, [(1, 1), (1, -1), (-1, 1), (-1, -1)])


class QueenRule(PieceRule):

    def legal_destinations(self, board: Board, piece: Piece) -> set[Position]:
        return self._slide(board, piece, [(0, 1), (0, -1), (1, 0), (-1, 0),
                                          (1, 1), (1, -1), (-1, 1), (-1, -1)])


class KnightRule(PieceRule):

    def legal_destinations(self, board: Board, piece: Piece) -> set[Position]:
        destinations = set()
        for dr, dc in [(2, 1), (2, -1), (-2, 1), (-2, -1),
                       (1, 2), (1, -2), (-1, 2), (-1, -2)]:
            pos = Position(piece.cell.row + dr, piece.cell.col + dc)
            if not board.is_within_bounds(pos):
                continue
            occupant = board.get_piece(pos)
            if occupant is None or occupant.color != piece.color:
                destinations.add(pos)
        return destinations


class KingRule(PieceRule):

    def legal_destinations(self, board: Board, piece: Piece) -> set[Position]:
        destinations = set()
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                pos = Position(piece.cell.row + dr, piece.cell.col + dc)
                if not board.is_within_bounds(pos):
                    continue
                occupant = board.get_piece(pos)
                if occupant is None or occupant.color != piece.color:
                    destinations.add(pos)
        return destinations

class PawnRule(PieceRule):

    def legal_destinations(self, board: Board, piece: Piece) -> set[Position]:
        from models.piece import PieceColor

        destinations = set()
        direction = -1 if piece.color == PieceColor.WHITE else 1
        row, col = piece.cell.row, piece.cell.col

        forward = Position(row + direction, col)
        if board.is_within_bounds(forward) and board.get_piece(forward) is None:
            destinations.add(forward)

            # double step from starting row
            start_row = 6 if piece.color == PieceColor.WHITE else 1
            two_steps = Position(row + 2 * direction, col)
            if row == start_row and board.is_within_bounds(two_steps) and board.get_piece(two_steps) is None:
                destinations.add(two_steps)

        for dc in [-1, 1]:
            capture = Position(row + direction, col + dc)
            if not board.is_within_bounds(capture):
                continue
            occupant = board.get_piece(capture)
            if occupant is not None and occupant.color != piece.color:
                destinations.add(capture)

        return destinations