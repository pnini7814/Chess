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
        self._draw_legal_moves(frame, snapshot)
        self._draw_cooldowns(frame, snapshot)
        self.piece_renderer.draw(frame, snapshot.pieces, snapshot.current_time)
        self._draw_selection(frame, snapshot)
        if snapshot.game_over:
            self._draw_game_over(frame)
        return frame

    def _draw_legal_moves(self, frame: Img, snapshot: GameSnapshot) -> None:
        import numpy as np
        for pos in snapshot.legal_moves:
            x = pos.col * CELL_SIZE
            y = pos.row * CELL_SIZE
            overlay = frame.img[y:y + CELL_SIZE, x:x + CELL_SIZE].copy()
            yellow = np.array([0, 220, 255, 255], dtype=np.uint8)
            frame.img[y:y + CELL_SIZE, x:x + CELL_SIZE] = (
                overlay * 0.5 + yellow * 0.5
            ).astype(np.uint8)


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

    def _draw_cooldowns(self, frame: Img, snapshot: GameSnapshot) -> None:
        import numpy as np
        for cd in snapshot.cooldowns:
            x = cd.col * CELL_SIZE
            y = cd.row * CELL_SIZE
            bar_height = int(CELL_SIZE * (1.0 - cd.progress))
            if bar_height <= 0:
                continue
            y_bar = y + CELL_SIZE - bar_height
            overlay = frame.img[y_bar:y_bar + bar_height, x:x + CELL_SIZE].copy()
            yellow = np.array([0, 220, 255, 255], dtype=np.uint8)
            frame.img[y_bar:y_bar + bar_height, x:x + CELL_SIZE] = (
                overlay * 0.4 + yellow * 0.6
            ).astype(np.uint8)

