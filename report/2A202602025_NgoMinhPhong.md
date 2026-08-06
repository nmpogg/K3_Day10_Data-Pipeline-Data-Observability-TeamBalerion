# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin         | Nội dung                  |
| ------------------ | -------------------------- |
| Họ và tên       | Ngô Minh Phong             |
| MSSV               | 2A202602025                     |
| Khóa/Lớp         | K3              |
| Tên nhóm         | Balerion     |
| Vai trò chính    | Tích hợp hệ thống & Pipeline Orchestration                 |
| Repository         | https://github.com/nmpogg/K3_Day10_Data-Pipeline-Data-Observability-TeamBalerion |
| Ngày hoàn thành | 2026-08-06               |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao  | Trạng thái                                 |
| ------------------ | --------------------- | ---------------- | ----------------- | -------------------------------------------- |
| Baseline Orchestration | `src/pipelines/phase1.py` | Toàn bộ các module con (ingestion, cleaning, eval, observability) | Artifacts chuẩn, metrics baseline | Hoàn thành |
| Corruption & Repair Flow | `src/pipelines/corruption_flow.py` | Cấu hình tham số, `corrupt_clean_dataframe` | `corrupted_metrics.json`, `repaired_metrics.json`, `corruption_log.json` | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động                         | Thành viên/module được hỗ trợ | Kết quả                    |
| ------------------------------------ | ------------------------------------ | ---------------------------- |
| Debug Lỗi Fallback LLM Judge | Nguyễn Thùy Trang / `metrics.py` | Tìm ra lỗi do `with_structured_output()` không chạy được trên HuggingFace và giúp viết lại prompt sinh JSON. |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao       | Cách xác minh         |
| --------------------------- | ----------------------------- | ------------------------- | ----------------------- |
| Chạy luồng tích hợp Phase 1 | `script/run_phase1.py` | `data/results/baseline_metrics.json` | Chạy lệnh `python script/run_phase1.py` |
| Chạy luồng tích hợp Phase 2 | `script/run_corruption_flow.py` | `data/reports/corruption_report.md` | Chạy lệnh `python script/run_corruption_flow.py` |

Nêu một output cụ thể mà phần việc của bạn tạo ra hoặc giúp xác minh:

File `data/reports/corruption_report.md` là bằng chứng mạnh mẽ nhất thể hiện sự điều phối thành công của orchestration: so sánh toàn diện 3 pha (Baseline, Corrupted, Repaired).

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Làm thế nào để gắn kết tất cả các module xử lý dữ liệu (ingestion, cleaning, QA retrieval, eval) thành một chuỗi tự động hoàn toàn mà không cần can thiệp tay giữa các bước? Làm sao để tự động build lại index khi dữ liệu thay đổi (corrupted -> repaired)?

### Cách triển khai

Sử dụng script `phase1.py` và `corruption_flow.py` đóng vai trò là "nhạc trưởng". Gọi tuần tự từng module với các đầu ra/đầu vào truyền cho nhau. Bổ sung các bước tạo `LocalEmbeddingIndex` mới mỗi khi thay đổi dataset để đánh giá lại QA.

### Input, output và contract

| Thành phần                   | Mô tả                                     |
| ------------------------------ | ------------------------------------------- |
| Input                          | Module code từ các thành viên khác |
| Output                         | Metrics và báo cáo tổng hợp |
| Module phụ thuộc             | `crossref.py`, `cleaning.py`, `quality.py`, `metrics.py` |
| Module sử dụng output        | Reporting module |
| Điều kiện lỗi cần xử lý | Xử lý lỗi nếu module LLM crash bằng catch Exception hoặc fallback. |

### Cách xác minh

```bash
python script/run_corruption_flow.py
```

- **Kết quả mong đợi:** Báo cáo markdown cuối cùng so sánh được cả 3 giai đoạn.
- **Kết quả thực tế:** Code chạy trơn tru, xuất báo cáo `corruption_report.md` chính xác.
- **Artifact/log:** `data/reports/corruption_report.md`

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Khi chạy flow repair, làm sao để chắc chắn dữ liệu sạch?
- **Các phương án đã cân nhắc:** (1) Sửa ngược lại từ DataFrame lỗi. (2) Đọc lại từ Raw Records gốc.
- **Phương án đã chọn:** Đọc lại từ Raw Records gốc (`papers.json`).
- **Lý do:** Đây là best practice của Data Engineering (tính Immutability). Dữ liệu gốc luôn đúng, ta chạy lại cleaning pipeline từ đầu sẽ chắc chắn lấp được chỗ hổng thay vì "chữa cháy" thủ công.
- **Bằng chứng quyết định phù hợp:** Score Repair hồi phục 100%.

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:** Repaired Score thấp hơn Baseline dù nội dung y hệt.
- **Nguyên nhân gốc:** LLM model bị crash khi sinh kết quả đánh giá, dẫn đến fallback về hàm F1. F1 đếm chữ rất cứng nhắc nên chỉ lệch 1 từ là đánh rớt điểm thê thảm.
- **Cách xử lý:** Cùng với Thùy Trang sửa `metrics.py` để không dùng hàm `with_structured_output` mà bắt model tự sinh JSON thô.
- **Cách xác minh sau khi sửa:** `python script/run_corruption_flow.py` xuất ra Repaired Judge Accuracy 100%.
- **Điều học được:** Fallback metric ngớ ngẩn đôi khi còn có hại hơn là bắn thẳng lỗi.

## 7. Hiểu biết về luồng end-to-end

1. **Dữ liệu đi từ Crossref đến vector index như thế nào?** Fetch -> JSON raw -> Clean & concat string -> Chunking -> Vector Embeddings -> ChromaDB Index.
2. **Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality ra sao?** Retrieval dùng `document IDs` ground-truth để tính Hit Rate. Answer quality so sánh câu sinh ra với `ground_truth` answer.
3. **Quality checks khác freshness monitoring ở điểm nào trong bài lab?** Quality check coi tính đúng đắn cấu trúc/loại bỏ rỗng. Freshness đo độ "cũ" của record theo thời gian thực (Age Days).
4. **Vì sao phải dùng cùng test set cho baseline, corrupted và repaired?** Để cố định control variable, đảm bảo điểm thay đổi là do Dữ Liệu thay đổi chứ không phải do câu hỏi khó lên.
5. **Repair được xem là thành công dựa trên artifact và metric nào?** Dựa trên `repaired_metrics.json` có điểm bằng hoặc tiệm cận `baseline_metrics.json`.

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal          | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| ---------------------- | -------: | --------: | -------: | ------------------------- |
| `retrieval_hit_rate` |      100% |     83.33% |      100% | Mất title làm Retriever hoàn toàn "mù" |
| `mean_token_f1`      |      0.67 |       0.51 |      0.69 | F1 thể hiện rõ sự phá hoại của text noise |
| `judge_accuracy`     |      100% |     66.67% |      100% | Độ dốc rõ rệt chứng minh LLM hiểu context |
| `mean_judge_score`   |      5.0 |       3.67 |      5.0 | Sự hồi phục là hoàn hảo |
| Quality checks         |      Pass |       Fail |      Pass | Bắt lỗi Duplicate, Blank Summary rất nhạy |
| Freshness status       |      Fresh |       Stale |      Fresh | Freshness giúp bắt dữ liệu quá hạn xuất sắc |

### Kết luận từ số liệu

1. **Data corruption** (Xóa Title/Authors) → **Quality signal thay đổi** (Completeness/Freshness fail) → **Agent metric thay đổi** (Retrieval giảm, Accuracy sập).
2. **Repair action** (Rebuild từ raw) → **Quality/freshness signal phục hồi** (Về Pass/Fresh) → **Agent metric phục hồi** (Accuracy đạt lại 100%).

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất

1. Orchestration bằng code Python (không dùng Airflow) cần try-catch và logging rất cẩn thận.
2. Việc chia tách môi trường cho Ingestion và Retrieval là vô cùng quan trọng (Data Contract).
3. RAG Agent thông minh tới đâu cũng vô dụng nếu dữ liệu nhúng (Embedding Data) bị hỏng hoặc chứa rác.

### Nếu có thêm thời gian

Mình sẽ triển khai Apache Airflow DAG cho luồng pipeline này để theo dõi tự động thay vì dùng script chạy tuần tự.

## 10. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Ngô Minh Phong
**Ngày xác nhận:** 2026-08-06
