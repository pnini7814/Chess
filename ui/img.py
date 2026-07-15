import cv2
import numpy as np
from pathlib import Path

class Img:
    def __init__(self, img=None):
        self.img = img

    def read(self, path, size=None, keep_aspect=True):
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Could not load image: {path}")

        img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
        if img is None:
            data = path.read_bytes()
            img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_UNCHANGED)

        if img is None:
            raise FileNotFoundError(f"Could not load image: {path}")

        if size is not None:
            if keep_aspect:
                h, w = img.shape[:2]
                target_w, target_h = size
                scale = min(target_w / w, target_h / h)
                new_w = max(1, int(w * scale))
                new_h = max(1, int(h * scale))
                img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
            else:
                img = cv2.resize(img, size, interpolation=cv2.INTER_AREA)

        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGRA)
        elif img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

        self.img = img
        return self

    def draw_on(self, other, x, y):
        if self.img is None:
            raise ValueError("Source image is empty")

        if other.img is None:
            raise ValueError("Target image is empty")

        src = self.img
        dst = other.img

        if src.shape[2] != dst.shape[2]:
            if dst.shape[2] == 4:
                src = cv2.cvtColor(src, cv2.COLOR_BGR2BGRA)
            else:
                src = cv2.cvtColor(src, cv2.COLOR_BGRA2BGR)

        h, w = src.shape[:2]
        x2 = x + w
        y2 = y + h

        if x2 > dst.shape[1] or y2 > dst.shape[0]:
            raise ValueError("Image does not fit into target area")

        if src.shape[2] == 4 and dst.shape[2] == 4:
            alpha = src[:, :, 3] / 255.0
            for c in range(3):
                dst[y:y + h, x:x + w, c] = (
                    alpha * src[:, :, c] + (1 - alpha) * dst[y:y + h, x:x + w, c]
                ).astype(np.uint8)
            return other

        dst[y:y + h, x:x + w] = src
        return other

    def put_text(self, text, x, y, font_scale=1.0, color=(0, 0, 0, 255), thickness=2):
        if self.img is None:
            raise ValueError("Image is empty")

        if self.img.shape[2] == 4:
            bgr_color = color[:3][::-1]
        else:
            bgr_color = color[:3][::-1]

        cv2.putText(
            self.img,
            text,
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            bgr_color,
            thickness,
            cv2.LINE_AA,
        )
        return self

    def draw_rect(self, x1, y1, x2, y2, color=(255, 0, 0, 255), thickness=2):
        if self.img is None:
            raise ValueError("Image is empty")

        bgr_color = color[:3][::-1]
        cv2.rectangle(self.img, (x1, y1), (x2, y2), bgr_color, thickness)
        return self

    def draw_circle(self, x, y, radius, color=(255, 0, 0, 255), thickness=2):
        if self.img is None:
            raise ValueError("Image is empty")

        bgr_color = color[:3][::-1]
        cv2.circle(self.img, (x, y), radius, bgr_color, thickness)
        return self

    @staticmethod
    def new(width, height, color=(255, 255, 255, 255)):
        if len(color) == 4:
            img = np.full((height, width, 4), color, dtype=np.uint8)
        else:
            img = np.full((height, width, 3), color, dtype=np.uint8)
        return Img(img)

    def save(self, path):
        if self.img is None:
            raise ValueError("Image is empty")
        cv2.imwrite(path, self.img)
        return self

    def show(self, title="img"):
        if self.img is None:
            raise ValueError("Image is empty")
        cv2.imshow(title, self.img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return self