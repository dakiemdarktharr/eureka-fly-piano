# Bản đồ não ruồi và thay đổi trong Fly Piano v5

Ngày đối chiếu: 18/09/2026. Tôi dùng Exa để tìm tài liệu theo ba nhóm: giải phẫu connectome, mô hình động lực học và học điều khiển vận động. Nhật ký ban đầu gồm 9 truy vấn, mỗi truy vấn yêu cầu 5 kết quả; **45 là số vị trí kết quả yêu cầu, không phải 45 nguồn độc lập đã thẩm định**. Các kết luận dưới đây dựa trên bài báo gốc, tài liệu của tác giả và dữ liệu đã tải kiểm tra. Năm ảnh người dùng cung cấp được dùng làm tham chiếu giao diện; chưa xác minh được nguồn chính xác của video/ứng dụng trong ảnh.

## Nghiên cứu người dùng nhắc tới

**FlyWire 2024** công bố mạng dây nối của toàn bộ não ruồi cái trưởng thành: 139.255 neuron và khoảng 50 triệu synapse hóa học giữa chúng. Đây là bản đồ cấu trúc; nó không chứa sẵn toàn bộ hoạt động khi thực hiện một nhiệm vụ. Nguồn: Dorkenwald và cộng sự, *Neuronal wiring diagram of an adult brain*, Nature, 02/10/2024. https://www.nature.com/articles/s41586-024-07558-y

**BANC 2026** mở rộng sang não và dây thần kinh bụng trong cùng mẫu. Bài báo công bố ngày 08/06/2026 mô tả các vòng phản hồi cảm giác–cơ quan thực hiện tại chỗ, liên kết bởi đường lên và đường xuống. Tuy vậy, lamina và ocellar ganglion không có trong thể tích này; “đã map hoàn hảo mọi neuron toàn con ruồi” là cách nói quá mức. Bản đồ vẫn cần mô hình động lực học và giả định đầu vào/đầu ra để mô phỏng hành vi. Nguồn: Bates, Phelps và cộng sự, *Distributed control circuits across a brain-and-cord connectome*, Nature. https://www.nature.com/articles/s41586-026-10735-w

## Các nghiên cứu liên quan và quyết định áp dụng

| Nguồn gốc | Điều có thể sử dụng | Quyết định trong v5 |
|---|---|---|
| Schlegel và cộng sự, Nature 2024, *Whole-brain annotation and multi-connectome cell typing of Drosophila* — https://www.nature.com/articles/s41586-024-07686-5 | Chú giải cell type và đối chiếu giữa connectome | Ghép hình thái với hoạt động theo ID; ghi rõ phép chiếu neuron đồng dạng giữa FlyWire và MANC. Không coi đồng dạng là cùng tế bào. |
| Shiu và cộng sự, Nature 2024, *A Drosophila computational brain model reveals sensorimotor processing* — https://www.nature.com/articles/s41586-024-07763-9 | Mô hình LIF từ connectome có dự đoán được kiểm chứng cho feeding/grooming | Dùng làm cơ sở phân biệt hoạt động mô hình và thực nghiệm. Không đổi rate thành “spike” chỉ để giống ảnh; không suy rộng kiểm chứng feeding/grooming sang piano. |
| Lappalainen và cộng sự, Nature 2024, *Connectome-constrained networks predict neural activity across the fly visual system* — https://doi.org/10.1038/s41586-024-07939-3 | Học tham số chưa biết trong mạng bị ràng buộc bởi connectome, đối chiếu tín hiệu với thực nghiệm | Giữ dấu và cấu trúc synapse; lưu tín hiệu từng neuron để có thể kiểm tra. Chưa có dữ liệu thực nghiệm piano tương ứng để xác nhận tín hiệu hiện tại. |
| Jin và cộng sự, *FlyGM*, arXiv 2026 — https://arxiv.org/abs/2602.17997 | Mô hình đồ thị, imitation và chính sách điều khiển cơ thể | Imitation từ bộ điều khiển chuyên gia là hướng tiếp theo; chưa triển khai expert policy hoặc tuyên bố thành tích RL dựa trên preprint. |
| Rajagopalan và cộng sự, PNAS 2023, *Reward expectations direct learning and drive operant matching in Drosophila* — https://doi.org/10.1073/pnas.2221415120 | Vai trò reward expectation trong học hành vi | Giữ reward khớp nốt có phạt bỏ sót/bấm thừa. Không gọi CEM là dopamine, không suy ra tăng reward tùy ý sẽ tăng khả năng học của chân. |
| Zakka và cộng sự, RoboPianist, CoRL 2023 — https://proceedings.mlr.press/v229/zakka23a.html | Mục tiêu nốt có cấu trúc, lookahead, phối hợp tiếp xúc và điều khiển | Giữ lookahead 150 ms, điểm tiếp xúc và phạt bấm thừa; báo cáo cả precision, recall và F1. Hình thái bàn tay của benchmark khác ruồi nên không so trực tiếp điểm số. |
| MANC, FlyEM/Janelia — https://www.janelia.org/project-team/flyem/manc-connectome | Hình thái và mạng vận động dây thần kinh bụng trưởng thành | Tải SWC thật; hiển thị 410 hình thái có tọa độ tương thích và đủ 412 tín hiệu của mạch. |

Tài liệu dữ liệu của nhóm tác giả: https://github.com/sjcabs/fly_connectome_data_tutorial/blob/main/data/dataset_documentation/manc_data.md . Mỗi file đầu vào có URL và hash trong file hiển thị. Kho này cung cấp metadata MANC v1.2.1, SWC và mesh neuropil.

## Thay đổi đã thực hiện

1. Lưu trực tiếp 412 giá trị rate mỗi frame; kiểm tra DN trong vector này trùng đúng kênh DN cũ. Viewer không tạo ánh sáng ngẫu nhiên hoặc suy hoạt động từ nốt mục tiêu.
2. Dùng point/line cloud từ những đoạn SWC thật, có lớp bề mặt VNC; cho chọn neuron, lọc vùng, xem trace, heatmap, số active và trung bình theo vùng.
3. Xác nhận bodyId và cell type bằng metadata độc lập: **412/412 trùng**. Hai file DN có tọa độ không tương thích với mesh native nên không vẽ trong VNC; không tự căn chỉnh bằng mắt.
4. Mỗi episode luyện là đúng **100 sự kiện nốt**; chuỗi kỹ năng cũng đúng 100. Giữ nốt trùng, nốt không gán được chân và đánh giá toàn bài riêng. Block cuối chồng lấn và việc cắt ranh giới hợp âm được ghi rõ.
5. Thêm sáu gain cue mục tiêu → E1, giữ gain ban đầu bằng 0 khi chuyển checkpoint. Đây là thử nghiệm đường vào thiết kế, lấy cảm hứng từ điều khiển phân cấp/phản hồi tại chỗ; không phải triển khai trực tiếp mạch học BANC.
6. Đo cue 0/10/30 trên cùng 100 nốt; kết quả bằng nhau. Chưa xác lập lợi ích học. Giữ số liệu âm tính thay vì chọn một minh họa đẹp để tuyên bố cải thiện.
7. Tách v5 khỏi dữ liệu v4, lưu cấu hình, hash, checkpoint và lịch sử. Chuyển protocol từ trọng số cũ có ghi thời gian đã dùng; không giả là resume optimizer chính xác.

## Kết quả chẩn đoán và hoạt động vùng

Checkpoint v4b, seed tác vụ 91001, 100 nốt tổng hợp dài 55,42 giây mô phỏng: **17 nốt khớp, 83 thiếu, 37 thừa**, tổng 54 lần bấm. Precision 31,48%; recall 17%; F1 22,08%. Đây là một chuỗi cụ thể trong phạm vi IK thuận lợi, không phải độ chính xác trên mọi bản nhạc. Một trăm sự kiện cho độ phân giải 1 điểm phần trăm ở recall, không bảo đảm sai số thống kê chỉ 1%.

Trong replay này, số neuron active trung bình (rate > 1) là T1 **35,59/148**, T2 **25,82/125**, T3 **10,20/137**, đường xuống/cổ **2/2**. Rate trung bình lần lượt khoảng 2,15; 1,58; 0,37; 27,25 đơn vị mô hình. Các giá trị được tính từ file nhị phân có hash, xuất trong `results/region_activity.json` và CSV từng neuron. DN được cấp drive bên ngoài liên tục; hoạt động cao của DN không tự nó là dấu hiệu “học nhiều”.

## Những vấn đề reviewer vẫn có thể hỏi

| Vấn đề | Cách giải quyết mạnh hơn | Fallback trung thực |
|---|---|---|
| Mạch 412 neuron không phải toàn não | Chuyển sang BANC cùng cá thể; xác lập đường cảm giác, đường xuống, VNC và output cơ thể; kiểm chứng từng module trước khi ghép | Giới hạn kết luận ở mạch vận động có hỗ trợ kỹ thuật, như v5 hiện tại |
| Ánh sáng có thực sự là hoạt động sinh học? | So với calcium/electrophysiology hoặc thao tác neuron trong tác vụ có thể làm trên ruồi thật | Chỉ gọi là rate dự đoán của mô hình, công bố phương trình, scale và các đầu vào thiết kế |
| Não có thực sự quyết định phím? | Bỏ đường tắt target→IK; học policy từ cue, trạng thái cơ thể và phản hồi; so với controller không connectome cùng ngân sách | Mô tả đúng là mạng điều biến vận động dưới bộ lập lịch/IK |
| Cue mới có ích hay chỉ thêm tham số? | Nhiều seed, cue bật/tắt, cùng checkpoint/ngân sách; kiểm tra saturation của decoder và tiếp xúc | Báo cáo thử nghiệm hiện tại không cải thiện, không tuyên bố lợi ích |
| 100 nốt có đủ chứng minh học? | Nhiều chuỗi 100 nốt chưa luyện, chia tập trước, CI theo seed/chuỗi; đo learning curve và retention | Dùng /100 làm chẩn đoán dễ hiểu, không suy khái quát hóa từ một lượt |
| Theo dõi trên bài đã luyện dễ overfit | Tách đoạn/bài test, không dùng test chọn checkpoint; kiểm soát ngân sách từng điều kiện | Gọi đúng là chất lượng trên bài đã luyện |
| Chấm từ sheet sai hoặc hợp âm không khả thi | Hiệu đính MusicXML độc lập, audit unison/tempo; đối chứng oracle IK và giới hạn reach/polyphony | Giữ nốt không khả thi trong mẫu số, công bố OMR chưa kiểm chứng |
| Thiếu bằng chứng nhân quả vùng active | Ablation neuron/nhóm, shuffle đầu vào, rewiring có bảo toàn degree, so với feedforward/RNN | Bảng hoạt động chỉ mô tả đồng biến, không gán chức năng mới |

Chuyển sang toàn BANC và học đọc sheet thị giác là hai mở rộng lớn cần thiết kế thí nghiệm riêng. Không dùng hình ảnh một não sáng toàn bộ để ngụ ý hai việc đó đã hoàn thành. Không có cơ sở bảo đảm chấp nhận Q2 từ một demo hoặc ngưỡng precision cụ thể.
