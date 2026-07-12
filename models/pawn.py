from models.piece import Piece


class Pawn(Piece):

    @property
    def kind(self) -> str:
        return "pawn"
