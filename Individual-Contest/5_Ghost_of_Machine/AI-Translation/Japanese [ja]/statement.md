# 機械の亡霊

- **制限時間:** 10 minutes
- **ベースラインスコア:** 28.6
- **科学委員会スコア:** 93.41
- **環境:** GPU 1基（≈16 GB VRAM）、インターネット接続なし
- **解答サイズ:** `solution.ipynb` ≤ 20 MB
- **ストレージ:** 5 GB
- **事前学習済みモデル:** **[bge-base-en-v1.5](https://yastatic.net/s3/contest/ioai/5/01_BAAI_bge-base-en-v1.5_MODEL_CARD.html)** のみ — テキスト**エンコーダ**（embedding model）。


## 課題

Kazakhstan国立公文書館で奇妙なことが起きています。司書たちは、一部の本は以前と異なる結末だったと言いますが、誰もそれを証明できません。どの写しも同じであり、どの物語にも依然として筋が通っているからです。あなたはAI研究者として、変更箇所を特定するよう招かれました。
![亡霊](../../ghost.jpg)

ある文章は人間が書いたテキストとして始まり、途中のある時点で、ひそかに言語モデルが生成した続きへと切り替わります。全体として読むと、1つの一貫した文章に見えますが、途中のどこかで書き手が人間から機械へと変わります。あなたの課題は、**その切り替わり、すなわち人間による部分が終わり、機械による部分が始まる文字インデックスを見つけること**です。

各サンプルは1つの文字列 `text` です。境界はちょうど1つあります。境界より前はすべて人間によるものであり、境界以降はすべて機械によって生成されたものです。

## データセット

境界をそれぞれ1つ含む、プレーンテキストの英語文章です。

- **Part A**（境界より前）: 人間が書いたテキストの抜粋。
- **Part B**（境界以降）: Part Aを条件として言語モデルが生成した続き。
- 各部分は少なくとも180 wordsで、全体の長さは~500–800 wordsです。
- **`boundary_char_index`** はPart Aが終わる文字オフセットです。
  `text[:boundary_char_index]` は人間による部分であり、
  `text[boundary_char_index:].lstrip()` は機械による部分です。

#### 提供されるもの

**2つのフォルダ**が提供されます。

| フォルダ | サンプル数 | `answers.jsonl`? | 用途 |
|--------|---------|------------------|-----------|
| `dataset/train/` | 1,221 | ✅ 含まれる | 手法の学習／fine-tuning |
| `dataset/test_public/`  | 380   | ✅ 含まれる（dev用コピー） | パイプラインの実行とローカルでの自己採点 |

**採点時**には、`dataset/test_public/` フォルダが**非公開の評価セットに置き換えられます**。形式は同じですが、**`answers.jsonl` は含まれません**。その評価セットに対してnotebookが再実行され、notebookが生成した `answers.jsonl` が採点されます。

- 公開leaderboardでは、非公開の **test_leaderboard_a** セット（380 samples）を使用します。

- 最終順位では、非公開の **test_leaderboard_b** セット（380 samples）を使用します。

3つの評価セットはすべて同じサイズであり、`train` と同じ分布から抽出されているため、ローカルでの `dataset/test_public/` スコアはleaderboardスコアの妥当な推定値となります。

#### ディスク上の形式

```
dataset/train/data.jsonl      # one JSON object per line: {"id": "...", "text": "..."}
dataset/train/answers.jsonl   # {"id": "...", "boundary_char_index": 1842}
dataset/test_public/data.jsonl       # {"id": "...", "text": "..."}
dataset/test_public/answers.jsonl    # dev copy only — ABSENT in the hidden grading set
```

- `answers.jsonl` 内のIDは、`data.jsonl` 内のIDと一致します。
- 学習またはfine-tuningを行う際には、`dataset/train/`（正解付き）を利用できます。

## 出力（提出形式）

**`solution.ipynb` という名前でなければならない、単一のnotebook**を提出します。この正確なファイル名が必須です。それ以外のものは実行されずに却下されます。

notebookは **`dataset/test_public/data.jsonl` を読み込み**、リポジトリのルートに単一のファイル **`answers.jsonl`** を書き出さなければなりません。各行には、各サンプルIDを予測した境界の文字インデックスに対応付けるJSON objectを1つずつ出力します。

```json
{"id": "example_000123", "boundary_char_index": 1790}
{"id": "example_000124", "boundary_char_index": 2450}
```

- `boundary_char_index` は、**`[0, len(text)]` 内の整数**でなければなりません。
- `dataset/test_public/data.jsonl` 内のすべてのIDは、ちょうど1回ずつ現れるべきです。`answers.jsonl` に含まれていないサンプル（または値が整数でない、もしくは範囲外であるサンプル）は、そのサンプルについて0点となります。

## 採点

各サンプルについて、`p` を予測したインデックス、`t` を真の境界とします。サンプルごとのスコアは、文字単位の距離に応じて指数関数的に減衰します。

$$\text{score} = \exp\!\left(-\frac{|p - t|}{\tau}\right) \in (0, 1], 
~ \text{where} ~ \tau = 100.$$

これにより、スコアは次のように変化します。
- **=1.0** — 境界の文字と完全に一致。
- **≈0.78** — 25 charactersのずれ。- **≈0.61** — 50 charactersのずれ。
- **≈0.37** — 100 charactersのずれ。
- **≈0.01** — 500 charactersのずれ。

**最終スコアは、split内の全サンプルに対するサンプルごとのスコアの平均**です（0–100 scaleで報告されます）。このmetricでは、完全一致だけでなく、境界に*近い*予測も評価されます。

## 制約

- **環境:** GPU 1基（≈16 GB VRAM）、採点時にはインターネット接続なし — 以下で許可されているモデルはすでに提供されています。実行全体の**実時間制限は10 minutes**です。これには、採点時に行うすべての学習／fine-tuningと、評価セットに対する推論の**両方**が含まれなければなりません。
- **使用可能な事前学習済みモデル** — 以下がすべてであり、他の事前学習済みweightsは使用できません。このモデルは**環境内に事前に用意されています**（通常どおり、たとえば `from_pretrained` として読み込んでください。採点時にはインターネット接続がありません）。
  - **bge-base-en-v1.5** — 110M-parameterのテキスト**エンコーダ**（embedding model）。sentence/passage embeddingsを生成するものであり、生成言語モデルではありません。**そのまま（frozen featuresとして）使用することも、`train` splitでfine-tuningすることもできます**（full fine-tuningは16 GB / 10-minuteの制限内で実行可能です）。
- 古典的／統計的ツールの使用には制限がありません。自分で計算したembedding featuresの上に、任意のfeature-based model（たとえばscikit-learnのclassifierまたはregressor）を構築できます。*事前学習済みdeep-learning weights*に関する制限は、上記のリストにあるものだけです。

## ベースライン

提供される `solution.ipynb` は単純な参照用です。`dataset/train/` から単一の「平均境界比率」を推定し、すべてのテスト文章について、長さにその同じ比率を掛けた位置を予測します。非公開の **test_leaderboard_a** splitで**28.6**を記録し、read-`dataset/test_public/` → write-`answers.jsonl` の処理を実行できるテンプレートとしてのみ存在します。

同じsplitおよび同じ10-minute制限で測定された**科学委員会スコア93.41**は、許可されたエンコーダを `train` でfine-tuningし、文単位のchangepointとして切り替わりを特定することで得られたものです。これは上限ではありません。このmetricにおける最大値は100です。
