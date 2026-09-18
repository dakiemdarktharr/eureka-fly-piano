# V4: các câu hỏi phản biện, cách xử lý và phương án dự phòng

Tài liệu đi cùng bản thảo và app, không phải thư trả lời cho một journal cụ thể. "Đã xử lý" chỉ có nghĩa đã có thay đổi và bằng chứng tương ứng; không có nghĩa rủi ro khoa học đã biến mất. Ngày: 2026-09-18.

## Quyết định biên tập hiện tại

Phiên bản này là nghiên cứu thăm dò: adaptive: F1 test trung bình 0.343; frozen: F1 test trung bình 0.330; rewired: F1 test trung bình 0.341. Tổng learner wall time của hai lượt: 53.64 phút. Số ô đạt cả skill và sequence gate: 0/9. Chưa đủ bằng chứng để gọi manuscript là sẵn sàng nộp Q2; các điểm còn mở bên dưới phải được giữ trong paper.

Một bài Q2 cần câu hỏi rõ và bằng chứng đủ sức trả lời. Mục tiêu khả thi của dự án là đánh giá học tiếp xúc chính xác trong bộ điều khiển lai có prior connectome, dưới ngân sách định lượng. Mục tiêu "mô phỏng ruồi đủ lâu để kết luận ruồi có thể/không thể chơi piano" không phù hợp với mô hình hiện tại. Không thể hứa tỷ lệ acceptance khi chưa chọn journal và chưa có bộ thí nghiệm xác nhận.

## Các điểm đã sửa trong v4

1. Có bộ đếm bước vật lý mới, tách tối ưu, đánh giá và xuất replay; không dùng tốc độ video để quy đổi tuổi mô phỏng.

2. Giữ timestep, noslip và solver; batching được kiểm tra bằng trạng thái cuối và sự kiện. Bốn worker CPU cho thông lượng benchmark cao hơn một worker.

3. Dùng các hệ số synapse và kích thích MN có thể học; ghi rõ readout nào vẫn kỹ thuật. V3 giữ nguyên làm lịch sử, không đổi nhãn kết quả cũ thành học synapse.

4. Dùng reward một-một, phạt nốt thiếu/thừa, đánh giá cả precision và recall. Không bấm không được coi là thành công.

5. Chạy ba seed, có nhánh synapse cố định và rewired, có tập synthetic test riêng và không dùng hai bài nhạc để tối ưu.

6. App có biểu đồ tiến trình, thời gian thực/mô phỏng, từng nhánh, replay tiếp xúc, nốt rơi hữu hạn và cổng chất lượng trước full-song demo.

7. Lưu lượt thăm dò không đạt cùng nguyên nhân đổi phương pháp. Không xóa kết quả âm để chỉ giữ phiên bản có vẻ tốt hơn.

## Ma trận vấn đề - cách xử lý chính - fallback

| Vấn đề reviewer sẽ hỏi | Cách xử lý chính và trạng thái | Fallback có thể chấp nhận |
|---|---|---|
| 1. "Đang nghiên cứu cái gì?" | Đã thu hẹp thành học tiếp xúc của một hệ lai trong ngân sách tính toán; định nghĩa outcome trước lượt v4b | Nộp như bài benchmark/phần mềm có giới hạn rõ nếu chưa có kết quả cơ chế |
| 2. Một năm mô phỏng có thật? | Đã có công thức dt x steps và log; mục tiêu 8.766x không đạt trên cấu hình đo | Báo trải nghiệm thực đo và giới hạn máy; không đổi tên epoch thành năm |
| 3. Có cộng nhầm chín con ruồi thành một không? | Đã tách số bước từng ô, tổng toàn chiến dịch và evaluation; giải thích reset/CEM | Chỉ báo số mẫu mỗi policy-search cell, bỏ hoàn toàn khái niệm tuổi |
| 4. Tăng tốc có đổi bài toán? | Batching giữ mẫu điều khiển, timestep và contact; test parity chính xác trên probe | Dùng scalar CPU reference nếu một tối ưu không qua parity |
| 5. Vì sao không dùng GPU? | Đã probe thật; noslip không được hỗ trợ trong bản cài; giữ lỗi và phiên bản | CPU workers; GPU chỉ dùng sau nghiên cứu tương đương và hiệu chuẩn |
| 6. Timestep có hội tụ? | Chưa. Cần dt 0,1/0,2/0,4 ms trên cùng control, onset/force/penetration và CI | Chỉ gọi numerical model ở dt cố định; không kết luận lực sinh học |
| 7. Chân chạm đúng điểm chưa? | Đã phát hiện body-origin khác mặt collision; v4b học bias ngang | Xây inverse-contact-kinematics; nếu chưa có, báo giới hạn hình học và không gán lỗi cho não |
| 8. Chân quá rộng so với phím? | Cần đo bề rộng mặt hỗ trợ theo pose và lập bản đồ khả thi; chưa giải quyết hoàn toàn | Một bàn phím cảm biến có spacing hiệu chuẩn, công bố là môi trường khác và đánh giá lại |
| 9. Tại sao ngực cố định? | Công bố tethering là giả định giảm bài toán; chưa mô phỏng thăng bằng | Giữ scope tethered contact-control, không nói biểu diễn tự do |
| 10. Servo có phải cơ bắp ruồi? | Không; bài ghi rõ position servo kỹ thuật, đơn vị lực native | Bỏ diễn giải năng lượng sinh học; dùng công actuator như chỉ số kỹ thuật |
| 11. Cái gì trong mạng được học? | Đã liệt kê 24 synapse-group gains + 6 MN offsets; còn 19 readout parameters | Chỉ tuyên bố tối ưu effective controller parameters, không gọi synaptic plasticity sinh học |
| 12. Bộ não có nhận và hiểu nốt? | Không trực tiếp; mục tiêu đi qua scheduler/IK. Bài đã nêu giới hạn | Đổi câu hỏi sang motor gating; nghiên cứu encoder goal-to-neural sau bằng đối chứng riêng |
| 13. Connectome có thật sự giúp? | Có ba seed và rewired cùng chiều tham số; chưa đủ kiểm định ưu thế | Báo không có bằng chứng ưu thế nếu dữ liệu không hỗ trợ, không ép kết luận dương |
| 14. Đối chứng frozen có cùng năng lực? | Không: frozen học 25, adaptive học 49; báo là ablation chứ không baseline capacity-matched | Thêm đối chứng 24 tham số phi-synapse hoặc MLP/RNN phù hợp cùng ngân sách |
| 15. Rewired có giữ phân bố trọng số? | Bảo toàn degree và outgoing weights, không incoming strength; công bố rõ | Thêm null model giữ strength/loại neuron/nhóm chân tùy giả thuyết |
| 16. Readout có bù và che topology? | Có thể; cần khóa riêng bias ngang, gate và kích thích trong các ablation | Giới hạn mọi kết luận ở hệ lai, không quy thành cơ chế riêng của graph |
| 17. "Reward mạnh" có hợp lý? | Reward đúng có hệ số 5 nhưng so với các phạt/shaping; không phải cường độ dopamine | Dùng sensitivity sweep rồi khóa hệ số; không tăng reward vô hạn khi học không đạt |
| 18. Có farm reward bằng bấm lặp? | Đã có matching một-một, refractory và phạt extra; unit test kiểm chứng | Nếu tạo adversarial policy vẫn khai thác được, chuyển sang event ledger chặt hơn và rerun |
| 19. Precision cao nhưng bỏ gần hết nốt? | Đã yêu cầu recall cùng precision và F1; mẫu số gồm tất cả mục tiêu | Báo đường precision-recall/coverage và tuyệt đối không lọc nốt khó sau thử |
| 20. Contact threshold có được chọn để nâng điểm? | Detector giữ cố định từ v3; chưa có calibration lực với bàn phím thật | Báo sensitivity ở nhiều ngưỡng, không gọi event là âm thanh piano thật |
| 21. 85% có ý nghĩa khoa học gì? | Là tiêu chí kỹ thuật do dự án chọn, không phải ngưỡng sinh học hay chuẩn journal | Báo đường học liên tục cùng khoảng bất định, không dùng một ngưỡng để che xu hướng |
| 22. Dừng khi vượt ngưỡng có bias? | V4 dùng trần compute, chọn bằng validation, test tách riêng và không học lại trong cùng run | Với nghiên cứu xác nhận: khóa stopping rule và test một lần sau seed độc lập |
| 23. Validation quá nhỏ? | Đúng: 12 nốt/seed mỗi lần; có nguy cơ overfit chọn checkpoint | Tăng ngân hàng task và chia theo pitch/tempo/layout, giảm tần suất validation; v4 chỉ là pilot |
| 24. Test có đủ mới? | Khác seed nhưng cùng tập pitch, timing và reset; chưa phải OOD | Gọi đúng in-distribution holdout; thêm test tempo/pitch/transposition/physics mới |
| 25. Sửa phương pháp sau xem dữ liệu? | Có, v4a dẫn tới v4b; giữ cả hai, tạo holdout mới và công bố exploratory | Chạy một replication hoàn toàn độc lập sau khi khóa v4; không gọi v4 là preregistered |
| 26. Chín ô có ngân sách bằng nhau? | Cùng vòng round-robin và population; vòng cuối có thể không đủ cho tất cả | So sánh ở cùng số bước/thế hệ chung từ history; báo thêm wall-clock chứ không thay nhau |
| 27. Ba seed có đủ thống kê? | Chưa cho kết luận mạnh; trình bày từng seed, không coi từng nốt là replicate độc lập | Dùng effect size mô tả và tăng seed dựa trên variance/power pilot, không bịa CI hẹp |
| 28. Chưa có baseline học mạnh? | Chưa chạy PPO/DroQ/MLP direct action cùng budget | Định vị bài hiện tại là infrastructure/pilot; chưa nộp bài tuyên bố SOTA |
| 29. Hai bài nhạc là dữ liệu chuẩn chưa? | OMR đầy đủ có warning, chưa note-by-note verification | Dùng synthetic làm benchmark chính; sheet/music chỉ demo có ghi giới hạn hoặc xin MusicXML/MIDI đã kiểm tra |
| 30. Sáu chân chơi hợp âm 7-8 nốt? | Không bảo đảm; phải báo unassigned/infeasible target trong full-song score | Chuyển soạn có ghi mapping và giữ metric so với bản gốc, không âm thầm bỏ nốt |
| 31. Nốt rơi có làm lộ tương lai? | Viewer/controller chỉ dùng 150 ms cục bộ; tiền xử lý phân chân toàn bài vẫn là prior | Đổi sang online scheduler cùng cửa sổ và so sánh riêng trước khi gọi end-to-end online |
| 32. Vùng não sáng có đo được không? | Không; DNg100 là chiếu mô hình lên morphology khác cá thể. UI đã ghi rõ | Hiển thị sơ đồ VNC theo chức năng, không gán anatomy giả cho neuron thiếu tọa độ |
| 33. Hình ảnh đẹp có thay kết quả? | Không: app tách mục tiêu/contact và khóa full-song demo chưa đạt chuẩn | Cung cấp replay thất bại cùng event log, bỏ montage chọn đoạn đẹp |
| 34. Luật học có giống ruồi thật? | CEM là search ngoài mạng; chưa có dopamine, eligibility trace hay plasticity local | Không dùng thuật ngữ biological learning; nghiên cứu local rule như một dự án riêng có dữ liệu kiểm chứng |
| 35. Có tái lập được không? | Có mã, seed, checksum, log; data/asset rights chưa hoàn toàn công khai | Phát synthetic fixtures và mô hình toy mở; thu xếp giấy phép trước khi tuyên bố fully reproducible |
| 36. Kết quả âm nói lên điều gì? | Chỉ giới hạn của cấu hình, thuật toán và budget đã thử | Nêu failure-mode có cơ chế và phép can thiệp kiểm chứng; không tuyên bố ruồi không thể chơi piano |
| 37. Các voice trùng có thành mục tiêu không thể thực hiện? | Sanity check có 1/29 duplicate onset-pitch và 7/55 overlap cùng pitch ở Merry/Pool; chưa chuẩn hóa tie/unison | Xác minh nhạc lý rồi tạo physical-key target riêng với mapping về source; synthetic vẫn là benchmark chính |

## Bộ thí nghiệm ưu tiên trước khi nộp

Gói A, cơ học: đối chiếu mặt tiếp xúc, spacing phím, spring/damping, lực/penetration và timestep. Định trước dung sai bằng yêu cầu tác vụ, không đặt sau khi nhìn số đo. Một oracle điều khiển hình học phải đạt chuẩn trên tập reachable trước khi lỗi được gán cho mạng học. Nếu oracle chưa đạt, sửa môi trường/decoder trước khi tăng hàng giờ train.

Gói B, nhận dạng đóng góp: adaptive, fixed-synapse, rewired, mạng tắt/unity gate, MLP/RNN direct hoặc cùng decoder. Khóa hoặc ablate từng nhóm readout và MN offset. So sánh cả cùng bước vật lý và cùng wall-clock; ghi số tham số, số candidate, solver warning, domain và diện tích dưới đường học. Chọn số seed bằng variance pilot và nguồn lực, không cam kết một số seed tùy ý là đủ.

Gói C, chuyển giao: tập train pitch/timing/layout cố định; validation riêng; test mới theo tempo, quãng, reset pose và nhiễu lực. Hai tác phẩm được chép lại/đối chiếu độc lập. Bổ sung release/duration, tốc độ, polyphony, coverage và các nốt không phân chân được. Chạy full-song khi skill đủ, báo cả nguyên bản và chuyển soạn nếu có.

Gói D, tái lập: khóa phiên bản, checksum tất cả mesh và ma trận; ghi chính xác release connectome; giải quyết quyền phân phối; chạy lại từ môi trường sạch và một máy độc lập. App và paper phải lấy số từ cùng artifact kết quả, không nhập tay.

Nếu không đủ nguồn lực cho A-D, hướng fallback có mục tiêu rõ nhất là bài phương pháp về kiểm định benchmark tiếp xúc có prior connectome và kế toán compute, với kết quả âm được phân tích. Cần kiểm tra journal có nhận bài công cụ/benchmark hoặc kết quả âm đúng chuyên ngành; không dùng chỉ số Q2 như một tiêu chí duy nhất.

## Deep search tăng tốc: điều có thể và chưa thể làm

Đã rà 45 vị trí kết quả Exa theo ba hướng; trích được 44 kết quả/38 URL duy nhất. [MuJoCo Python](https://mujoco.readthedocs.io/en/3.9.0/python.html) và [source rollout](https://github.com/google-deepmind/mujoco/blob/main/python/mujoco/rollout.py) hỗ trợ batching/pool nhưng cần bảo toàn vòng feedback. [MuJoCo Warp](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html) phù hợp throughput nhiều world; probe model này chưa chạy được vì noslip. [RoboPianist](https://proceedings.mlr.press/v229/zakka23a.html) ủng hộ thiết kế shaping/lookahead, không bảo đảm một giờ đủ học.

Đường tăng tốc tiếp theo hợp lý là: giảm chi phí không làm đổi dynamics; đo lại trên workload có contact; xây một surrogate có kiểm chứng nếu cần GPU; và cải thiện hiệu quả mẫu. Mục tiêu một năm/giờ vẫn là một yêu cầu chưa đạt. Không có bằng chứng cho phép hứa đạt bằng một vài chỉnh sửa trên laptop hiện tại.
