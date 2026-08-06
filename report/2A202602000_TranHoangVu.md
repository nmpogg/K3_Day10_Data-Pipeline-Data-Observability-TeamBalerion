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
| Data Cleaning | `src/ingestion/cleaning.py` | `data/raw/crossref_records.json` | `data/clean/papers_clean.csv` và `text_for_embedding` | Hoàn thành |
| Data Quality Check | `src/observability/quality.py` | `papers_clean.csv` | `baseline_quality_check.json`, `freshness_report.json` | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động                         | Thành viên/module được hỗ trợ | Kết quả                    |
| ------------------------------------ | ------------------------------------ | ---------------------------- |
| Thiết lập Data Model | Nguyễn Thùy Trang | Cung cấp cấu trúc `text_for_embedding` để Trang chạy test set chính xác. |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao       | Cách xác minh         |
| --------------------------- | ----------------------------- | ------------------------- | ----------------------- |
| Làm sạch HTML, nối mảng Tác giả | `cleaning.py` | `papers_clean.csv` | Mở CSV kiểm tra |
| Đo lường Quality / Freshness | `quality.py` | `baseline_quality_check.json`, `freshness_report.json` | Đọc JSON report thấy `"passed": true` |

Nêu một output cụ thể mà phần việc của bạn tạo ra hoặc giúp xác minh:

Module đo lường `quality.py` do mình lập trình đã tự động phát hiện chính xác bản ghi bị Stale (ngày 2000-01-01) và bản ghi bị trùng ID do kịch bản Corruption tạo ra, qua đó gắn flag `"passed": false` và báo động Data Quality failure.

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Dữ liệu thô từ Crossref chứa HTML tags rác và các trường Array phức tạp (`authors`, `categories`). Ngoài ra, cần hệ thống giám sát (Data Quality Observability) để tự động phát hiện và cảnh báo các sự cố rác dữ liệu (Data Drift, Missing Values, Stale Records, Duplicates).

### Cách triển khai

1. **Data Cleaning (`cleaning.py`)**:
   - Loại bỏ HTML tags bằng Regex `<.*?>` cho cả Title và Summary.
   - Gộp mảng `authors` thành chuỗi `authors_joined` và `categories` thành `categories_joined`.
   - Tạo trường thông tin tích hợp `text_for_embedding` phục vụ embedding.
   - Tính toán `summary_chars` và `age_days` (số ngày từ ngày xuất bản đến ngày chạy pipeline).

2. **Data Quality & Freshness (`quality.py`)**:
   - Xây dựng 5 quy tắc kiểm soát chất lượng dữ liệu:
     - **Completeness & Nulls**: Đếm số lượng rỗng ở `paper_id` và `title`.
     - **Uniqueness**: Kiểm tra trùng lặp `paper_id` (`paper_id_duplicates`).
     - **Validity**: Cảnh báo summary quá ngắn (`summary_chars < 10`).
     - **Freshness Threshold**: Đánh dấu các bản ghi quá hạn có `age_days > 180` ngày (`freshness_threshold_days = 180`).

### Input, output và contract

| Thành phần                   | Mô tả                                     |
| ------------------------------ | ------------------------------------------- |
| Input                          | `data/raw/crossref_records.json` (List `PaperRecord`) |
| Output                         | Cleaned DataFrame + JSON Quality Reports |
| Module phụ thuộc             | `crossref.py` |
| Module sử dụng output        | `phase1.py`, `corruption_flow.py` |
| Điều kiện lỗi cần xử lý | Parse an toàn chuỗi ngày tháng không chuẩn ISO/YYYY-MM-DD và xử lý trường hợp missing values. |

### Cách xác minh

```bash
python script/run_phase1.py
```

- **Kết quả mong đợi:** Tạo ra thư mục `data/quality` chứa `baseline_quality_check.json` và `freshness_report.json` với trạng thái `"passed": true` và `"is_fresh": true`.
- **Kết quả thực tế:** Đúng như kỳ vọng.
- **Artifact/log:** `data/quality/baseline_quality_check.json`, `data/quality/freshness_report.json`

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Nên dùng framework cồng kềnh như Great Expectations hay tự viết module kiểm tra với Pandas?
- **Các phương án đã cân nhắc:** Great Expectations suite vs Lightweight Pandas-based Quality Inspector.
- **Phương án đã chọn:** Tự phát triển module Pandas custom trong `quality.py`.
- **Lý do:** Giảm nhẹ dependency, dễ tích hợp trực tiếp vào pipeline `phase1.py` và `corruption_flow.py`, hoàn toàn chủ động điều chỉnh các ngưỡng Uniqueness, Completeness và Freshness.
- **Bằng chứng quyết định phù hợp:** Chạy siêu nhanh, ổn định, báo cáo xuất dạng JSON gọn nhẹ dễ tiêu thụ.

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:** KeyError `summary_chars` khi chạy Quality Checks trên Corrupted Data.
- **Nguyên nhân gốc:** Kịch bản corruption xóa tóm tắt (`summary = ""`) nhưng không đồng bộ lại cột phụ thuộc `summary_chars`.
- **Cách xử lý:** Cập nhật lại hàm `corrupt_clean_dataframe` để tính toán lại `summary_chars` và `text_for_embedding` sau khi làm hỏng dữ liệu.
- **Cách xác minh sau khi sửa:** Quality check phát hiện đúng `summary_too_short: 1` và `passed: false`.
- **Điều học được:** Data drift ở cột chính sẽ kéo theo sai lệch ở tất cả các cột dẫn xuất (derived columns).

## 7. Hiểu biết về luồng end-to-end

1. **Dữ liệu đi từ Crossref đến vector index như thế nào?** Crossref API -> `crossref_response.json` -> Parse thành `PaperRecord` -> Clean bằng Pandas -> Document Chunks -> ChromaDB Vector Store.
2. **Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality ra sao?** Evaluator lấy top-k `retrieved_doc_ids` từ Chroma index đối chiếu với `ground_truth_doc_ids` trong `test_set.json` để tính Hit Rate và Token F1.
3. **Quality checks khác freshness monitoring ở điểm nào trong bài lab?** Quality checks đo đạc tính toàn vẹn (Completeness, Uniqueness, Length), còn Freshness monitoring đo tuổi thọ dữ liệu (`age_days`) so với mốc thời gian thực.
4. **Vì sao phải dùng cùng test set cho baseline, corrupted và repaired?** Để cố định biến số đánh giá (Frozen C2 Testset), đảm bảo mọi sự sụt giảm hay phục hồi của metrics đều do chất lượng dữ liệu thay đổi.
5. **Repair được xem là thành công dựa trên artifact và metric nào?** Cả Data Quality Report khôi phục status `"passed": true`, Freshness báo `"is_fresh": true` và Metrics (`retrieval_hit_rate` = 1.0) trở lại mức Baseline.

## 8. Phân tích kết quả

### Metrics & Data Quality 3 Trạng thái

| Metric/Signal | Baseline | Corrupted | Repaired | Nhận xét cá nhân |
| :--- | :---: | :---: | :---: | :--- |
| **Retrieval Hit Rate** | **1.0 (100%)** | **0.833 (83.3%)** | **1.0 (100%)** | Dữ liệu lỗi khiến RAG bỏ sót tài liệu quan trọng |
| **Mean Token F1** | **0.675** | **0.511** | **0.691** | Độ chính xác câu trả lời giảm đáng kể khi rác dữ liệu |
| **Judge Accuracy** | **1.0 (100%)** | **0.667 (66.7%)** | **1.0 (100%)** | LLM Judge đánh giá chất lượng phản hồi sụt giảm |
| **Mean Judge Score** | **5.0 / 5.0** | **3.67 / 5.0** | **5.0 / 5.0** | Điểm số phục hồi hoàn toàn sau bước Repair |
| **Quality Passed** | **✅ Pass** | **❌ Fail** | **✅ Pass** | Observability bắt đúng lỗi trùng lặp & thiếu dữ liệu |
| **Freshness Status** | **✅ Fresh** | **❌ Stale** | **✅ Fresh** | Phát hiện chính xác tài liệu bị đổi ngày về năm 2000 |

### Kết luận từ số liệu

1. **Tác hại của dữ liệu rác**: Chỉ cần 4/24 bản ghi bị làm hỏng (Xóa summary, đổi ngày về năm 2000, nhân đôi ID, chèn nhiễu) đã làm Hit Rate giảm 16.7% và Token F1 giảm từ 0.675 xuống 0.511.
2. **Khả năng quan sát (Observability)**: Module `quality.py` đã hoàn thành xuất sắc nhiệm vụ khi lập tức gắn cờ **Fail** ở bước Corrupted và trả về **Pass** khi dữ liệu được Repair từ nguồn thô chuẩn.

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
