from models.piece import Piece


class Knight(Piece):

    @property
    def kind(self) -> str:
        return "knight"
