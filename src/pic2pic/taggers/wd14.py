"""WD14 标签器（SmilingWolf 系列 ONNX 模型）。

模型和标签表首次使用时从 Hugging Face 下载并缓存。默认用 EVA02-Large v3，
在 16GB 显卡上很轻松；装了 onnxruntime-gpu 会自动用 CUDA，否则用 CPU。
"""

from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image

from ..tags import normalize
from .base import TagResult

DEFAULT_REPO = "SmilingWolf/wd-eva02-large-tagger-v3"

# selected_tags.csv 的 category 列
CATEGORY_GENERAL = 0
CATEGORY_CHARACTER = 4
CATEGORY_RATING = 9


class WD14Tagger:
    def __init__(
        self,
        repo_id: str = DEFAULT_REPO,
        general_threshold: float = 0.35,
        character_threshold: float = 0.85,
        model_dir: str | Path | None = None,
    ) -> None:
        self.repo_id = repo_id
        self.general_threshold = general_threshold
        self.character_threshold = character_threshold
        self.model_dir = Path(model_dir) if model_dir else None
        self._session = None
        self._labels: list[tuple[str, int]] = []
        self._size = 448

    def _files(self) -> tuple[Path, Path]:
        if self.model_dir:
            return self.model_dir / "model.onnx", self.model_dir / "selected_tags.csv"
        from huggingface_hub import hf_hub_download

        model = hf_hub_download(self.repo_id, "model.onnx")
        labels = hf_hub_download(self.repo_id, "selected_tags.csv")
        return Path(model), Path(labels)

    def load(self) -> None:
        if self._session is not None:
            return
        import onnxruntime as ort

        model_path, labels_path = self._files()
        with open(labels_path, newline="", encoding="utf-8") as f:
            self._labels = [(row["name"], int(row["category"])) for row in csv.DictReader(f)]
        available = ort.get_available_providers()
        providers = [p for p in ("CUDAExecutionProvider", "CPUExecutionProvider") if p in available]
        self._session = ort.InferenceSession(str(model_path), providers=providers)
        # 输入形状为 [batch, height, width, 3]
        self._size = int(self._session.get_inputs()[0].shape[1])

    def preprocess(self, image: Image.Image):
        import numpy as np

        image = image.convert("RGBA")
        canvas = Image.new("RGBA", image.size, (255, 255, 255, 255))
        canvas.alpha_composite(image)
        image = canvas.convert("RGB")
        # 白边补成正方形，再缩放到模型输入尺寸
        side = max(image.size)
        square = Image.new("RGB", (side, side), (255, 255, 255))
        square.paste(image, ((side - image.width) // 2, (side - image.height) // 2))
        square = square.resize((self._size, self._size), Image.BICUBIC)
        array = np.asarray(square, dtype=np.float32)[:, :, ::-1]  # RGB -> BGR
        return np.ascontiguousarray(array)[None, ...]

    def tag(self, image: Image.Image) -> TagResult:
        self.load()
        inputs = self.preprocess(image)
        input_name = self._session.get_inputs()[0].name
        probs = self._session.run(None, {input_name: inputs})[0][0]
        result = TagResult()
        for (name, category), score in zip(self._labels, probs, strict=True):
            score = float(score)
            tag = normalize(name)
            if category == CATEGORY_RATING:
                result.rating[tag] = score
            elif category == CATEGORY_CHARACTER and score >= self.character_threshold:
                result.characters[tag] = score
            elif category == CATEGORY_GENERAL and score >= self.general_threshold:
                result.general[tag] = score
        result.general = dict(sorted(result.general.items(), key=lambda kv: -kv[1]))
        return result
