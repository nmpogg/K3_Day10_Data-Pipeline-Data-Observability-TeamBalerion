from __future__ import annotations

from typing import Any

import pandas as pd

from core.config import Settings


def run_data_quality_checks(df: pd.DataFrame, settings: Settings, report_name: str) -> dict[str, Any]:
    """TODO(student): tao bo data quality checks.

    Pseudo-code:
    1. Check row count.
    2. Check `paper_id` not null va unique.
    3. Check `title` not null.
    4. Check do dai `summary`.
    5. Check freshness bang `age_days`.
    6. Ghi ket qua vao `data/quality/`.
    """
    from core.utils import write_json

    total_rows = len(df)
    
    # 2. Check `paper_id` not null va unique
    paper_id_nulls = int(df['paper_id'].isnull().sum()) if 'paper_id' in df else total_rows
    paper_id_duplicates = int(df['paper_id'].duplicated().sum()) if 'paper_id' in df else total_rows

    # 3. Check `title` not null
    title_nulls = int(df['title'].isnull().sum()) if 'title' in df else total_rows

    # 4. Check do dai `summary`
    if 'summary_chars' in df:
        summary_too_short = int((df['summary_chars'] < 10).sum())
    elif 'summary' in df:
        summary_too_short = int((df['summary'].str.len() < 10).sum())
    else:
        summary_too_short = total_rows

    # 5. Check freshness bang `age_days`
    stale_rows = int((df['age_days'] > settings.freshness_threshold_days).sum()) if 'age_days' in df else 0

    results = {
        "report_name": report_name,
        "row_count": total_rows,
        "paper_id_nulls": paper_id_nulls,
        "paper_id_duplicates": paper_id_duplicates,
        "title_nulls": title_nulls,
        "summary_too_short": summary_too_short,
        "stale_rows": stale_rows,
        "passed": bool(paper_id_nulls == 0 and paper_id_duplicates == 0 and title_nulls == 0 and summary_too_short == 0)
    }

    # 6. Ghi ket qua vao `data/quality/`
    settings.paths.quality_dir.mkdir(parents=True, exist_ok=True)
    safe_name = report_name.lower().replace(' ', '_')
    out_path = settings.paths.quality_dir / f"{safe_name}.json"
    write_json(out_path, results)
    
    return results


def build_freshness_report(df: pd.DataFrame, settings: Settings, report_path) -> dict[str, Any]:
    """TODO(student): tong hop freshness report.

    Pseudo-code:
    1. Tim latest va oldest published date.
    2. Dem so dong stale.
    3. Tao payload:
       - latest_published
       - oldest_published
       - stale_rows
       - total_rows
       - is_fresh
    4. Ghi JSON report.
    """
    from core.utils import write_json
    import pathlib
    
    total_rows = len(df)
    latest_published = str(df['published'].max()) if 'published' in df and not df.empty else "N/A"
    oldest_published = str(df['published'].min()) if 'published' in df and not df.empty else "N/A"
    
    stale_rows = int((df['age_days'] > settings.freshness_threshold_days).sum()) if 'age_days' in df else 0
    is_fresh = bool(stale_rows == 0)
    
    payload = {
        "latest_published": latest_published,
        "oldest_published": oldest_published,
        "stale_rows": stale_rows,
        "total_rows": total_rows,
        "is_fresh": is_fresh
    }
    
    out_path = pathlib.Path(report_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(out_path, payload)
    
    return payload
