# Fly Piano v5 — 100 nốt và hoạt động từng neuron

Phiên bản này bổ sung quan sát tín hiệu từng neuron và đổi đơn vị episode thành **100 sự kiện nốt yêu cầu**. V4 cùng số liệu nghiên cứu cũ được giữ riêng. V5 vẫn là mô hình mạch vận động gồm 412 neuron, không phải mô phỏng động lực học toàn bộ não ruồi.

## Mở chương trình

Chạy `Start-FlyPianoV5.ps1`, hoặc `dist/FlyPianoLabV5/FlyPianoLabV5.exe`. Giao diện ở http://127.0.0.1:8879/. Cổng 8878 dành cho v4. Chọn “Kiểm tra 100 nốt”, phát mô phỏng hoặc kéo thanh thời gian. Khung MANC cho xoay, phóng to, lọc T1/T2/T3, chỉ hiện neuron active và chọn nhánh để xem bodyId, cell type cùng trace. Heatmap có đủ 412 kênh.

Não FlyWire và VNC MANC được trình bày riêng vì chúng thuộc hai mẫu khác nhau. Hai DNg100 trong khung não là phép chiếu tín hiệu lên neuron đồng dạng, không phải synapse đã đo nối hai mẫu. Giao diện không tạo tín hiệu cho optic lobes, mushroom bodies hay các vùng ngoài mạch hiện tại.

## Đọc điểm đúng cách

- Số nốt đúng trên 100 = matched / 100, tương ứng recall của bài kiểm tra này.
- Precision = matched / số lần bấm thực tế. Một mô hình bấm rất ít không được điểm cao chỉ vì tránh bấm sai.
- F1 kết hợp precision và recall. Ghép một-một cùng cao độ, sai số onset tối đa ±100 ms; bấm thừa không kiếm được thưởng nhiều lần.
- 100 nốt là 100 **sự kiện**, có thể lặp cao độ; không có nghĩa đàn có 100 phím. Chuỗi tổng hợp hiện tại lấy các phím trong phạm vi IK thuận lợi của mỗi chân, không đại diện đồng đều cả 88 phím.

Mỗi candidate trong luyện hai bài được đánh giá trên một block đúng 100 sự kiện gốc. Block cuối chồng lấn để đủ 100; hợp âm có thể bị cắt ở ranh giới block. Mọi sự kiện vẫn nằm trong lịch lấy mẫu, kể cả nốt trùng và nốt chưa gán chân. Đánh giá/replay toàn bài giữ đủ 2.401 và 1.502 nốt. Điểm block và điểm toàn bài là hai phép đo khác nhau.

Không dừng sớm theo precision. Ngân sách tối đa 120 phút/bài, 90% dành cho tối ưu và 10% dự phòng đánh giá/xuất replay. Các đoạn theo dõi thuộc chính bài luyện; chúng không phải test khái quát hóa. Nếu không đủ thời gian xuất toàn bài, trạng thái ghi rõ incomplete.

## Tín hiệu và giải phẫu

Mỗi frame lưu trực tiếp toàn bộ vector `net.r` của 412 neuron, kèm thứ tự bodyId. Viewer ghép theo ID, không lấy vị trí hàng làm định danh ngầm. Thang sáng 0–50 đơn vị rate; ngưỡng active > 1 chỉ là lựa chọn hiển thị. Đây không phải spike, Hz được hiệu chuẩn hay calcium thực nghiệm. Một neuron sáng không chứng minh nó đã học hoặc cần thiết về nhân quả cho tác vụ.

Tải được 412 SWC; bảng metadata độc lập xác nhận 412/412 bodyId và cell type trùng. 410 file có tọa độ µm tương thích với mesh VNC. Hai file DNg100 (10093, 10339) có tọa độ không tương thích, bị loại khỏi view VNC thay vì tự đoán phép biến đổi. Tín hiệu của chúng vẫn nằm trong heatmap và bảng vùng. Mỗi neuron giữ tối đa 600 **đoạn cạnh thật** để hiển thị; không nối các điểm không liên quan. Không dùng bản hiển thị rút gọn để sửa trọng số mạng.

`prepare_neuroanatomy.py` tái tạo dữ liệu từ kho công khai của nhóm BANC/MANC, ghi URL và SHA-256. MANC được ghi công theo CC-BY; xem nguồn trong báo cáo nghiên cứu. `assets/raw/` và file hiển thị lớn không đưa lên Git. Bản Windows cục bộ có file hiển thị đã chuẩn bị.

## Thay đổi cơ chế học

Giữ CEM và reward theo tiếp xúc vật lý. Bổ sung sáu gain 0–50 cho tín hiệu mục tiêu có lookahead 150 ms tới E1 của từng chân, đưa tổng tham số lên 55. Đây là đường vào **thiết kế**, không phải đường thị giác–vận động đã được xác nhận. Tín hiệu dùng ở bước điều khiển tiếp theo, trễ 2 ms. Checkpoint cũ được thêm sáu số 0 để giữ hành vi ban đầu.

Thử nghiệm chẩn đoán 100 nốt với cue 0, 10 và 30 đều được 17 nốt đúng/54 lần bấm: P=31,48%, R=17%, F1=22,08%; không có cảnh báo solver. Chưa có bằng chứng cue giúp cải thiện. Ở checkpoint này, gate của bốn chân bão hòa ở 1 và hai chân ở 0 trong replay, nên độ nhạy của bộ giải mã vận động là một hạn chế đáng kiểm tra tiếp. Không dùng ba kết quả này để chọn warm start.

V5 lưu snapshot optimizer gồm mean, sigma, RNG và best để kiểm toán. Nút luyện hiện tạo lượt mới; chưa có chức năng khôi phục chính xác một lượt bị dừng. Khi chuyển từ v4, checkpoint được dùng làm warm start và thời gian đã dùng được trừ khỏi ngân sách, nhưng optimizer khởi tạo lại do protocol thay đổi. Không gọi việc này là resume chính xác.

## Tái lập và kiểm tra

Dùng Python của v4: `../v4/.venv/Scripts/python.exe`. Chạy các script từ thư mục gốc repo:

```text
project/v4/.venv/Scripts/python.exe project/v5/prepare_neuroanatomy.py
project/v4/.venv/Scripts/python.exe -m unittest discover -s project/v5 -p "test_*.py"
project/v4/.venv/Scripts/python.exe project/v5/validate_hundred.py
project/v4/.venv/Scripts/python.exe project/v5/analyze_activity.py
project/v4/.venv/Scripts/python.exe project/v5/verify_worker.py
project/v4/.venv/Scripts/python.exe project/v5/app.py
```

`validate_hundred.py` là một chẩn đoán seed đơn, không đủ cho kết luận thống kê về học. Kết quả, trace neuron CSV, nguồn nghiên cứu và kiểm tra ID nằm trong `results/` và `research/`. Muốn so sánh thuật toán cần nhiều seed, ngân sách bằng nhau, bài test chưa luyện, ablation cue/feedback/connectome và kiểm tra sheet độc lập.

Các dữ liệu mô hình v2/connectome và sheet riêng vẫn cần có trên máy; repo không tự chứa toàn bộ tài sản riêng. Không build lại thư mục `dist` khi app ở đó đang chạy vì PyInstaller thay thế thư mục này; sao lưu runtime trước khi build.
