# 土豆

- **时间限制：** 10 分钟
- **环境：** 一块 GPU（≈16 GB VRAM），无互联网
- **解决方案大小：** `solution.ipynb` ≤ 1 MB
- **存储空间：** 5 GB 

## 任务
 
你的朋友建议玩一个猜词游戏。
他作为裁判，从一个固定词表中选取一个隐藏单词，而你必须在最多 30 轮内找到它。
每一轮，裁判会比较两个单词，并报告哪一个在语义上更接近
隐藏单词。每局游戏都从
固定单词对 `lamp vs potato` 开始，因为它们是你朋友最喜欢的两样事物。随后，你的程序
提出一个新单词。比较中胜出的单词会被保留，
并与你下一次提出的单词进行比较。
一旦你提出的单词与隐藏单词完全相同，你就赢得该局游戏。匹配
不区分大小写。你提出的每个单词都必须位于 `dataset/vocabulary.json` 中。

`solution.ipynb` 中提供了一个完整示例，其中包含协议(protocol)和数据加载。
你可以修改 PublicEmbeddingPlayer 类。你的程序只初始化一次，并在一次运行中完成所有游戏；
协议会在每局游戏开始时创建一个新的 PublicEmbeddingPlayer。

## 裁判

你的程序向裁判发送一个 JSON 对象，裁判则以一个 JSON 对象响应。

以下是一个完整示例，其中仅为解释协议而显示了隐藏单词：

```text
Hidden word: shovel          Fixed opening: lamp vs potato

<- {"turn": 1, "winner_word": "potato", "verdict": "second", "word1": "lamp",   "word2": "potato"}
-> {"new_word": "rock"}
<- {"turn": 2, "winner_word": "rock",   "verdict": "second", "word1": "potato", "word2": "rock"}
-> {"new_word": "hammer"}
<- {"turn": 3, "winner_word": "hammer", "verdict": "second", "word1": "rock",   "word2": "hammer"}
-> {"new_word": "shovel"}                                    <- matches: game won
-> {"status": "win"}
```

轮次编号从 1 到 30。

`verdict` 的可能取值为：`first`，表示 word1 更接近；`second`，表示 word2 更接近；或
`same`，表示两个单词与隐藏单词的接近程度相同。

`winner_word` 是为下一次比较保留的单词。当裁定为 `same` 时，第一个单词会被保留。

## 数据集

所有数据划分共享：

- `dataset/vocabulary.json` — 1602 个互不相同的小写单词。隐藏单词始终是
  其中之一。
- `dataset/public_embeddings.npy` — `float32`，形状为 `(1602, 2560)`。第 `i` 行
  对应词表中的单词 `i`。这些是**公开**嵌入(public embeddings)；
  裁判使用另一种私有表示(private representation)。

各数据划分均为隐藏单词的集合：

| 数据划分 | 单词数 | 答案 | 用途 |
|---|---|---|---|
| `test_public` | 120 | ✅ `dataset/test_public.json` | 运行你的解决方案并自行评分 |
| `test_leaderboard_a` | 120 | 隐藏 | 实时排行榜 |
| `test_leaderboard_b` | 120 | 隐藏 | 最终排名 |

不存在 `train` 数据划分——不会从带标签的行中拟合任何内容(nothing is fitted from labelled rows)。

### 提供的模型

本任务随附两个可能使用的预训练嵌入模型：

```text
models/Qwen/Qwen3-Embedding-0.6B
[Qwen Embedding model card](https://yastatic.net/s3/contest/ioai/3/01_Qwen_Qwen3-Embedding-0.6B_MODEL_CARD.html)
models/BAAI/bge-m3
[bge-m3 model card](https://yastatic.net/s3/contest/ioai/3/02_BAAI_bge-m3_MODEL_CARD.html)
```

两者都必须从其本地路径加载；使用 Hugging Face Hub ID（例如
`"BAAI/bge-m3"`）会触发下载并导致失败，因为评测离线进行。每个
目录中都包含一个可运行的 `example.py`，用于展示离线调用方式。

可用库：`numpy`、`torch`、`sentence-transformers`。无互联网、无
下载，也不可使用其他软件包。

## 输出

无。这是一项交互式任务：你的解决方案不写入答案文件；而是按照上述方式通过
stdin/stdout 与裁判通信。

## 评分指标

在第 `t` 轮找到隐藏单词的一局得分为 `1.0 - 0.02 × max(0, t - 10)`；未能
在 30 轮内解决的一局得分为 `0`。因此，第 1–10 轮得分为 `1.00`，第 20 轮得分为 `0.80`，第
30 轮得分为 `0.60`。

你的任务得分为各局平均得分 × 100，范围在 `0.00` 和 `100.00` 之间。

10 分钟的时间限制是一个统一预算，涵盖启动、准备以及测试集中全部 120
局游戏。

## 如何提交

1. 打开 `solution.ipynb`，编辑 `PublicEmbeddingPlayer`，并运行所有单元格以确保其正常工作。
2. 你也可以选择在本地检查：`python local_test.py solution.ipynb --limit 5`。
   本地裁判使用**公开**嵌入，因此其分数
   仅供参考。
3. 保存 `solution.ipynb`。
4. 打开 JupyterLab 左侧边栏中的 Git 选项卡。
5. 暂存(Stage) `solution.ipynb`（点击其旁边的 **+** 图标）。
6. 输入提交消息并点击 Commit。
7. 点击带向上箭头的云朵图标进行推送。
8. 返回此竞赛页面并点击 Submit，所填写的提交消息须与你之前提供的消息一致。

仅提交一个名为 `solution.ipynb` 的文件，其中应包含所有必要的准备和推理过程。
