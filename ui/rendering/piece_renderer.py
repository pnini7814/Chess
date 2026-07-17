from __future__ import annotations
import json
from pathlib import Path

from ui.config import GameConfig
from ui.img import Img
from view.renderer import PieceSnapshot

STATE_MAP = {
    "idle": "idle",
    "moving": "move",
    "jump": "jump",
    "short_rest": "short_rest",
    "long_rest": "long_rest",
}


class PieceRenderer:
    def __init__(self, assets_root: Path | None = None, cell_size: int | None = None):
        self.assets_root = assets_root or self._default_assets_root()
        self.cell_size = cell_size or GameConfig().cell_pixel_size
        self._cache: dict[str, tuple[list[Img], int]] = {}

    @staticmethod
    def _default_assets_root() -> Path:
        return Path(__file__).resolve().parents[1] / "assets (1)" / "assets" / "assets" / "pieces_mine"

    def draw(self, canvas: Img, pieces: tuple[PieceSnapshot, ...], current_time: int) -> None:
        for piece in pieces:
            sprite = self._get_frame(piece, current_time)
            if sprite is None:
                continue
            sprite.draw_on(canvas, piece.pixel_x, piece.pixel_y)

    def _get_frame(self, piece: PieceSnapshot, current_time: int) -> Img | None:
        state = STATE_MAP.get(piece.state, "idle")
        key = f"{piece.kind}:{piece.color}:{state}"

        if key not in self._cache:
            frames, fps = self._load_state(piece.kind, piece.color, state)
            if not frames:
                return None
            self._cache[key] = (frames, fps)

        frames, fps = self._cache[key]
        frame_index = (current_time // (1000 // fps)) % len(frames)
        return frames[frame_index]

    def _load_state(self, kind: str, color: str, state: str) -> tuple[list[Img], int]:
        directory = self._piece_folder_name(kind, color)
        state_dir = self.assets_root / directory / "states" / state
        sprites_dir = state_dir / "sprites"
        config_path = state_dir / "config.json"

        if not sprites_dir.exists() or not config_path.exists():
            return [], 4

        fps = 4
        try:
            config = json.loads(config_path.read_text())
            fps = config["graphics"]["frames_per_sec"]
        except Exception:
            pass

        frames = []
        for png in sorted(sprites_dir.glob("*.png")):
            img = Img().read(str(png), size=(self.cell_size, self.cell_size), keep_aspect=True)
            frames.append(img)
        return frames, fps

    @staticmethod
    def _piece_folder_name(kind: str, color: str) -> str:
        kind_code = "N" if kind.lower() == "knight" else kind[0].upper()
        color_code = "w" if color.lower() == "white" else "b"
        return f"{color_code}{kind_code}"
