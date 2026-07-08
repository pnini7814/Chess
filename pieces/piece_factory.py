from pieces.piece import Piece
from pieces.king import King
from pieces.queen import Queen
from pieces.rook import Rook
from pieces.bishop import Bishop
from pieces.knight import Knight
from pieces.pawn import Pawn


class PieceFactory:

    _registry: dict[str, type[Piece]] = {
        "K": King,
        "Q": Queen,
        "R": Rook,
        "B": Bishop,
        "N": Knight,
        "P": Pawn,
    }

    @classmethod
    def register(cls, symbol: str, piece_class: type[Piece]) -> None:
        cls._registry[symbol] = piece_class

    @classmethod
    def create(cls, color: str, symbol: str) -> Piece:
        piece_class = cls._registry.get(symbol)
        if piece_class is None:
            raise ValueError(f"Unknown piece type: {symbol}")
        return piece_class(color)

    @classmethod
    def from_token(cls, token: str) -> Piece:
        return cls.create(token[0], token[1])

    @classmethod
    def known_symbols(cls) -> set[str]:
        return set(cls._registry.keys())
