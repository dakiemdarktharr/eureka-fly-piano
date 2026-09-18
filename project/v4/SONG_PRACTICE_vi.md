# Luyện trực tiếp hai bài piano sau v4

Yêu cầu mới bỏ điều kiện precision trước khi luyện hoặc xem hai bài; không đặt precision thấp làm mục tiêu. Ngân sách mới là tối đa **120 phút mỗi bài**, hai lượt nối tiếp. 90% mỗi lượt dành cho tối ưu và theo dõi, 10% còn lại dành cho đánh giá toàn bài và ghi replay. Thời gian khởi tạo worker nằm trong ngân sách.

Hai bộ tham số chuyên biệt cùng khởi đầu từ adaptive seed 0 của chiến dịch `20260918T060329`. Không chọn seed theo kết quả test. CEM tiếp tục tối ưu 49 tham số bằng phần thưởng v4, quần thể 8, elite 3, bốn worker CPU. Không đổi bước thời gian vật lý, ngưỡng tiếp xúc hoặc cách ghép nốt.

Mỗi đoạn lấy toàn bộ onset trong một cửa sổ 4 giây, giữ thời lượng nốt và phân công chân từ toàn bài. Các cửa sổ không rỗng được duyệt theo thứ tự xáo trộn không lặp cho đến hết một vòng. Trạng thái cơ thể được reset giữa các đoạn; đây là hạn chế của việc luyện theo đoạn. Nhật ký ghi số ID nốt thực sự đã luyện. Nốt không phân công được chân vẫn nằm trong mẫu số. Giữ các voice event gốc, kể cả unison trùng onset: số liệu chưa phải bản chép vật lý từng phím đã được chuyên gia kiểm chứng.

Theo dõi tám đoạn trải đều bài mỗi năm thế hệ, chọn checkpoint theo F1 khi không có cảnh báo solver. Các đoạn theo dõi có thể đã được luyện, **không phải validation độc lập**. Cuối lượt, đánh giá baseline và checkpoint cố định trên toàn bài. Kết quả toàn bài không được dùng để chọn lại checkpoint. Replay xuất không phụ thuộc precision, nhưng chỉ khi mô phỏng toàn bài hoàn tất trong ngân sách. Nếu hết thời gian hoặc có lỗi, trạng thái phải ghi chưa hoàn tất; không dựng replay giả.

Đây là thực nghiệm bổ sung về điều khiển trên hai bài đã luyện, không chứng minh trí nhớ bài hát, đọc sheet, khái quát hóa hay khả năng của ruồi sinh học. Paper v4 và các số liệu thí nghiệm cũ được giữ nguyên. Kết quả mới nằm trong `runtime/runs/<run_id>` và bản tổng hợp `results/<run_id>.json`.

Chạy trong app bằng nút **Luyện hai bài piano**, hoặc `python train_songs.py --minutes 120 --workers 4`. Số phút là ngân sách **mỗi bài**. Máy cần duy trì hoạt động trong suốt lượt chạy; việc đóng cửa sổ trình duyệt không dừng worker.
