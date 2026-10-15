import pytest
from PIL import Image

from pic2pic.taggers.base import TagResult


class FakeTagger:
    """按顺序返回预设结果，不加载任何模型。"""

    def __init__(self, results):
        self.results = list(results)
        self.calls = 0

    def tag(self, image):
        result = self.results[self.calls % len(self.results)]
        self.calls += 1
        return result


@pytest.fixture
def make_image():
    def _make(size=(64, 32), color=(200, 100, 50)):
        return Image.new("RGB", size, color)

    return _make


@pytest.fixture
def fake_results():
    return [
        TagResult(
            general={
                "1girl": 0.99,
                "watercolor (medium)": 0.8,
                "upper body": 0.7,
                "cat ears": 0.9,
                "pastel colors": 0.6,
            },
            characters={},
            rating={"general": 0.9, "sensitive": 0.1},
        ),
        TagResult(
            general={
                "1girl": 0.98,
                "watercolor (medium)": 0.7,
                "upper body": 0.5,
                "school uniform": 0.8,
                "pastel colors": 0.65,
            },
            rating={"general": 0.8, "sensitive": 0.2},
        ),
    ]
