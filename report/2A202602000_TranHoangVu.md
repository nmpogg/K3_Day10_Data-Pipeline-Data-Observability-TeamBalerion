# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin         | Nội dung                  |
| ------------------ | -------------------------- |
| Họ và tên       | Trần Hoàng Vũ             |
| MSSV               | 2A202602000                     |
| Khóa/Lớp         | K3              |
| Tên nhóm         | Balerion     |
| Vai trò chính    | Data Cleaning & Quality Observability                 |
| Repository         | https://github.com/nmpogg/K3_Day10_Data-Pipeline-Data-Observability-TeamBalerion |
| Ngày hoàn thành | 2026-08-06               |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao  | Trạng thái                                 |
| ------------------ | --------------------- | ---------------- | ----------------- | -------------------------------------------- |
| Data Cleaning | `src/ingestion/cleaning.py` | `data/raw/papers.json` | `data/clean/papers_clean.csv` và `text_for_embedding` | Hoàn thành |
| Data Quality Check | `src/observability/quality.py` | `papers_clean.csv` | `baseline_quality_check.json`, `freshness_report.json` | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động                         | Thành viên/module được hỗ trợ | Kết quả                    |
| ------------------------------------ | ------------------------------------ | ---------------------------- |
| Thiết lập Data Model | Nguyễn Thùy Trang | Cung cấp cấu trúc `text_for_embedding` để Trang chạy test set chính xác. |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao       | Cách xác minh         |
| --------------------------- | ----------------------------- | ------------------------- | ----------------------- |
| Làm sạch HTML, nối mảng Tác giả | `cleaning.py` | `papers_clean.csv` | Mở csv kiểm tra |
| Đo lường Quality / Freshness | `quality.py` | `quality_check.json` | Đọc JSON report thấy "passed": true |

Nêu một output cụ thể mà phần việc của bạn tạo ra hoặc giúp xác minh:

Module đo lường `quality.py` do mình code đã tự động bắt quả tang chính xác bản ghi nào có ngày bị Stale (2000-01-01) do Đại tạo ra, và báo "passed": false.

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Dữ liệu thô từ Crossref lẫn HTML tags rác và các trường Array phức tạp. Ngoài ra, cần công cụ giám sát (observability) để cảnh báo tự động khi dữ liệu hỏng.

### Cách triển khai

Dùng Regex `<.*?>` loại HTML trong `cleaning.py`. Dùng Pandas `apply(join)` biến mảng tác giả thành chuỗi. Ở `quality.py`, mình viết hàm quét DataFrame, đếm missing ID, đếm length của summary và filter ngày xuất bản xem có lớn hơn 365 days_age không.

### Input, output và contract

| Thành phần                   | Mô tả                                     |
| ------------------------------ | ------------------------------------------- |
| Input                          | Raw dict records |
| Output                         | Cleaned DataFrame + JSON report |
| Module phụ thuộc             | `crossref.py` |
| Module sử dụng output        | `phase1.py` |
| Điều kiện lỗi cần xử lý | Xử lý an toàn khi parse chuỗi ngày không đúng chuẩn YYYY-MM-DD. |

### Cách xác minh

```bash
uv run python script/run_phase1.py
```

- **Kết quả mong đợi:** Tạo ra thư mục `data/quality` chứa 2 file JSON kết luận Data Fresh & Clean.
- **Kết quả thực tế:** Đúng như kỳ vọng.
- **Artifact/log:** `data/quality/baseline_quality_check.json`

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Nên dùng tool như Great Expectations hay tự viết code pandas cho lab này?
- **Các phương án đã cân nhắc:** Dùng Great Expectations vs Code tự custom Pandas.
- **Phương án đã chọn:** Tự custom Pandas logic check `quality.py`.
- **Lý do:** Giảm nhẹ dependency, dễ dàng kiểm soát luồng output json, đáp ứng đủ requirement về Uniqueness, Completeness và Freshness nhanh chóng cho tập dữ liệu nhỏ.
- **Bằng chứng quyết định phù hợp:** Chạy ổn định không vướng config cồng kềnh.

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:** KeyError `summary_chars` khi chạy Quality trên Corrupted Data.
- **Nguyên nhân gốc:** Hàm corruption trước đây xóa `summary` nhưng không set `summary_chars = 0`.
- **Cách xử lý:** Trao đổi với Đại sửa lại code update đồng bộ cả 2 cột.
- **Cách xác minh sau khi sửa:** Cảnh báo `summary_too_short: 1` hoạt động hoàn hảo.
- **Điều học được:** Data drift có thể xảy ra ở bất kỳ biến dẫn xuất nào.

## 7. Hiểu biết về luồng end-to-end

1. **Dữ liệu đi từ Crossref đến vector index như thế nào?** API -> Local JSON -> Pandas Df -> Langchain Documents -> ChromaDB.
2. **Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality ra sao?** So khớp ID.
3. **Quality checks khác freshness monitoring ở điểm nào trong bài lab?** Quality check coi tính hoàn thiện, không lỗi. Freshness đo thời điểm cập nhật.
4. **Vì sao phải dùng cùng test set cho baseline, corrupted và repaired?** Triệt tiêu sai số do câu hỏi.
5. **Repair được xem là thành công dựa trên artifact và metric nào?** Cả Data Quality Report và Metrics Score phải pass 100%.

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal          | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| ---------------------- | -------: | --------: | -------: | ------------------------- |
| `retrieval_hit_rate` |      1.0 |       0.833 |      1.0 | Observability hoàn thành nhiệm vụ cảnh báo |
| `mean_token_f1`      |      0.67 |       0.51 |      0.69 | F1 bị phá vỡ hoàn toàn |
| `judge_accuracy`     |      1.0 |     0.667 |      1.0 | Metrics rớt thê thảm |
| `mean_judge_score`   |      5.0 |       3.67 |      5.0 | Phục hồi hoàn toàn |
| Quality checks         |      Pass |       Fail |      Pass | Cảnh báo Data drift tốt |
| Freshness status       |      Fresh |       Stale |      Fresh | Tuổi thọ data được tracking chuẩn |

### Kết luận từ số liệu

1. **Data corruption** → **Signal Fail** → **Hit Rate Giảm**.
2. **Repair action** → **Signal Pass** → **Metrics về mức 5.0**.

Dữ liệu rác thực sự là thảm họa cho RAG. Chỉ 4 bản ghi bị lỗi trên 24 bản ghi đã kéo theo hệ thống mất phương hướng.

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất

1. Observability là must-have cho data pipeline.
2. Cleaning rules phải cover cả biến sinh ra thêm (`text_for_embedding`).
3. Luôn phải lường trước dữ liệu Missing Value.

### Nếu có thêm thời gian

Mình sẽ triển khai Great Expectations cho các bảng lớn thực sự thay vì hardcode bằng Pandas.

## 10. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Trần Hoàng Vũ
**Ngày xác nhận:** 2026-08-06
