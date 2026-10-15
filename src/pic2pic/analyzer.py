"""从一张或多张参考图生成风格卡。

多张图时按标签出现比例筛选：同一画师/同一风格的图里反复出现的标签才算风格，
只在一两张里出现的多半是那张图的内容。
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from pathlib import Path

from PIL import Image

from .describers import Describer
from .style_card import StyleCard
from .taggers.base import Tagger, TagResult
from .tags import categorize


def aggregate(
    results: list[TagResult],
    min_consistency: float = 0.5,
    max_subject_tags: int = 20,
) -> StyleCard:
    """把多张图的标签合并成一张风格卡（不含描述和来源）。"""
    if not results:
        raise ValueError("至少需要一张图")
    n = len(results)
    general = Counter(tag for r in results for tag in r.general)
    scores: dict[str, float] = {}
    for r in results:
        for tag, score in r.general.items():
            scores[tag] = scores.get(tag, 0.0) + score / n

    consistency = {tag: count / n for tag, count in general.items()}
    kept = [t for t in general if consistency[t] >= min_consistency]
    # 出现比例高的在前，比例相同按平均置信度
    kept.sort(key=lambda t: (-consistency[t], -scores[t]))
    groups = categorize(kept)

    characters = Counter(tag for r in results for tag in r.characters)
    ratings = Counter(r.top_rating for r in results)

    return StyleCard(
        style=groups["style"],
        composition=groups["composition"],
        subject=groups["subject"][:max_subject_tags],
        count=groups["count"],
        characters=[t for t, c in characters.items() if c / n >= min_consistency],
        rating=ratings.most_common(1)[0][0],
        consistency={t: round(consistency[t], 3) for t in kept},
    )


def analyze_images(
    images: Iterable[str | Path | Image.Image],
    tagger: Tagger,
    describer: Describer | None = None,
    name: str = "untitled",
    min_consistency: float = 0.5,
) -> StyleCard:
    loaded: list[Image.Image] = []
    sources: list[str] = []
    for item in images:
        if isinstance(item, Image.Image):
            loaded.append(item)
            sources.append(getattr(item, "filename", "") or "<memory>")
        else:
            with Image.open(item) as im:
                im.load()
                loaded.append(im.copy())
            sources.append(str(item))

    card = aggregate([tagger.tag(im) for im in loaded], min_consistency=min_consistency)
    card.name = name
    card.source_images = sources
    if describer is not None:
        # 第一阶段只描述第一张，多图描述的合并留到后续阶段
        card.description = describer.describe(loaded[0])
    return card
