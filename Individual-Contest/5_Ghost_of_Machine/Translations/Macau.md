# 機器之幽靈

- **時間限制：** 10 minutes
- **基線分數：** 28.6
- **環境：** 一張 GPU（≈16 GB VRAM），無網際網路
- **解答大小：** `solution.ipynb` ≤ 20 MB
- **儲存空間：** 5 GB
- **預訓練模型：** 僅限 **[bge-base-en-v1.5](https://yastatic.net/s3/contest/ioai/5/01_BAAI_bge-base-en-v1.5_MODEL_CARD.html)**——文字**編碼器**（嵌入模型）。


## 任務

哈薩克國家檔案館正發生一些怪事。圖書館員表示，有些書以前的結局並不相同，但沒有人能證明此事——每一分副本都一樣，而且每個故事仍然合乎情理。你受邀以 AI 研究員的身分找出這些變動。
![幽靈](../ghost.jpg)

一段文字以人類撰寫的內容開始，並在某個時刻悄然切換為由語言模型產生的續文。整體閱讀時，它看起來像是一篇連貫的文章——但在中途某處，作者從人類變成了機器。你的任務是**找出該切換點：人類部分結束，且機器部分開始之處的字符索引**。

每個樣本都是單一字符串 `text`。恰好存在一個邊界。該邊界
之前的所有內容皆由人類撰寫；從該邊界起的所有內容皆由機器產生。

## 數據集

純文字英文篇章，每篇各有一個邊界。

- **A 部分**（邊界之前）：一段由人類撰寫的文字節錄。
- **B 部分**（從邊界起）：語言模型以 A 部分為條件
  產生的續文。
- 兩個部份都至少有 180 words；總長度約為 500–800 words。
- **`boundary_char_index`** 是 B 部分第一個字符的下標：`text[boundary_char_index:]` 是機器部分，而`text[:boundary_char_index]` 是人類部分，兩者之間會由一個空格進行分割。
  

#### 你會獲得的內容

你會收到**兩個資料夾**：

| 資料夾 | 樣本數 | `answers.jsonl`？ | 用途 |
|--------|---------|------------------|-----------|
| `dataset/train/` | 1,221 | ✅ 已包含 | 訓練／微調你的方法 |
| `dataset/test_public/`  | 380   | ✅ 已包含（開發用副本） | 執行你的流程並在本機自行評分 |

在**評分時**，你的 `dataset/test_public/` 資料夾會被**隱藏的評估集取代**。其有著同樣的格式，但**不包含 `answers.jsonl`**。系統會在其上重新執行你的 notebook，並對其產生的 `answers.jsonl` 進行評分。

- 公開排行榜使用隱藏的 **test_leaderboard_a** 集（380 samples）。

- 最終排名使用隱藏的 **test_leaderboard_b** 集（380 samples）。

這三個測試集的大小相同，且取樣自與 `train` 相同的分布，因此你本機的 `dataset/test_public/` 分數可合理估計你的排行榜分數。

#### 磁碟格式

```
dataset/train/data.jsonl      # one JSON object per line: {"id": "...", "text": "..."}
dataset/train/answers.jsonl   # {"id": "...", "boundary_char_index": 1842}
dataset/test_public/data.jsonl       # {"id": "...", "text": "..."}
dataset/test_public/answers.jsonl    # dev copy only — ABSENT in the hidden grading set
```

- `answers.jsonl` 中的 ID 與 `data.jsonl` 中的 ID 相符。
- 每當你進行訓練或微調時，皆可使用 `dataset/train/`（含答案）。

## 輸出（提交格式）

你必須提交**單一 notebook，且其名稱必須被命名為 `solution.ipynb`**。此確切檔名為必要條件。任何其他檔名都會在不被執行的情況下遭到拒絕。

你的 notebook 必須**讀取 `dataset/test_public/data.jsonl`**，並在儲存庫根目錄寫入單一檔案 **`answers.jsonl`**——每行一個 JSON 物件，將
每個樣本 ID 對應至你預測的邊界字符索引：

```json
{"id": "example_000123", "boundary_char_index": 1790}
{"id": "example_000124", "boundary_char_index": 2450}
```

- `boundary_char_index` 必須是**位於 `[0, len(text)]` 內的整數**。
- `dataset/test_public/data.jsonl` 中的每個 ID 都應恰好出現一次。若某個樣本未出現於 `answers.jsonl` 中（或其值不是整數／超出範圍），則該樣本得 0 分。

## 評分

對於每個樣本，令 `p` 為你的預測索引，`t` 為真實邊界。每個樣本的分數會隨字符距離呈指數衰減：

$$\text{score} = \exp\!\left(-\frac{|p - t|}{\tau}\right) \in (0, 1], 
~ \text{where} ~ \tau = 100.$$

這會使分數呈現以下情況：
- **=1.0**——邊界字符完全正確；
- **≈0.78**——相差 25 characters；- **≈0.61**——相差 50 characters；
- **≈0.37**——相差 100 characters；
- **≈0.01**——相差 500 characters。

**最終分數是**該數據集中所有樣本之逐樣本分數的平均值
（以 0–100 的尺度展示）。此評分指標會獎勵*接近*正確位置的結果，而不僅是完全正確的結果。

## 限制

- **環境：** 一張 GPU（≈16 GB VRAM），評分時無網際網路——允許使用的模型（如下）已預先提供。整次執行的**實際時間預算：10 minutes**——這必須涵蓋你在評分時進行的任何訓練／微調，**以及**在評估集上進行的推理。
- **允許的預訓練模型**——以下為完整清單；不得使用任何其他預訓練權重。該模型已**預先提供於環境中**（以一般方式載入，例如
  `from_pretrained`；評分時無網際網路）：
  - **bge-base-en-v1.5**——一個 110M-parameter 的文字**編碼器**（嵌入模型）。它會產生句子／篇章嵌入；它不是生成式語言模型。你可以**直接使用（凍結特徵），或在 `train` 數據集上微調**（完整微調需符合 16 GB / 10-minute 預算）。
- 傳統／統計工具不受限制：你可以在自行計算的嵌入特徵之上，建立任何以特徵為基礎的模型（例如 scikit-learn 分類器或迴歸器）。
  *預訓練深度學習權重*僅限於上述清單。
