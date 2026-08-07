# Khoai tây

- **Giới hạn thời gian:** 10 minutes
- **Môi trường:** một GPU (≈16 GB VRAM), không có internet
- **Kích thước lời giải:** `solution.ipynb` ≤ 1 MB
- **Dung lượng lưu trữ:** 5 GB 

## Nhiệm vụ
 
Bạn của bạn đề nghị chơi một trò chơi đoán từ.
Bạn ấy, với vai trò giám khảo, chọn một từ ẩn từ một bộ từ vựng cố định, và bạn phải tìm ra từ đó trong nhiều nhất 30 lượt.
Ở mỗi lượt, giám khảo so sánh hai từ và cho biết từ nào gần hơn về mặt ngữ nghĩa với
từ ẩn. Mỗi ván chơi bắt đầu từ
cặp cố định `lamp vs potato`, vì chúng là hai trong số những thứ yêu thích của bạn bạn. Sau đó, chương trình của bạn
đề xuất một từ mới. Từ thắng trong phép so sánh được giữ lại
và được so sánh với đề xuất tiếp theo của bạn. 
Bạn thắng một ván ngay khi đề xuất chính xác từ ẩn. Việc đối sánh
không phân biệt chữ hoa chữ thường. Mọi từ bạn đề xuất phải nằm trong `dataset/vocabulary.json`.

Có một ví dụ đầy đủ trong `solution.ipynb` với giao thức và cách tải dữ liệu. 
Bạn có thể thay đổi lớp PublicEmbeddingPlayer. Chương trình của bạn được khởi tạo một lần và chơi mọi ván trong một lần chạy duy nhất;
giao thức tạo một PublicEmbeddingPlayer mới khi bắt đầu mỗi ván.

## Giám khảo

Chương trình của bạn gửi một đối tượng JSON đến Giám khảo và Giám khảo phản hồi bằng một đối tượng JSON. 

Một ví dụ hoàn chỉnh, trong đó từ ẩn chỉ được hiển thị để giải thích giao thức:

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

Các lượt được đánh chỉ số từ 1 đến 30.

Các lựa chọn của `verdict` là `first` nghĩa là word1 gần hơn, `second` nghĩa là word2 gần hơn hoặc
`same` nghĩa là cả hai từ đều gần từ ẩn như nhau. 

`winner_word` là từ được giữ lại cho lần so sánh tiếp theo. Khi có phán quyết `same`, từ đầu tiên được giữ lại.

## Dataset

Được dùng chung cho mọi split:

- `dataset/vocabulary.json` — 1602 từ viết thường duy nhất. Từ ẩn luôn là
  một trong các từ này.
- `dataset/public_embeddings.npy` — `float32`, có shape `(1602, 2560)`. Hàng `i`
  tương ứng với từ `i` trong bộ từ vựng. Đây là các embedding *công khai*; 
  giám khảo sử dụng một biểu diễn riêng tư khác.

Các split là các tập hợp từ ẩn:

| Split | Số từ | Đáp án | Dùng để |
|---|---|---|---|
| `test_public` | 120 | ✅ `dataset/test_public.json` | chạy lời giải của bạn và tự chấm điểm |
| `test_leaderboard_a` | 120 | ẩn | bảng xếp hạng trực tiếp |
| `test_leaderboard_b` | 120 | ẩn | xếp hạng cuối cùng |

Không có split `train` — không có gì được fit từ các hàng có nhãn (kho^ng co' ta^.p train vi day la unsupervised learning).

### Các mô hình được cung cấp

Hai mô hình embedding pretrained được cung cấp kèm theo nhiệm vụ và có thể được sử dụng:

```text
models/Qwen/Qwen3-Embedding-0.6B
[Qwen Embedding model card](https://yastatic.net/s3/contest/ioai/3/01_Qwen_Qwen3-Embedding-0.6B_MODEL_CARD.html)
models/BAAI/bge-m3
[bge-m3 model card](https://yastatic.net/s3/contest/ioai/3/02_BAAI_bge-m3_MODEL_CARD.html)
```

Cả hai đều phải được tải từ đường dẫn cục bộ tương ứng; một Hugging Face hub id như
`"BAAI/bge-m3"` sẽ kích hoạt việc tải xuống và thất bại, vì quá trình chấm diễn ra offline. Mỗi
thư mục chứa một `example.py` có thể chạy được, minh họa lời gọi offline.

Các thư viện khả dụng: `numpy`, `torch`, `sentence-transformers`. Không có internet, không
tải xuống, không có package nào khác.

## Đầu ra

Không có. Đây là một nhiệm vụ tương tác: lời giải của bạn không ghi tệp đáp án; nó giao tiếp với
giám khảo qua stdin/stdout như mô tả ở trên.

## Chỉ số đánh giá

Một ván chơi tìm được từ ở lượt `t` nhận được `1.0 - 0.02 × max(0, t - 10)` điểm; một ván không được giải
trong vòng 30 lượt nhận được `0` điểm. Vì vậy, các lượt 1–10 nhận được `1.00` điểm, lượt 20 nhận được `0.80` điểm, lượt
30 nhận được `0.60` điểm.

Điểm nhiệm vụ của bạn là điểm trung bình của các ván × 100, nằm trong khoảng từ `0.00` đến `100.00`.

Giới hạn 10-minute là một ngân sách duy nhất bao gồm việc khởi động, chuẩn bị và toàn bộ 120
ván chơi trong test set. 

## Cách nộp bài

1. Mở `solution.ipynb`, chỉnh sửa `PublicEmbeddingPlayer`, và chạy tất cả các cell để bảo đảm nó hoạt động.
2. Nếu muốn, hãy kiểm tra cục bộ: `python local_test.py solution.ipynb --limit 5`.
   Giám khảo cục bộ sử dụng các embedding *công khai*, vì vậy điểm của nó
   chỉ mang tính tham khảo.
3. Lưu `solution.ipynb`.
4. Mở tab Git trong thanh bên trái của JupyterLab.
5. Stage `solution.ipynb` (biểu tượng **+** bên cạnh tệp).
6. Nhập một commit message và nhấp vào Commit.
7. Nhấp vào biểu tượng đám mây có mũi tên hướng lên để push.
8. Quay lại trang Contest này và nhấp vào Submit, với commit message khớp với commit message bạn đã cung cấp.

Chỉ nộp đúng một tệp, có tên `solution.ipynb`, bao gồm mọi bước chuẩn bị và suy luận cần thiết.
