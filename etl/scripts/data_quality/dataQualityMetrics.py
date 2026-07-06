import json
from pathlib import Path
import pandas as pd

def build_metrics_summary():
    base_dir = Path(__file__).resolve().parent
    report_dir = base_dir / "reports"
    output_file = report_dir / "dq_metrics_summary.csv"

    report_files = [
        "dq_dim_customer.json",
        "dq_dim_date.json",
        "dq_dim_payment.json",
        "dq_dim_product.json",
        "dq_dim_seller.json",
        "dq_fact_sale_item.json",
    ]

    def valid_values(d):
        return [v for v in d.values() if isinstance(v, (int, float)) and v >= 0]

    def safe_sum_dict(d):
        return sum(valid_values(d))

    def completeness_pct(report):
        rows = report["counts"]["transformed_rows"]
        checks = report["transformed_checks"]
        null_required = checks.get("null_required", {})
        empty_required = checks.get("empty_required", {})
        cols_considered = len(valid_values(null_required))

        if rows == 0 or cols_considered == 0:
            return None

        nulls = safe_sum_dict(null_required)
        empties = safe_sum_dict(empty_required)
        total_cells = rows * cols_considered
        invalid_cells = nulls + empties

        return round(100 * (total_cells - invalid_cells) / total_cells, 2)

    def validity_pct(report):
        rows = report["counts"]["transformed_rows"]
        checks = report["transformed_checks"]
        domain_violations = checks.get("domain_violations", {})
        range_violations = checks.get("range_violations", {})
        total_rule_cols = len(valid_values(domain_violations)) + len(valid_values(range_violations))

        if rows == 0 or total_rule_cols == 0:
            return None

        violations = safe_sum_dict(domain_violations) + safe_sum_dict(range_violations)
        total_checks = rows * total_rule_cols

        return round(100 * (total_checks - violations) / total_checks, 2)

    def uniqueness_pct(report):
        rows = report["counts"]["transformed_rows"]
        dup = report["transformed_checks"].get("duplicate_business_keys", -1)

        if rows == 0 or dup < 0:
            return None

        return round(100 * (rows - dup) / rows, 2)

    def consistency_pct(report):
        rows_t = report["counts"]["transformed_rows"]
        rows_l = report["counts"]["loaded_rows"]

        if rows_t == 0:
            return None

        score = 100.0 if rows_t == rows_l else round(100 * min(rows_t, rows_l) / rows_t, 2)

        extra = report.get("extra_metrics", {})
        penalties = sum(v for v in extra.values() if isinstance(v, (int, float)) and v >= 0)

        if penalties > 0:
            score = round(max(0, 100 * (rows_t - penalties) / rows_t), 2)

        return score

    def classify_table(job_name):
        if "dim_" in job_name:
            return "dimension"
        if "fact_" in job_name:
            return "fact"
        return "unknown"

    rows = []

    for file_name in report_files:
        path = report_dir / file_name
        with open(path, "r", encoding="utf-8") as f:
            report = json.load(f)

        rows.append({
            "file_name": file_name,
            "job_name": report.get("job_name"),
            "table_name": report.get("loaded_table_name"),
            "table_type": classify_table(report.get("job_name", "")),
            "source_rows": report["counts"].get("source_rows"),
            "transformed_rows": report["counts"].get("transformed_rows"),
            "loaded_rows": report["counts"].get("loaded_rows"),
            "validity_pct": validity_pct(report),
            "completeness_pct": completeness_pct(report),
            "consistency_pct": consistency_pct(report),
            "uniqueness_pct": uniqueness_pct(report),
            "status": report.get("status"),
        })

    df = pd.DataFrame(rows)
    df.to_csv(output_file, index=False, encoding="utf-8")
    return str(output_file)