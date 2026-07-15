from ui.img import Img
from ui.rendering.board_renderer import BoardRenderer
from ui.rendering.piece_renderer import PieceRenderer
from view.renderer import GameSnapshot
from realtime.motion import CELL_SIZE


class BoardView:
    def __init__(self, board_renderer=None, piece_renderer=None):
        self.board_renderer = board_renderer or BoardRenderer()
        self.piece_renderer = piece_renderer or PieceRenderer()

    def render(self, snapshot: GameSnapshot) -> Img:
        frame = self.board_renderer.render()
        self.piece_renderer.draw(frame, snapshot.pieces)
        self._draw_selection(frame, snapshot)
        if snapshot.game_over:
            self._draw_game_over(frame)
        return frame

    def _draw_selection(self, frame: Img, snapshot: GameSnapshot) -> None:
        selected = snapshot.selected_cell
        if selected is None:
            return

        x1 = selected.col * CELL_SIZE
        y1 = selected.row * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        frame.draw_rect(x1 + 4, y1 + 4, x2 - 4, y2 - 4, color=(0, 255, 0, 255), thickness=4)

    def _draw_game_over(self, frame: Img) -> None:
        text = "GAME OVER"
        x = frame.img.shape[1] // 2 - 180
        y = frame.img.shape[0] // 2
        frame.put_text(text, x, y, font_scale=2.0, color=(0, 0, 255, 255), thickness=5)