from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from PIL import Image


@dataclass
class TagResult:
    """一张图的标签结果，分数为 0~1 的置信度。标签已转为提示词写法（空格分隔）。"""

    general: dict[str, float] = field(default_factory=dict)
    characters: dict[str, float] = field(default_factory=dict)
    rating: dict[str, float] = field(default_factory=dict)

    @property
    def top_rating(self) -> str:
        if not self.rating:
            return "general"
        return max(self.rating, key=self.rating.get)


class Tagger(Protocol):
    def tag(self, image: Image.Image) -> TagResult: ...
