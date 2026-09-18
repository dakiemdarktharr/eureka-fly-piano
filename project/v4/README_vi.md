# Fly Piano Lab v4

App nghiên cứu học điều khiển tiếp xúc của một mô hình ruồi với prior connectome. Đây là bộ điều khiển lai: scheduler/IK nhận mục tiêu nốt; mạng điều biến động tác ấn. Không phải mô phỏng toàn bộ não, đọc sheet bằng mắt hay chứng minh khả năng ruồi sinh học.

## Mở app

Trên máy đã đóng gói, chạy `dist/FlyPianoLabV4/FlyPianoLabV4.exe` hoặc `Start-FlyPianoV4.ps1`. App mở ở `http://127.0.0.1:8878`. Bundle là thư mục, cần giữ nguyên EXE và `_internal` cùng dữ liệu runtime. Không cần cài Python để dùng bundle. Đừng công khai bundle riêng có sheet và input chưa rõ quyền phân phối.

Từ source: tạo môi trường Python 3.12, cài `requirements.txt`, cung cấp các private input kế thừa v2 rồi chạy `python project/v4/app.py`. API `/api/health` liệt kê input thiếu. MuJoCo được khóa ở 3.9.0; torch và MuJoCo Warp không phải dependency của learner. Chúng chỉ được cài trong môi trường khảo sát tăng tốc; GPU probe bị chặn do noslip.

## Cách đọc giao diện

Thời gian thực là wall-clock của chiến dịch. Giây mô phỏng cộng dồn gồm chín ô thí nghiệm và cả đánh giá. Cột trải nghiệm học của từng ô chỉ tính bước đã dùng trong tối ưu. CEM chạy nhiều ứng viên và reset mỗi episode, nên không có "một con ruồi sống liên tục" tương ứng tổng này.

Biểu đồ là F1 validation, bảng cuối dùng test khi có. Nút tạo chiến dịch mới dùng tối đa 60 phút chung cho tất cả ô. Nút dừng kết thúc tối ưu sau lô hiện tại và chạy đánh giá checkpoint đã chọn; không tiếp tục học trên cùng test của run đã kết thúc. Kết quả v4a thăm dò và v4b chính của lần phát triển này được tính chung dưới trần một giờ, chi tiết trong paper.

Nốt rơi có cửa sổ 150 ms; màu vàng là mục tiêu, màu xanh là tiếp xúc thật. Thanh nốt không tác động vật lý. Brain viewer chỉ chiếu rate DN lên hai DNg100 đồng dạng, không hiển thị toàn bộ các synapse VNC được học. Có thể nghe mục tiêu hoặc nốt tiếp xúc, hai nguồn được ghi rõ.

Hai bản Merry-Go-Round of Life và In The Pool chỉ mở thành demo toàn bài sau khi primary adaptive seed 0 đạt skill P/R >=95% và sequence P>85%, R/F1>=85% trên test giữ riêng. Nếu không đạt, app giữ replay kỹ năng chẩn đoán; không tự phát hai bài bằng MIDI mục tiêu để giả làm hành vi đã học. Source hai bài vẫn giữ đầy đủ; OMR chưa note-by-note verified.

## Mô hình học

49 tham số: 24 hệ số synapse theo nhóm (giữ graph/sign), 6 kích thích MN, 6 gate gain, 6 press extension, 6 lateral correction, 1 press advance. CEM population 10 / elite 3; ba seed; adaptive, fixed-synapse và degree-preserving rewired. Fixed-synapse vẫn học 25 tham số còn lại, không phải mạng hoàn toàn cố định.

Mô hình vật lý giữ dt 0,2 ms, control/rate 2 ms, noslip 5 và solver iterations 50. CPU batching giữ đúng thứ tự 1 step -> contact sample -> 9 steps. Parallelism là nhiều world/candidate độc lập; không nhảy qua thời gian vật lý.

## Lệnh kiểm tra và tái lập

```text
python project/v4/test_protocol.py
python project/v4/benchmark.py
python project/v4/train.py --minutes 60 --workers 4
python project/v4/train.py --export RUN_ID
python project/v4/build_paper.py --run RUN_ID
docker compose -f compose.v4.yaml up --build
```

`build_paper.py` cần matplotlib, ReportLab và font Arial trên Windows; app không cần chúng. Script paper hiện tái dựng báo cáo phát triển v4a/v4b đã khóa, không phải trình tạo bài tự động cho mọi dataset tùy ý. Giấy phép và attribution asset kế thừa trong `project/v2/assets`.

Container mount dữ liệu riêng chỉ đọc và một volume trạng thái; mặc định cổng host chỉ bind localhost. Mã nguồn/repo không gồm sheet riêng, matrix/input chưa được cấp phép đầy đủ, môi trường Python hay bundle Windows. CI không có private input nên chỉ chạy các kiểm tra protocol độc lập dữ liệu và kiểm tra app khởi động; kiểm tra cơ học/replay đầy đủ được thực hiện cục bộ.

## Tài liệu và giới hạn

Paper và hồ sơ phản biện ở `output/pdf`; source tiếng Việt, figure, CSV và evidence ở `paper`. Deep search, benchmark và lỗi GPU ở `research`. V3 không bị chỉnh sửa. Đây là pilot kỹ thuật, chưa chứng minh ưu thế connectome, hội tụ cơ học hoặc đạt chuẩn nộp Q2.
