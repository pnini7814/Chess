from ui.rendering.board_renderer import BoardRenderer


class BoardView:
    def __init__(self, board_renderer=None):
        self.board_renderer = board_renderer or BoardRenderer()

    def render(self):
        return self.board_renderer.render()