from ui.config import GameConfig
from ui.img import Img


class BoardRenderer:
    def __init__(self, config=None):
        self.config = config or GameConfig()

    def render(self) -> Img:
        width = self.config.board_width * self.config.cell_pixel_size
        height = self.config.board_height * self.config.cell_pixel_size

        light = (240, 217, 181, 255)
        dark = (181, 136, 99, 255)

        board = Img.new(width, height, color=light)

        for row in range(self.config.board_height):
            for col in range(self.config.board_width):
                x = col * self.config.cell_pixel_size
                y = row * self.config.cell_pixel_size

                color = dark if (row + col) % 2 == 0 else light
                cell = Img.new(self.config.cell_pixel_size, self.config.cell_pixel_size, color=color)
                cell.draw_on(board, x, y)

        return board