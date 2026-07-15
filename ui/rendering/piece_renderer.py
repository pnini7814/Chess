from __future__ import annotations
from pathlib import Path

from ui.config import GameConfig
from ui.img import Img
from view.renderer import PieceSnapshot


class PieceRenderer:
    def __init__(self, assets_root: Path | None = None, cell_size: int | None = None):
        self.assets_root = assets_root or self._default_assets_root()
        self.cell_size = cell_size or GameConfig().cell_pixel_size
        self._sprite_cache: dict[str, Img] = {}

    @staticmethod
    def _default_assets_root() -> Path:
        return Path(__file__).resolve().parents[2] / "temp_repo" / "CTD26" / "pieces1"

    def draw(self, canvas: Img, pieces: tuple[PieceSnapshot, ...]) -> None:
        for piece in pieces:
            sprite = self._load_sprite(piece.kind, piece.color)
            if sprite is None:
                continue
            sprite.draw_on(canvas, piece.pixel_x, piece.pixel_y)

    def _load_sprite(self, kind: str, color: str) -> Img | None:
        key = f"{kind}:{color}"
        if key in self._sprite_cache:
            return self._sprite_cache[key]

        asset_dir = self._sprite_directory(kind, color)
        sprite_file = self._find_idle_sprite(asset_dir)
        if sprite_file is None:
            return None

        sprite = Img().read(
            str(sprite_file),
            size=(self.cell_size, self.cell_size),
            keep_aspect=True,
        )
        self._sprite_cache[key] = sprite
        return sprite

    def _sprite_directory(self, kind: str, color: str) -> Path:
        kind_code = "N" if kind.lower() == "knight" else kind[0].upper()
        color_code = "W" if color.lower() == "white" else "B"
        return self.assets_root / f"{kind_code}{color_code}" / "states" / "idle"

    def _find_idle_sprite(self, directory: Path) -> Path | None:
        if not directory.exists() or not directory.is_dir():
            return None

        png_files = sorted(directory.rglob("*.png"))
        return png_files[0] if png_files else None