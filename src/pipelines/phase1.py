from __future__ import annotations

import logging
from datetime import datetime, UTC

from core.config import load_settings
from ingestion.crossref import fetch_source_records, load_raw_records
from ingestion.cleaning import build_clean_dataframe, save_clean_dataframe
from retrieval.index import LocalEmbeddingIndex
from evaluation.testset import build_test_set
from evaluation.metrics import evaluate_pipeline
from observability.quality import run_data_quality_checks, build_freshness_report
from observability.reporting import generate_phase1_report

logger = logging.getLogger(__name__)

def main() -> None:
    # 1. Load settings.
    settings = load_settings()
    logger.info("Loaded settings.")

    # 2. Load hoac fetch raw records.
    if settings.refresh_source or not settings.paths.raw_records_json.exists():
        logger.info("Fetching raw records from source...")
        raw_records = fetch_source_records(settings)
    else:
        logger.info("Loading existing raw records...")
        raw_records = load_raw_records(settings.paths.raw_records_json)

    source_summary = {
        "total_raw": len(raw_records),
        "source": settings.source_api
    }

    # 3. Clean data.
    logger.info("Cleaning raw records...")
    df_clean = build_clean_dataframe(raw_records, datetime.now(UTC))
    source_summary["total_clean"] = len(df_clean)

    # 4. Save clean CSV/JSON.
    logger.info("Saving clean data...")
    save_clean_dataframe(df_clean, settings)

    # 5. Build Chroma index.
    logger.info("Building Chroma index...")
    index = LocalEmbeddingIndex.build(df_clean, settings, settings.paths.embeddings_json)

    # 6. Tao hoac load evaluation set.
    if settings.refresh_test_set or not settings.paths.eval_testset.exists():
        logger.info("Building evaluation test set...")
        build_test_set(df_clean, settings.paths.eval_testset)
    else:
        logger.info("Using existing evaluation test set.")

    # 7. Evaluate.
    logger.info("Evaluating baseline pipeline...")
    eval_bundle = evaluate_pipeline(
        settings=settings,
        index=index,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=settings.paths.baseline_metrics,
        answers_output_path=settings.paths.baseline_answers,
    )

    # 8. Run quality checks va freshness report.
    logger.info("Running data quality checks and freshness report...")
    quality_results = run_data_quality_checks(df_clean, settings, "Baseline Quality Check")
    freshness_results = build_freshness_report(df_clean, settings, settings.paths.freshness_report)

    # 9. Tao markdown report.
    logger.info("Generating markdown report...")
    generate_phase1_report(
        report_path=settings.paths.baseline_report,
        source_summary=source_summary,
        metrics=eval_bundle.summary,
        quality=quality_results,
        freshness=freshness_results,
    )
    
    logger.info("Phase 1 Pipeline completed successfully.")
