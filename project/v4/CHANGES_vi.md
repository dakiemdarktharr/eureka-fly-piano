# Những gì đã thay đổi trong v4

| Yêu cầu | Kết quả thực hiện |
|---|---|
| Deep search tăng tốc | 3 hướng, 9 truy vấn Exa, 38 URL kết quả duy nhất; báo cáo nguồn và quyết định trong research |
| Một năm mô phỏng / một giờ thực | Đã tính yêu cầu 8.766x và đo máy thật; chưa đạt. Không tạo một quy đổi giả |
| GPU | Đã nhận RTX 5050 8 GiB và thử MuJoCo Warp; bị chặn do noslip. CPU chuẩn được giữ |
| Tăng tốc đã áp dụng | Batching các bước giữ control, 4 worker tồn tại lâu, cache mạng/model, không render khi học |
| Giữ fidelity | dt 0,2 ms, control 2 ms, noslip 5, solver 50; probe scalar/batched cho qpos và note events giống nhau |
| Thời gian học tối đa một giờ | Lượt thăm dò và lượt cuối cùng tính chung; có bảng kế toán wall time và bước mới. Dev/benchmark/export tách riêng |
| Học tham số thần kinh | 24 hệ số synapse có ràng buộc graph/sign và 6 hệ số kích thích MN, cùng 19 readout parameters |
| Sửa lỗi vị trí tiếp xúc | Thêm học bias ngang giữa đích IK và mặt collision; chưa thay bằng inverse contact kinematics hoàn chỉnh |
| Reward mới | Thưởng đúng một-một, phạt thiếu/thừa, duration IoU, timing, shaping nhỏ và công actuator; không mô phỏng dopamine |
| Đối chứng | Adaptive, fixed-synapse, degree-preserving rewired; ba seed; fixed-synapse vẫn học phần còn lại |
| Mốc thời gian | History mỗi thế hệ và bảng validation tại 5/15/30/45 phút khi đủ thời gian; không liên tục xem test |
| Hai bản nhạc | Giữ nguyên input đầy đủ; không dùng để tối ưu; chỉ mở demo v4 khi skill và sequence test đạt chuẩn |
| Piano Tiles trong 3D | Nốt rơi cùng cửa sổ cục bộ 150 ms, đúng vị trí phím; thanh chỉ hiển thị, không tạo lực |
| Não 3D | Bề mặt FlyWire và hai DNg100 đồng dạng, chiếu rate mô hình; không tô giả toàn não hoặc gọi là calcium đo được |
| App hoàn chỉnh | Dashboard, replay/audio, job controls có token, đọc PDF/log, bundle Windows tự chứa, Docker và CI |
| Paper v4 tiếng Việt | Bản thảo phương pháp/kết quả cùng hồ sơ 37 vấn đề reviewer, cách xử lý chính và fallback |
| Bảo toàn v3 | Không sửa mã/paper/log v3; v4 là thư mục và commit mới |

Những điều chưa được coi là hoàn tất về khoa học: hiệu chuẩn cơ học/timestep, điều khiển end-to-end không IK, lợi ích nhân quả của connectome, test OOD rộng, ground truth nhạc được kiểm tra độc lập và quyền tái phân phối đầy đủ. Bản thảo không cam kết acceptance Q2 hoặc kết luận về giới hạn học của ruồi sinh học.
