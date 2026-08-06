# Group Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin bài nộp

| Thông tin         | Nội dung                  |
| ------------------ | -------------------------- |
| Khóa/Lớp         | K3              |
| Tên nhóm         | Balerion     |
| Repository         | https://github.com/nmpogg/K3_Day10_Data-Pipeline-Data-Observability-TeamBalerion |
| Ngày hoàn thành | 2026-08-06               |

### Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò chính | Module/deliverable sở hữu |
| --: | --- | --- | --- | --- |
| 1 | Ngô Minh Phong | 2A202602025 | Tích hợp hệ thống, Pipeline Orchestration | `src/pipelines/phase1.py`, `src/pipelines/corruption_flow.py` |
| 2 | Nguyễn Văn Đại | 2A202601245 | Data Ingestion, Corruption Logic | `src/ingestion/crossref.py`, `src/ingestion/corruption.py` |
| 3 | Trần Hoàng Vũ | 2A202602000 | Data Cleaning, Data Quality Observability | `src/ingestion/cleaning.py`, `src/observability/quality.py` |
| 4 | Nguyễn Thùy Trang | 2A202601559 | Evaluation, Metrics & Reporting | `src/evaluation/testset.py`, `src/observability/reporting.py`, `metrics.py` |

## 2. Tóm tắt kết quả

**Tóm tắt của nhóm:**

Nhóm đã triển khai thành công toàn bộ vòng đời của dữ liệu từ việc fetch qua Crossref API, làm sạch (cleaning), đánh giá hiệu suất của mô hình LLM (baseline metrics), cho tới việc tạo ra kịch bản làm bẩn dữ liệu (corruption flow) và phục hồi hoàn toàn (repaired flow). Hệ thống baseline đã tạo ra đầy đủ các artifact như `papers_clean.csv`, file đánh giá chất lượng và JSON báo cáo.

Khi áp dụng kịch bản corruption khắc nghiệt (xóa trắng tiêu đề và tác giả, làm cũ ngày xuất bản, tiêm nhiễu độc hại `[SPAM]`), chất lượng dữ liệu tụt giảm thê thảm kéo theo độ chính xác của LLM Judge giảm mạnh từ 100% xuống còn 66.67%. 

Tuy nhiên, với cơ chế repair bằng cách tái tạo lại từ raw records, toàn bộ chỉ số đã phục hồi 100%, xóa sổ hoàn toàn rác nhiễu và lấp đầy các trường bị mất. Blocker còn lại lớn nhất là Ragas chưa được kích hoạt do cấu hình mô hình LLM chuyên sâu cần token HF Hub. Nhóm hiện đang sử dụng LLM Judge đánh giá trên Token F1 kết hợp với parsing JSON thủ công làm phương pháp đánh giá thay thế rất ổn định.

## 3. Kiến trúc và luồng dữ liệu

### Luồng end-to-end

```text
Crossref API
    -> raw response/raw records
    -> cleaning và data modeling
    -> embedding + ChromaDB index
    -> evaluation baseline
    -> quality/freshness reports
    -> corruption
    -> re-index và re-evaluate
    -> repair từ dữ liệu nguồn
    -> comparison report
```

### Trách nhiệm của từng khối

| Khối             | Input          | Xử lý chính             | Output/artifact          | Owner          |
| ----------------- | -------------- | -------------------------- | ------------------------ | -------------- |
| Ingestion         | Crossref API   | Fetch, retry, parse API response thành raw records | `data/raw/papers.json` | Nguyễn Văn Đại |
| Cleaning          | `data/raw/papers.json` | Chuẩn hóa ngày, xóa thẻ HTML, nối chuỗi tác giả | `data/clean/papers_clean.csv` | Trần Hoàng Vũ |
| Embedding/index   | `data/clean/papers_clean.csv` | Embed `text_for_embedding` vào index | `data/embeddings/` | Ngô Minh Phong |
| Evaluation        | Test set JSON  | Run QA Retrieval, tính token_f1, dùng LLM chấm điểm | `data/results/baseline_metrics.json` | Nguyễn Thùy Trang |
| Observability     | Cleaned records | Kiểm tra missing value, stale rows, duplicate IDs | `data/quality/baseline_quality_check.json` | Trần Hoàng Vũ |
| Corruption/repair | Cleaned DF | Phá hỏng dữ liệu, rebuild lại sạch từ raw | `data/results/corruption_log.json` | Nguyễn Văn Đại |
| Orchestration     | Toàn bộ config | Tự động hóa Pipeline từ Phase 1 tới Phase 2 | `data/reports/corruption_report.md` | Ngô Minh Phong |

## 4. Cách tái hiện kết quả

### Cấu hình không chứa secret

| Biến/cấu hình             | Giá trị sử dụng |
| ---------------------------- | ------------------- |
| `LLM_PROVIDER`             | OPENROUTER |
| `LLM_MODEL`                | inclusionai/ling-3.0-flash:free |
| Embedding model              | sentence-transformers/all-MiniLM-L6-v2 |
| Số lượng Crossref records    | 24 records        |
| Retrieval `top_k`            | 3                 |
| Freshness threshold          | 365 days          |
| Random seed, nếu có        | Không áp dụng |

### Lệnh cài đặt

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .
```

### Lệnh chạy

Baseline:

```bash
python script/run_phase1.py
```

Corruption flow:

```bash
python script/run_corruption_flow.py
```

### Kết quả tái hiện

| Lệnh             | Trạng thái                                    | Thời điểm chạy gần nhất | Bằng chứng                         |
| ----------------- | ----------------------------------------------- | ----------------------------- | ------------------------------------ |
| Baseline pipeline | Thành công | 2026-08-06 11:30 | `data/results/baseline_metrics.json` |
| Corruption flow   | Thành công | 2026-08-06 11:30 | `data/results/corruption_log.json` |

## 5. Ingestion, cleaning và data contract

### Nguồn dữ liệu

| Thuộc tính                | Giá trị                             |
| --------------------------- | ------------------------------------- |
| Source                      | Crossref REST API |
| Query/filter                | query="large language models", filter="has-abstract:true" |
| Thời điểm lấy dữ liệu | 2026-08-06 |
| Số record nhận được    | 24 |
| Cơ chế retry/backoff      | tenacity retry 3 lần, backoff cấp số nhân |

### Raw và clean schema

| Trường        | Kiểu dữ liệu | Bắt buộc?  | Ý nghĩa   | Xử lý khi thiếu/sai |
| --------------- | --------------- | ------------ | ----------- | ---------------------- |
| `paper_id` | Chuỗi (str) | Có | Định danh DOI của bài báo | Báo lỗi hoặc drop |
| `title` | Chuỗi | Có | Tên bài báo | Drop record |
| `summary` | Chuỗi | Có | Tóm tắt (Abstract) nội dung | Drop record nếu rỗng hoặc độ dài < 100 kí tự |
| `published` | Ngày (str) | Có | Ngày phát hành chuẩn ISO | Default "Unknown" hoặc drop |

### Quy tắc cleaning

| Quy tắc                                 | Quality dimension liên quan | Số record bị tác động | Cách xác minh      |
| ---------------------------------------- | ---------------------------- | -------------------------: | -------------------- |
| Loại record có `title` rỗng | Completeness | 0 | `df[df['title'] == ""]` |
| Bỏ HTML tag khỏi abstract, title | Conformity/Format | 24 | Kiểm tra regex sau parse |
| Loại bỏ summary ngắn hơn 100 ký tự | Completeness | 0 | `df[df['summary_chars'] < 100]` |
| Gộp danh sách tác giả thành 1 chuỗi | Data Structure | 24 | Schema validation |

Giải thích cách nhóm tạo `text_for_embedding`, document ID và `age_days`:

- `text_for_embedding`: Nối chuỗi bằng cách thêm nhãn "Title: [title] | Authors: [authors] | Summary: [summary]". Việc này giúp embedding model (bge) nắm bắt ngữ nghĩa tốt hơn cho từng trường.
- `document ID`: Lấy trực tiếp DOI từ Crossref làm `paper_id` duy nhất.
- `age_days`: Tính sự chênh lệch (đơn vị ngày) giữa `published date` và ngày chạy pipeline (`run_date`) bằng `datetime.timedelta`.

## 6. Evaluation setup

| Thành phần                             | Cấu hình thực tế          |
| ---------------------------------------- | ----------------------------- |
| Số câu hỏi                            | 12                 |
| Các `question_type`                    | factual, summary, date, author, category |
| Ground-truth document ID                 | Gắn cứng ID chính xác trong `test_set.json` |
| Embedding model                          | sentence-transformers/all-MiniLM-L6-v2 |
| Vector store/collection                  | LocalEmbeddingIndex |
| Retrieval `top_k`                       | 3 |
| LLM provider/model                       | OPENROUTER |
| Test set dùng chung cho ba trạng thái | `data/eval/test_set.json` |

Giải thích vì sao test set được giữ nguyên khi đánh giá baseline, corrupted và repaired:

Việc đóng băng (freeze) bộ Test Set với các ground-truth tĩnh là để đảm bảo tính công bằng (fair comparison) khi so sánh hiệu suất giữa 3 trạng thái. Nếu dữ liệu thay đổi và bộ câu hỏi cũng thay đổi theo, chúng ta không thể biết được sự thay đổi của score là do mô hình/hệ thống dở tệ đi hay là do bộ câu hỏi trở nên khó hơn.

## 7. Kết quả baseline

### Artifact checklist

| Artifact                 | Đường dẫn thực tế                | Trạng thái | Ghi chú   |
| ------------------------ | -------------------------------------- | ------------ | ---------- |
| Raw response/records     | `data/raw/`                          | Có | Đầy đủ 24 files |
| Cleaned dataset          | `data/clean/`                        | Có | `papers_clean.csv/json` |
| Embedding manifest/index | `data/embeddings/`                   | Có | Index vector của baseline |
| Evaluation set           | `data/eval/`                         | Có | 14 câu hỏi đóng băng |
| Baseline metrics         | `data/results/baseline_metrics.json` | Có | Accuracy 100% |
| Quality/freshness        | `data/quality/`                      | Có | Passed hoàn toàn |
| Baseline report          | `data/reports/phase1_report.md`      | Có | Render Markdown |

### Baseline metrics

| Metric                 |       Giá trị | Diễn giải                             |
| ---------------------- | --------------: | --------------------------------------- |
| `retrieval_hit_rate` |     1.00 (100%) | Đạt tối đa vì mô hình embedding hoạt động tốt trên `text_for_embedding` chứa toàn bộ title/authors. |
| `mean_token_f1`      |     0.6754 | Mức độ trùng lặp từ vựng tốt giữa câu trả lời sinh ra và Ground-Truth. |
| `judge_accuracy`     |     1.00 (100%) | LLM đánh giá mọi câu trả lời của mô hình đều chính xác so với ground-truth. |
| `mean_judge_score`   |     5.0/5.0 | Điểm độ hoàn thiện của câu trả lời đạt mức tối đa tuyệt đối. |
| Ragas, nếu có        | N/A | Bị vô hiệu hóa (`RUN_RAGAS` không bật) để tránh limit rate HF. |

## 8. Data quality và freshness

### Quality checks

| Check        | Quality dimension | Ngưỡng/kỳ vọng | Kết quả baseline      | Bằng chứng |
| ------------ | ----------------- | ------------------ | ----------------------- | ------------ |
| `paper_id_duplicates` | Uniqueness | 0 | Pass (0) | `baseline_quality_check.json` |
| `summary_too_short` | Completeness | 0 | Pass (0) | `baseline_quality_check.json` |

### Freshness

| Thuộc tính               | Giá trị                           |
| -------------------------- | ----------------------------------- |
| Freshness được đo tại | Cleaned Dataset `age_days` |
| Timestamp mới nhất       | 2026-08-01 |
| Ngưỡng freshness         | Tối đa 365 ngày (1 năm) |
| Trạng thái baseline      | Fresh |
| Lý do                     | Bản ghi cũ nhất được ghi nhận là 2026-02-13, hoàn toàn thỏa mãn nhỏ hơn ngưỡng 1 năm. |

## 9. Corruption scenarios và repair

| Corruption         | Cách tạo | Record bị tác động | Quality signal kỳ vọng | Tác động thực tế | Cách repair   |
| ------------------ | ---------- | ---------------------: | ------------------------ | --------------------- | -------------- |
| Blank Summary & Title | Gán "" vào Summary, "MISSING_TITLE" vào title | 1 | Failed Completeness | Bị trừ điểm do mất context | Rebuild lại từ raw |
| Stale Date & Blank Authors | Đổi publish = 2000-01-01, đổi tác giả | 1 | Failed Freshness | Bị trừ điểm do AI trả lời "Unknown Author" | Rebuild lại từ raw |
| Extreme Noise | Chèn chuỗi spam dài | 1 | Failed Data Validity | Bị trừ điểm trầm trọng | Rebuild lại từ raw |
| Duplicates | Copy paste bản ghi bằng `pd.concat` | 1 | Failed Uniqueness | Log ghi nhận Duplicate | Rebuild lại từ raw `drop_duplicates` |

Corruption log:

- Đường dẫn: `data/results/corruption_log.json`
- Trạng thái: Có
- Nhận xét: Log ghi nhận rất tốt đầy đủ ID bị tác động, cũng như tham số của hành động làm bẩn.

Giải thích cách repair đảm bảo dữ liệu được phục hồi từ nguồn đáng tin cậy thay vì chỉ che kết quả lỗi:

Repair flow trong `src/pipelines/corruption_flow.py` (bước 6) không cố gắng "sửa" cái sai trên file `corrupted_clean.csv`. Thay vào đó, nó fetch trực tiếp lại **Raw Records** (`data/raw/papers.json`) - đây là Source of Truth. Tiếp đến, nó đẩy lại đống Raw Data này qua hàm `build_clean_dataframe()`. Nhờ đó mọi rác, mọi missing data đều được lấp đầy nguyên gốc!

## 10. So sánh baseline, corrupted và repaired

| Metric/signal            | Baseline | Corrupted | Repaired | Thay đổi do corruption | Mức phục hồi | Nhận xét   |
| ------------------------ | -------: | --------: | -------: | -----------------------: | --------------: | ------------ |
| `retrieval_hit_rate`   |      100% |     83.33% |      100% |  Giảm mạnh |  100% | Mất Title làm retriever mù |
| `mean_token_f1`        |   0.6754 |    0.5111 |    0.6913 |  Giảm nghiêm trọng | Hồi phục (sai số từ) | Noise làm hỏng F1 |
| `judge_accuracy`       |      100% |    66.67% |      100% |  Sụp đổ |  100% | LLM không thể trả lời đúng |
| `mean_judge_score`     |      5.0 |       3.67 |       5.0 |  Giảm đáng kể |  100% | Phục hồi hoàn hảo |
| Quality checks pass/fail |     Pass |     Fail |     Pass |  Phát hiện ra lỗi |  Pass | Great Observability |
| Freshness status         |    Fresh |    Stale |    Fresh | Phát hiện data cũ | Fresh | Dữ liệu cũ bị bắt bài |

Nêu ít nhất hai kết luận có quan hệ nhân quả được hỗ trợ bởi artifacts:

1. [Blank Summary & Blank Title] → [Failed Data Completeness / Mất Semantics] → [Retrieval Hit Rate sụt giảm + LLM Judge mất phương hướng dẫn đến rớt Accuracy thê thảm].
2. [Rebuild DataFrame directly from Raw Records] → [Data Freshness & Completeness được khôi phục 100%] → [Agent metric recovery 100% do context nhúng trở nên chính xác tuyệt đối như Baseline].

## 11. Vấn đề tích hợp quan trọng

- **Triệu chứng:** Pipeline bị lỗi khi thực thi hàm LLM đánh giá (Judge), khiến nó luôn rơi vào cơ chế Fallback Heuristic đếm Token F1 ngớ ngẩn. Việc này khiến dữ liệu Repaired bị đánh rớt điểm so với Baseline dù giống nhau hoàn toàn về nghĩa (chỉ khác một chút xíu về dùng từ/format).
- **Nguyên nhân:** Hàm `with_structured_output()` trong LangChain không hỗ trợ cho Local HuggingFace Models.
- **Cách xử lý:** Thay đổi hàm `_judge_answer` trong `src/evaluation/metrics.py`. Viết lại System Prompt bắt LLM phải trả về raw JSON Object, sau đó chạy `json.loads` thủ công từ chuỗi sinh ra.
- **Cách xác minh:** `python script/run_corruption_flow.py` đã chạy thành công, điểm số Repaired và Baseline khớp hoàn hảo ở mức Judge Score = 5.0/5.0.

## 12. Giới hạn và hướng cải thiện

| Giới hạn hiện tại | Ảnh hưởng   | Hướng cải thiện có thể kiểm chứng |
| --------------------- | -------------- | ----------------------------------------- |
| Fallback metric còn quá đơn giản (đếm Token F1) | Khiến cho hệ thống không linh hoạt chấm điểm đồng nghĩa | Dùng BLEU/ROUGE Score thay thế cho Token F1 trong fallback. |
| Test set tạo bằng tay có nguy cơ bias | Không phản ánh hết độ bao phủ của data. | Dùng LLM (Qwen/Llama) để tự sinh test_set từ nguồn Data Cleaned thông qua prompt Generator. |

## 13. Checklist trước khi nộp

- [x] Thông tin nhóm và repository chính xác.
- [x] Phân công khớp với module, artifact và kết quả thực tế.
- [x] Lệnh tái hiện đã được chạy lại trên phiên bản dùng để nộp.
- [x] Baseline, corrupted và repaired dùng cùng evaluation set.
- [x] Bảng metrics khớp với các file trong `data/results/`.
- [x] Quality/freshness conclusions khớp với `data/quality/`.
- [x] Các đường dẫn báo cáo và artifact truy cập được.
- [x] Mỗi thành viên đã hoàn thành báo cáo vai trò riêng.
- [x] Không có `.env`, API key, token hoặc secret trong source, report, log hay ảnh.
