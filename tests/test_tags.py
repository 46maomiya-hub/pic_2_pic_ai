from pic2pic.tags import categorize, escape_parens, normalize


def test_normalize_keeps_kaomoji():
    assert normalize("looking_at_viewer") == "looking at viewer"
    assert normalize("^_^") == "^_^"


def test_categorize():
    groups = categorize(
        ["1girl", "watercolor (medium)", "from above", "cat ears", "blue theme", "solo"]
    )
    assert groups["count"] == ["1girl", "solo"]
    assert groups["style"] == ["watercolor (medium)", "blue theme"]
    assert groups["composition"] == ["from above"]
    assert groups["subject"] == ["cat ears"]


def test_escape_parens():
    assert escape_parens("watercolor (medium)") == r"watercolor \(medium\)"
