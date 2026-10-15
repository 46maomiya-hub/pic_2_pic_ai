"""pic2pic：学习二次元图片风格，反推结构化提示词。"""

from .analyzer import aggregate, analyze_images
from .style_card import PRESETS, StyleCard

__all__ = ["PRESETS", "StyleCard", "aggregate", "analyze_images"]
__version__ = "0.1.0"
