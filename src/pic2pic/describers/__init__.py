from typing import Protocol

from PIL import Image

from .qwen_vl import QwenVLDescriber


class Describer(Protocol):
    def describe(self, image: Image.Image) -> str: ...


__all__ = ["Describer", "QwenVLDescriber"]
