import json
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any

import pandas as pd


REPORT_DIR = Path(__file__).parent / "reports"


def _safe_int(value) -> int:
    try:
        return int(value)
    except Exception:
        return 0


def _null_counts(df: pd.DataFrame, columns: List[str]) -> Dict[str, int]:
    result = {}
    for col in columns:
        if col in df.columns:
            result[col] = _safe_int(df[col].isna().sum())
        else:
            result[col] = -1
    return result


def _empty_string_counts(df: pd.DataFrame, columns: List[str]) -> Dict[str, int]:
    result = {}
    for col in columns:
        if col in df.columns:
            result[col] = _safe_int(
                df[col].astype(str).str.strip().eq("").sum()
            )
        else:
            result[col] = -1
    return result


def _duplicate_count(df: pd.DataFrame, subset: Optional[List[str]]) -> int:
    if not subset:
        return 0
    if not all(col in df.columns for col in subset):
        return -1
    return _safe_int(df.duplicated(subset=subset).sum())


def _domain_violations(df: pd.DataFrame, allowed_values: Optional[Dict[str, List[Any]]]) -> Dict[str, int]:
    result = {}
    if not allowed_values:
        return result

    for col, allowed in allowed_values.items():
        if col not in df.columns:
            result[col] = -1
            continue
        valid_set = set(allowed)
        violations = (~df[col].isin(valid_set) & df[col].notna()).sum()
        result[col] = _safe_int(violations)

    return result


def _range_violations(df: pd.DataFrame, numeric_ranges: Optional[Dict[str, Dict[str, Any]]]) -> Dict[str, int]:
    result = {}
    if not numeric_ranges:
        return result

    for col, limits in numeric_ranges.items():
        if col not in df.columns:
            result[col] = -1
            continue

        series = pd.to_numeric(df[col], errors="coerce")
        violations = pd.Series(False, index=series.index)

        if "min" in limits and limits["min"] is not None:
            violations = violations | (series < limits["min"])
        if "max" in limits and limits["max"] is not None:
            violations = violations | (series > limits["max"])

        result[col] = _safe_int(violations.fillna(False).sum())

    return result


_VALID_TABLE_NAME = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_.]*$')

def _table_row_count(engine, table_name: str) -> int:
    if not _VALID_TABLE_NAME.match(table_name):
        raise ValueError(f"Invalid table name: {table_name!r}")
    query = f"SELECT COUNT(*) AS cnt FROM {table_name}"
    df = pd.read_sql(query, engine)
    return _safe_int(df.iloc[0]["cnt"])


def build_dq_report(
    job_name: str,
    source_df: pd.DataFrame,
    transformed_df: pd.DataFrame,
    engine_dw,
    loaded_table_name: str,
    required_columns_source: Optional[List[str]] = None,
    required_columns_transformed: Optional[List[str]] = None,
    business_key_columns_source: Optional[List[str]] = None,
    business_key_columns_transformed: Optional[List[str]] = None,
    allowed_values_source: Optional[Dict[str, List[Any]]] = None,
    allowed_values_transformed: Optional[Dict[str, List[Any]]] = None,
    numeric_ranges_source: Optional[Dict[str, Dict[str, Any]]] = None,
    numeric_ranges_transformed: Optional[Dict[str, Dict[str, Any]]] = None,
    extra_metrics: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:

    required_columns_source = required_columns_source or []
    required_columns_transformed = required_columns_transformed or []
    extra_metrics = extra_metrics or {}

    loaded_rows = _table_row_count(engine_dw, loaded_table_name)

    report = {
        "job_name": job_name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "loaded_table_name": loaded_table_name,
        "counts": {
            "source_rows": _safe_int(len(source_df)),
            "transformed_rows": _safe_int(len(transformed_df)),
            "loaded_rows": loaded_rows,
            "source_to_transformed_delta": _safe_int(len(transformed_df) - len(source_df)),
            "transformed_to_loaded_delta": _safe_int(loaded_rows - len(transformed_df)),
        },
        "source_checks": {
            "null_required": _null_counts(source_df, required_columns_source),
            "empty_required": _empty_string_counts(source_df, required_columns_source),
            "duplicate_business_keys": _duplicate_count(source_df, business_key_columns_source),
            "domain_violations": _domain_violations(source_df, allowed_values_source),
            "range_violations": _range_violations(source_df, numeric_ranges_source),
        },
        "transformed_checks": {
            "null_required": _null_counts(transformed_df, required_columns_transformed),
            "empty_required": _empty_string_counts(transformed_df, required_columns_transformed),
            "duplicate_business_keys": _duplicate_count(transformed_df, business_key_columns_transformed),
            "domain_violations": _domain_violations(transformed_df, allowed_values_transformed),
            "range_violations": _range_violations(transformed_df, numeric_ranges_transformed),
        },
        "extra_metrics": extra_metrics,
    }

    report["status"] = "OK"
    if loaded_rows != len(transformed_df):
        report["status"] = "WARNING"

    transformed_nulls = report["transformed_checks"]["null_required"]
    transformed_empties = report["transformed_checks"]["empty_required"]
    transformed_dup = report["transformed_checks"]["duplicate_business_keys"]

    if any(v > 0 for v in transformed_nulls.values() if v >= 0):
        report["status"] = "WARNING"
    if any(v > 0 for v in transformed_empties.values() if v >= 0):
        report["status"] = "WARNING"
    if transformed_dup > 0:
        report["status"] = "WARNING"

    return report


def save_dq_report(report: Dict[str, Any]) -> str:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    file_name = f"{report['job_name']}.json"
    file_path = REPORT_DIR / file_name

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    return str(file_path)