import pytest

from pic2pic.style_card import PRESETS, StyleCard


@pytest.fixture
def card():
    return StyleCard(
        name="test",
        style=["watercolor (medium)", "pastel colors"],
        composition=["upper body"],
        subject=["cat ears"],
        count=["1girl"],
        description="Soft light from the left.",
    )


def test_prompt_order_and_quality(card):
    prompt = card.to_prompt("illustrious")
    assert prompt.startswith("masterpiece, best quality")
    assert prompt.index("1girl") < prompt.index("cat ears") < prompt.index("upper body")
    assert r"watercolor \(medium\)" in prompt


def test_subject_replacement_keeps_style(card):
    prompt = card.to_prompt("noobai", subject=["dog ears", "maid"])
    assert "cat ears" not in prompt
    assert "dog ears, maid" in prompt
    assert "pastel colors" in prompt
    assert prompt.startswith("masterpiece, best quality, newest")


def test_animagine_rating_and_suffix(card):
    prompt = card.to_prompt("animagine")
    assert "rating: general" in prompt
    assert prompt.endswith("masterpiece, high score, great score, absurdres")


def test_description_optional(card):
    assert "Soft light" not in card.to_prompt()
    assert card.to_prompt(include_description=True).endswith("Soft light from the left.")


def test_all_presets_have_negative(card):
    for model in PRESETS:
        assert card.negative_prompt(model)


def test_json_roundtrip(card, tmp_path):
    path = card.save(tmp_path / "cards" / "test.json")
    assert StyleCard.load(path) == card
