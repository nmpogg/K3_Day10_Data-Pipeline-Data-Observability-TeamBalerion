# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin         | Nội dung                  |
| ------------------ | -------------------------- |
| Họ và tên       | Nguyễn Văn Đại             |
| MSSV               | 2A202601245                     |
| Khóa/Lớp         | K3              |
| Tên nhóm         | Balerion     |
| Vai trò chính    | Data Ingestion & Corruption Logic                 |
| Repository         | https://github.com/nmpogg/K3_Day10_Data-Pipeline-Data-Observability-TeamBalerion |
| Ngày hoàn thành | 2026-08-06               |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao  | Trạng thái                                 |
| ------------------ | --------------------- | ---------------- | ----------------- | -------------------------------------------- |
| Data Ingestion | `src/ingestion/crossref.py` | API Query | Thư mục `data/raw/` chứa JSON papers | Hoàn thành |
| Data Corruption | `src/ingestion/corruption.py` | `corrupted_clean_csv` | `corrupted_clean.csv` với rác | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động                         | Thành viên/module được hỗ trợ | Kết quả                    |
| ------------------------------------ | ------------------------------------ | ---------------------------- |
| Đánh giá schema raw data | Trần Hoàng Vũ | Giúp Vũ định nghĩa schema cho bước cleaning. |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao       | Cách xác minh         |
| --------------------------- | ----------------------------- | ------------------------- | ----------------------- |
| Lấy dữ liệu Crossref | `crossref.py` | 24 file json raw | Kiểm tra thư mục `data/raw/` |
| Phá hủy dữ liệu mạnh tay | `corruption.py` | Corruption Logs | Mở `data/results/corruption_log.json` |

Nêu một output cụ thể mà phần việc của bạn tạo ra hoặc giúp xác minh:

File `data/results/corruption_log.json` và bộ kịch bản lỗi cực mạnh như "Extreme Noise" hay "Blank Title & Author" giúp kiểm chứng được ranh giới chịu đựng của RAG.

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Làm thế nào để fetch dữ liệu từ REST API ổn định và tránh bị chặn? Làm thế nào để tạo ra các loại lỗi dữ liệu phổ biến trong thực tế (data drift, null values, noise, stale data)?

### Cách triển khai

Sử dụng thư viện `requests` kết hợp `tenacity` để gọi API Crossref với cơ chế backoff mũ.
Ở luồng corruption, sử dụng Pandas DataFrame để can thiệp trực tiếp vào index, ghi đè Title/Author thành rỗng, đổi ngày thành 2000-01-01 và tiêm chuỗi SPAM 10 lần vào `text_for_embedding`.

### Input, output và contract

| Thành phần                   | Mô tả                                     |
| ------------------------------ | ------------------------------------------- |
| Input                          | Cleaned DataFrame |
| Output                         | Corrupted DataFrame |
| Module phụ thuộc             | `cleaning.py` |
| Module sử dụng output        | `phase1.py` / `corruption_flow.py` |
| Điều kiện lỗi cần xử lý | ID không tồn tại khi apply corruption |

### Cách xác minh

```bash
python script/run_corruption_flow.py
```

- **Kết quả mong đợi:** Logs sinh ra đúng ID và hành động, hệ thống RAG không thể trả lời các câu hỏi bị nhiễu.
- **Kết quả thực tế:** RAG sập accuracy từ 100% -> 66.67%.
- **Artifact/log:** `data/results/corruption_log.json`

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Lúc đầu việc xóa summary không làm điểm hệ thống giảm đi.
- **Các phương án đã cân nhắc:** Đổi seed / Thay câu hỏi khó / Đập nát title và authors.
- **Phương án đã chọn:** Đập nát luôn title và authors của bài báo bị lỗi.
- **Lý do:** Retriever Dense Index phụ thuộc cực mạnh vào text context. Title là semantic anchor. Việc xóa Title phản ánh đúng Data Missing Values trong đời thực.
- **Bằng chứng quyết định phù hợp:** Hit rate giảm còn 83%.

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:** Bị rate limit Crossref.
- **Nguyên nhân gốc:** Gửi nhiều request liên tục không có email headers.
- **Cách xử lý:** Bổ sung `mailto` header.
- **Cách xác minh sau khi sửa:** Chạy lại `crossref.py` 100% thành công.
- **Điều học được:** Gọi API luôn phải tuân thủ chính sách "Polite Pool".

## 7. Hiểu biết về luồng end-to-end

1. **Dữ liệu đi từ Crossref đến vector index như thế nào?** Fetch -> JSON -> Filter HTML -> Df -> Txt -> Chromadb.
2. **Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality ra sao?** Giữ làm tham chiếu chéo để đánh giá model sinh.
3. **Quality checks khác freshness monitoring ở điểm nào trong bài lab?** Quality check coi format, rỗng. Freshness đo tuổi thọ (Age).
4. **Vì sao phải dùng cùng test set cho baseline, corrupted và repaired?** Để so sánh A/B test chuẩn xác.
5. **Repair được xem là thành công dựa trên artifact và metric nào?** Dựa trên `repaired_metrics.json` có điểm tiệm cận 1.0.

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal          | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| ---------------------- | -------: | --------: | -------: | ------------------------- |
| `retrieval_hit_rate` |      1.0 |       0.833 |      1.0 | Dữ liệu Corrupt thực sự đã phá được Index |
| `mean_token_f1`      |      0.67 |       0.51 |      0.69 | Text spam phá vỡ hoàn toàn context |
| `judge_accuracy`     |      1.0 |     0.667 |      1.0 | Thành công mĩ mãn |
| `mean_judge_score`   |      5.0 |       3.67 |      5.0 | Ổn định |
| Quality checks         |      Pass |       Fail |      Pass | Cảnh báo Data drift tốt |
| Freshness status       |      Fresh |       Stale |      Fresh | Quá hạn 2000-01-01 bị bắt trúng |

### Kết luận từ số liệu

1. **Data corruption** → **Signal Fail** → **Hit Rate Giảm**.
2. **Repair action** → **Signal Pass** → **Metrics về mức 5.0**.

Corruption gây nhiễu văn bản (SPAM) là thứ ảnh hưởng ghê gớm nhất vì RAG LLM dễ bị Jailbreak bởi nội dung rác.

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất

1. Tầm quan trọng của data validation trước khi đưa cho AI.
2. Cơ chế backoff của API calls.
3. Data observability giúp biết data hỏng *khi nào*, thay vì đợi user report.

### Nếu có thêm thời gian

Mình sẽ viết rule corruption động dựa trên schema validator của Pandera.

## 10. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Nguyễn Văn Đại
**Ngày xác nhận:** 2026-08-06
