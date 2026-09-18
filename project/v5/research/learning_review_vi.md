# Học hiệu quả hơn: đối chiếu tài liệu và quyết định v5

Đối chiếu ngày 18/09/2026. Tìm bằng Exa theo ba nhóm: học điều khiển, cơ chế thưởng sinh học, và video của nhóm tác giả. Tám truy vấn yêu cầu tổng cộng 43 vị trí kết quả; đây không phải 43 nguồn độc lập đã được thẩm định. Ưu tiên tài liệu từ 18/09/2025 đến 18/09/2026, giữ các nghiên cứu nền tảng cũ khi cần. Nhật ký URL ở `learning_search_20260918.json`. Không thể bảo đảm đã tìm hết mọi công trình mới.

## Những công trình làm thay đổi quyết định

**FlyGM, bản v3 ngày 14/06/2026, preprint.** Chính sách đồ thị được khởi tạo bằng imitation learning từ các quỹ đạo chuyên gia, sau đó tinh chỉnh bằng PPO. Đây là điểm cần cập nhật so với cách đọc bản đầu: kết quả điều khiển cuối của v3 thuộc quy trình IL+PPO. Tác vụ là vận động/định hướng của flybody, không phải đánh piano. Muốn áp dụng imitation vào dự án này phải có bộ điều khiển mẫu tạo tiếp xúc đúng trước; một nhãn nốt đúng chưa phải hành động servo đúng. [Bài gốc](https://arxiv.org/html/2602.17997v3).

**FLYNN, bản HTML tháng 07/2026, preprint.** DAgger dùng chuyên gia VFH* và PID có thông tin môi trường đặc quyền để dạy mạng từ topology não ruồi. Sinh viên chỉ nhận tín hiệu cảm giác. Thực nghiệm điều hướng robot không trực tiếp chứng minh khả năng học tiếp xúc bằng chân ruồi. Quyết định: ưu tiên tạo và kiểm chứng teacher cơ học trước khi triển khai DAgger; không gọi checkpoint CEM hiện tại là imitation learning. [Bài gốc](https://arxiv.org/html/2607.00025), [mã tác giả](https://github.com/ben-gitdev/fly-gym).

**ENOMAD, iScience, trực tuyến 15/12/2025.** Công trình *Reinforcement learning in densely recurrent biological networks* phối hợp tìm kiếm tiến hóa với tìm kiếm cục bộ MADS trên mạng hồi quy sinh học; thí nghiệm không phải piano ruồi. V5 áp dụng ý tưởng chuyển chế độ khi plateau: CEM → tìm kiếm tọa độ → CEM rộng hơn. Thuật toán mới không phải bản sao ENOMAD hay MADS và không được hưởng các bảo đảm hội tụ của chúng. [Bài gốc](https://www.cell.com/iscience/fulltext/S2589-0042(25)02697-5).

**CANTABILE, nộp 16/09/2026, preprint đang phản biện.** Công trình piano robot kết hợp thưởng độ trung thực cường độ với độ phủ onset để tránh bỏ nốt khó nhằm tăng điểm. V5 áp dụng nguyên tắc chống bỏ nốt bằng recall tối thiểu 60% khi xét mục tiêu precision 80%. Đây là lựa chọn vận hành của dự án, chưa được chứng minh tối ưu. Không triển khai hoặc tuyên bố đạt velocity-F1 của CANTABILE. [Bài gốc](https://arxiv.org/abs/2609.18213).

**Saito và cộng sự, Current Biology, trực tuyến 23/04/2026; số báo 04/05/2026.** Hai autoreceptor dopamine điều chỉnh gain tín hiệu thưởng theo cường độ: Dop1R1 khuếch đại vùng cường độ thấp, Dop2R làm giảm tín hiệu ở cường độ cao trong thí nghiệm của bài. Kết quả này không ủng hộ giả định “cứ thưởng mạnh hơn thì học tốt hơn”. V5 tối ưu điểm hành vi, không mô phỏng mạch dopamine hay cơ chế autoreceptor. [Bài gốc](https://www.cell.com/current-biology/fulltext/S0960-9822(26)00397-0).

**Topological Sensitivity in Connectome-Constrained Neural Networks, 05/04/2026, preprint.** Đối chứng khởi tạo chung và hoán đổi giữ bậc làm thay đổi kết luận về ưu thế topology trong nghiên cứu này. V5 vì thế không dùng một đường học đẹp hoặc ánh sáng neuron làm bằng chứng rằng connectome vượt mạng nhân tạo. Muốn kết luận nhân quả cần đối chứng cùng số tham số, khởi tạo, dữ liệu và ngân sách. [Bài gốc](https://arxiv.org/abs/2604.04033).

## Video nên xem, và điều video không chứng minh

1. [FlyGM — video của LNS Group](https://www.youtube.com/watch?v=XVP8RdXqyGw), kèm [trang dự án](https://lnsgroup.cc/research/FlyGM). Có cảnh vận động, heatmap và đồ thị tín hiệu. Đã đọc transcript; chưa xác minh được ngày đăng video. Không suy ra thời điểm đăng từ ngày sửa paper. Hình đồ thị force-directed không đồng nghĩa tọa độ giải phẫu neuron.
2. [Eon — bài giải thích mô phỏng và các đoạn minh họa của nhóm](https://eon.systems/updates/embodied-brain-emulation). Nhóm tác giả mô tả đây là công việc tích hợp đang phát triển; controller đi bộ có huấn luyện imitation, một số tín hiệu thị giác chưa ảnh hưởng đáng kể tới hành vi. Không dùng các video lan truyền với tiêu đề “không huấn luyện” làm chứng cứ. Trang này hữu ích để hiểu các lớp brain–body thực sự được ghép như thế nào.

Các video là minh họa hệ thống; không thay thế protocol, đối chứng và số liệu. Chưa xác định được nguồn chính xác của các ảnh chụp người dùng gửi.

## Quyết định đã triển khai

Giữ mô hình 412 neuron, 55 tham số và bộ chấm vật lý hiện có. Tín hiệu mục tiêu đi vào mạng qua sáu gain E1, còn score-to-IK vẫn là hỗ trợ kỹ thuật. Tối ưu P + 0,5 F1 − 2 max(0; 0,6 − R); chỉ xếp hạng candidate cộng thêm 0,01 tanh(reward cũ), còn chọn checkpoint bằng điểm validation không có shaping. Bốn lần validation không cải thiện quá 0,005 kích hoạt đổi phương pháp. CEM đánh giá mỗi năm thế hệ; tìm kiếm tọa độ đánh giá mỗi thế hệ, vì vậy hai chế độ có chi phí đánh giá khác nhau.

Kỹ năng luyện theo curriculum: 25% đầu của thời gian tối ưu dùng ba cao độ dễ nhất mỗi chân, sau đó mở lên 12; validation và test luôn dùng mức 12 cao độ. Hai chuỗi validation, mỗi chuỗi 100 nốt, chọn checkpoint. Ba chuỗi test riêng, mỗi chuỗi 100 nốt, chỉ đánh giá sau khi khóa checkpoint. Khoảng Wilson 95% cho tỷ lệ nốt chỉ có ý nghĩa mô tả vì các sự kiện trong cùng episode không độc lập; không thay thế nhiều seed mô hình.

Lịch mới có tối đa 60 phút kỹ năng, rồi 120 phút Merry và 120 phút Pool; 85% mỗi ngân sách cho tối ưu/validation, phần còn lại cho đánh giá và replay. Hai nhánh bài nhạc bắt đầu độc lập từ cùng checkpoint kỹ năng, không lấy Merry làm khởi tạo Pool. Mỗi episode bài nhạc giữ đúng 100 sự kiện gốc; toàn bài vẫn được chấm riêng, giữ cả nốt trùng và nốt không gán được chân. Không loại nốt khó để nâng precision.

## Các thử nghiệm bị loại khỏi bản chạy chính

Trên cùng 100 mục tiêu seed 82001, checkpoint v4b với decoder cũ đạt 17 khớp/70 lần bấm, P=24,29%, R=17%. Ép gate bằng 1 cho cùng checkpoint cho 17/126, P=13,49%. IK lấy điểm thấp nhất của mesh chân cho cùng checkpoint chỉ đạt 17/126; ép gate tiếp làm tăng bấm thừa. Các điều kiện này không phải upper bound tối ưu và không chứng minh giới hạn sinh học. Chúng cho thấy phải kiểm chứng teacher cơ học trước khi dùng imitation. IK mới chưa đạt nên không được dùng trong đợt chính. File probe lưu đầy đủ tham số và kết quả âm tính.

## Fallback và điều kiện nâng cấp tiếp

Nếu CEM và tìm kiếm tọa độ vẫn plateau, giữ checkpoint tốt nhất và kết thúc đúng ngân sách. Báo cáo chưa đạt P80/R60. Hướng tiếp theo là lập bản đồ tiếp xúc thực theo chân/cao độ, kiểm chứng teacher trên nốt chưa hiệu chuẩn, rồi mới thu quỹ đạo để học imitation và tinh chỉnh RL. Nếu teacher không đạt thì giảm phạm vi nghiên cứu thành bài hiệu chuẩn điều khiển tiếp xúc; không diễn giải thất bại là não ruồi không thể học. Nếu teacher đạt nhưng mạng không đạt, so sánh decoder đơn giản, mạng không connectome và mạng hoán đổi với ngân sách bằng nhau để định vị nút thắt.
