from __future__ import annotations

import pandas as pd


def corrupt_clean_dataframe(df: pd.DataFrame, output_log_path) -> pd.DataFrame:
    """TODO(student): simulate nhieu dang data corruption.

    Pseudo-code:
    1. Drop mot so latest records.
    2. Blank summary o mot so dong.
    3. Inject noise vao text.
    4. Lam title bi truncate.
    5. Lam published date cu di.
    6. Add duplicate rows.
    7. Rebuild `text_for_embedding`.
    8. Ghi corruption log vao output_log_path.
    """
    import json
    from pathlib import Path
    
    corrupted_df = df.copy()
    logs = []
    
    # Kịch bản 1: Xóa tóm tắt (Blank Summary)
    target_id_1 = "10.2118/234689-pa"
    idx1 = corrupted_df[corrupted_df['paper_id'] == target_id_1].index
    if not idx1.empty:
        corrupted_df.loc[idx1, 'summary'] = ""
        if 'summary_chars' in corrupted_df:
            corrupted_df.loc[idx1, 'summary_chars'] = 0
        
        # Re-build text_for_embedding
        row = corrupted_df.loc[idx1[0]]
        title = row.get('title', '')
        authors = row.get('authors', '')
        corrupted_df.loc[idx1, 'text_for_embedding'] = f"Title: {title} | Authors: {authors} | Summary: "
        logs.append({"paper_id": target_id_1, "action": "blank_summary"})
        
    # Kịch bản 2: Làm cũ dữ liệu (Stale Date)
    target_id_2 = "10.1111/exsy.70341"
    idx2 = corrupted_df[corrupted_df['paper_id'] == target_id_2].index
    if not idx2.empty:
        corrupted_df.loc[idx2, 'published'] = "2000-01-01"
        if 'age_days' in corrupted_df:
            corrupted_df.loc[idx2, 'age_days'] = 9999
        logs.append({"paper_id": target_id_2, "action": "stale_date"})
        
    # Kịch bản 3: Gây nhiễu nội dung (Add Noise)
    target_id_3 = "10.1007/s10278-026-02086-9"
    idx3 = corrupted_df[corrupted_df['paper_id'] == target_id_3].index
    if not idx3.empty:
        noise = " \n[SPAM] Buy cheap watches! Click here! [/SPAM]\n "
        corrupted_df.loc[idx3, 'text_for_embedding'] = corrupted_df.loc[idx3, 'text_for_embedding'] + noise
        logs.append({"paper_id": target_id_3, "action": "add_noise"})

    # Kịch bản 4: Tạo trùng lặp (Duplicates)
    target_id_4 = "10.21203/rs.3.rs-10178277/v1"
    idx4 = corrupted_df[corrupted_df['paper_id'] == target_id_4].index
    if not idx4.empty:
        row_to_dup = corrupted_df.loc[idx4].copy()
        corrupted_df = pd.concat([corrupted_df, row_to_dup], ignore_index=True)
        logs.append({"paper_id": target_id_4, "action": "duplicate"})

    # Ghi log
    out_path = Path(output_log_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(logs, f, indent=2)
        
    return corrupted_df
