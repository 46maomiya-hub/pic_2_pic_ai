from pic2pic.cli import _expand, main
from pic2pic.style_card import StyleCard


def test_prompt_command(tmp_path, capsys):
    card = StyleCard(style=["flat color"], subject=["cat ears"], count=["1girl"])
    path = card.save(tmp_path / "c.json")
    assert main(["prompt", str(path), "--model", "noobai", "--subject", "dog ears, maid"]) == 0
    out = capsys.readouterr().out
    assert "dog ears, maid" in out and "cat ears" not in out
    assert "负向提示词" in out


def test_expand_dir(tmp_path, make_image):
    make_image().save(tmp_path / "b.png")
    make_image().save(tmp_path / "a.jpg")
    (tmp_path / "notes.txt").write_text("x")
    assert [p.name for p in _expand([str(tmp_path)])] == ["a.jpg", "b.png"]
