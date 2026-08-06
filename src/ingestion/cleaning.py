from __future__ import annotations

import re
from dataclasses import asdict
from datetime import datetime

import pandas as pd

from core.config import Settings
from ingestion.crossref import PaperRecord


def remove_html_tags(text: str) -> str:
    """Loại bỏ thẻ XML/HTML."""
    if not isinstance(text, str):
        return ""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text).strip()


def build_clean_dataframe(records: list[PaperRecord], run_date: datetime) -> pd.DataFrame:
    """Clean raw records thanh dataframe san sang de embed.

    Pseudo-code:
    1. Normalize title, summary, authors, categories.
    2. Parse published/updated date.
    3. Tinh age_days.
    4. Tao cot helper:
       - authors_joined
       - categories_joined
       - summary_chars
       - text_for_embedding
    5. Drop duplicates va filter row xau.
    6. Sort dataframe va return.
    """
    if not records:
        return pd.DataFrame()
        
    df = pd.DataFrame([asdict(r) for r in records])
    
    # Chuẩn hóa trường text: loại bỏ HTML tags
    df['title'] = df['title'].apply(remove_html_tags)
    df['summary'] = df['summary'].apply(remove_html_tags)
    
    # Tính toán summary_chars
    df['summary_chars'] = df['summary'].str.len()
    
    # Lọc bản ghi rác: loại bỏ title rỗng hoặc summary < 100 ký tự
    df = df[df['title'].str.strip() != ""]
    df = df[df['summary_chars'] >= 100]
    
    if df.empty:
        return df
        
    # Xử lý tác giả & category: Gộp list thành chuỗi
    df['authors_joined'] = df['authors'].apply(lambda x: ", ".join(x) if isinstance(x, list) else "")
    df['categories_joined'] = df['categories'].apply(lambda x: ", ".join(x) if isinstance(x, list) else "")
    
    # Tạo text_for_embedding
    df['text_for_embedding'] = "Title: " + df['title'] + " | Authors: " + df['authors_joined'] + " | Summary: " + df['summary']
    
    # Xử lý ngày tháng và tính age_days
    def parse_and_diff(date_str):
        try:
            parts = str(date_str).split("T")[0].split("-")
            year = int(parts[0])
            month = int(parts[1]) if len(parts) > 1 else 1
            day = int(parts[2]) if len(parts) > 2 else 1
            pub_date = datetime(year, month, day, tzinfo=run_date.tzinfo)
            return (run_date - pub_date).days
        except Exception:
            return 0

    df['age_days'] = df['published'].apply(parse_and_diff)
    
    # Định dạng published về YYYY-MM-DD
    def format_date(date_str):
        try:
            parts = str(date_str).split("T")[0].split("-")
            year = parts[0]
            month = parts[1].zfill(2) if len(parts) > 1 else "01"
            day = parts[2].zfill(2) if len(parts) > 2 else "01"
            return f"{year}-{month}-{day}"
        except Exception:
            return date_str
            
    df['published'] = df['published'].apply(format_date)
    
    # Xóa trùng lặp và sắp xếp
    df = df.drop_duplicates(subset=['paper_id'])
    df = df.sort_values(by='published', ascending=False).reset_index(drop=True)
    
    return df


def save_clean_dataframe(df: pd.DataFrame, settings: Settings) -> None:
    """Lưu kết quả làm sạch vào CSV và JSON."""
    settings.paths.clean_csv.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(settings.paths.clean_csv, index=False, encoding="utf-8")
    df.to_json(settings.paths.clean_json, orient="records", force_ascii=False, indent=2)
