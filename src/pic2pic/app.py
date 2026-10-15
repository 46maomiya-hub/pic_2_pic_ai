"""Gradio 单页界面：上传参考图 → 风格卡 + 提示词。

python -m pic2pic.app
"""

from __future__ import annotations

from .style_card import PRESETS

_tagger = None
_describer = None


def _get_tagger():
    global _tagger
    if _tagger is None:
        from .taggers import WD14Tagger

        _tagger = WD14Tagger()
    return _tagger


def _get_describer():
    global _describer
    if _describer is None:
        from .describers import QwenVLDescriber

        _describer = QwenVLDescriber()
    return _describer


def run_analysis(files, name, model, subject, use_vlm, min_consistency):
    from .analyzer import analyze_images

    if not files:
        return "", "", "请先上传图片"
    paths = [getattr(f, "name", f) for f in files]
    describer = _get_describer() if use_vlm else None
    card = analyze_images(
        paths, _get_tagger(), describer, name=name or "untitled", min_consistency=min_consistency
    )
    new_subject = [t.strip() for t in subject.split(",") if t.strip()] if subject else None
    prompt = card.to_prompt(model, subject=new_subject, include_description=True)
    return prompt, card.negative_prompt(model), card.to_json()


def build_ui():
    import gradio as gr

    with gr.Blocks(title="pic2pic 风格学习") as demo:
        gr.Markdown("## pic2pic：上传参考图，反推风格卡与提示词")
        with gr.Row():
            with gr.Column():
                files = gr.File(
                    label="参考图（可多张）", file_count="multiple", file_types=["image"]
                )
                name = gr.Textbox(label="风格卡名称", value="my-style")
                model = gr.Dropdown(choices=sorted(PRESETS), value="illustrious", label="目标底模")
                subject = gr.Textbox(label="新主体标签（可选，逗号分隔）")
                min_consistency = gr.Slider(0.1, 1.0, value=0.5, step=0.05, label="多图标签一致性")
                use_vlm = gr.Checkbox(label="用 Qwen-VL 补充描述（需要 vlm 依赖）")
                run = gr.Button("分析", variant="primary")
            with gr.Column():
                prompt = gr.Textbox(label="正向提示词", lines=6)
                negative = gr.Textbox(label="负向提示词", lines=3)
                card_json = gr.Code(label="风格卡 JSON", language="json")
        run.click(
            run_analysis,
            inputs=[files, name, model, subject, use_vlm, min_consistency],
            outputs=[prompt, negative, card_json],
        )
    return demo


if __name__ == "__main__":
    build_ui().launch()
