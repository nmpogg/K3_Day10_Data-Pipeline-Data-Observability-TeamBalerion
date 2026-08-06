from __future__ import annotations

from typing import Any


def generate_phase1_report(
    report_path,
    source_summary: dict[str, Any],
    metrics: dict[str, Any],
    quality: dict[str, Any],
    freshness: dict[str, Any],
) -> None:
    """TODO(student): viet markdown report cho baseline phase."""
    import pathlib

    markdown = f"""# 📊 Báo cáo Baseline Phase 1

## 1. 📝 Source Summary
| Metric | Value |
| --- | --- |
| **Source API** | {source_summary.get('source', 'N/A')} |
| **Tổng số raw records** | {source_summary.get('total_raw', 0)} |
| **Tổng số cleaned records** | {source_summary.get('total_clean', 0)} |

## 2. 🎯 Metrics & Evaluation
| Metric | Score |
| --- | --- |
| **Số câu hỏi (Samples)** | {metrics.get('samples', 0)} |
| **Retrieval Hit Rate** | {metrics.get('retrieval_hit_rate', 0.0):.2%} |
| **Mean Token F1** | {metrics.get('mean_token_f1', 0.0):.4f} |
| **Judge Accuracy** | {metrics.get('judge_accuracy', 0.0):.2%} |
| **Mean Judge Score** | {metrics.get('mean_judge_score', 0.0):.2f}/5.0 |

## 3. 🛡️ Data Quality & Freshness

### Data Quality
**Status:** {'🟢 Passed' if quality.get('passed') else '🔴 Failed'}

| Issue Type | Count |
| --- | --- |
| **Lỗi thiếu ID** | {quality.get('paper_id_nulls', 0)} |
| **Lỗi trùng ID** | {quality.get('paper_id_duplicates', 0)} |
| **Lỗi thiếu Title** | {quality.get('title_nulls', 0)} |
| **Lỗi Summary quá ngắn** | {quality.get('summary_too_short', 0)} |

### Freshness
**Status:** {'🟢 Fresh' if freshness.get('is_fresh') else '🔴 Stale'}

| Metric | Detail |
| --- | --- |
| **Mới nhất** | {freshness.get('latest_published', 'N/A')} |
| **Cũ nhất** | {freshness.get('oldest_published', 'N/A')} |
| **Số dòng quá hạn (Stale)** | {freshness.get('stale_rows', 0)} |
"""

    out_path = pathlib.Path(report_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(markdown)


def generate_corruption_report(
    report_path,
    baseline_metrics: dict[str, Any],
    corrupted_metrics: dict[str, Any],
    repaired_metrics: dict[str, Any],
    corrupted_quality: dict[str, Any],
    repaired_quality: dict[str, Any],
    corrupted_freshness: dict[str, Any],
    repaired_freshness: dict[str, Any],
) -> None:
    """TODO(student): viet markdown report so sanh baseline/corrupted/repaired."""
    import pathlib

    markdown = f"""# 🚨 Báo cáo Corruption & Repair Phase 2

## 1. 🎯 So sánh Metrics & Evaluation

| Metric | Baseline | Corrupted | Repaired |
| --- | --- | --- | --- |
| **Retrieval Hit Rate** | {baseline_metrics.get('retrieval_hit_rate', 0.0):.2%} | {corrupted_metrics.get('retrieval_hit_rate', 0.0):.2%} | {repaired_metrics.get('retrieval_hit_rate', 0.0):.2%} |
| **Mean Token F1** | {baseline_metrics.get('mean_token_f1', 0.0):.4f} | {corrupted_metrics.get('mean_token_f1', 0.0):.4f} | {repaired_metrics.get('mean_token_f1', 0.0):.4f} |
| **Judge Accuracy** | {baseline_metrics.get('judge_accuracy', 0.0):.2%} | {corrupted_metrics.get('judge_accuracy', 0.0):.2%} | {repaired_metrics.get('judge_accuracy', 0.0):.2%} |
| **Mean Judge Score** | {baseline_metrics.get('mean_judge_score', 0.0):.2f}/5.0 | {corrupted_metrics.get('mean_judge_score', 0.0):.2f}/5.0 | {repaired_metrics.get('mean_judge_score', 0.0):.2f}/5.0 |

## 2. 🛡️ So sánh Data Quality

| Issue Type | Corrupted | Repaired |
| --- | --- | --- |
| **Passed Status** | {'🟢 Yes' if corrupted_quality.get('passed') else '🔴 No'} | {'🟢 Yes' if repaired_quality.get('passed') else '🔴 No'} |
| **Lỗi thiếu ID** | {corrupted_quality.get('paper_id_nulls', 0)} | {repaired_quality.get('paper_id_nulls', 0)} |
| **Lỗi trùng ID** | {corrupted_quality.get('paper_id_duplicates', 0)} | {repaired_quality.get('paper_id_duplicates', 0)} |
| **Lỗi thiếu Title** | {corrupted_quality.get('title_nulls', 0)} | {repaired_quality.get('title_nulls', 0)} |
| **Lỗi Summary quá ngắn** | {corrupted_quality.get('summary_too_short', 0)} | {repaired_quality.get('summary_too_short', 0)} |

## 3. ⏱️ So sánh Freshness

| Metric | Corrupted | Repaired |
| --- | --- | --- |
| **Fresh Status** | {'🟢 Yes' if corrupted_freshness.get('is_fresh') else '🔴 No'} | {'🟢 Yes' if repaired_freshness.get('is_fresh') else '🔴 No'} |
| **Số dòng quá hạn (Stale)** | {corrupted_freshness.get('stale_rows', 0)} | {repaired_freshness.get('stale_rows', 0)} |
| **Mới nhất** | {corrupted_freshness.get('latest_published', 'N/A')} | {repaired_freshness.get('latest_published', 'N/A')} |
| **Cũ nhất** | {corrupted_freshness.get('oldest_published', 'N/A')} | {repaired_freshness.get('oldest_published', 'N/A')} |
"""

    out_path = pathlib.Path(report_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(markdown)
