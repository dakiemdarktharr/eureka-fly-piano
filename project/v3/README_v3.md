# Fly Piano Lab v3 — hướng dẫn chạy

Ứng dụng nghiên cứu cục bộ: tối ưu 16 tham số điều khiển chân bằng CEM, giữ connectome cố định, xem đường học và replay hai bản piano trên mô hình 3D. Mục tiêu 85% chưa đạt trong lượt thăm dò đã chạy; không có học synapse sinh học.

## Mở app Windows đã đóng gói

Chạy `project/v3/dist/FlyPianoLab/FlyPianoLab.exe`, hoặc `project/v3/Start-FlyPiano.ps1`. Giữ nguyên cả thư mục `FlyPianoLab`; không chỉ sao chép riêng file EXE. Trình duyệt mở tại `http://127.0.0.1:8877/`. Nếu server cũ đang dùng cổng này, EXE mở giao diện đang có.

App gồm Huấn luyện, Mô phỏng 3D và Paper & giới hạn. Chọn ngân sách và seed để tạo lượt mới; “Tiếp tục” thêm ngân sách cho lượt được chọn. “Tạm dừng” lưu RNG/quần thể; phần đánh giá dở sẽ chạy lại. “Tạo replay checkpoint” chạy đầy đủ hai bài từ tham số đã lưu, sau đó chọn “Đã học” trong viewer. Chỉ một worker thao tác dữ liệu tại một thời điểm.

Replay là dữ liệu mô phỏng đã tính trước, không phải solver chạy trực tiếp trong trình duyệt. Âm thanh tiếp xúc và mục tiêu là hai lựa chọn riêng. Màu trên hai DNg100 là rate mô hình chiếu lên homolog giải phẫu khác cá thể, không phải đo hoạt động não.

Trạng thái ghi ở `runtime` cạnh EXE; ở source mode là `project/v3/runtime`. Có thể đặt `FLYPIANO_STATE` sang thư mục khác. Để xem cùng campaign từ source và EXE, đặt biến này tới cùng thư mục runtime, nhưng chỉ chạy một app/worker quản lý nó. Gói EXE cục bộ có dữ liệu do người dùng cung cấp; không upload nó lên public release.

## Chạy từ source

Python 3.12. Môi trường hiện có tại `project/v2/.venv` có toàn bộ dependency. Clone mới có thể dùng môi trường riêng:

```powershell
python -m venv project/v3/.venv
project/v3/.venv/Scripts/python -m pip install -r project/v3/requirements.txt
project/v3/.venv/Scripts/python project/v3/app.py
```

Repo không kèm dữ liệu riêng tư. Sao chép các file đã được cấp quyền vào đúng đường dẫn:

| Vị trí | Nội dung |
|---|---|
| `project/connectome/weights.npy`, `neurons.csv` | Phân đồ thị đã dùng trong manifest |
| `project/v2/data/{merry,pool}_score.json` | Score OMR tạm thời có schema của v2 |
| `project/v2/data/ik_cache.npz` | IK cache đúng body/keyboard |
| `project/v2/data/{merry,pool}_{full,constant}.{json,bin}` | Replay baseline để viewer xem ngay |
| `project/v2/data/{merry,pool}_reference.mid` | MIDI mục tiêu tùy chọn |
| `project/v2/scores/private/*.pdf` | Sheet đối chiếu tùy chọn, đúng tên source_pdf |

Định dạng score gồm `duration`, `notes`, `bars`; manifest và parser v2 giải thích nguồn. Không thay arbitrary MIDI vào JSON rồi giữ fingerprint cũ. App hiển thị danh sách thiếu; không âm thầm tạo dữ liệu giả. `ik_cache.npz` phải đi cùng body đã khóa. Những run mới kiểm tra hash score và plant khi resume; lượt đầu lịch sử chỉ có score hash, manifest sau chạy ghi rõ thời điểm quan sát.

```powershell
project/v3/.venv/Scripts/python project/v3/train.py --minutes 15 --seed 0
project/v3/.venv/Scripts/python project/v3/train.py --run RUN_ID --resume --minutes 60
project/v3/.venv/Scripts/python project/v3/train.py --run RUN_ID --export
```

Ưu tiên các nút app để tránh khởi chạy nhiều CLI cùng ghi một run. Không chạy CLI đồng thời với worker app.

## Docker Compose

Docker Desktop/Engine cần được cài trên máy chạy. Máy phát triển hiện tại không có Docker; kiểm tra build/start Linux thực hiện riêng trong GitHub Actions, xem trạng thái workflow trước khi suy ra đã pass.

```powershell
docker compose up --build -d
docker compose logs -f
docker compose down
```

Mở `http://127.0.0.1:8877/`. Compose bind cổng vào loopback; graph, score và replay v2 mount read-only; `flypiano_state` là volume lưu campaign. Không dùng `down -v` nếu muốn giữ các run. Clone mới phải chuẩn bị dữ liệu ở bảng trên. Container không chứa PDF/OMR/replay riêng tư. `/api/health` có `ok` cho server và `ready` cho đầu vào; CI không có dữ liệu phải trả `ready=false` rõ ràng.

Docker smoke test không kiểm định hội tụ hoặc tái lập physics Windows/Linux. Thí nghiệm so host cần cùng input hashes và tolerance khoa học, chưa được hoàn tất ở v3.

## Đóng gói Windows và tạo paper

```powershell
project/v2/.venv/Scripts/python -m pip install pyinstaller==6.18.0
project/v2/.venv/Scripts/python project/v3/build_windows.py
```

Builder tạo onedir, kèm body/brain, private inputs và hai PDF nếu đã có. Muốn tái xuất paper cần matplotlib, ReportLab, NumPy và font Arial Windows; môi trường `.venv` ở gốc đã có:

```powershell
.venv/Scripts/python project/v3/build_paper.py --run RUN_ID
```

Phải xuất cả hai replay trước để bảng demonstration có dữ liệu thật. Script xuất `paper/checkpoint_results.csv`, `evidence_v3.json`, hình và hai PDF. Nó không tự điền kết quả mong muốn.

## Protocol và kết quả ban đầu

CEM dùng 6 ứng viên + incumbent, clip 6 giây mỗi bài. Split theo ô nhịp trong cùng tác phẩm; validation và test mỗi phần lấy 2 clip mỗi bài. Đây không phải đánh giá toàn bộ miền held-out hoặc tác phẩm mới. Detector tiếp xúc giữ cố định. Xem `PROTOCOL.md` và paper để biết tham số/giới hạn.

Thành công cần P >0,85, R/F1 ≥0,85 cho cả hai bài, ba checkpoint theo lịch liên tiếp, không solver warning. Hết ngân sách không được coi là thành công. Resume sau khi đã mở test làm test tiếp theo trở thành exploratory.

Lượt `20260918T043824-s0-5816`: 903,42 giây tối ưu, 172 ứng viên, 24 thế hệ hoàn tất. Macro-F1 validation 0,103 → 0,161; plateau từ 5 đến 15 phút. Test macro-F1 0,074. Một seed, OMR tạm thời; không CI thống kê, không khẳng định lợi ích connectome.

## Kiểm thử và nguồn

```powershell
project/v2/.venv/Scripts/python -m unittest discover -s project/v3/tests -v
```

`tests/ui_check.cjs` dùng Playwright và biến `PLAYWRIGHT_MODULE`, `CHROMIUM_PATH`, `APP_URL` tùy chọn. `qa/validation_summary.json` ghi các kiểm tra cục bộ thực tế; workflow `.github/workflows/v3-ci.yml` kiểm tra source/container không có private inputs. Thử pause/resume và frozen app có log riêng. Không coi test chưa chạy là pass.

Nguồn body: NeuroMechFly Apache-2.0; Three.js MIT; brain surface navis-flybrains GPL-3.0; skeleton release liên quan CC-BY-4.0. Xem `project/v2/assets/attribution.json` và `licenses`. Quyền tái phân phối graph/score còn cần xác minh trước công bố. Repo này không cấp lại quyền cho dữ liệu của bên thứ ba.
