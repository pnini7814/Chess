from models.board import Board


class BoardPrinter:

    def print(self, board: Board) -> None:
        for row in range(board.rows):
            tokens = []
            for col in range(board.cols):
                from models.position import Position
                piece = board.get_piece(Position(row, col))
                tokens.append(str(piece) if piece is not None else ".")
            print(" ".join(tokens))
