from models.piece import Piece


class King(Piece):

    @property
    def kind(self) -> str:
        return "king"
