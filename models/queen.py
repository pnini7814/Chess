from models.piece import Piece


class Queen(Piece):

    @property
    def kind(self) -> str:
        return "queen"
