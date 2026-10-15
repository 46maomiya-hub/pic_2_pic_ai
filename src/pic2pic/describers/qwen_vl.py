"""用 Qwen-VL 补充一句画面描述（构图、氛围、光影），标签很难表达这些。

默认 Qwen2.5-VL-3B-Instruct，bf16 约 8GB 显存，和 SDXL 不同时运行时 16GB 足够。
7B 版本 bf16 约 16GB，在 5070 Ti 上需要量化。
"""

from __future__ import annotations

from PIL import Image

DEFAULT_MODEL = "Qwen/Qwen2.5-VL-3B-Instruct"

DEFAULT_INSTRUCTION = (
    "Describe the art style of this anime illustration in one English sentence of at most "
    "40 words. Focus on composition, camera angle, lighting, color palette and mood. "
    "Do not describe the character's identity or clothing."
)


class QwenVLDescriber:
    def __init__(self, model_id: str = DEFAULT_MODEL, max_new_tokens: int = 96) -> None:
        self.model_id = model_id
        self.max_new_tokens = max_new_tokens
        self._model = None
        self._processor = None

    def load(self) -> None:
        if self._model is not None:
            return
        from transformers import AutoModelForImageTextToText, AutoProcessor

        self._processor = AutoProcessor.from_pretrained(self.model_id)
        self._model = AutoModelForImageTextToText.from_pretrained(
            self.model_id, torch_dtype="auto", device_map="auto"
        )

    def describe(self, image: Image.Image, instruction: str = DEFAULT_INSTRUCTION) -> str:
        self.load()
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image.convert("RGB")},
                    {"type": "text", "text": instruction},
                ],
            }
        ]
        inputs = self._processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(self._model.device)
        output = self._model.generate(**inputs, max_new_tokens=self.max_new_tokens)
        new_tokens = output[:, inputs["input_ids"].shape[1] :]
        text = self._processor.batch_decode(new_tokens, skip_special_tokens=True)[0]
        return text.strip()
