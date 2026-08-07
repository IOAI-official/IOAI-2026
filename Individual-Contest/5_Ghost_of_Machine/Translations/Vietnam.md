# Bóng ma trong Cỗ máy

- **Giới hạn thời gian:** 10 phút
- **Điểm baseline:** 28.6
- **Môi trường:** một GPU (≈16 GB VRAM), không có internet
- **Kích thước lời giải:** `solution.ipynb` ≤ 20 MB
- **Dung lượng lưu trữ:** 5 GB
- **Mô hình pretrained:** chỉ **[bge-base-en-v1.5](https://yastatic.net/s3/contest/ioai/5/01_BAAI_bge-base-en-v1.5_MODEL_CARD.html)** — một **encoder** văn bản (mô hình embedding).


## Nhiệm vụ

Những điều kỳ lạ đang xảy ra tại Cơ quan Lưu trữ Quốc gia Kazakhstan. Các thủ thư nói rằng một số cuốn sách trước đây từng có kết thúc khác, nhưng không ai có thể chứng minh điều đó — mọi bản sao đều giống nhau, và mọi câu chuyện vẫn hợp lý. Bạn được mời với tư cách là một nhà nghiên cứu AI để xác định vị trí của những thay đổi.
![Bóng ma](../ghost.jpg)

Một đoạn văn bắt đầu là văn bản do con người viết và, tại một thời điểm nào đó, âm thầm chuyển
sang phần tiếp nối do một mô hình ngôn ngữ tạo ra. Khi đọc toàn bộ, nó trông giống như
một văn bản mạch lạc duy nhất — nhưng ở đâu đó giữa chừng, tác giả chuyển từ con người
sang máy. Nhiệm vụ của bạn là **tìm điểm chuyển đó: chỉ số ký tự nơi phần do
con người viết kết thúc và phần do máy viết bắt đầu**.

Mỗi mẫu là một chuỗi duy nhất `text`. Có đúng một ranh giới. Mọi thứ
trước ranh giới đó là do con người viết; mọi thứ từ đó trở đi là do máy tạo ra.

## Dataset

Các đoạn văn bản tiếng Anh thuần văn bản, mỗi đoạn có một ranh giới.

- **Phần A** (trước ranh giới): một đoạn trích từ văn bản do con người viết.
- **Phần B** (từ ranh giới trở đi): phần tiếp nối do một mô hình ngôn ngữ tạo ra,
  với điều kiện là Phần A.
- Mỗi phần có ít nhất 180 từ; tổng độ dài là ~500–800 từ.
- **`boundary_char_index`** là vị trí của **kí tự đầu tiên của Phần B**:
  `text[boundary_char_index:]` là phần do máy viết.
  `text[:boundary_char_index]` là phần do con người viết với duy nhất một khoảng trắng ngăn cách hai phần

#### Những gì bạn được cung cấp

Bạn nhận được **hai thư mục**:

| Thư mục | Số mẫu | `answers.jsonl`? | Dùng để |
|--------|---------|------------------|-----------|
| `dataset/train/` | 1,221 | ✅ có kèm | huấn luyện / fine-tune phương pháp của bạn |
| `dataset/test_public/`  | 380   | ✅ có kèm (bản sao dev) | chạy pipeline và tự chấm điểm cục bộ |

Tại **thời điểm chấm**, thư mục `dataset/test_public/` của bạn được **thay thế bằng một
tập đánh giá ẩn**. Tập này có cùng định dạng nhưng **không có `answers.jsonl`**. Notebook của bạn được chạy lại trên tập này, và `answers.jsonl` mà notebook tạo ra sẽ được chấm điểm.

- Bảng xếp hạng công khai sử dụng tập **test_leaderboard_a** ẩn (380 mẫu).

- Xếp hạng cuối cùng sử dụng tập **test_leaderboard_b** ẩn (380 mẫu).

Cả ba tập đánh giá đều có cùng kích thước và được lấy từ cùng phân phối với `train`, vì vậy điểm
`dataset/test_public/` cục bộ của bạn là một ước lượng hợp lý cho điểm trên bảng xếp hạng của bạn.

#### Định dạng trên đĩa

```
dataset/train/data.jsonl      # một JSON object trên mỗi dòng: {"id": "...", "text": "..."}
dataset/train/answers.jsonl   # {"id": "...", "boundary_char_index": 1842}
dataset/test_public/data.jsonl       # {"id": "...", "text": "..."}
dataset/test_public/answers.jsonl    # chỉ có ở bản sao dev — KHÔNG CÓ trong tập đánh giá ẩn
```

- Các id trong `answers.jsonl` khớp với các id trong `data.jsonl`.
- `dataset/train/` (có đáp án) luôn tồn tại khi bạn huấn luyện hoặc fine-tune.

## Đầu ra (định dạng bài nộp)

Bạn nộp **một notebook duy nhất, phải được đặt tên là `solution.ipynb`**. Tên tệp chính xác này là bắt buộc. Mọi tên khác đều bị từ chối mà không được chạy.

Notebook của bạn phải **đọc `dataset/test_public/data.jsonl`** và ghi một tệp duy nhất
**`answers.jsonl`** tại thư mục gốc của repository — mỗi dòng là một đối tượng JSON, ánh xạ
id của từng mẫu tới chỉ số ký tự ranh giới mà bạn dự đoán:

```json
{"id": "example_000123", "boundary_char_index": 1790}
{"id": "example_000124", "boundary_char_index": 2450}
```

- `boundary_char_index` phải là một **số nguyên thuộc `[0, len(text)]`**.
- Mỗi id trong `dataset/test_public/data.jsonl` phải xuất hiện đúng một lần. Một mẫu bị thiếu
  trong `answers.jsonl` (hoặc có giá trị không phải số nguyên / nằm ngoài phạm vi) nhận điểm 0
  cho mẫu đó.

## Chấm điểm

Với mỗi mẫu, gọi `p` là chỉ số bạn dự đoán và `t` là ranh giới thực. Điểm cho mỗi mẫu giảm theo hàm mũ theo khoảng cách ký tự:

$$\text{score} = \exp\!\left(-\frac{|p - t|}{\tau}\right) \in (0, 1], 
~ \text{where} ~ \tau = 100.$$

Điều này dẫn đến các mức điểm sau:
- **=1.0** — chính xác ký tự ranh giới;
- **≈0.78** — lệch 25 ký tự;
- **≈0.61** — lệch 50 ký tự;
- **≈0.37** — lệch 100 ký tự;
- **≈0.01** — lệch 500 ký tự.

**Điểm cuối cùng là giá trị trung bình** của điểm trên mỗi mẫu trong toàn bộ các mẫu của split
(được báo cáo trên thang điểm 0–100). Metric này tưởng thưởng việc dự đoán *gần đúng*, không chỉ chính xác tuyệt đối.

## Ràng buộc

- **Môi trường:** một GPU (≈16 GB VRAM), không có internet tại thời điểm chấm — mô hình được phép  (bên dưới) đã được cung cấp sẵn.
- **Ngân sách thời gian thực: 10 phút** cho toàn bộ lần chạy — khoảng thời gian này phải bao gồm mọi quá trình huấn luyện / fine-tune mà bạn thực hiện tại thời điểm chấm **cộng với** suy luận trên tập đánh giá.
- **Mô hình pretrained được phép** — danh sách này là đầy đủ; không được sử dụng bất kỳ trọng số pretrained nào khác. Mô hình này được **cung cấp sẵn trong môi trường** (hãy tải theo cách thông thường, ví dụ: `from_pretrained`; không có internet tại thời điểm chấm):
  - **bge-base-en-v1.5** — một **encoder** văn bản có 110M tham số (mô hình embedding). Mô hình này tạo ra embedding của câu/đoạn văn; nó không phải là mô hình ngôn ngữ sinh. 
  Bạn có thể sử dụng nó **nguyên trạng (các đặc trưng đóng băng) hoặc fine-tune nó trên split `train`** (fine-tune toàn bộ phù hợp với ngân sách 16 GB / 10 phút).
- Các công cụ cổ điển / thống kê không bị hạn chế: bạn có thể xây dựng bất kỳ mô hình dựa trên đặc trưng nào (ví dụ: các bộ phân loại hoặc hồi quy scikit-learn) trên các đặc trưng embedding do chính bạn tính toán. *Các trọng số deep learning pretrained* chỉ bị giới hạn theo danh sách bên trên.
