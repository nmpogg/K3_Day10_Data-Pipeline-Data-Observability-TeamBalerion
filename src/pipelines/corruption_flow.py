from __future__ import annotations

import json
import logging
from datetime import datetime, UTC
import pandas as pd

from core.config import load_settings
from ingestion.corruption import corrupt_clean_dataframe
from ingestion.cleaning import build_clean_dataframe
from ingestion.crossref import load_raw_records
from retrieval.index import LocalEmbeddingIndex
from evaluation.metrics import evaluate_pipeline
from observability.quality import run_data_quality_checks, build_freshness_report
from observability.reporting import generate_corruption_report

logger = logging.getLogger(__name__)

def main() -> None:
    settings = load_settings()
    logger.info("Loaded settings.")

    # 1. Load baseline metrics va clean dataset.
    with open(settings.paths.baseline_metrics, "r") as f:
        baseline_metrics = json.load(f)
    
    clean_csv = settings.paths.clean_csv
    df_clean = pd.read_csv(clean_csv)

    # 2. Tao corrupted dataframe.
    logger.info("Corrupting data...")
    corruption_log_path = settings.paths.corruption_log
    df_corrupted = corrupt_clean_dataframe(df_clean, corruption_log_path)

    # 3. Save corrupted artifacts.
    corrupted_csv = settings.paths.corrupted_clean_csv
    df_corrupted.to_csv(corrupted_csv, index=False)

    # 4. Rebuild index va evaluate (Corrupted).
    logger.info("Building corrupted index...")
    corrupted_embeddings_json = settings.paths.corrupted_embeddings_json
    corrupted_index = LocalEmbeddingIndex.build(df_corrupted, settings, corrupted_embeddings_json)
    
    logger.info("Evaluating corrupted pipeline...")
    corrupted_metrics_path = settings.paths.corrupted_metrics
    corrupted_answers_path = settings.paths.corrupted_answers
    corrupted_eval_bundle = evaluate_pipeline(
        settings=settings,
        index=corrupted_index,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=corrupted_metrics_path,
        answers_output_path=corrupted_answers_path,
    )
    
    # 5. Run quality checks/freshness tren corrupted data.
    logger.info("Running corrupted quality checks...")
    corrupted_quality = run_data_quality_checks(df_corrupted, settings, "Corrupted Quality Check")
    corrupted_freshness_path = settings.paths.freshness_report.with_name("corrupted_freshness.json")
    corrupted_freshness = build_freshness_report(df_corrupted, settings, corrupted_freshness_path)

    # 6. Repair lai tu raw records.
    logger.info("Loading raw records to repair...")
    raw_records = load_raw_records(settings.paths.raw_records_json)
    df_repaired = build_clean_dataframe(raw_records, datetime.now(UTC))
    
    repaired_csv = settings.paths.repaired_clean_csv
    df_repaired.to_csv(repaired_csv, index=False)

    # 7. Evaluate repaired dataset.
    logger.info("Building repaired index...")
    repaired_embeddings_json = settings.paths.repaired_embeddings_json
    repaired_index = LocalEmbeddingIndex.build(df_repaired, settings, repaired_embeddings_json)
    
    logger.info("Evaluating repaired pipeline...")
    repaired_metrics_path = settings.paths.repaired_metrics
    repaired_answers_path = settings.paths.repaired_answers
    repaired_eval_bundle = evaluate_pipeline(
        settings=settings,
        index=repaired_index,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=repaired_metrics_path,
        answers_output_path=repaired_answers_path,
    )
    
    logger.info("Running repaired quality checks...")
    repaired_quality = run_data_quality_checks(df_repaired, settings, "Repaired Quality Check")
    repaired_freshness_path = settings.paths.freshness_report.with_name("repaired_freshness.json")
    repaired_freshness = build_freshness_report(df_repaired, settings, repaired_freshness_path)

    # 8. Tao comparison report.
    logger.info("Generating corruption report...")
    report_path = settings.paths.comparison_report
    generate_corruption_report(
        report_path=report_path,
        baseline_metrics=baseline_metrics,
        corrupted_metrics=corrupted_eval_bundle.summary,
        repaired_metrics=repaired_eval_bundle.summary,
        corrupted_quality=corrupted_quality,
        repaired_quality=repaired_quality,
        corrupted_freshness=corrupted_freshness,
        repaired_freshness=repaired_freshness,
    )
    
    logger.info("Corruption flow completed successfully.")
