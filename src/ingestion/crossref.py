from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import requests

from core.config import Settings

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class PaperRecord:
    paper_id: str
    title: str
    summary: str
    authors: list[str]
    categories: list[str]
    primary_category: str
    published: str
    updated: str
    abs_url: str
    pdf_url: str
    comment: str


def parse_crossref_payload(payload: dict) -> list[PaperRecord]:
    """Parse Crossref payload thanh list PaperRecord.

    Pseudo-code:
    1. Duyet `payload["message"]["items"]`.
    2. Lay DOI, title, abstract, authors, subject, dates, URLs.
    3. Chuan hoa text va bo record khong hop le.
    4. Tra ve list `PaperRecord`.
    """
    records = []
    items = payload.get("message", {}).get("items", [])
    
    for item in items:
        title_list = item.get("title", [])
        title = title_list[0] if title_list else ""
        
        # summary: crossref uses 'abstract' but sometimes we can use 'description' if available. 
        summary = item.get("abstract", "")
        if not summary:
            # Fallback if crossref has some description somewhere
            summary = item.get("description", "")
            
        if not title or not summary:
            continue
            
        paper_id = item.get("DOI", "")
        
        author_list = item.get("author", [])
        authors = []
        for author in author_list:
            given = author.get("given", "")
            family = author.get("family", "")
            full_name = f"{given} {family}".strip()
            if full_name:
                authors.append(full_name)
                
        categories = item.get("subject", [])
        primary_category = categories[0] if categories else ""
        
        # Extract published date
        published_info = item.get("published-print", item.get("published-online", {}))
        published_parts = published_info.get("date-parts", [[]])[0]
        if published_parts:
            published = "-".join(str(p).zfill(2) for p in published_parts)
        else:
             # fallback to created date
             published = item.get("created", {}).get("date-time", "")
             
        # Extract updated date
        updated = item.get("indexed", {}).get("date-time", "")
        
        abs_url = item.get("URL", "")
        
        link_list = item.get("link", [])
        pdf_url = ""
        for link in link_list:
            if link.get("content-type") == "application/pdf":
                pdf_url = link.get("URL", "")
                break
                
        comment = ""
        
        record = PaperRecord(
            paper_id=paper_id,
            title=title,
            summary=summary,
            authors=authors,
            categories=categories,
            primary_category=primary_category,
            published=published,
            updated=updated,
            abs_url=abs_url,
            pdf_url=pdf_url,
            comment=comment
        )
        records.append(record)
        
    return records


def fetch_source_records(settings: Settings) -> list[PaperRecord]:
    """Goi source API, luu raw response, parse thanh records.

    Pseudo-code:
    1. Tao params tu `settings.source_query`, `settings.source_filter`, `settings.max_results`.
    2. Goi API voi retry cho cac status code nhu 429/503.
    3. Luu raw response vao `settings.paths.raw_api_response`.
    4. Parse payload bang `parse_crossref_payload`.
    5. Luu records vao `settings.paths.raw_records_json`.
    """
    url = "https://api.crossref.org/works"
    params = {
        "query": settings.source_query,
        "filter": settings.source_filter,
        "rows": settings.max_results
    }
    
    max_retries = 3
    retry_delay = 2
    payload = None
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code in (429, 503):
                logger.warning(f"Got {response.status_code} from Crossref API. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            response.raise_for_status()
            payload = response.json()
            break
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                logger.error(f"Failed to fetch data from Crossref API after {max_retries} attempts.")
                raise e
            logger.warning(f"Request error: {e}. Retrying in {retry_delay}s...")
            time.sleep(retry_delay)
            retry_delay *= 2
            
    if payload is None:
        raise RuntimeError("Failed to fetch data from Crossref API.")
        
    # Ensure raw directory exists
    settings.paths.raw_api_response.parent.mkdir(parents=True, exist_ok=True)
    
    with open(settings.paths.raw_api_response, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        
    records = parse_crossref_payload(payload)
    
    # Dump records to json
    records_dict = [asdict(r) for r in records]
    with open(settings.paths.raw_records_json, "w", encoding="utf-8") as f:
        json.dump(records_dict, f, ensure_ascii=False, indent=2)
        
    return records


def load_raw_records(path: Path) -> list[PaperRecord]:
    """Doc JSON snapshot va map thanh `PaperRecord`."""
    with open(path, "r", encoding="utf-8") as f:
        records_dict = json.load(f)
        
    records = [PaperRecord(**r) for r in records_dict]
    return records
