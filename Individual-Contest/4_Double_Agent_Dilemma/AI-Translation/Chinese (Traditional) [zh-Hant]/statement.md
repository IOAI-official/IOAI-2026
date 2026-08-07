# 雙重間諜困境

- **時間限制：** 12 分鐘。
- **儲存空間：** 5 GB
- **環境：** 單一 GPU（≈16 GB VRAM），無網際網路
- **解答大小：** `solution.ipynb` ≤ 1 MB
- **Baseline 分數：** 0 
- **科學委員會分數：** 96.99 

在阿斯塔納的國家 AI 中心，兩個電腦模型——Model R（一個 ResNet-18）與 Model V（一個 ViT-Tiny）——正在分析照片。目前，兩個模型的表現都完美無缺，準確率達到 100%，並且在每一張影像上的判斷都一致。為了測試它們聰明的「大腦」究竟有多麼不同，首席科學家向你提出一項挑戰：對每張照片的像素進行微小、幾乎不可見的變更，使 Model R 與 Model V 完全意見相左。

![圖片](../../dilemma.jpg)

## 1. 任務

兩個預訓練影像分類器會查看同一張影像。在本任務提供的影像上，兩個分類器的準確率皆為 100%。

- **Model R**：`torchvision.models.resnet18`（一個 CNN，ResNet18）。
- **Model V**：`timm` 的 `vit_tiny_patch16_224`（一個 Transformer，ViT-Tiny）。

你的任務是為每張影像建立一個小幅變更（「擾動」），使兩個模型產生不同的判斷。對於每張影像，你必須建立**兩個不同的**擾動：

- **類型 A**：加入擾動後，Model R 仍能正確分類影像，但 Model V 會錯誤分類。
- **類型 B**：加入擾動後，Model V 仍能正確分類影像，但 Model R 會錯誤分類。

每個擾動都必須足夠*小*，使其難以察覺。擾動越小，分數越高（請參閱第 5 節）。擾動會直接在像素層級套用至原始影像。

## 2. 公開資料

本任務提供一組影像，分為兩個資料分割——`train`（100 張影像）與
`test_public`（100 張影像）——每個分割中的影像解析度各異。所有影像皆來自 ImageNet-1K 的 1000 個類別，而 Model R 與 Model V 在兩個分割上皆達到 100% 的準確率。

提供以下檔案：

```text
train/images/*.png         # 100 images in PNG format
train/labels.json          # maps each image index to its correct class
test_public/images/*.png   # 100 images in PNG format
test_public/labels.json    # maps each image index to its correct class
```

評分時，你的 `dataset/test_public/` 資料夾會被透明地替換為兩組隱藏影像集（`test_leaderboard_a` 與 `test_leaderboard_b`），以進行正式評分。每個影像集都包含 **100 張影像**，採用 PNG 格式，並附有一個標籤檔案。 

**注意：在本任務中，可存取測試資料集中的標籤。**

## 3. 輸出格式

對於每張影像，你必須產生兩個檔案：

```text
{index}_a.pt   # Type A perturbation
{index}_b.pt   # Type B perturbation
```

- `{index}`（`0`、`1`、`2`、...）須與資料集中影像的名稱相符。
- 每個檔案都是使用 `torch.save` 儲存的單一 tensor。其形狀必須為`3 x H x W`，其中 `H` 與 `W` 須符合該影像的**原始**解析度（而非 `224 x 224`）。
- 程式碼應只產生一個 ZIP 檔案，即 `submission.zip`。請將所有 `.pt` 檔案放置於 ZIP 壓縮檔的最上層，不得包含外層資料夾或任何子目錄。 

```text
submission.zip
├── 0_a.pt
├── 0_b.pt
└── 1_a.pt
└── ...
```

若輸出格式存在任何問題，notebook 將會向你發出警示。

## 4. 限制

- **模型：** 你必須使用 `torchvision.models.resnet18(pretrained=True)` 與 `timm.create_model('vit_tiny_patch16_224', pretrained=True)`。不得使用其他預訓練模型。
- **轉換流程（評估時強制執行）：** `Resize(256) → CenterCrop(224) →
  Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])`. See Section 3 of `baseline.ipynb`，以瞭解詳細資訊。 
- **擾動解析度：** 必須符合原始影像的**原始**解析度（而非 224×224）。tensor 會在轉換流程*之前*加入原始影像。
- **輸出格式：** 僅可使用 `.pt` 檔案——不得使用 PNG/JPG。tensor 會加入原始影像，且像素值在預處理前會被裁切至 `[0, 1]`。
- **檔案命名：** 平坦列出，嚴格採用 `{index}_a.pt`／`{index}_b.pt` 格式。zip 中不得包含子目錄。
- **函式庫：** `torch`、`torchvision`、`timm`。 

## 5. 評分

最終分數的計算方式如下。令 `M` 為該分割中的影像數量，$Score_A$ 為成功的類型 A 擾動數量，而 $Score_B$ 為成功的類型 B 擾動數量：
$$
S_{final} = \frac{Score_A + Score_B}{2M} \times PF
$$

PF 是一個用於懲罰具有高範數之擾動的函數，並且在效能上限附近非常敏感。它它被限制在 0.5 到 1 的範圍內。完整實作可見於 `solution.ipynb` 的第  8 節。 

![圖片](../../curves.jpeg)
圖：懲罰函數的曲線。

## 6. 檢查提交內容

notebook 中設有檢查機制，若存在格式問題便會向你發出警示；該機制位於 `solution.ipynb` notebook 的第 7 節。

## 7. 本機測試

`solution.ipynb` 包含一個完整且可運作的範例。它會載入公開資料、兩個模型與官方評分器，並寫出一個提交用 ZIP 檔案。開始前請先閱讀。

## 8. 如何提交

- 將你的變更儲存至 `solution.ipynb`。
- 開啟 JupyterLab 左側邊欄中的 Git 分頁。
- 將 `solution.ipynb` 加入 **Stage**（其旁邊的 + 圖示）。
- 輸入 commit 訊息，然後按一下 **Commit**。
- 按一下帶有向上箭頭的雲朵圖示以進行 push。
- 返回此競賽頁面，然後按一下 **Submit**。

請恰好提交一個名為 `solution.ipynb` 的檔案。
