from models.piece import Piece


class Rook(Piece):

    @property
    def kind(self) -> str:
        return "rook"
