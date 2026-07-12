from models.piece import Piece, PieceColor
from models.position import Position
from models.king import King
from models.queen import Queen
from models.rook import Rook
from models.bishop import Bishop
from models.knight import Knight
from models.pawn import Pawn


_COLOR_MAP = {
    "w": PieceColor.WHITE,
    "b": PieceColor.BLACK,
}


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
    def create(cls, symbol: str, color: PieceColor, cell: Position, piece_id: str | None = None) -> Piece:
        piece_class = cls._registry.get(symbol)
        if piece_class is None:
            raise ValueError(f"Unknown piece symbol: {symbol}")
        return piece_class(color=color, cell=cell, piece_id=piece_id)

    @classmethod
    def from_token(cls, token: str, cell: Position, piece_id: str | None = None) -> Piece:
        color = _COLOR_MAP.get(token[0])
        if color is None or token[1] not in cls._registry:
            raise ValueError(f"Unknown token: {token}")
        return cls.create(token[1], color, cell, piece_id)

    @classmethod
    def known_symbols(cls) -> set[str]:
        return set(cls._registry.keys())
