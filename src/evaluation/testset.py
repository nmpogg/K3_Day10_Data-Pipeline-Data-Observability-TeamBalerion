from __future__ import annotations

from typing import Any

import pandas as pd


def build_test_set(df: pd.DataFrame, output_path) -> list[dict[str, Any]]:
    """TODO(student): tao bo evaluation set tu cleaned dataframe.

    Pseudo-code:
    1. Kiem tra so luong document toi thieu.
    2. Chon mot so paper dai dien.
    3. Tao nhieu loai cau hoi:
       - summary
       - authors
       - date
       - categories
    4. Moi row can co:
       - id
       - question_type
       - question
       - ground_truth
       - ground_truth_doc_ids
    5. Ghi file JSON vao output_path.
    """
    import json
    import pathlib


    if len(df) < 5:
        raise ValueError("Không đủ dữ liệu để tạo test set (cần ít nhất 5 bài).")
        
    questions = []
    
    # Generate 5 questions about authors from the first 5 papers
    for i, row in df.head(5).iterrows():
        q_id = f"q_author_{i+1}"
        title = row.get('title', '')
        authors = row.get('authors_joined', '')
        if not authors and isinstance(row.get('authors'), list):
            authors = ", ".join(row['authors'])
            
        q = {
            "id": q_id,
            "question_type": "factual",
            "question": f"Who are the authors of the paper titled '{title}'?",
            "ground_truth": f"The authors of the paper are: {authors}.",
            "ground_truth_doc_ids": [row['paper_id']]
        }
        questions.append(q)
        
    # Generate 5 questions about publication date from the next 5 papers
    for i, row in df.iloc[5:10].iterrows():
        q_id = f"q_date_{i+1}"
        title = row.get('title', '')
        published = row.get('published', 'Unknown')
        
        q = {
            "id": q_id,
            "question_type": "factual",
            "question": f"When was the paper '{title}' published?",
            "ground_truth": f"The paper was published on {published}.",
            "ground_truth_doc_ids": [row['paper_id']]
        }
        questions.append(q)
        
    # Write to JSON file
    output_path = pathlib.Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
        
    return questions
