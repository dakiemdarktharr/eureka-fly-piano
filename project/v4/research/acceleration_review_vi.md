# Tăng tốc học điều khiển ruồi: kết quả nghiên cứu và quyết định v4

Ngày tra cứu: 18/09/2026. Exa được dùng cho 3 hướng: tăng thông lượng vật lý CPU, tăng thông lượng GPU, tăng hiệu quả học. Có 9 truy vấn với 45 vị trí kết quả yêu cầu; parser ghi nhận 44 kết quả và 38 URL kết quả duy nhất. Đây không phải 45 bài báo đã đọc đầy đủ. Nhật ký URL nằm trong search_audit.json. Tài liệu chính thức và nghiên cứu gốc được ưu tiên; kết quả quảng bá tốc độ không được chuyển thẳng sang mô hình ruồi hiện tại.

## 1. Một năm trong một giờ nghĩa là gì?

Lấy một năm bằng 365,25 ngày: RTF cần thiết = 365,25 x 24 = 8.766. Với bước vật lý 0,0002 s, cần 43.830.000 bước vật lý mới/giây thực. Không được đạt con số này bằng cách đổi nhãn thời gian, phát video nhanh, nhân số epoch, hay đọc lại buffer. Trải nghiệm của các môi trường song song có thể cộng để đo chi phí tìm chính sách, nhưng không trở thành một đời trải nghiệm liên tục của một con ruồi.

Trong v4, CEM thử nhiều bộ tham số khác nhau, và 9 ô thí nghiệm là 3 seed x 3 loại mạng. Vì vậy cần báo riêng: tổng tất cả bước, bước dùng để tối ưu từng ô, bước validation/test, và bước xuất replay. Mỗi episode đặt lại trạng thái cơ thể và mạng. Không có bằng chứng về trí nhớ liên tục kéo dài hàng năm.

## 2. Những hướng đã khảo sát

| Hướng | Bằng chứng và điều kiện | Quyết định cho v4 |
|---|---|---|
| Gom mj_step khi control không đổi | Python binding có nstep; giảm lần vào Python/GIL. Không được gom qua mốc cần phản hồi | Áp dụng mẫu 1 bước - đo tiếp xúc - 9 bước; giữ dt 0,2 ms và phản hồi 2 ms |
| Tiến trình CPU tồn tại lâu | Mỗi tiến trình giữ model/data riêng; tránh khởi tạo lại mesh trong từng episode | Áp dụng 4 worker, cache mẫu mạng theo seed/variant, không render lúc học |
| mujoco.rollout trong C++ | API chính thức có thread pool; nhận chuỗi điều khiển open-loop, state và warmstart | Chưa dùng cho vòng kín hiện tại vì phải bảo toàn phản hồi tiếp xúc mỗi 2 ms. Có thể dùng cho replay điều khiển đã ghi |
| MuJoCo Warp | Nhắm tới nhiều world song song trên NVIDIA; một world không nhất thiết nhanh hơn CPU | Probe trên RTX 5050 8 GiB thất bại do noslip solver chưa hỗ trợ; không tắt để lấy số tốc độ |
| Giảm số iteration solver | Có thể tăng tốc nhưng thay đổi nghiệm tiếp xúc | Không áp dụng khi chưa có kiểm thử lực, độ lún, trượt và sự kiện nốt |
| Tăng timestep hoặc giảm tần số điều khiển | Tăng giây mô phỏng mỗi lần gọi nhưng có thể bỏ lỡ va chạm và làm đổi tác vụ | Không áp dụng; v2 chưa chứng minh hội tụ theo timestep |
| Bỏ visual mesh khỏi training model | Có thể giảm tải tài nguyên; phải giữ nguyên collision/inertia | Không sửa collider. V4 đã bỏ tạo scene JSON và frame trong vòng tối ưu |
| Sparse neural operator | Graph 412 node, 2.592 cạnh; phép nhân CSR tránh ma trận đặc | Giữ CSR; không chuyển mạng nhỏ sang GPU để tránh copy host-device mỗi 2 ms |
| Curriculum | Học hành vi đơn giản trước chuỗi khó làm giảm khó khăn thăm dò | Áp dụng 6 nốt chậm, cao độ thuộc nhóm reachable; mở rộng sau chuẩn validation |
| Reward có shaping | RoboPianist dùng mức nhấn phím, vị trí ngón và năng lượng; thưởng đúng đơn thuần khó khám phá | Áp dụng thưởng sự kiện ghép một-một và shaping nhỏ có chặn. Không gọi là dopamine sinh học |
| Replay buffer / nhiều gradient update | Có thể tăng hiệu quả từ mẫu; không tạo trải nghiệm vật lý mới | Không dùng trong CEM v4; không cộng số lần đọc dữ liệu vào giây mô phỏng |
| Imitation teacher / surrogate / coarse-to-fine | Có triển vọng giảm số rollout đắt, nhưng gây phụ thuộc teacher và sai lệch mô hình | Hướng tiếp theo, cần đánh giá cuối trên cùng mô hình vật lý chuẩn và báo riêng dữ liệu teacher |

## 3. Bằng chứng thực nghiệm trên máy này

AMD Ryzen AI 5 340, 6 core / 12 thread; NVIDIA RTX 5050 Laptop, 8.151 MiB theo nvidia-smi. MuJoCo 3.9.0, NumPy 2.5.3. Probe GPU dùng mujoco-warp 3.9.0.1 và Warp 1.17.0; lỗi noslip được tái hiện sau khi khóa MuJoCo 3.9.0. Model có 214 qpos / 214 velocity coordinates, 157 geom, 42 actuator; đây là một cảnh có tiếp xúc khá lớn, không tương đương benchmark cart-pole.

Benchmark CPU trước tối ưu cuối cùng gồm một chuỗi 3 nốt, 10.350 bước mỗi rollout. Sáu lần chạy xen kẽ bật/tắt batching cho sai khác qpos cuối bằng 0 và danh sách sự kiện giống hệt. RTF các lần batched: 2,930; 3,270; 2,817; scalar: 2,689; 2,786; 2,376. Đây là kiểm tra tương đương thực thi cho cùng mô hình, không phải xác nhận mô hình đúng sinh học.

Thông lượng với 12 rollout và worker đã khởi tạo: 1 worker = 3,425x; 2 = 7,399x; 3 = 11,603x; 4 = 13,807x. Không có cảnh báo solver trong các rollout này. Tốc độ bốn worker vẫn thấp hơn 8.766x khoảng 635 lần. Kết quả ngắn chưa đo ổn định nhiệt lâu dài; tốc độ chiến dịch hoàn chỉnh trong paper mới là phép đo thực tế gồm cả tối ưu, ghi log và đánh giá. Không ngoại suy tuyến tính sang hàng trăm máy.

## 4. Vì sao không đơn giản bật GPU?

Lỗi thực tế là `NotImplementedError: noslip solver not implemented.` Mô hình CPU dùng noslip_iterations = 5. Tắt noslip tạo một mô hình tiếp xúc khác; cần kiểm tra chuẩn CPU và GPU trên nhiều quỹ đạo cùng điều khiển, các ca chạm cạnh phím, giữ nốt, trượt, lực nhỏ và nhiều chân. Phải đo sai lệch lực và độ lún, tỷ lệ sự kiện khác nhau, F1 ở các cửa sổ thời gian, memory và thời gian compile. Chỉ sau khi đạt tiêu chí định trước mới có thể dùng GPU để học và đánh giá cuối trên CPU chuẩn.

Cách dự phòng hợp lệ hiện tại là worker CPU. Một hướng nghiên cứu riêng là xây một bàn phím/đầu chân đơn giản hơn được hiệu chuẩn với mô hình chuẩn; lúc đó phải công bố đây là surrogate. Không được gọi một triệu lượt surrogate là một triệu lượt của mô hình đầy đủ.

## 5. Hiệu quả học và tốc độ mô phỏng là hai kết quả khác nhau

RoboPianist dùng DroQ, 5 triệu mẫu cho mỗi bài và 3 seed; quan sát gồm trạng thái cơ thể và mục tiêu có lookahead. Những kết quả đó không chứng minh rằng chỉ tăng hệ số reward là đủ. Nghiên cứu gốc còn chỉ ra vai trò của shaping, lookahead và chiều tác vụ. V4 chọn CEM ít chiều để thăm dò hệ số synapse và hiệu chỉnh readout trong ngân sách nhỏ; chưa chạy so sánh CEM với DroQ/PPO nên không gọi CEM là tối ưu nhất.

Whole-body fly và FlyGM là prior art trực tiếp. V4 không thể đặt novelty ở việc đầu tiên ghép connectome với cơ thể ruồi, hay đầu tiên dùng RL điều khiển côn trùng. Đóng góp hợp lý hơn là một benchmark tiếp xúc âm nhạc có kế toán compute, tách target khỏi sự kiện vật lý, giới hạn lookahead, kiểm tra cơ học và công khai các trường hợp không đạt chuẩn.

## Nguồn chính

1. [MuJoCo Python 3.9.0](https://mujoco.readthedocs.io/en/3.9.0/python.html): nstep, rollout, warmstart và thread pool.

2. [MuJoCo Warp documentation](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html) và [mã nguồn dự án](https://github.com/google-deepmind/mujoco_warp): mục tiêu thông lượng GPU, tương thích tính năng. Phiên bản stable có thể khác bản probe; lỗi cục bộ là bằng chứng cho cấu hình đã cài.

3. [MuJoCo rollout source](https://github.com/google-deepmind/mujoco/blob/main/python/mujoco/rollout.py): API open-loop và quản lý pool. Không dùng API main để giả định hành vi của một bản cũ mà không thử.

4. [MuJoCo simulation benchmark](https://mujoco.readthedocs.io/en/stable/programming/samples.html): kiểm soát contact, warmup, CPU frequency và workload khi đo tốc độ.

5. [NVIDIA Warp installation](https://nvidia.github.io/warp/stable/user_guide/installation.html): driver/toolkit và đặc điểm triển khai GPU.

6. [RoboPianist, CoRL/PMLR 2024](https://proceedings.mlr.press/v229/zakka23a.html) và [toàn văn tác giả](https://arxiv.org/html/2304.04150v3): DroQ, reward, lookahead, số mẫu và số seed.

7. [NeuroMechFly v2, Nature Methods 2024](https://www.nature.com/articles/s41592-024-02497-y): nền tảng mô phỏng cơ thể và cảm giác-vận động.

8. [Whole-body physics simulation of fruit fly behavior, Nature 2025](https://www.nature.com/articles/s41586-025-09029-4): mô hình cơ thể và học điều khiển; không phải body asset đang dùng trong v4.

9. [FlyGM, preprint 2026](https://arxiv.org/abs/2602.17997): connectome graph và điều khiển embodied, đối chứng rewired/random/MLP. Chưa được xem như kết luận độc lập đã tái lập.

10. [Empirical Design in Reinforcement Learning, JMLR 2024](https://jmlr.org/papers/v25/23-0183.html): thiết kế thí nghiệm và độ tin cậy đánh giá.
