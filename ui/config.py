"""Game configuration."""
from dataclasses import dataclass


@dataclass
class GameConfig:
    """UI configuration."""
    cell_pixel_size: int = 75  # pixels per square
    board_width: int = 8
    board_height: int = 8