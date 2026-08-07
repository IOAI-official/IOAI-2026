# Robot Truy đuổi

- **Giới hạn thời gian:** 5 phút
- **Môi trường:** một GPU (≈16 GB VRAM), không có internet
- **Kích thước lời giải:** `solution.ipynb` ≤ 1 MB
- **Dung lượng lưu trữ:** 5 GB 

## Nhiệm vụ

Có sáu robot. Mỗi robot hoạt động trong một căn phòng nhỏ được biểu diễn bằng một lưới. Mỗi căn phòng có một vùng có thể chơi `6×6` được bao quanh bởi các bức tường, vì vậy mảng `image` đầy đủ có kích thước `8×8` (vùng có thể chơi + tường).

Mỗi robot nhận được một chỉ dẫn bằng tiếng Anh mô tả một nhiệm vụ. Ảnh chụp trạng thái có thể được lấy tại bất kỳ thời điểm nào trong khi robot đang thực hiện nhiệm vụ đó. Mục tiêu của bạn là dự đoán hành động tiếp theo của robot.

Các robot không phải lúc nào cũng đi theo đường ngắn nhất. Robot 0 có thể hành xử khác Robot 1, nhưng mỗi robot tuân theo một kiểu hành vi nhất quán riêng. Hãy sử dụng các ví dụ huấn luyện, trong đó có các hành động tiếp theo đúng, để học các kiểu hành vi này.

![Robot](../../robot.jpg)

Có ba loại nhiệm vụ:

- **đi tới** một vật thể, ví dụ `"approach the red ball"`;
- **nhặt** một vật thể, ví dụ `"grab the blue key"`;
- **đặt một vật thể cạnh một vật thể khác**, ví dụ
  `"place the red box beside the green ball"`.

Cùng một chỉ dẫn có thể được viết theo nhiều cách. Tập kiểm tra có thể chứa các tổ hợp mới của những cụm từ, màu sắc và loại vật thể quen thuộc. Tuy nhiên, mọi từ, mẫu cụm từ, màu sắc, loại vật thể và loại nhiệm vụ được sử dụng trong tập kiểm tra cũng xuất hiện trong tập huấn luyện.

Mỗi mẫu có các trường sau:

| Trường | Ý nghĩa |
|---|---|
| `robot_id` | đây là robot nào trong số 6 robot (`0`–`5`) |
| `image` | căn phòng, một mảng số nguyên `8×8×2` trong đó kênh 0 chứa object_idx dạng phân loại (ví dụ: 1=ô trống, 2=tường, 10=robot) và kênh 1 chứa colour_idx dạng phân loại (0–5). |
| `direction` | hướng mà robot hiện đang quay mặt |
| `mission` | chỉ dẫn ngôn ngữ tự nhiên nhìn thấy được |
| `carrying` | `null` hoặc `[object_idx, colour_idx]` đối với vật thể đang được mang |

Các hàng là những ảnh chụp trạng thái độc lập theo thứ tự ngẫu nhiên. Chúng không tạo thành các episode, và không có quan sát hay hành động trước đó tại thời điểm đánh giá.

`visualize_dataset.ipynb` được cung cấp cho phép bạn kiểm tra các quan sát mà mô hình có thể sử dụng trong những tình huống khác nhau.

## Mã hóa lưới

`image[row][column] = [object_idx, colour_idx]`. Chỉ số thứ nhất là hàng theo chiều từ trên xuống dưới, và chỉ số thứ hai là cột theo chiều từ trái sang phải. Mảng bao gồm đường viền tường bên ngoài, vì vậy phần nội thất có thể di chuyển là `6×6`.

ID vật thể:

| id | vật thể |
|---:|---|
| 1 | ô trống |
| 2 | tường |
| 5 | chìa khóa |
| 6 | quả bóng |
| 7 | hộp |
| 10 | robot |
| 11 | token |

Các token có thể xuất hiện trong phòng nhưng không bao giờ được nhắc tên trong nhiệm vụ.

ID màu là `0` đỏ, `1` xanh lá, `2` xanh dương, `3` tím, `4` vàng và `5` xám. Kênh màu không có ý nghĩa đối với các ô trống và tường.

Ảnh chỉ có hai kênh nêu trên. Hướng của robot được cung cấp một lần trong trường `direction` cấp cao nhất; hướng này không được lặp lại bên trong `image`.

## Hành động

Đối với các mã `0`–`3`, các hành động di chuyển sử dụng ánh xạ tuyệt đối sau:

| hành động | ý nghĩa |
|---:|---|
| 0 | di chuyển lên |
| 1 | di chuyển xuống |
| 2 | di chuyển sang trái |
| 3 | di chuyển sang phải |
| 4 | nhặt |
| 5 | thả |


Trường `direction` cho biết hướng quay mặt hiện tại bằng cách sử dụng: 0 = Lên (hàng - 1), 1 = Xuống (hàng + 1), 2 = Trái (cột - 1), 3 = Phải (cột + 1).

Một hành động di chuyển trước tiên xoay robot theo hướng tuyệt đối đó, rồi thử di chuyển robot một ô. Một bức tường hoặc vật thể có thể chặn chuyển động, nhưng hướng vẫn thay đổi. `pick up` và `drop` chỉ tác động lên ô đích liền kề được xác định bởi hướng (ví dụ: nếu direction=0, hành động tác động lên (row - 1, col)).

## Dataset

Bạn nhận được hai thư mục:

| Thư mục | Số hàng | `labels.json`? | Dùng để |
|---|---:|---|---|
| `dataset/train/` | 60,000 | có | huấn luyện mô hình của bạn |
| `dataset/test_public/` | 3,600 | có trong bản phát triển | chạy và tự chấm điểm pipeline của bạn |

Mỗi thư mục chứa `observations.json`, một danh sách JSON gồm các mẫu được mô tả
ở trên. `labels.json` là một danh sách JSON các hành động được căn chỉnh tương ứng (`0`–`5`).

Tập huấn luyện chứa chính xác 10,000 hàng cho mỗi robot và 20,000 hàng từ mỗi
nhóm nhiệm vụ. Tập kiểm tra công khai chứa 600 hàng cho mỗi robot. Hãy bọc `image` bằng
`numpy.asarray(...)` nếu bạn cần một mảng.

Tại thời điểm chấm điểm, `dataset/test_public/` được thay thế một cách trong suốt bằng một tập ẩn gồm
3,600 quan sát có cùng định dạng, nhưng không có `labels.json`. Bảng xếp hạng
công khai sử dụng `test_leaderboard_a`; thứ hạng cuối cùng sử dụng
`test_leaderboard_b`. Một notebook đọc nhãn kiểm tra vô điều kiện sẽ thất bại.
Chỉ đọc nhãn từ `dataset/train/`.

## Đầu ra

Ghi `predictions.json` vào thư mục làm việc của notebook. Tệp này phải là một danh sách JSON
chứa một hành động số nguyên (`0`–`5`) cho mỗi hàng của
`dataset/test_public/observations.json`, theo cùng thứ tự. Đối với một tập kiểm tra giả định chứa sáu mẫu, một đầu ra hợp lệ sẽ là:

```json
[0, 3, 2, 2, 5, 4]
```

Tệp JSON bị thiếu hoặc không hợp lệ, số lượng dự đoán không đúng, một giá trị không phải số nguyên,
hoặc một hành động nằm ngoài `{0,1,2,3,4,5}` sẽ bị từ chối mà không được chấm điểm.

## Chấm điểm

Điểm số là **độ chính xác trung bình theo từng robot** trên thang `0`–`100`. Độ chính xác trước tiên
được tính độc lập cho từng robot, sau đó được lấy trung bình trên cả sáu robot. Do đó, mỗi
robot có trọng số bằng nhau.

## Cách nộp bài

1. Mở `solution.ipynb` và chạy tất cả các ô.
2. Xác nhận rằng tệp này ghi `predictions.json` với 3,600 dự đoán cho tập kiểm tra
   công khai.
3. Cải thiện mô hình nếu bạn muốn; baseline được cung cấp chỉ minh họa
   định dạng đầu vào và đầu ra bắt buộc.
4. Trong thẻ Git của JupyterLab, stage và commit `solution.ipynb`, sau đó push tệp đó.
5. Quay lại trang Cuộc thi và nhấp vào **Nộp bài**.

Chỉ nộp đúng một tệp có tên `solution.ipynb`.
