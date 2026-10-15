"""风格卡：一组参考图学到的风格，可保存为 JSON、渲染成目标模型的提示词。"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .tags import escape_parens


@dataclass(frozen=True)
class ModelPreset:
    """不同二次元底模对质量词和标签顺序的约定。"""

    name: str
    quality_prefix: list[str]
    quality_suffix: list[str]
    negative: str


PRESETS: dict[str, ModelPreset] = {
    "illustrious": ModelPreset(
        name="Illustrious XL",
        quality_prefix=["masterpiece", "best quality", "amazing quality"],
        quality_suffix=[],
        negative=(
            "worst quality, low quality, lowres, bad anatomy, bad hands, extra digits, "
            "jpeg artifacts, signature, watermark, username, blurry"
        ),
    ),
    "noobai": ModelPreset(
        name="NoobAI XL",
        quality_prefix=["masterpiece", "best quality", "newest", "absurdres", "highres"],
        quality_suffix=[],
        negative=(
            "worst quality, old, early, low quality, lowres, signature, username, logo, "
            "bad hands, mutated hands, mammal, anthro, furry"
        ),
    ),
    "animagine": ModelPreset(
        name="Animagine XL 4.0",
        quality_prefix=[],
        quality_suffix=["masterpiece", "high score", "great score", "absurdres"],
        negative=(
            "lowres, bad anatomy, bad hands, text, error, missing finger, extra digits, "
            "fewer digits, cropped, worst quality, low quality, low score, bad score, "
            "average score, signature, watermark, username, blurry"
        ),
    ),
}


@dataclass
class StyleCard:
    """一张风格卡。

    style / composition 是要迁移的部分；subject 是参考图里的具体内容，
    生成新图时通常替换成自己的主体。
    """

    name: str = "untitled"
    style: list[str] = field(default_factory=list)
    composition: list[str] = field(default_factory=list)
    subject: list[str] = field(default_factory=list)
    count: list[str] = field(default_factory=list)
    characters: list[str] = field(default_factory=list)
    rating: str = "general"
    description: str = ""
    source_images: list[str] = field(default_factory=list)
    # 标签 -> 在参考图中出现的比例（0~1），多图学习时用来判断风格是否稳定
    consistency: dict[str, float] = field(default_factory=dict)

    def to_prompt(
        self,
        model: str = "illustrious",
        subject: list[str] | None = None,
        include_characters: bool = False,
        include_description: bool = False,
    ) -> str:
        """渲染成正向提示词。

        subject 传入时替换参考图的主体，只保留风格和构图，这是「同风格新图」的用法。
        """
        preset = PRESETS[model]
        body: list[str] = []
        body += self.count
        if include_characters:
            body += self.characters
        if model == "animagine":
            body.append(f"rating: {self.rating}")
        body += self.subject if subject is None else subject
        body += self.composition
        body += self.style
        parts = preset.quality_prefix + [escape_parens(t) for t in _dedupe(body)]
        parts += preset.quality_suffix
        prompt = ", ".join(parts)
        if include_description and self.description:
            prompt = f"{prompt}. {self.description}"
        return prompt

    def negative_prompt(self, model: str = "illustrious") -> str:
        return PRESETS[model].negative

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, text: str) -> StyleCard:
        return cls(**json.loads(text))

    def save(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json(), encoding="utf-8")
        return path

    @classmethod
    def load(cls, path: str | Path) -> StyleCard:
        return cls.from_json(Path(path).read_text(encoding="utf-8"))


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out
