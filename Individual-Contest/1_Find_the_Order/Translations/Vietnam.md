# Tìm thứ tự

- **Giới hạn thời gian:** 10 phút (thoi gian tune va inference cho moi luot danh gia, co giai thich ben duoi)
- **Môi trường:** một GPU (≈16 GB VRAM), không có internet
- **Kích thước lời giải:** `solution.ipynb` ≤ 1 MB
- **Dung lượng lưu trữ:** 5 GB 

## Bài toán

Bạn được cung cấp các đoạn hội thoại tiếng Anh bằng lời nói giữa hai người tham gia, *Người nói A* và *Người nói B*. Mỗi đoạn hội thoại được phân chia thành các lượt nói, trong đó mỗi lượt chỉ chứa lời nói của một người. Mỗi lượt được lưu dưới dạng một tệp âm thanh `.wav` riêng biệt, vì vậy một đoạn hội thoại hoàn chỉnh được biểu diễn bằng một tập hợp các tệp `.wav`, mỗi tệp tương ứng với một lượt. 

Đáng tiếc là các lượt đã bị xáo trộn ngẫu nhiên, nên cuộc hội thoại không còn hợp lý. Trong tên tệp `chunk_{k}.wav`, `k` chỉ đoạn thứ k trong tập đã bị xáo trộn, chứ không phải lượt thứ k trong đoạn hội thoại gốc.

**‼️ Nhiệm vụ của bạn là khôi phục thứ tự thời gian ban đầu của cuộc hội thoại.**

![Tìm thứ tự](../find_the_order.jpg)

---

## Dataset

Mỗi đoạn hội thoại chứa các tệp âm thanh `n` có tên `chunk_0.wav`, `chunk_1.wav`, …, `chunk_{n-1}.wav`. Các đoạn là những lượt nói riêng lẻ. Tên tệp chỉ tương ứng với thứ tự đã bị xáo trộn. Chúng không cho biết vị trí của một đoạn trong cuộc hội thoại gốc. Mỗi đoạn hội thoại có 7–20 đoạn, đơn kênh, 44.1 kHz (bạn có thể
lấy mẫu lại).

**`prefix.json` chứa các chỉ số tên tệp của hai đoạn đầu tiên trong mỗi cuộc hội thoại.** Thông tin này xác định phần mở đầu thực sự của đoạn hội thoại và loại bỏ sự mơ hồ giữa việc đọc cuộc hội thoại theo chiều xuôi hoặc chiều ngược.

Ví dụ: `11: [7, 12]` có nghĩa là lượt thứ nhất và thứ hai của đoạn hội thoại 11 lần lượt là `chunk_7.wav` và `chunk_12.wav`.

### Những gì bạn nhận được

Bạn nhận được **hai thư mục có định dạng giống hệt nhau**:

| Thư mục | Đoạn hội thoại | `answers.json`? | Dùng để |
|--------|-----------|-----------------|-----------|
| `dataset/train/` | 1,288 | ✅ có | huấn luyện / tinh chỉnh mô hình của bạn |
| `dataset/test_public/`  | 100   | ✅ có | chạy pipeline và tự chấm điểm cục bộ |

Trong thời gian chấm điểm, thư mục `dataset/test_public/` của bạn được thay thế một cách minh bạch bằng
một `hidden evaluation set` (`test_leaderboard_a` cho bảng xếp hạng công khai và `test_leaderboard_b` cho bảng xếp hạng cuối cùng) — các thư mục này có cùng kích thước và định dạng với `dataset/test_public/` nhưng không có `answers.json`.

Notebook của bạn được thực thi lại trên dữ liệu đó, và tệp `answers.json` mà nó tạo ra được dùng để chấm điểm. Các đoạn hội thoại kiểm thử được giữ lại đến từ cùng một phân phối với `train` (ty le phan bo difficutly cua cac cau giong voi train), vì vậy điểm `test_public` cục bộ của bạn là một bản xem trước đáng tin cậy.

### Cấu trúc thư mục

```bash
dataset/train/
    prefix.json  # {dialogue_id: [first_idx, second_idx]} filename index 
    answers.json  # {dialogue_id: P}  ground-truth order (rank convention)
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

## Đầu ra

Đối với mỗi đoạn hội thoại, hãy xác định thứ tự thời gian ban đầu của các đoạn âm thanh. Dự đoán của bạn phải là một hoán vị `P` của `{0, 1, …, n−1}`, trong đó `P[i]` là vị trí thời gian được dự đoán của `chunk_i.wav` (0 = đầu tiên).

Tệp đầu ra `answers.json` của bạn phải ánh xạ mỗi ID đoạn hội thoại tới hoán vị được dự đoán của nó:

```json
{
  "17": [2, 0, 1],
  "42": [0, 1],
  "108": [3, 1, 0, 4, 2, 5]
}
```

### Ví dụ

Một đoạn hội thoại có 3 đoạn đã bị xáo trộn `chunk_0, chunk_1, chunk_2`:

| đoạn đã bị xáo trộn | nội dung lời nói | vị trí thực (hạng) |
|----------------|----------------|----------------------|
| `chunk_0.wav` | *"No worries — I'll send you the notes afterwards."* | 2 (cuối cùng) |
| `chunk_1.wav` | *"Hey, are you coming to the three o'clock meeting?"* | 0 (đầu tiên) |
| `chunk_2.wav` | *"I can't — I've got a dentist appointment then."* | 1 |

Thứ tự thực là **chunk_1 → chunk_2 → chunk_0**, do đó `P = [2, 0, 1]`, và `prefix.json` chứa `[1, 2]`.

⚠️ **P phải là một hoán vị hợp lệ:** độ dài n, được đánh chỉ số từ 0, mỗi giá trị xuất hiện đúng một lần. Các giá trị trùng lặp, bị thiếu hoặc nằm ngoài phạm vi (ví dụ: được đánh chỉ số từ 1) sẽ nhận điểm 0 cho đoạn hội thoại đó; một đoạn hội thoại bị thiếu trong tệp cũng vậy (bai nop thieu mot doan hoi thoai so voi file goc ban dau). Tệp sai định dạng hoặc không phải JSON sẽ bị từ chối.

## Chấm điểm

Cách chấm điểm cho nhiệm vụ này là **độ chính xác thứ tự theo cặp**. Cách chấm này kiểm tra mọi cặp đoạn và đặt câu hỏi: _đoạn nào trong hai đoạn phải xuất hiện trước?_ Một cặp là đúng nếu dự đoán của bạn đưa ra cùng câu trả lời với đáp án chuẩn. Đối với một đoạn hội thoại có `n` đoạn, có $$M = n(n-1)/2$$ cặp; gọi `I` là số nghịch thế — các cặp được sắp xếp khác với đáp án chuẩn:

$$\text{score} = 1 - \frac{I}{M} \in [0, 1]$$

ℹ️ **Điểm cuối cùng là trung bình của điểm theo từng đoạn hội thoại trên tất cả
các đoạn hội thoại trong tập phân chia.**

## Các mô hình được phép

Bạn chỉ có thể sử dụng các mô hình được huấn luyện trước sau đây để giải quyết nhiệm vụ này, cả trong quá trình huấn luyện lẫn đánh giá. Tất cả các mô hình này đã được tải xuống và có sẵn trong môi trường. Bạn có thể xem các ví dụ về cách sử dụng chúng trong notebook baseline `solution.ipynb`. Xin lưu ý rằng bạn không thể sử dụng bất kỳ mô hình nào khác và chương trình của bạn không có quyền truy cập internet.

- **Biểu diễn tiếng nói:** **wav2vec 2.0**. **Whisper encoder** cũng có thể được sử dụng làm bộ trích xuất đặc trưng.
[Thẻ mô hình wav2vec](https://yastatic.net/s3/contest/ioai/1/01_facebook_wav2vec2-base-960h_MODEL_CARD.html)

- **Nhận dạng tiếng nói tự động (ASR):** **OpenAI Whisper** (bất kỳ kích thước nào).
[Thẻ mô hình Whisper](https://yastatic.net/s3/contest/ioai/1/03_openai_whisper-small_MODEL_CARD.html)
- **Mô hình ngôn ngữ:** **Qwen2.5-0.5B**, có thể được sử dụng theo phương thức zero-shot hoặc được tinh chỉnh trên tập phân chia `train` được cung cấp.
[Thẻ mô hình Qwen](https://yastatic.net/s3/contest/ioai/1/02_Qwen_Qwen2.5-0.5B_MODEL_CARD.html)
Lưu ý rằng giới hạn 10 phút phải bao gồm mọi hoạt động huấn luyện hoặc tinh chỉnh mà bạn thực hiện tại thời điểm chấm điểm, cộng với suy luận trên tập đánh giá.

## Cách nộp bài

- Mở `solution.ipynb` và chạy tất cả các ô. Xác nhận rằng notebook ghi `answers.json` vào thư mục làm việc với một hoán vị cho mọi đoạn hội thoại trong `dataset/test_public/` (100 đoạn hội thoại). Tại thời điểm chấm điểm, notebook được chạy lại trên tập kiểm thử ẩn và tệp `answers.json` mà nó tạo ra tại đó được chấm điểm.
- Cải thiện lời giải nếu bạn muốn — hoặc không; chỉ riêng baseline cũng xác thực pipeline.
- Mở tab Git trong thanh bên trái của JupyterLab.
- **Stage** `solution.ipynb` (biểu tượng + bên cạnh tệp).
- Nhập thông điệp commit và nhấp vào **Commit**.
- Nhấp vào biểu tượng đám mây có mũi tên hướng lên để push.
- Quay lại trang Cuộc thi này và nhấp vào **Submit**.

Chỉ nộp đúng một tệp, có tên `solution.ipynb`.
