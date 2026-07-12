from models.piece import Piece


class Bishop(Piece):

    @property
    def kind(self) -> str:
        return "bishop"
