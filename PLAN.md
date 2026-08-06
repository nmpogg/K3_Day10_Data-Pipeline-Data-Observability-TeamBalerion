# Kế Hoạch Phân Công Công Việc Nhóm 

Dựa trên yêu cầu của project (Data Pipeline & Data Observability), công việc được chia cho 4 thành viên. Các thành phần quan trọng, cốt lõi sẽ do Ngô Minh Phong đảm nhận để đảm bảo chất lượng và tiến độ hệ thống, các công việc khác được chia đều cho các thành viên còn lại.

## 1. Ngô Minh Phong (2A202602025)
**Nhiệm vụ:**
- **Xây dựng Data Pipeline Baseline (Bước 9):** Viết `src/pipelines/phase1.py` để kết nối toàn bộ luồng từ lúc load data, cleaning, embedding, đến evaluation.
- **Xây dựng Data Quality & Reporting (Bước 11):** Viết `src/observability/quality.py` và `src/observability/reporting.py` để theo dõi, đánh giá chất lượng và độ tươi (freshness) của dữ liệu.
- **Data Corruption & Re-evaluation (Bước 12, 13, 14):** Viết `src/ingestion/corruption.py` và `src/pipelines/corruption_flow.py` để giả lập dữ liệu bẩn, chạy lại pipeline, và xuất report so sánh.
- **Review và Tích hợp:** Support các thành viên khác khi gặp lỗi, ráp nối toàn bộ code thành một hệ thống hoàn chỉnh.

**Gợi ý cách làm tốt nhất:**
- **Architecture & Logging:** Sử dụng logging chi tiết ở mỗi giai đoạn chuyển tiếp trong pipeline để dễ dàng debug data type mismatch.
- **Data Quality:** Thiết lập các rule kiểm tra thật chặt chẽ (vd: missing summary < 5%, freshness limit).
- **Corruption Flow:** Làm bẩn dữ liệu một cách tinh tế (như làm sai lệch một vài ngày xuất bản, truncate mất một nửa title, v.v) để thấy rõ sự sụt giảm ở các metrics (như Token F1, Hit Rate), từ đó đưa ra kết luận thuyết phục nhất trong file so sánh.

## 2. Nguyễn Văn Đại (2A202601245)
**Nhiệm vụ:** 
- **Load Raw Data từ API (Bước 3):** Hoàn thành module `src/ingestion/crossref.py`.

**Gợi ý cách làm tốt nhất:**
- **API Handling:** Tìm hiểu kỹ tài liệu của Crossref API. Bắt buộc phải có cơ chế `try-except` và `timeout` khi gọi request để pipeline không bị sập nếu API server down.
- **Data Parsing:** Bóc tách JSON trả về cẩn thận, chỉ giữ lại các fields thiết yếu (tiêu đề, tác giả, abstract, ngày xuất bản) và lưu ở định dạng chuẩn (JSON Lines hoặc một format dễ đọc) vào `data/raw/`.

## 3. Trần Hoàng Vũ (2A202602000)
**Nhiệm vụ:**
- **Làm Sạch Dữ Liệu - Cleaning Data (Bước 4):** Hoàn thành module `src/ingestion/cleaning.py`.

**Gợi ý cách làm tốt nhất:**
- **Xử lý Null/Missing:** Lọc bỏ các bài không có thông tin cần thiết. Với ngày xuất bản bị khuyết một phần, cần có chiến lược điền bù (imputation) hoặc loại bỏ hợp lý.
- **Chuẩn hóa văn bản:** Chuyển đổi định dạng ngày tháng về chuẩn chung để tính `age_days` tuyệt đối chính xác.
- **Text cho Vector Store:** Tạo trường `text_for_embedding` bằng cách ghép Title và Abstract (có thể thêm keyword) một cách mượt mà nhất để tăng khả năng search của mô hình.

## 4. Nguyễn Thùy Trang (2A202601559)
**Nhiệm vụ:**
- **Tạo Evaluation Set (Bước 5):** Hoàn thành module `src/evaluation/testset.py`.

**Gợi ý cách làm tốt nhất:**
- **Chất lượng bộ test:** Bộ câu hỏi không nên chỉ có các câu hỏi "có/không", hãy soạn thêm những câu hỏi yêu cầu mô hình phải lấy từ context ra (factual QA).
- **Tính chính xác:** Cực kỳ cẩn thận khi map `ground_truth_doc_ids` với câu hỏi. Nếu map sai, điểm Retrieval Hit Rate của cả pipeline sẽ bằng 0. Nên tự sinh một vài test case và rà soát thủ công để đảm bảo ground_truth thật sự đúng và rõ ràng.
