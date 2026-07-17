from pathlib import Path
from ui.config import GameConfig
from ui.img import Img


class BoardRenderer:
    def __init__(self, config=None):
        self.config = config or GameConfig()

    def render(self) -> Img:
        board_path = Path(__file__).resolve().parents[1] / "assets (1)" / "assets" / "assets" / "board.png"
        size = (
            self.config.board_width * self.config.cell_pixel_size,
            self.config.board_height * self.config.cell_pixel_size,
        )
        return Img().read(str(board_path), size=size, keep_aspect=False)
