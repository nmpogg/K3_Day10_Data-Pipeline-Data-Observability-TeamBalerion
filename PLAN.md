# Kế Hoạch Phân Công Công Việc Nhóm 

Dựa trên yêu cầu của project (Data Pipeline & Data Observability), khối lượng công việc được chia đều cho 4 thành viên. Mỗi người sẽ đảm nhận 2 module chính, chia theo từng mảng chuyên môn cụ thể. Các luồng (flow) tích hợp quan trọng nhất đòi hỏi sự tỉ mỉ để hệ thống chạy mượt mà từ đầu đến cuối sẽ do Ngô Minh Phong đảm nhận.

## 1. Ngô Minh Phong (2A202602025)
**Mảng phụ trách:** Xây dựng Pipeline & Tích hợp hệ thống
**Nhiệm vụ cụ thể:**
- **Pipeline Baseline (Bước 9):** Viết `src/pipelines/phase1.py` để kết nối toàn bộ module (load data -> cleaning -> embedding -> evaluation).
- **Pipeline Corruption & Re-evaluation (Bước 13, 14):** Viết `src/pipelines/corruption_flow.py` để chạy lại luồng khi dữ liệu bẩn và so sánh kết quả.

**Gợi ý cách làm tốt nhất:**
- Sử dụng logging chi tiết ở mỗi bước chuyển tiếp trong pipeline để theo dõi luồng dữ liệu.
- Trong file so sánh, cần thiết kế cấu trúc rõ ràng để nêu bật được sự khác biệt (sụt giảm) về metrics (Hit Rate, Token F1) khi dữ liệu bị lỗi và sự phục hồi khi dữ liệu được sửa.

## 2. Nguyễn Văn Đại (2A202601245)
**Mảng phụ trách:** Data Ingestion & Manipulation
**Nhiệm vụ cụ thể:** 
- **Load Raw Data từ API (Bước 3):** Hoàn thành module `src/ingestion/crossref.py`.
- **Data Corruption (Bước 12):** Hoàn thành module `src/ingestion/corruption.py` để tạo các kịch bản làm bẩn dữ liệu.

**Gợi ý cách làm tốt nhất:**
- Phần gọi API cần bắt buộc có `try-except` và `timeout` để tránh treo hệ thống.
- Phần làm bẩn dữ liệu (Corruption) cần đa dạng hóa các kịch bản (ví dụ: làm null một vài summary, truncate title, thay đổi publish_date thành tương lai/quá khứ xa) để test tính chịu đựng của hệ thống.

## 3. Trần Hoàng Vũ (2A202602000)
**Mảng phụ trách:** Data Quality & Processing
**Nhiệm vụ cụ thể:**
- **Làm Sạch Dữ Liệu (Bước 4):** Hoàn thành module `src/ingestion/cleaning.py`.
- **Data Quality Checks (Bước 11):** Hoàn thành module `src/observability/quality.py` để xây dựng các rules kiểm tra độ tươi và chất lượng dữ liệu.

**Gợi ý cách làm tốt nhất:**
- Khi làm sạch dữ liệu, cần xử lý triệt để các trường hợp missing values (VD: bỏ qua hoặc điền giá trị mặc định). Ghép Title và Abstract để tạo text chuẩn cho việc embedding.
- Các rules trong Data Quality cần chặt chẽ (VD: không được phép có null ở các cột quan trọng, cảnh báo nếu dữ liệu quá cũ dựa trên `age_days`). Việc này cần phối hợp chặt với dữ liệu đầu ra của phần làm sạch.

## 4. Nguyễn Thùy Trang (2A202601559)
**Mảng phụ trách:** Evaluation & Reporting
**Nhiệm vụ cụ thể:**
- **Tạo Evaluation Set (Bước 5):** Hoàn thành module `src/evaluation/testset.py`.
- **Sinh Data Quality Report (Bước 11):** Hoàn thành module `src/observability/reporting.py`.

**Gợi ý cách làm tốt nhất:**
- Bộ test set cần có đa dạng các loại câu hỏi (đặc biệt là factual QA). Cực kỳ cẩn thận khi đối chiếu `ground_truth_doc_ids` với nội dung để đảm bảo đánh giá Retrieval chính xác.
- Ở module reporting, đảm bảo file Markdown xuất ra trình bày dưới dạng bảng hoặc biểu đồ dễ nhìn, thể hiện rõ ràng các metrics Pass/Fail của Data Quality.
