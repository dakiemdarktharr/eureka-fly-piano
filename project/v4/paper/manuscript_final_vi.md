# Học điều khiển tiếp xúc phím bằng mô hình vận động ruồi có cấu trúc connectome

Bản thảo v4. Kết quả thí nghiệm tổng hợp được khóa ngày 2026-09-18.

## Tóm tắt

Điều khiển một cơ thể ruồi mô phỏng chạm đúng phím đòi hỏi phối hợp hoạt động mạng vận động với hình học bàn chân và cơ học tiếp xúc. Nghiên cứu này đánh giá một bộ điều khiển lai gồm mạng 412 neuron có cấu trúc từ connectome, bộ giải động học ngược và cơ thể NeuroMechFly trên bàn phím thu nhỏ. Hai câu hỏi được xét là mức hiệu năng đạt được trong ngân sách một giờ tính toán và mức tăng thông lượng khi giữ nguyên bước thời gian, bộ giải và cách lấy mẫu tiếp xúc.

Thuật toán cross-entropy method (CEM) tối ưu 49 tham số: 24 hệ số synapse theo nhóm, 6 hệ số điều chỉnh ngưỡng neuron vận động và 19 tham số điều khiển đầu ra. Hai cấu hình đối chứng giữ synapse cố định hoặc hoán đổi cạnh có bảo toàn bậc; mỗi cấu hình được chạy với ba seed. Điểm số dựa trên ghép một-một giữa nốt mục tiêu và sự kiện tiếp xúc vật lý. Thí nghiệm v4b dùng 2786.11 giây thực, thực hiện 140,197,900 bước vật lý, trong đó 116,017,900 bước dùng để tối ưu. F1 trung bình trên tập kiểm tra là 0.343 ở nhánh adaptive, 0.330 ở nhánh frozen, 0.341 ở nhánh rewired.

Trong phép đo thông lượng ngắn, bốn tiến trình CPU đạt 13,807 giây mô phỏng cộng dồn trên một giây thực. Giá trị này thấp hơn nhiều so với mức 8.766 cần để tạo lượng trải nghiệm tương đương một năm trong một giờ. Thử nghiệm GPU không chạy được với thiết lập noslip của mô hình. Các kết quả cho thấy giới hạn hiện tại của bộ điều khiển và môi trường tiếp xúc đang xét; chúng chưa xác lập lợi ích riêng của cấu trúc connectome hoặc giới hạn học của ruồi sinh học.

Từ khóa: điều khiển vận động; Drosophila; connectome; tiếp xúc vật lý; tối ưu không đạo hàm; ngân sách tính toán.

## 1. Mục tiêu nghiên cứu

Nghiên cứu xét khả năng cải thiện độ chính xác tiếp xúc phím bằng cách tối ưu các tham số thần kinh và cơ học của một bộ điều khiển lai. Hiệu năng được đo trên chuỗi nốt tổng hợp, với dữ liệu huấn luyện, lựa chọn checkpoint và kiểm tra cuối được xác định bằng các seed riêng. Đồng thời, chúng tôi đo thông lượng vật lý trước và sau khi gom bước thực thi, với cùng bộ giải và pha lấy mẫu.

Cách thiết kế này cho phép phân biệt ba vấn đề: cải thiện trong quá trình tối ưu, chuyển sang chuỗi mới cùng phân phối và thực hiện một tác phẩm dài. Thí nghiệm chính tập trung vào hai vấn đề đầu. Hai bản nhạc piano được chuẩn bị cho bước đánh giá ứng dụng, có yêu cầu cao hơn về tốc độ, đa âm và tầm với.

Đóng góp của nghiên cứu là một quy trình đo tiếp xúc có đối chứng cấu trúc mạng, nhật ký riêng cho bước tối ưu và đánh giá, cùng phần mềm kiểm tra lại hành vi từ sự kiện vật lý. Phạm vi này bổ sung một tác vụ vận động chính xác cho mô hình ruồi có cấu trúc connectome, thay vì đề xuất một mô hình toàn não hoặc một thuật toán học mới.

## 2. Nghiên cứu liên quan

NeuroMechFly v2 cung cấp một nền tảng mô phỏng cảm giác-vận động ở ruồi [1]. Một mô hình toàn thân ruồi khác đã được dùng để học các hành vi vận động phức tạp [2]. FlyGM đã khảo sát một bộ điều khiển đồ thị connectome cho cơ thể ruồi và so sánh với đồ thị hoán đổi và MLP [3]. Các nghiên cứu này đặt nền tảng cho việc kết hợp connectome với cơ thể mô phỏng; tác vụ tiếp xúc phím ở đây khảo sát một yêu cầu vận động cụ thể trên nền tảng đó.

RoboPianist dùng mục tiêu có lookahead và phần thưởng nhấn phím, vị trí ngón cùng chi phí năng lượng; thí nghiệm báo cáo DroQ với 5 triệu mẫu cho mỗi bài và ba seed [4]. Tác vụ này khác về hình thái, số bậc tự do và mức hỗ trợ hình học, nên không dùng số đo của RoboPianist làm đối chứng định lượng trực tiếp. Các nguyên tắc thiết kế thí nghiệm RL yêu cầu xem xét biến thiên theo seed, cách chọn cấu hình và chi phí đánh giá [5].

MuJoCo Python hỗ trợ nhiều bước giữ nguyên lệnh điều khiển trong một lần gọi và thực thi mô phỏng CPU đa luồng [6]. MuJoCo Warp tập trung vào thông lượng nhiều môi trường trên GPU, nhưng tính tương đương chức năng cần được kiểm tra trên phiên bản cụ thể [7]. Kết quả tốc độ từ một mô hình nhỏ không được áp sang toàn bộ mô hình tiếp xúc ruồi-bàn phím.

## 3. Mô hình và phạm vi của việc học

### 3.1 Cơ thể, bàn phím và đơn vị

Cơ thể dựa trên FlyGym/NeuroMechFly 2.1.0; ngực cố định; có 42 bộ chấp hành servo vị trí ở sáu chân. Cảnh vật lý gồm 214 tọa độ vị trí, 214 tọa độ vận tốc và 157 đối tượng hình học. Bàn phím có 88 phím tương ứng MIDI 21-108, cách tâm 0,055 mm. Mỗi phím là một khối có khớp trượt với độ cứng 5 và hệ số cản 0,006 theo hệ đơn vị mm, g, s; lực g.mm/s² tương ứng micro-newton. Đây là các thông số kỹ thuật giả định, không phải một đàn piano chuẩn được thu nhỏ theo luật tương tự cơ học.

Mô hình tính va chạm giữa hình học đầu bàn chân và các phím. Chưa bao gồm tự va chạm toàn thân, cơ bắp, mỏi cơ, pedal, cơ chế búa đàn hoặc toàn bộ xúc giác. Âm thanh trong app được tổng hợp từ sự kiện tiếp xúc hoặc từ mục tiêu, và hai nguồn được người dùng chọn rõ ràng. Không dùng âm thanh mục tiêu để chấm điểm.

### 3.2 Mạng vận động và tính bất định sinh học

Đồ thị được lấy từ bản xuất MANC trong kho mã của Pugliese và cộng sự [8], commit 10e7661bf414ba7b4c2edf795cd36d0f878c17c0, tập W_20260522_allSynapses. Bản xuất không ghi phiên bản neuPrint nền; đây là một khoảng trống trong nguồn gốc dữ liệu. Bộ lọc giữ DNg100, IN17A001, INXXX466, IN16B036 và motor neuron thuộc các phân nhóm chân. Mạng có 2 neuron dẫn truyền xuống (DN), 18 neuron trong nhóm CPG và 392 neuron vận động (MN); 2.592 cạnh tổng hợp từ 18.831 synapse của dữ liệu đầu vào. Ma trận thưa được nhân hệ số toàn cục 0,03; chuẩn hóa thể tích tác động vào tham số gain/ngưỡng neuron. Mô hình rate dùng ngưỡng, gain, giới hạn rate và hằng số thời gian phụ thuộc giả định thể tích cùng khởi tạo theo seed; tích phân Euler ở 2 ms và trễ giả định 4 ms. Tín hiệu kích thích DN bằng 500; phản hồi lực được chuẩn hóa, chặn và chiếu vào một neuron E1 trên mỗi chân.

Shiu và cộng sự [9] kiểm chứng hành vi trên một mô hình toàn não. Mô hình vận động rút gọn ở đây có tập neuron, tham số và cách ghép với cơ thể khác, nên cần được kiểm chứng riêng. Dấu tác động của chất dẫn truyền thần kinh được giữ theo dự đoán trong dữ liệu đầu vào; độ nhạy đối với sai số dự đoán chưa được đánh giá. Không đủ dữ liệu để xem số synapse như conductance thật hoặc xem rate tính toán như firing rate đã hiệu chuẩn. Kết nối từ mục tiêu âm nhạc đến bộ lập lịch, chiếu phản hồi cảm giác, ánh xạ quần thể motor neuron sang servo đều là lựa chọn mô hình hóa. Điều này giới hạn suy luận về thần kinh học.

### 3.3 Tham số được tối ưu

Với W là ma trận có hàng biểu diễn neuron hậu synapse, phiên bản thích nghi dùng W'ij = exp(alpha_g(i)) Wij. Nhóm g(i) gồm từng neuron CPG trong 18 neuron và từng quần thể MN của sáu chân. Các hàng DN giữ hệ số 1. Alpha bị chặn trong [-0,69; 0,69]; cấu trúc zero/nonzero và dấu của cạnh không đổi. Sáu hệ số kích thích MN được trừ khỏi ngưỡng của các neuron trong từng quần thể, trong [-50; 50] đơn vị mô hình. Đây là hệ số hiệu dụng được tối ưu ngoại tuyến, không phải luật plasticity đã được xác nhận ở ruồi.

| Khối tham số | Số lượng | Vai trò và giới hạn |
|---|---|---|
| Hệ số synapse theo nhóm | 24 | Chỉ thay biên độ dương của cạnh đã có; không thêm kết nối |
| Kích thích MN theo chân | 6 | Điều chỉnh ngưỡng; có thể tạo hoạt động nền, không diễn giải như dopamine |
| Log-gain của gate | 6 | Nhân đầu ra quần thể, sau đó chặn trong [0;1] |
| Độ mở rộng động tác ấn | 6 | Thay biên độ nội suy giữa hover và press |
| Hiệu chỉnh ngang | 6 | Dịch đích hiệu dụng tối đa ±0,275 mm; nội suy bảng IK |
| Tiến thời điểm ấn | 1 | Từ 0 đến 80 ms để bù trễ cơ học |

Tổng cộng 49 tham số ở nhánh thích nghi và hoán đổi. Nhánh giữ synapse cố định tối ưu 25 tham số còn lại, gồm cả hệ số điều chỉnh ngưỡng MN. So sánh này đo tác động của việc cho phép thay đổi hệ số synapse, nhưng đồng thời thay đổi số tham số tự do. Nhánh hoán đổi giữ cùng 49 tham số với nhánh thích nghi.

Bộ lập lịch nhận cao độ và thời gian rồi chọn chân theo hình học. Bộ giải động học ngược (IK) tạo tư thế mục tiêu; mạng vận động điều biến mức ấn của từng chân. Mạng không nhận tên nốt hoặc ảnh bản nhạc. Vì các tham số điều khiển đầu ra cũng được tối ưu, mức cải thiện đo được phản ánh toàn bộ hệ thống lai.

![Kiến trúc](figures/architecture.png)

Hình 1. Hai thang thời gian của bộ điều khiển. (A) Mục tiêu nốt đi qua bộ lập lịch và IK; đầu ra mạng điều biến mức ấn, còn lực tiếp xúc trở lại mạng qua phản hồi cảm giác. (B) Sau mỗi lượt mô phỏng, sự kiện tiếp xúc được ghép với mục tiêu để tính thưởng cho CEM. Nét đứt biểu diễn cập nhật phân phối tham số giữa các thế hệ. Sơ đồ thể hiện cấu hình thí nghiệm tổng hợp v4b; lượt luyện bài bổ sung dùng quần thể 8 thay vì 10 ứng viên.

## 4. Tác vụ, thưởng và quy trình đánh giá

### 4.1 Chuỗi tổng hợp và dữ liệu âm nhạc

Tác vụ tổng hợp đầu tiên gồm sáu nốt không chồng lấn, lần lượt giao cho sáu chân, bắt đầu ở 0,4 s, cách nhau 0,55 s, giữ 0,22 s; tổng episode 3,72 s sau làm tròn. Mỗi chân lấy ngẫu nhiên trong ba cao độ có sai số IK nhỏ nhất của chân đó. Tập huấn luyện dùng seed tác vụ 10000 + số thế hệ; tập lựa chọn checkpoint (validation) dùng 71001 và 71002; tập kiểm tra cuối (test) dùng 91001-91004. Các seed môi trường khác nhau chủ yếu thay cao độ, chưa thay tư thế ban đầu hay thông số vật lý. Phép kiểm tra này đo chuyển giao giữa các mẫu cùng phân phối, với biến thiên chủ yếu ở cao độ.

Sau khi validation đạt precision và recall ít nhất 0,95, chương trình mở nhóm 12 cao độ có sai số IK thấp cho mỗi chân. Nếu test kỹ năng đạt chuẩn, một test chuỗi nhanh hơn dùng 12 nốt, khoảng cách 0,30 s và giữ 0,16 s được chạy. Chuỗi này đòi precision >0,85, recall và F1 >=0,85. Các ngưỡng được áp dụng cho ước lượng điểm trên tập kiểm tra nhỏ; độ bất định của hiệu năng quần thể chưa được lượng hóa. Chương trình học mở rộng tập cao độ nhưng chưa luyện riêng chuỗi nhanh. Kết quả của bước này vì thế còn phụ thuộc khả năng chuyển sang tốc độ mới.

Trong quy trình thí nghiệm tổng hợp v4b, replay toàn bài chỉ được xuất sau khi đạt cả hai ngưỡng kỹ năng. Merry-Go-Round of Life có 237 ô nhịp, 2.401 nốt, khoảng 316,04 s và đa âm tối đa 8; In The Pool có 69 ô viết, 73 ô khi tính lặp, 1.502 nốt, khoảng 238,46 s và đa âm tối đa 7. Các con số là từ bản OMR đang có, chưa được một nhạc công kiểm tra độc lập từng nốt. Hai bản nhạc không được dùng để tối ưu hoặc chọn checkpoint của thí nghiệm tổng hợp v4b. Kiểm tra cấu trúc phát hiện 1/29 nốt dư do trùng cùng pitch và onset, cùng 7/55 cặp chồng thời gian ở cùng pitch, lần lượt cho Merry/Pool. Các trường hợp này cần được đối chiếu với bản nhạc để phân biệt đồng âm giữa các bè, dấu nối và tái nhấn. Việc chấm theo sự kiện vật lý từng phím cần một ánh xạ về các bè nguồn. Dữ liệu hiện tại giữ các sự kiện theo bè, chưa gộp những trường hợp đó.

Tầm với và số chân giới hạn khả năng thực hiện các hợp âm trong bản gốc. Do đó, mọi nốt không phân công được chân vẫn được giữ trong mẫu số đánh giá. Một bản chuyển soạn, nếu được sử dụng về sau, cần được đánh giá riêng và có danh sách thay đổi so với bản gốc.

### 4.2 Quan sát hữu hạn và giao diện nốt rơi

Ở mỗi chân, bộ lập lịch đưa mục tiêu kế tiếp vào điều khiển tối đa 150 ms trước thời điểm bắt đầu nốt (onset). App thể hiện cùng cửa sổ bằng thanh nốt rơi trên đúng phím trong cảnh 3D; đầu thanh tới bàn phím ở onset, chiều dài thể hiện phần thời gian giữ còn trong cửa sổ. Thanh nốt chỉ phục vụ hiển thị và không tham gia mô phỏng va chạm. Replay hiển thị riêng màu mục tiêu và tiếp xúc thực. Tư thế được lưu ở 24 fps, nhưng sự kiện chấm điểm được phát hiện ở 500 Hz và lưu riêng; không chấm từ các frame video.

Trong bộ lập lịch toàn bài, phân công chân ban đầu được tính từ chuỗi có sẵn. Vì vậy cửa sổ 150 ms chỉ giới hạn mục tiêu vào bộ điều khiển cục bộ; chưa loại bỏ mọi lợi thế từ tiền xử lý toàn bản nhạc. Phạm vi quan sát hữu hạn này vì thế chưa tương đương với một tác nhân xử lý toàn bộ bản nhạc trực tuyến.

### 4.3 Sự kiện nốt và phần thưởng

Lực pháp tuyến từ tiếp xúc bàn chân-phím được cộng theo phím. Onset cần lực ít nhất 0,003 micro-newton trong 16 ms; release cần dưới 0,0015 micro-newton trong 24 ms; khoảng chống lặp 40 ms. Cùng bộ phát hiện được giữ qua mọi cấu hình. Mẫu tiếp xúc lấy sau bước vật lý đầu tiên của mỗi khối 2 ms, gắn nhãn thời gian đầu khối; độ lệch quy ước 0,2 ms được giữ nhất quán, nhỏ hơn cửa sổ ghép chính 100 ms.

Điểm số dựa trên ghép một-một giữa các sự kiện cùng cao độ, tối đa hóa số cặp trong ±100 ms rồi ưu tiên sai lệch nhỏ. Precision = TP/(TP+FP); recall = TP/(TP+FN); F1 là trung bình điều hòa. Không có nốt phát thì precision được quy ước 0. Mỗi mục tiêu chỉ được thưởng đúng một lần; bấm lặp hoặc bấm thêm phím không tạo thêm TP.

Phần thưởng mỗi lượt được tính bằng: R = (5TP - 2FN - FP)/N + 0,5 IoU - 0,5 MAE/0,1 + 0,1D/T - min(0,1; 10^-5 E). N là số nốt mục tiêu; IoU là trung bình độ chồng lấn thời gian giữ của các cặp đã ghép; MAE chỉ tính trên cặp ghép; D tích phân độ gần đích exp(-khoảng cách/0,08 mm) trong lúc có mục tiêu; E là tích phân trị tuyệt đối công suất bộ chấp hành. Thành phần thưởng theo khoảng cách bị chặn ở 0,1; tiêu chí thành công vẫn phụ thuộc các sự kiện nốt. Nếu có cảnh báo solver, phần thưởng bằng -10^6 và phép đánh giá có cảnh báo không được vượt ngưỡng thành công.

IoU và MAE có tính điều kiện theo cặp được ghép, nên phải đọc cùng recall. Việc chọn hệ số 5 không phải chứng cứ về cường độ phần thưởng sinh học; nhân đồng loạt mọi hệ số không tự làm thuật toán học nhanh hơn. Chưa có phân tích đầy đủ về đóng góp của từng thành phần thưởng.

### 4.4 Tối ưu, đối chứng và tính thăm dò

Mỗi thế hệ CEM có 10 ứng viên; ba ứng viên có phần thưởng cao nhất được dùng để cập nhật phân phối. Trung bình và độ lệch chuẩn được trộn với tỷ trọng 0,6 cho ba ứng viên được chọn; sigma có sàn bằng 3% bề rộng miền tham số. Mỗi thế hệ gồm trung bình hiện tại, checkpoint tốt nhất và các mẫu mới; các nhánh cùng seed dùng cùng chuỗi ngẫu nhiên khởi tạo và cùng seed tác vụ theo thế hệ. Chọn checkpoint theo F1 trên tập lựa chọn; phần thưởng trung bình nhân 10^-6 được dùng để phân biệt các trường hợp có cùng F1. Không chọn checkpoint theo test.

Ba cấu hình: adaptive, frozen-synapses và rewired. Nhánh rewired hoán đổi cặp cạnh để bảo toàn bậc vào và bậc ra; trọng số đi cùng neuron nguồn, nên tổng trọng số đi vào từng neuron có thể thay đổi. Cả ba dùng cùng cơ thể, bộ lập lịch, hàm thưởng, bộ phát hiện tiếp xúc và bộ điều khiển đầu ra. Số seed mạng là 0, 1, 2. Các thế hệ được chạy luân phiên giữa chín ô thí nghiệm, có thể nhận lượng tính toán khác nhau ở vòng cuối khi hết ngân sách. Số bước và thời gian của từng ô được báo riêng để thể hiện chênh lệch này.

Một lượt thăm dò v4a dùng 37 tham số được dừng sau khi phát hiện sai lệch giữa gốc đốt chân và mặt tiếp xúc. V4b thêm kích thích MN và hiệu chỉnh ngang, dùng bộ validation/test mới. Kết quả v4a và thời gian đã dùng được giữ lại. Do phương pháp được sửa sau lượt thăm dò, kết quả được xem là bằng chứng khám phá. Phân tích báo từng seed và thống kê mô tả; các nốt trong cùng một lượt chạy không được xem là những lần lặp độc lập.

## 5. Tăng tốc thực thi và ghi nhận thời gian

Mô phỏng dùng MuJoCo 3.9.0, bước thời gian vật lý 0,2 ms và bước cập nhật mạng/điều khiển 2 ms. Bộ tích phân là implicitfast; số vòng lặp bộ giải tối đa là 50 và noslip_iterations = 5. Mỗi tiến trình giữ một môi trường vật lý và mẫu mạng trong bộ nhớ. Việc xuất dữ liệu hình học và khung hình được tắt trong tối ưu. Lệnh điều khiển được giữ qua một bước, lấy mẫu, rồi gom chín bước còn lại. Trong phép kiểm tra cặp, cách chạy từng bước và cách gom bước nhận cùng đầu vào, cho trạng thái vị trí cuối và sự kiện tiếp xúc giống hệt. Phép kiểm tra này xác nhận thay đổi thực thi trên trường hợp đã xét; hội tụ số của mô hình cần được đánh giá riêng.

RTF_total = dt x tổng số bước vật lý mới / tổng giây thực chiến dịch. Số bước tối ưu và đánh giá được lưu riêng từng ô. Thời gian xuất replay được ghi riêng, không cộng vào trải nghiệm đã dùng để tối ưu. Giai đoạn khởi tạo mạng 100 bước chỉ là 0,2 s tích phân mạng và không được tính như 0,2 s tương tác cơ thể. Các lượt mô phỏng bắt đầu lại từ trạng thái ban đầu, các ứng viên CEM khác nhau và các seed khác nhau không tạo thành một quỹ đạo liên tục của một não duy nhất.

Mốc một năm/giờ đòi RTF 8.766, tức 43,83 triệu bước vật lý/giây ở dt hiện tại. Thử nghiệm MuJoCo Warp 3.9.0.1 / Warp 1.17.0 trên RTX 5050 Laptop 8 GiB dừng do `noslip solver not implemented`. Không có số thông lượng GPU hợp lệ cho mô hình này. Thay đổi noslip, hình học va chạm, số vòng lặp bộ giải hoặc bước thời gian đều cần được đánh giá lại về ảnh hưởng tới tiếp xúc.

![Thông lượng](figures/throughput.png)

Hình 2. Thông lượng benchmark CPU gồm tiếp xúc chủ động, sau khởi tạo tiến trình. Cột mục tiêu một năm/giờ chỉ là yêu cầu toán học; trục hoành dùng thang logarithm. Benchmark này được chạy trước hiệu chỉnh v4b; thông lượng chiến dịch cuối được báo riêng.

## 6. Kết quả

### 6.1 Ngân sách và lượng trải nghiệm

Lượt v4a 20260918T055453 dừng sau 432.30 s. Lượt v4b 20260918T060329 có trần 3.150 s; quy trình được sửa sau lượt thăm dò và dành 88% ngân sách cho tối ưu. Tổng thực tế hai lượt là 3218.41 s, nằm trong trần 3.600 s. V4b có 116,017,900 bước tối ưu và 24,180,000 bước đánh giá; RTF toàn chiến dịch v4b là 10.064. Tổng giây mô phỏng không phải thời gian của một quỹ đạo học liên tục. Benchmark, phát triển phần mềm và xuất video/replay không nằm trong ngân sách learner này.

| Giai đoạn | Giây thực | Giây mô phỏng mới |
|---|---|---|
| V4a thăm dò, 37 tham số | 432.30 | 5379.12 |
| V4b, 49 tham số | 2786.11 | 28039.58 |
| Tổng hai lượt | 3218.41 | 33418.70 |

### 6.2 Học và chuyển giao trong phân phối

F1 trung bình trên tập kiểm tra là 0.343 ở nhánh adaptive, 0.330 ở nhánh frozen, 0.341 ở nhánh rewired. Số thế hệ hoàn tất theo ô nằm trong [69, 70]. Điểm trên tập lựa chọn dao động qua các thế hệ. Checkpoint cuối được chọn theo F1 cao nhất trên tập này, nên có thể khác bộ tham số của thế hệ cuối. Với ba seed, các chênh lệch trung bình được xem là mô tả; chưa đủ để xác lập ưu thế giữa các cấu hình.

| Mốc thực (phút) | Seed | P trung bình | R trung bình | F1 trung bình | F1 min-max | Trễ tối đa (s) |
|---|---|---|---|---|---|---|
| 5 | 3 | 0.137 | 0.194 | 0.160 | 0.133-0.200 | 28.6 |
| 15 | 3 | 0.226 | 0.306 | 0.260 | 0.148-0.345 | 34.0 |
| 30 | 3 | 0.257 | 0.333 | 0.289 | 0.167-0.414 | 44.8 |
| 45 | 3 | 0.283 | 0.333 | 0.305 | 0.174-0.444 | 41.9 |

Các mốc dùng điểm validation gần nhất không vượt mốc, trung bình trên ba seed adaptive; cột trễ cho biết độ cũ lớn nhất của điểm đo. Đây không phải test lặp lại sau mỗi mốc.

![Đường học](figures/learning.png)

Hình 3. F1 trên tập lựa chọn checkpoint theo thời gian thực, tách theo seed. Mỗi điểm tương ứng một thế hệ. Do tập này nhỏ và được dùng lặp lại, đường học có thể phản ánh cả sự thích nghi với tập lựa chọn.

| Mạng / seed | Phút mô phỏng tối ưu | Precision | Recall | F1 | TP / mục tiêu | Cảnh báo |
|---|---|---|---|---|---|---|
| adaptive / 0 | 43.40 | 0.353 | 0.250 | 0.293 | 6 / 24 | 0 |
| frozen / 0 | 43.40 | 0.450 | 0.375 | 0.409 | 9 / 24 | 0 |
| rewired / 0 | 43.25 | 0.304 | 0.292 | 0.298 | 7 / 24 | 0 |
| adaptive / 1 | 42.78 | 0.259 | 0.292 | 0.275 | 7 / 24 | 0 |
| frozen / 1 | 42.78 | 0.257 | 0.375 | 0.305 | 9 / 24 | 0 |
| rewired / 1 | 42.78 | 0.367 | 0.458 | 0.407 | 11 / 24 | 0 |
| adaptive / 2 | 42.78 | 0.429 | 0.500 | 0.462 | 12 / 24 | 0 |
| frozen / 2 | 42.78 | 0.259 | 0.292 | 0.275 | 7 / 24 | 0 |
| rewired / 2 | 42.78 | 0.350 | 0.292 | 0.318 | 7 / 24 | 0 |

![Theo mẫu vật lý mới](figures/sample_efficiency.png)

Hình 4. F1 trên tập lựa chọn checkpoint theo số bước vật lý dùng để tối ưu từng ô. Các bước đánh giá được loại khỏi trục hoành. Biểu đồ cho phép đối chiếu hiệu năng ở lượng trải nghiệm tương đương.

### 6.3 Minh họa hành vi và lượt luyện bài bổ sung

Trong thí nghiệm tổng hợp v4b, 0/9 ô đạt đồng thời các ngưỡng kỹ năng và chuỗi. Cấu hình dùng để minh họa được xác định trước là adaptive seed 0. Cấu hình này chưa đạt các ngưỡng nên kết quả v4b chỉ có replay chuỗi kỹ năng. Replay chẩn đoán cố định có 6 nốt, P=0.667, R=0.333, F1=0.444; nó chỉ là một trong các đoạn test, không thay thế kết quả 24 nốt ở bảng trên. Sau khi khóa kết quả v4b, một lượt bổ sung luyện trực tiếp hai bài được khởi chạy với ngân sách tối đa 60 phút mỗi bài. Hai checkpoint riêng cùng khởi đầu từ adaptive seed 0; CEM dùng 8 ứng viên và 3 elite, theo các đoạn có onset trong cửa sổ 4 s. Checkpoint được chọn trên các đoạn theo dõi có thể đã được luyện; replay toàn bài được xuất không phụ thuộc ngưỡng precision. Lượt bổ sung chưa được đưa vào các bảng kết quả của bản thảo này và không phải kiểm tra khái quát hóa sang bài mới.

![Replay chẩn đoán](figures/demo.jpg)

Hình 5. Giao diện xem lại chuỗi kỹ năng ở thời điểm 1,05 s, adaptive seed 0. Mục tiêu và tiếp xúc có màu riêng. Ảnh được lấy từ lượt kiểm tra tổng hợp v4b, trước khi mở chế độ luyện trực tiếp hai bài.

Giao diện hiển thị lại chuyển động chân/phím và hai neuron DNg100 trong bề mặt não 3D. Màu biểu diễn mức hoạt động DN được chiếu từ mạng MANC lên neuron đồng dạng của FlyWire, khác cá thể và giới tính. Các neuron thật trong mô hình học chủ yếu thuộc VNC; độ sáng DN trên hình não không biểu diễn toàn bộ thay đổi tham số đã học. Màu sắc biểu diễn tín hiệu tính toán, không phải phép đo hoạt động thần kinh trên động vật.

## 7. Thảo luận

Ba cấu hình đạt F1 kiểm tra trung bình gần nhau. Với ba seed và phạm vi tác vụ hẹp, dữ liệu chưa phân biệt được lợi ích của cấu trúc connectome với tác động của các tham số điều khiển đầu ra. Nhánh giữ synapse cố định có ít tham số tự do hơn hai nhánh còn lại, trong khi phép hoán đổi cạnh giữ bậc nhưng thay đổi tổng trọng số đi vào từng neuron. Hai đặc điểm này cần được xét khi diễn giải so sánh.

Sai lệch tiếp xúc là một nguồn lỗi đáng chú ý. Gốc đốt chân dùng trong IK không trùng mặt hình học va chạm; một nghiệm IK có sai số nhỏ vẫn có thể tạo tiếp xúc ở phím lân cận. Hệ số hiệu chỉnh ngang ở v4b bù một phần sai lệch đó, nhưng chưa thay thế mô hình động học dựa trên mặt tiếp xúc. Kiểm tra ưu tiên tiếp theo là đo tầm với, vùng tiếp xúc và đáp ứng phím bằng bộ điều khiển hình học tham chiếu, trước khi quy sai sót cho mạng thần kinh.

Các tham số thần kinh cũng chưa cho phép nhận dạng một cơ chế học riêng. Hai mươi bốn hệ số synapse tác động theo nhóm, còn điều chỉnh ngưỡng MN và các tham số đầu ra có thể bù cho thay đổi cấu trúc mạng. Những phép so sánh tiếp theo cần lần lượt cố định các nhóm tham số này và bổ sung mạng không dùng connectome với số tham số, dữ liệu và ngân sách tương ứng.

Phạm vi kiểm tra hiện tại gồm sáu nốt chậm, tập cao độ nhỏ và tư thế khởi đầu cố định. Nó chưa đại diện cho hợp âm, bước nhảy cao độ, thay đổi nhịp độ hoặc một tác phẩm kéo dài vài phút. Lượt luyện trực tiếp hai bài bổ sung kiểm tra hoạt động của hệ trên dữ liệu đã luyện; một thí nghiệm chuyển giao cần các bài hoặc cấu trúc nốt chưa xuất hiện trong tối ưu.

Các kết quả còn phụ thuộc một máy, một thuật toán tìm kiếm, tập lựa chọn 12 nốt và tập kiểm tra 24 nốt cho mỗi seed. Chưa có đánh giá có hệ thống về độ nhạy theo phần thưởng, ngưỡng lực, bước thời gian và nhiễu cơ học. Kiểm tra tương đương của cách gom bước xác nhận một thay đổi trong thực thi, nhưng chưa chứng minh hội tụ số hoặc độ chính xác sinh cơ học. Các bước còn thiếu này giới hạn kết luận ở cấu hình mô phỏng đã đo.

## 8. Kết luận

Quy trình thực thi trên CPU tăng thông lượng mà giữ nguyên cấu hình vật lý trong phép kiểm tra tương đương đã thực hiện. Trong thí nghiệm tổng hợp, F1 trung bình trên tập kiểm tra là 0.343 ở nhánh adaptive, 0.330 ở nhánh frozen, 0.341 ở nhánh rewired. Chênh lệch giữa các cấu hình còn nhỏ so với phạm vi biến thiên được quan sát qua các seed; dữ liệu chưa xác lập lợi ích riêng của việc tối ưu hệ số synapse. Các kết quả định hướng bước tiếp theo vào hiệu chuẩn tiếp xúc và đối chứng đóng góp của từng nhóm tham số. Kết luận hiện tại áp dụng cho bộ điều khiển lai và tác vụ mô phỏng đã xét.

## Dữ liệu và phần mềm

Mã v4, định nghĩa reward, detector, cấu hình, checksum nguồn, benchmark và kết quả tổng hợp được lưu trong repository dự án. Mã v3 và kết quả v3 được giữ nguyên. Các bản nhạc PDF/MIDI, replay lớn và dữ liệu đồ thị có điều kiện giấy phép được lưu riêng. Nguồn và giấy phép của NeuroMechFly, Three.js và FlyWire đi kèm gói phần mềm. Quyền tái phân phối bản xuất connectome chưa được xác nhận đầy đủ; khả năng tái lập từ kho mã công khai vì vậy còn phụ thuộc việc cung cấp các đầu vào này.

Mỗi lượt lưu run_id, các phiên bản thư viện, checksum các file mô hình/thuật toán chính, seed, ngân sách và kết quả từng ô. Cấu hình phần cứng: Ryzen AI 5 340, 6 core/12 thread; RTX 5050 Laptop 8 GiB. Hiệu năng phụ thuộc nhiệt và phần mềm nền. Không có thí nghiệm động vật sống trong quy trình này.

## Tài liệu tham khảo

[1] [NeuroMechFly v2, Nature Methods, 2024](https://www.nature.com/articles/s41592-024-02497-y).

[2] [Whole-body physics simulation of fruit fly behavior, Nature, 2025](https://www.nature.com/articles/s41586-025-09029-4).

[3] [Jin và cộng sự. Whole-Brain Connectomic Graph Model Enables Whole-Body Locomotion Control in Fruit Fly. arXiv:2602.17997, 2026, preprint](https://arxiv.org/abs/2602.17997).

[4] [Zakka và cộng sự. RoboPianist: Dexterous Piano Playing with Deep Reinforcement Learning. PMLR 229, 2024](https://proceedings.mlr.press/v229/zakka23a.html).

[5] [Empirical Design in Reinforcement Learning. JMLR 25, 2024](https://jmlr.org/papers/v25/23-0183.html).

[6] [MuJoCo Python documentation, phiên bản 3.9.0](https://mujoco.readthedocs.io/en/3.9.0/python.html).

[7] [MuJoCo Warp documentation](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html) và [repository chính thức](https://github.com/google-deepmind/mujoco_warp).

[8] [Pugliese và cộng sự. Connectome simulations identify a central pattern generator circuit for fly walking. bioRxiv, 2025, preprint](https://doi.org/10.1101/2025.09.12.675944). [Code/data repository](https://github.com/smpuglie/Pugliese_cpg_2025).

[9] [Shiu và cộng sự. A Drosophila computational brain model reveals sensorimotor processing. Nature 634, 210-219, 2024](https://www.nature.com/articles/s41586-024-07763-9).
