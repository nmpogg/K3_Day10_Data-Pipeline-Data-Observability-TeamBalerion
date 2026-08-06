# 🚨 Báo cáo Corruption & Repair Phase 2

## 1. 🎯 So sánh Metrics & Evaluation

| Metric | Baseline | Corrupted | Repaired |
| --- | --- | --- | --- |
| **Retrieval Hit Rate** | 100.00% | 100.00% | 100.00% |
| **Mean Token F1** | 0.6754 | 0.6400 | 0.6754 |
| **Judge Accuracy** | 100.00% | 91.67% | 100.00% |
| **Mean Judge Score** | 5.00/5.0 | 4.67/5.0 | 5.00/5.0 |

## 2. 🛡️ So sánh Data Quality

| Issue Type | Corrupted | Repaired |
| --- | --- | --- |
| **Passed Status** | 🔴 No | 🟢 Yes |
| **Lỗi thiếu ID** | 0 | 0 |
| **Lỗi trùng ID** | 1 | 0 |
| **Lỗi thiếu Title** | 0 | 0 |
| **Lỗi Summary quá ngắn** | 1 | 0 |

## 3. ⏱️ So sánh Freshness

| Metric | Corrupted | Repaired |
| --- | --- | --- |
| **Fresh Status** | 🔴 No | 🟢 Yes |
| **Số dòng quá hạn (Stale)** | 1 | 0 |
| **Mới nhất** | 2026-08-01 | 2026-08-01 |
| **Cũ nhất** | 2000-01-01 | 2026-02-13 |
