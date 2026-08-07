# 找出順序

- **時間限制：** 10 分鐘
- **環境：** 1 個 GPU（≈16 GB VRAM），無網際網路
- **解答大小：** `solution.ipynb` ≤ 1 MB
- **儲存空間：** 5 GB 

## 問題

你會獲得兩位參與者 *Speaker A* 與 *Speaker B* 之間的英語口語對話。每段對話會依說話者的發言輪次分爲`n`個片段（chunk），每個片段僅包含一位說話者的語音。每個片段均儲存為一個獨立的 `.wav` 音訊檔案，因此一段完整對話由一組 `n` 個 `.wav` 檔案表示，每個片段各有一個檔案。 

不幸的是，這些片段已被隨機打亂，因此對話不再連貫。在檔名 `chunk_{k}.wav` 中，`k` 指的是打亂後的第 k 個片段，而非原始對話中的第 k 個片段。

**‼️ 你的任務是重建對話原本的時間順序。**（換句話說，將`n`個片段依照正確的對話順序排序。）

![找出順序](../find_the_order.jpg)

---

## 資料集

每段對話包含名為 `n`、`chunk_0.wav`、`chunk_1.wav`、…、`chunk_{n-1}.wav` 的音訊檔案。每個片段是*Speaker A* 或 *Speaker B* 的發言。檔名僅對應打亂後的順序，並不表示片段在原始對話中的順序。每段對話有 7–20 個片段，單聲道，44.1 kHz（你可以重新取樣）。

**`prefix.json` 包含每段對話前兩個片段的檔名索引。** 這會指出對話真正的開頭，並消除以正向或反向閱讀對話時所產生的歧義。

例如：`11: [7, 12]` 表示對話 11 的第一與第二個輪次分別是 `chunk_7.wav` 與 `chunk_12.wav`。

### 你會獲得的內容

你會收到**兩個格式完全相同的資料夾**：

| 資料夾 | 對話數 | `answers.json`？ | 用途 |
|--------|-----------|-----------------|-----------|
| `dataset/train/` | 1,288 | ✅ 包含 | 訓練／微調你的模型 |
| `dataset/test_public/`  | 100   | ✅ 包含 | 執行你的 pipeline 並在本機自行評分 |

評分時，你的 `dataset/test_public/` 資料夾會被透明地替換為
`hidden evaluation set`（公開排行榜使用 `test_leaderboard_a`，最終排行榜使用 `test_leaderboard_b`）——它們的大小與格式均和 `dataset/test_public/` 相同，但不含 `answers.json`。

你的 notebook 會在該資料上再次執行，其產生的 `answers.json` 檔案將用於評分。留出測試對話與 `train` 來自相同的分布，因此你在本機取得的 `test_public` 分數能如實預示結果。

### 目錄結構

```bash
dataset/train/
    prefix.json  # {dialogue_id: [first_idx, second_idx]} filename index 
    answers.json  # {dialogue_id: P}  ground-truth order (正確答案順序, rank convention)
    <dialogue_id>/
        chunk_0.wav
        ...
        chunk_{n-1}.wav

dataset/test_public/
    prefix.json
    answers.json     # present only in the development copy
    <dialogue_id>/
        chunk_0.wav
        ...
        chunk_{n-1}.wav
```

---

## 輸出

對於每段對話，判定其音訊片段原本的時間順序。你的預測應為 `{0, 1, …, n−1}` 的一個排列 `P`，其中 `P[i]` 是 `chunk_i.wav` 的預測時間位置（0 = 第一個）。

你的輸出檔案 `answers.json` 應將每個對話 ID 對應至其預測排列：

```json
{
  "17": [2, 0, 1],
  "42": [0, 1],
  "108": [3, 1, 0, 4, 2, 5]
}
```

### 範例

某段對話有 3 個打亂後的片段 `chunk_0, chunk_1, chunk_2`：

| 打亂後的片段 | 語音內容 | 真實位置（排名） |
|----------------|----------------|----------------------|
| `chunk_0.wav` | *"No worries — I'll send you the notes afterwards."* | 2（最後） |
| `chunk_1.wav` | *"Hey, are you coming to the three o'clock meeting?"* | 0（第一個） |
| `chunk_2.wav` | *"I can't — I've got a dentist appointment then."* | 1 |

真實順序為 **chunk_1 → chunk_2 → chunk_0**，因此 `P = [2, 0, 1]`，而 `prefix.json` 會儲存 `[1, 2]`。

⚠️ **P 必須是真正的排列：** 長度為 n、使用 0 起始索引，且每個值恰好出現一次。重複值、缺少值或超出範圍的項目（例如使用 1 起始索引），都會使該對話得到 0 分；檔案中缺少某段對話時亦同。格式錯誤或非 JSON 的檔案將被拒絕。

## 評分

此任務的評分指標是**成對排序準確率**。它會檢查每一對片段並詢問：_兩者之中哪一個應該在前？_ 如果你的預測與 ground truth 給出的答案相同，該片段對即為正確。對於具有 `n` 個片段的對話，共有 $$M = n(n-1)/2$$ 個片段對；令 `I` 為逆序數——亦即與 ground truth 排序不同的片段對數量：

$$\text{score} = 1 - \frac{I}{M} \in [0, 1]$$

ℹ️ **最終分數是該資料分割中所有
對話之逐對話分數的平均值。**

## 允許使用的模型

在訓練與評估期間，你只能使用下列預訓練模型來解決此任務。所有這些模型都已下載並可在環境中使用。你可以在 baseline notebook `solution.ipynb` 中查看其使用範例。請注意，你不能使用任何其他模型，而且你的程式無法存取網際網路。

- **語音表徵：** **wav2vec 2.0**。也可以使用 **Whisper encoder** 作為特徵擷取器。
[wav2vec 模型卡](https://yastatic.net/s3/contest/ioai/1/01_facebook_wav2vec2-base-960h_MODEL_CARD.html)

- **自動語音辨識（ASR）：** **OpenAI Whisper**（任意大小）。
[Whisper 模型卡](https://yastatic.net/s3/contest/ioai/1/03_openai_whisper-small_MODEL_CARD.html)
- **語言模型：** **Qwen2.5-0.5B**，可採零樣本方式使用，或在提供的 `train` 資料分割上進行微調。
[Qwen 模型卡](https://yastatic.net/s3/contest/ioai/1/02_Qwen_Qwen2.5-0.5B_MODEL_CARD.html)
請注意，10 分鐘限制必須涵蓋你在評分時進行的任何訓練或微調，以及在評估集上的推論。

## 如何提交

- 開啟 `solution.ipynb` 並執行所有儲存格。確認它會在工作目錄中寫入 `answers.json`，且其中包含 `dataset/test_public/` 中每段對話的排列（100 段對話）。評分時，notebook 會在隱藏測試集上重新執行，並對其在該處產生的 `answers.json` 進行評分。
- 如果你想要，可以改進解答——也可以不改；僅使用 baseline 即可驗證 pipeline。
- 開啟 JupyterLab 左側邊欄中的 Git 分頁。
- 將 `solution.ipynb` **Stage**（點擊旁邊的 + 圖示）。
- 輸入 commit 訊息並點擊 **Commit**。
- 點擊帶有向上箭頭的雲朵圖示以推送。
- 返回此 Contest 頁面並點擊 **Submit**。

請提交恰好一個檔案，檔名為 `solution.ipynb`。
