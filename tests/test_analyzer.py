import pytest
from conftest import FakeTagger

from pic2pic.analyzer import aggregate, analyze_images


def test_single_image_keeps_everything(fake_results):
    card = aggregate(fake_results[:1])
    assert card.count == ["1girl"]
    assert set(card.style) == {"watercolor (medium)", "pastel colors"}
    assert card.composition == ["upper body"]
    assert card.subject == ["cat ears"]
    assert card.rating == "general"


def test_multi_image_filters_inconsistent_tags(fake_results):
    card = aggregate(fake_results, min_consistency=1.0)
    # 两张图都有的才保留：主体标签各出现一次，被过滤
    assert card.subject == []
    assert set(card.style) == {"watercolor (medium)", "pastel colors"}
    assert card.consistency["1girl"] == 1.0


def test_multi_image_low_threshold_keeps_subjects(fake_results):
    card = aggregate(fake_results, min_consistency=0.5)
    assert set(card.subject) == {"cat ears", "school uniform"}
    assert card.consistency["cat ears"] == 0.5


def test_empty_raises():
    with pytest.raises(ValueError):
        aggregate([])


class FakeDescriber:
    def describe(self, image):
        return "Warm backlight."


def test_analyze_images_from_paths(tmp_path, make_image, fake_results):
    paths = []
    for i in range(2):
        p = tmp_path / f"{i}.png"
        make_image().save(p)
        paths.append(p)
    tagger = FakeTagger(fake_results)
    card = analyze_images(paths, tagger, FakeDescriber(), name="demo")
    assert tagger.calls == 2
    assert card.name == "demo"
    assert card.source_images == [str(p) for p in paths]
    assert card.description == "Warm backlight."
