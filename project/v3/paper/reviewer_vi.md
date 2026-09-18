# Hồ sơ phản biện v3: vấn đề, cách xử lý chính và fallback

Góc nhìn biên tập · biomechanics · computer science · 18-09-2026

## Quyết định ở trạng thái hiện tại

Chưa nên nộp như bài chứng minh “ruồi học piano” hoặc whole-brain digital twin. Mục tiêu rõ và bảo vệ được của v3 là đo ảnh hưởng của tối ưu bộ đọc ra lên độ chính xác tiếp xúc, với connectome, body và detector cố định. Đây là bản thảo thăm dò. Việc có chương trình chạy được và paper đầy đủ không đồng nghĩa đã có bộ thí nghiệm đủ cho acceptance.

Không thể loại bỏ mọi câu hỏi của reviewer hay bảo đảm Q2. Có thể giảm những câu hỏi phát sinh do thiếu thông tin bằng evidence ledger: mỗi claim phải có protocol, file kết quả, đối chứng, giới hạn suy luận và điều kiện bác bỏ. Những hướng dưới đây là phương án xử lý, không phải các kết quả đã được thực hiện. “Fallback” là thu hẹp hoặc thay câu hỏi khoa học một cách minh bạch; không đổi metric sau khi thấy kết quả để gọi thất bại là thành công.

## A. Những vấn đề dễ dẫn đến desk reject

### R01. Tính mới có vượt việc ghép công cụ và thêm piano không?

Chính: lập bảng prior art theo graph, học, observation, decoder, body và validation; chứng minh một kết luận phương pháp tổng quát bằng nhiều decoder/tác vụ. Điều kiện đóng: có phát hiện mới, phân biệt được với đóng góp của NeuroMechFly và nguồn CPG. Fallback: software/methods paper, đánh giá utility và tái lập độc lập. Hiện tại: chưa có bằng chứng tính mới đủ rộng; UI là công cụ hỗ trợ.

### R02. Não có chọn nốt không hay scheduler làm sẵn?

Chính: xây nhánh decoder không truy cập score-to-IK, quy định observation horizon, task cue và feedback hợp lệ; so cùng observation/actuator/budget với decoder-only. Đóng khi can thiệp neural state tạo dự đoán phân biệt được với relay. Fallback: giữ kiến trúc đặc quyền nhưng chỉ nghiên cứu tối ưu readout và phân tích đường thông tin. Hiện tại: fallback đã áp dụng vào claim; đường tắt chưa bị loại bỏ.

### R03. “Học” có phải cập nhật synapse hoặc primitive không?

Chính: định nghĩa latent primitive, policy, loss, quy tắc học và phép composition; kiểm tra transfer sang motif/layout mới với model khóa. Fallback: gọi chính xác là CEM tối ưu 16 tham số kỹ thuật; bỏ claim neural memory và primitive emergent. Hiện tại: có optimizer thật và log tham số, nhưng fallback vẫn cần thiết vì graph cố định.

### R04. Connectome mang lại lợi ích gì?

Chính: huấn luyện graph thật, rewired giữ bậc/dấu, oscillator và decoder-only cùng dữ liệu, ngân sách và gain/power; paired evaluation trên test mới. Đóng khi hiệu ứng ổn định qua seed/sequence và vượt sai số số học. Fallback: công bố kết quả âm tính và điều kiện thất bại, không tuyên bố ưu thế. Hiện tại: constant v2 tốt hơn full; CEM v3 chưa có đối chứng được tối ưu tương đương.

### R05. Lesion failure có bị cài sẵn bởi gate không?

Chính: rescue gain, tín hiệu khớp phân bố/energy, shuffle phase giữ phổ và hoán đổi định danh chân; đăng ký trước phép thử tách mất công suất khỏi mất cấu trúc. Fallback: mô tả lesion là dependency của kiến trúc, không là bằng chứng sinh học. Hiện tại: gate khiến lesion có thể tắt ấn theo thiết kế; chưa đóng cơ chế.

### R06. Mô hình là whole-brain, brain–VNC hay VNC?

Chính: nếu mở rộng brain dynamics, dùng matching có độ tin cậy, kiểm tra boundary/cut edges và homolog thay thế; mọi cạnh phải có provenance. Fallback: nói rõ VNC 412 neuron với hai hình thái homolog ở não để hiển thị. Hiện tại: fallback đã áp dụng; không có toàn bộ brain dynamics hoặc synapse nối hai cá thể được đo.

## B. Học, tiêu chí dừng và thống kê

### R07. Vì sao chọn 85% và chỉ precision?

Chính: biện minh ngưỡng theo yêu cầu tác vụ và đường precision–recall; kiểm tra cả coverage và lỗi dư. Đóng khi ngưỡng đăng ký trước, detector khóa và cả hai bài đạt trên test mới. Fallback: giữ 85% là mục tiêu vận hành của người dùng, báo cáo khoảng cách đến mục tiêu. Hiện tại: v3 yêu cầu P >85%, R/F1 ≥85% cho cả hai bài; chưa có ý nghĩa sinh học cho ngưỡng.

### R08. Chỉ dừng khi đạt có gây thiên lệch hay chạy mãi không?

Chính: ngân sách tối đa định trước, ghi mọi lượt kể cả thất bại, target-gated stopping trên validation và test mới sau lựa chọn. Nếu phân tích kiểm định tuần tự thì dùng thiết kế thống kê phù hợp, không tái dùng p-value tĩnh. Fallback: giới hạn lượt, trạng thái budget_exhausted, resume có log. Hiện tại: đã thực hiện fallback; ba checkpoint cùng validation không phải ba mẫu độc lập.

### R09. So theo phút có công bằng giữa máy/thuật toán không?

Chính: báo phần cứng, thread, workload, training/evaluation time, physics steps và số objective evaluations; so cùng ngân sách tương tác lẫn compute. Fallback: chỉ so trong cùng host, luôn cung cấp trục bước mô phỏng. Hiện tại: app có nhiều clock và số bước, nhưng một lượt có tải máy thực tế; chưa benchmark phần cứng độc lập.

### R10. Validation có thực sự chưa dùng để học?

Chính: khóa split theo motif/sequence family, hyperparameter tuning trên development set, test composition mới chưa mở. Fallback: gọi đúng within-piece holdout và chỉ báo cáo thăm dò. Hiện tại: optimizer không dùng val gradient/ranking nhưng val dùng stopping; train-monitor dùng lặp có nguy cơ overfit. Chưa phải generalization sang tác phẩm mới.

### R11. Mẫu validation quá ít và reset đoạn có làm dễ tác vụ?

Chính: đánh giá toàn miền held-out liên tục hoặc nhiều đoạn bao phủ đã chọn trước, stratify chord/tempo/transition, giữ state hợp lệ khi cần. Fallback: ghi rõ 2 × 6 giây mỗi bài, cùng reset và cropping; replay toàn bài chỉ là demo. Hiện tại: đã công khai sampling; chưa thể suy ra performance toàn miền từ 12 giây.

### R12. Test sau resume còn độc lập không?

Chính: chốt một campaign trước test; nếu đã nhìn kết quả và thay quyết định, dùng test mới hoặc nested evaluation. Fallback: đánh dấu mọi test sau resume là exploratory, lưu toàn bộ history. Hiện tại: app ghi số lần test và cảnh báo phạm vi; không tự xóa lần test bất lợi.

### R13. Một seed có đủ không? Có pseudoreplication không?

Chính: dùng nhiều sequence độc lập và seed, chọn cỡ mẫu theo độ chính xác hiệu ứng mong muốn; paired contrast và hierarchical intervals phù hợp cấu trúc. Fallback: mô tả case study một seed, không p-value, không CI giả từ hàng nghìn nốt. Hiện tại: fallback áp dụng; seed không phải cá thể sinh học. Xem Patterson et al. và Agarwal et al. ở cuối tài liệu.

### R14. CEM có bị yếu hoặc overfit monitor không?

Chính: quét hyperparameter trên development set, so CEM với random search và optimizer thích hợp cùng budget; dùng train-monitor rộng/luân phiên, khóa trước xác nhận. Fallback: gọi đây là proof-of-function optimizer với 16 tham số, không SOTA hoặc đủ chứng minh trần hiệu suất. Hiện tại: một cấu hình CEM, monitor chỉ một đoạn mỗi bài; tăng phút chưa chắc chữa bottleneck.

### R15. Neural mix có thể học cách bỏ mạng không?

Chính: log mix và sensitivity; so mix cố định 1, mix học và mix 0 với budget khớp, kiểm tra rescue. Fallback: mọi cải thiện chỉ gán cho readout tổng thể, không cho connectome. Hiện tại: mix học trong [0,1], có đường bypass theo thiết kế; paper và viewer đã nêu rõ.

## C. Biomechanics và tính khả thi

### R16. Tỷ lệ phím–bàn chân và lực có hợp lý không?

Chính: bảng đơn vị/nguồn, đo hoặc biện minh spacing, stiffness, mass, damping, friction; quét tỷ lệ toe/key và bản đồ reachable. Đóng khi kết luận bền trong miền vật lý có nguồn. Fallback: gọi là giao diện cảm biến thu nhỏ giả định, không piano thật. Hiện tại: mm–g–s và µN đã nêu; chưa hiệu chuẩn ngoài mô phỏng.

### R17. Actuator có vượt sức cơ ruồi không?

Chính: mapping MN–muscle có nguồn, torque-limited actuator, độ trễ và kiểm chứng force/velocity; báo bão hòa và công. Fallback: mô hình robot dạng ruồi với position servo, không dự đoán sức cơ sinh học. Hiện tại: có log công actuator, chưa có cơ-gân hoặc torque chuẩn; log công không tự xác nhận cơ.

### R18. Tethering bỏ cân bằng, sáu chân có chơi được hợp âm 7–8 nốt?

Chính: tính feasibility bound theo đồng thời/reach/hold, tách allocator failure khỏi tracking; nếu untethered phải thêm ground support và balance objective. Fallback: giữ điều kiện tethered, thêm benchmark hợp âm trong miền khả thi; arrangement giản lược phải tách tên và báo nốt bỏ. Hiện tại: full score được giữ nhưng không hứa mọi hợp âm khả thi.

### R19. Contact detector có bị tối ưu để gian metric không?

Chính: hiệu chuẩn một chân–một phím, biên phím, hai chân, giữ/ngả; khóa ngưỡng bằng calibration set trước học; sensitivity ngưỡng và force impulse. Fallback: giữ một detector cố định và báo nốt dư thật, không tăng ngưỡng sau khi thấy P thấp. Hiện tại: detector không thuộc 16 tham số; thử hiệu chuẩn thực nghiệm còn thiếu.

### R20. Không có solver warning có nghĩa là hội tụ không?

Chính: convergence ladder dt/solver quality cho quỹ đạo, lực, impulse và event metric; yêu cầu sai số thấp hơn hiệu ứng nghiên cứu với tiêu chí chọn trước. Fallback: báo dải nhạy cảm, hạ claim thành mô tả hệ số hóa cụ thể. Hiện tại: v2 đã phát hiện F1 nhạy dt; chưa đóng. Không được bỏ kết quả này khỏi paper v3.

### R21. Self-collision, joint range và feedback có đủ sinh học không?

Chính: kiểm tra collision/cấu hình khớp theo anatomy, mapping proprioceptor có chứng cứ, perturbation kín thời điểm với delay/noise controls. Fallback: giữ phạm vi engineering và sensitivity, không giải thích phản xạ sinh học. Hiện tại: giới hạn IK kỹ thuật, feedback projection giả định và tethering; chưa có kiểm chứng cơ chế cảm giác.

### R22. Kết quả âm tính có thể chỉ do implementation sai?

Chính: positive controls tăng dần: contact tĩnh, single-key, trajectory oracle trong cùng giới hạn, synthetic motif đơn giản, rồi full task; error budget theo IK/allocator/contact/timing. Fallback: gọi là feasibility failure và công bố trace để tái lập, không kết luận connectome vô ích. Hiện tại: parity v2/v3 có nhưng chưa đủ positive controls để quy kết cơ chế.

## D. Dữ liệu, đo lường và hiển thị

### R23. Hai score toàn bài có đúng nốt không?

Chính: MusicXML/MIDI đúng arrangement có quyền sử dụng, hoặc hai lượt chép độc lập và adjudication theo ô; lưu lỗi note-level và changelog. Fallback: synthetic clean benchmark làm chính, hai OMR toàn bài chỉ demo provisional. Hiện tại: 18 trang bao phủ đủ, còn 3/12 cờ ô; không đánh giá OMR bằng chính file OMR.

### R24. Chỉ onset F1 có che lỗi giữ nốt, chord hoặc pedal?

Chính: báo onset/offset, duration IoU, chord exact match, pitch confusion, tempo drift và toàn bộ ngưỡng định trước. Fallback: chỉ gọi onset-event accuracy, không musical quality. Hiện tại: onset một-một, nhiều tolerance; duration IoU có điều kiện là chẩn đoán chưa xác nhận; pedal/rubato chưa có ground truth.

### R25. Sai số graph và neurotransmitter có bị bỏ qua?

Chính: manifest release, cut-edge audit, uncertainty ở NT/receptor/sign, nhiều graph hoặc homolog và sensitivity boundary/normalization. Fallback: kết luận về một mô hình rate cụ thể, không phổ quát ruồi. Hiện tại: node/cạnh và nguồn có; phiên bản export nền, receptor, gap junction và neuromodulation còn thiếu.

### R26. Neuron sáng trong não có phải dữ liệu hoạt động thật?

Chính: nguồn ID, tọa độ, transformation, thang màu cố định, homolog confidence; nếu so calcium phải có observation model và dữ liệu. Fallback: tô hai skeleton bằng rate mô hình, nhãn rõ cross-specimen projection, vùng chưa mô hình để trung tính. Hiện tại: fallback đã thực hiện; không thêm ánh sáng giả vào vùng não chưa có dynamics.

### R27. Demo đẹp có che sai nốt hoặc dùng soundtrack mục tiêu?

Chính: replay xuất từ telemetry, hash/time đồng bộ, target/contact tách, hiển thị miss/extra và mọi đoạn toàn bài. Fallback: silent replay nếu audio chưa xác minh, tuyệt đối không gọi target audio là model output. Hiện tại: hai kênh tách, full replay; performance thấp vẫn hiển thị.

## E. Tái lập, phần mềm và xuất bản

### R28. Resume có đổi thuật toán hoặc mất chi phí không?

Chính: lưu RNG/population/score hash/parameter/budget, kiểm tra pause giữa ứng viên và resume cùng trạng thái; mở test có history. Fallback: nếu provenance thay đổi, tạo run mới và giữ run cũ, không ghép learning curve. Hiện tại: atomic checkpoints và RNG có; resume phải kiểm tra fingerprint, phần tính dở được tính chi phí rồi chạy lại.

### R29. Chạy trên máy khác có giống không?

Chính: fresh environment, dependency lock, asset hash và cùng dữ liệu trên Windows/Linux; so trong tolerance đã biện minh. Fallback: công bố local-only reproducibility, Docker smoke test chỉ xác nhận app khởi động. Hiện tại: source tests, browser QA và gói Windows được kiểm tra theo log; không coi image build hoặc health=ok là tái lập physics.

### R30. Quyền dùng score, graph, mesh, âm thanh có rõ không?

Chính: license manifest, quyền connectivity export/arrangement và kế hoạch reviewer access; bộ benchmark public-domain/synthetic để tái lập công khai. Fallback: repo riêng tư chứa source/manifest, gói dữ liệu ở máy người dùng, giữ asset chưa rõ quyền khỏi public release. Hiện tại: score/OMR/replay/graph không source commit; vẫn phải xác minh trước nộp journal.

### R31. Docker/app có đủ để journal tái lập không?

Chính: cung cấp command, input schema, checksums, environment, expected outputs và clean-machine test; phân biệt ready thiếu dữ liệu với server health. Fallback: reviewer package được cấp quyền riêng và hướng dẫn import dữ liệu, không claim one-click public replication. Hiện tại: app Windows phục vụ người dùng; Docker tách dữ liệu riêng tư bằng volume.

### R32. Nhắm Q2 thế nào và điều gì phải làm trước khi nộp?

Chính: chọn journal theo scope phương pháp/computational biomechanics/software, kiểm tra quartile đúng năm và category; viết cover letter quanh đóng góp đã có bằng chứng. Fallback: workshop/software venue hoặc preprint thăm dò trong khi hoàn thiện thí nghiệm. Hiện tại: chưa chọn/khẳng định journal Q2 cụ thể; không có ước lượng acceptance hợp lệ.

## Lộ trình ưu tiên và điều kiện chuyển sang submission

1. Đóng đo lường trước: score tổng hợp sạch, positive controls, feasibility map, sensitivity dt/contact. Điều kiện qua: lỗi số học và detector nhỏ hơn hiệu ứng cần phân biệt; mọi lỗi còn lại được phân loại.

2. Đóng câu hỏi cơ chế: bỏ hoặc kiểm soát privileged decoder; train đối chứng cùng ngân sách, gain/power và input; lock protocol trước test mới. Điều kiện qua: có kết luận phân biệt được về vai trò connectome, kể cả âm tính có giá trị.

3. Đóng thống kê: nhiều motif/sequence và seed, sample-efficiency curves, uncertainty theo tầng, test mới không mở trong development. Điều kiện qua: hiệu ứng và độ bất định đủ cho kết luận, không lấy số nốt làm số cá thể.

4. Đóng khả năng tái lập/quyền dữ liệu: second-host reproduction, package hợp lệ, source/asset/version manifest, raw trace và script tạo mọi hình/bảng. Điều kiện qua: người độc lập chạy được các bảng chính và hiểu đúng trạng thái dữ liệu.

5. Chốt mức claim và journal: nếu chưa có validation sinh học, giữ hướng methods/engineering. Nếu muốn paper neuroscience cơ chế, cần dự đoán có thể bác bỏ và dữ liệu hành vi tự nhiên độc lập. Piano vẫn nằm trong demonstration; không cần bắt ruồi thật chơi đàn để kiểm chứng một giả thuyết vận động.

## Nguồn phương pháp và nền tảng

[Empirical Design in Reinforcement Learning — Patterson et al., JMLR 2024](https://jmlr.org/papers/v25/23-0183.html): thiết kế thực nghiệm, seed, đường học và lựa chọn endpoint.

[Deep RL at the Edge of the Statistical Precipice — Agarwal et al., NeurIPS 2021](https://proceedings.neurips.cc/paper/2021/hash/f514cec81cb148559cf475e7426eed5e-Abstract.html): giới hạn suy luận từ ít lượt chạy và báo cáo bất định.

[NeuroMechFly/FlyGym](https://neuromechfly.org/), [nguồn CPG](https://github.com/smpuglie/Pugliese_cpg_2025), [mô hình não Shiu et al.](https://www.nature.com/articles/s41586-024-07763-9), [comparative connectomics](https://pmc.ncbi.nlm.nih.gov/articles/PMC12222017/): nguồn hệ thống và giới hạn liên hệ giữa connectivity, embodiment và xác nhận sinh học.

Đây là tổng hợp và đề xuất thiết kế của nhóm cho mô hình hiện tại, không phải trích kết luận rằng các tài liệu nguồn đã xác nhận ruồi chơi piano.
