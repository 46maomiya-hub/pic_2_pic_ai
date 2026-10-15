# pic_2_pic_ai

学习 AI 图和绘画的风格，生成提示词与同风格的新图。主攻二次元，全部在本地显卡上运行（目标配置 RTX 5070 Ti 16GB）。

当前是**第一阶段：提示词反推**。上传一张或一组参考图，输出一张「风格卡」和可以直接用的正向/负向提示词。

## 风格卡是什么

参考图的标签被拆成几块，换主体时只保留风格和构图：

| 字段 | 内容 | 例子 |
| --- | --- | --- |
| `style` | 画风、媒介、上色、光影、色调 | `watercolor (medium)`, `pastel colors`, `backlighting` |
| `composition` | 取景、角度、视线 | `upper body`, `from above`, `looking at viewer` |
| `subject` | 参考图里的具体内容，生成新图时通常替换 | `cat ears`, `school uniform` |
| `count` / `characters` / `rating` | 人数、角色名、分级 | `1girl` |
| `description` | 可选，Qwen-VL 写的一句画面描述 | |
| `consistency` | 多图时每个标签出现的比例 | `{"pastel colors": 1.0}` |

多张图一起分析时，只保留在至少 `--min-consistency`（默认 50%）的图里都出现的标签，这样留下的是稳定的风格，而不是某一张图的内容。

## 安装

需要 Python 3.10+。5070 Ti 属于 50 系（Blackwell），PyTorch 请装 CUDA 12.8 及以上的版本。

```bash
git clone https://github.com/46maomiya-hub/pic_2_pic_ai.git
cd pic_2_pic_ai
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -e ".[tagger,ui]"          # 标签器 + 网页界面
# 想用显卡跑标签器：pip install onnxruntime-gpu
# 想加 Qwen-VL 描述：先按 pytorch.org 装 CUDA 12.8 版 torch，再 pip install -e ".[vlm]"
```

首次运行会从 Hugging Face 下载模型：WD14 EVA02-Large 标签器约 1.2GB，Qwen2.5-VL-3B 约 7GB。

## 使用

命令行：

```bash
# 分析一个文件夹里的参考图，保存风格卡
pic2pic analyze ./refs --name my-style --model noobai --out cards/my-style.json

# 加上 Qwen-VL 描述
pic2pic analyze ./refs/a.png --describe

# 复用风格卡，换成新主体
pic2pic prompt cards/my-style.json --model noobai --subject "1girl, fox ears, kimono"
```

网页界面：

```bash
python -m pic2pic.app
```

`--model` 支持 `illustrious`、`noobai`、`animagine`，会自动加上对应底模的质量词和负向提示词。

## 目录

```
src/pic2pic/
  tags.py          标签分类（风格/构图/主体）与格式化
  style_card.py    风格卡数据结构、各底模的提示词模板
  analyzer.py      单图/多图分析与标签聚合
  taggers/wd14.py  WD14 ONNX 标签器
  describers/      Qwen-VL 画面描述
  cli.py           命令行
  app.py           Gradio 界面
tests/             单元测试（不需要下载模型）
```

## 路线

1. **提示词反推**（当前）：WD14 + Qwen-VL，输出结构化风格卡。
2. **同风格生成**：Illustrious XL / NoobAI XL + IP-Adapter，在本地出图。
3. **评分闭环**：CLIP / DINOv2 风格相似度打分，自动改写提示词。
4. **风格库与 LoRA**：风格卡检索，用 15~30 张图训练 SDXL LoRA。

## 开发

```bash
pip install -e ".[dev,tagger]"
pytest
ruff check . && ruff format --check .
```
