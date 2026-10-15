import numpy as np
import pytest

from pic2pic.taggers.wd14 import WD14Tagger


class FakeInput:
    name = "input"
    shape = (1, 448, 448, 3)


class FakeSession:
    def __init__(self, probs):
        self.probs = np.array([probs], dtype=np.float32)
        self.seen = None

    def get_inputs(self):
        return [FakeInput()]

    def run(self, outputs, feeds):
        self.seen = feeds["input"]
        return [self.probs]


@pytest.fixture
def tagger():
    t = WD14Tagger()
    t._labels = [
        ("general", 9),
        ("sensitive", 9),
        ("1girl", 0),
        ("looking_at_viewer", 0),
        ("hat", 0),
        ("hatsune_miku", 4),
    ]
    t._session = FakeSession([0.7, 0.3, 0.95, 0.5, 0.1, 0.9])
    return t


def test_preprocess_pads_to_square_bgr(tagger, make_image):
    arr = tagger.preprocess(make_image(size=(100, 50), color=(255, 0, 0)))
    assert arr.shape == (1, 448, 448, 3)
    assert arr.dtype == np.float32
    center = arr[0, 224, 224]
    assert list(center) == [0.0, 0.0, 255.0]  # 红色在 BGR 里是最后一个通道
    assert list(arr[0, 0, 224]) == [255.0, 255.0, 255.0]  # 上方白边


def test_tag_thresholds(tagger, make_image):
    result = tagger.tag(make_image())
    assert result.general == {"1girl": pytest.approx(0.95), "looking at viewer": pytest.approx(0.5)}
    assert result.characters == {"hatsune miku": pytest.approx(0.9)}
    assert result.top_rating == "general"
