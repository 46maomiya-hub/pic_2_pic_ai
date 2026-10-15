"""命令行入口。

pic2pic analyze a.png b.png --name my-style --model noobai --out cards/my-style.json
pic2pic prompt cards/my-style.json --subject "1girl, cat ears, school uniform"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .style_card import PRESETS, StyleCard

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


def _expand(paths: list[str]) -> list[Path]:
    """参数可以是图片文件，也可以是文件夹（取其中的图片）。"""
    out: list[Path] = []
    for p in map(Path, paths):
        if p.is_dir():
            out += sorted(f for f in p.iterdir() if f.suffix.lower() in IMAGE_SUFFIXES)
        else:
            out.append(p)
    return out


def _split_tags(text: str | None) -> list[str] | None:
    if text is None:
        return None
    return [t.strip() for t in text.split(",") if t.strip()]


def _print_prompts(card: StyleCard, model: str, subject: list[str] | None) -> None:
    print("正向提示词：")
    print(card.to_prompt(model, subject=subject, include_description=True))
    print()
    print("负向提示词：")
    print(card.negative_prompt(model))


def cmd_analyze(args: argparse.Namespace) -> int:
    from .analyzer import analyze_images
    from .taggers import WD14Tagger

    images = _expand(args.images)
    if not images:
        print("没有找到图片", file=sys.stderr)
        return 1
    tagger = WD14Tagger(repo_id=args.tagger_repo, general_threshold=args.threshold)
    describer = None
    if args.describe:
        from .describers import QwenVLDescriber

        describer = QwenVLDescriber(model_id=args.vlm)
    card = analyze_images(
        images, tagger, describer, name=args.name, min_consistency=args.min_consistency
    )
    if args.out:
        print(f"风格卡已保存：{card.save(args.out)}\n")
    _print_prompts(card, args.model, None)
    return 0


def cmd_prompt(args: argparse.Namespace) -> int:
    card = StyleCard.load(args.card)
    _print_prompts(card, args.model, _split_tags(args.subject))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pic2pic", description="二次元图片风格学习与提示词反推")
    sub = parser.add_subparsers(dest="command", required=True)

    a = sub.add_parser("analyze", help="分析参考图，生成风格卡和提示词")
    a.add_argument("images", nargs="+", help="图片文件或文件夹")
    a.add_argument("--name", default="untitled", help="风格卡名称")
    a.add_argument("--model", choices=sorted(PRESETS), default="illustrious", help="目标底模")
    a.add_argument("--out", help="风格卡 JSON 保存路径")
    a.add_argument("--threshold", type=float, default=0.35, help="WD14 通用标签阈值")
    a.add_argument(
        "--min-consistency", type=float, default=0.5, help="多图时标签至少出现在多少比例的图里"
    )
    a.add_argument("--tagger-repo", default="SmilingWolf/wd-eva02-large-tagger-v3")
    a.add_argument("--describe", action="store_true", help="用 Qwen-VL 补充一句描述")
    a.add_argument("--vlm", default="Qwen/Qwen2.5-VL-3B-Instruct")
    a.set_defaults(func=cmd_analyze)

    p = sub.add_parser("prompt", help="用已保存的风格卡生成提示词，可替换主体")
    p.add_argument("card", help="风格卡 JSON")
    p.add_argument("--model", choices=sorted(PRESETS), default="illustrious")
    p.add_argument("--subject", help="新主体标签，逗号分隔；不填则沿用参考图主体")
    p.set_defaults(func=cmd_prompt)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
