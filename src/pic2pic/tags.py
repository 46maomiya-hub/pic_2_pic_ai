"""Danbooru 标签的分类与格式化。

风格卡把标签拆成「风格 / 构图 / 主体」三块，这样换主体时可以只保留风格块和构图块。
分类基于关键词表，宁可把不认识的标签归为主体，也不要把主体误当成风格。
"""

from __future__ import annotations

import re

# 画风、媒介、上色、光影、色调相关
STYLE_TAGS = {
    "anime coloring",
    "flat color",
    "cel shading",
    "gradient",
    "watercolor (medium)",
    "traditional media",
    "oil painting (medium)",
    "acrylic paint (medium)",
    "sketch",
    "lineart",
    "monochrome",
    "greyscale",
    "limited palette",
    "pastel colors",
    "muted colors",
    "vivid colors",
    "colorful",
    "high contrast",
    "realistic",
    "photorealistic",
    "3d",
    "pixel art",
    "chibi",
    "retro artstyle",
    "1980s (style)",
    "1990s (style)",
    "2000s (style)",
    "official art",
    "game cg",
    "cover",
    "illustration",
    "painterly",
    "impasto",
    "chromatic aberration",
    "film grain",
    "bloom",
    "lens flare",
    "backlighting",
    "rim lighting",
    "soft lighting",
    "dramatic lighting",
    "light particles",
    "light rays",
    "sunlight",
    "dappled sunlight",
    "glowing",
    "depth of field",
    "blurry background",
    "bokeh",
    "motion blur",
    "halftone",
    "screentone",
    "manga",
    "comic",
    "ukiyo-e",
    "spot color",
    "partially colored",
    "no lineart",
    "thick lineart",
    "sepia",
    "blue theme",
    "red theme",
    "green theme",
    "purple theme",
    "pink theme",
    "orange theme",
    "yellow theme",
    "black theme",
    "white theme",
    "dark",
    "simple background",
    "white background",
    "abstract background",
    "gradient background",
}

STYLE_PATTERNS = [
    re.compile(r"\(medium\)$"),
    re.compile(r"\(style\)$"),
    re.compile(r" theme$"),
    re.compile(r" lighting$"),
    re.compile(r"^(soft|hard|thick|thin|bold) (lines|lineart|outline)$"),
]

# 镜头、取景、角度、姿态朝向
COMPOSITION_TAGS = {
    "portrait",
    "close-up",
    "upper body",
    "cowboy shot",
    "full body",
    "lower body",
    "feet out of frame",
    "head out of frame",
    "from above",
    "from below",
    "from side",
    "from behind",
    "dutch angle",
    "pov",
    "wide shot",
    "very wide shot",
    "profile",
    "three quarter view",
    "looking at viewer",
    "looking away",
    "looking back",
    "looking up",
    "looking down",
    "facing viewer",
    "straight-on",
    "symmetry",
    "centered",
    "split screen",
    "multiple views",
    "fisheye",
    "panorama",
    "silhouette",
    "foreshortening",
    "perspective",
    "vanishing point",
    "negative space",
    "border",
    "letterboxed",
    "framed",
    "rule of thirds",
    "out of frame",
    "solo focus",
}

COUNT_PATTERN = re.compile(r"^(\d\+?|multiple|no) ?(girls?|boys?|others?|humans?)$|^solo$")

# WD14 标签里的颜文字保留下划线
KAOMOJI = {
    "0_0",
    "(o)_(o)",
    "+_+",
    "+_-",
    "._.",
    "<o>_<o>",
    "<|>_<|>",
    "=_=",
    ">_<",
    "3_3",
    "6_9",
    ">_o",
    "@_@",
    "^_^",
    "o_o",
    "u_u",
    "x_x",
    "|_|",
    "||_||",
}


def normalize(tag: str) -> str:
    """把 WD14 的下划线标签转成提示词里的写法。"""
    tag = tag.strip()
    if tag in KAOMOJI:
        return tag
    return tag.replace("_", " ")


def is_style(tag: str) -> bool:
    return tag in STYLE_TAGS or any(p.search(tag) for p in STYLE_PATTERNS)


def is_composition(tag: str) -> bool:
    return tag in COMPOSITION_TAGS


def is_count(tag: str) -> bool:
    return bool(COUNT_PATTERN.match(tag))


def categorize(tags: list[str]) -> dict[str, list[str]]:
    """把通用标签分成 count / style / composition / subject 四组，保持原顺序。"""
    groups: dict[str, list[str]] = {"count": [], "style": [], "composition": [], "subject": []}
    for tag in tags:
        if is_count(tag):
            groups["count"].append(tag)
        elif is_style(tag):
            groups["style"].append(tag)
        elif is_composition(tag):
            groups["composition"].append(tag)
        else:
            groups["subject"].append(tag)
    return groups


def escape_parens(tag: str) -> str:
    """SD 系 WebUI / ComfyUI 把括号当权重语法，标签里的括号需要转义。"""
    return tag.replace("(", r"\(").replace(")", r"\)")
