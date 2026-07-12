from view.renderer import Renderer, GameSnapshot, PieceSnapshot
from models.position import Position
from realtime.motion import CELL_SIZE


class ImageView(Renderer):

    def render(self, snapshot: GameSnapshot) -> None:
        self._draw_grid(snapshot.board_width, snapshot.board_height)
        for piece in snapshot.pieces:
            self._draw_piece(piece, snapshot.selected_cell)
        if snapshot.game_over:
            self._draw_game_over()

    def _draw_grid(self, width: int, height: int) -> None:
        pass  # drawing library call goes here

    def _draw_piece(self, piece: PieceSnapshot, selected_cell: Position | None) -> None:
        highlighted = (
            selected_cell is not None and
            piece.pixel_x // CELL_SIZE == selected_cell.col and
            piece.pixel_y // CELL_SIZE == selected_cell.row
        )
        pass  # drawing library call goes here

    def _draw_game_over(self) -> None:
        pass  # drawing library call goes here
