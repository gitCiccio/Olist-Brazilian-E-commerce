import pandas as pd

from logger.logger import AppLogger
from exception.exceptions import DataCleaningError

log = AppLogger(name="dw.build_dim_customer", log_file="dw_load.log")


def build_dim_customer(df_rcl: pd.DataFrame) -> pd.DataFrame:
    log.info("[build_dim_customer] Build started")

    if df_rcl is None:
        log.error("[build_dim_customer] Input dataframe is None")
        raise DataCleaningError("rcl_customers dataframe is None")

    if df_rcl.empty:
        log.error("[build_dim_customer] Input dataframe is empty")
        raise DataCleaningError("rcl_customers dataframe is empty")

    required_cols = [
        "customer_unique_id",
        "customer_region",
        "customer_city",
        "customer_state"
    ]

    missing = [c for c in required_cols if c not in df_rcl.columns]
    if missing:
        log.error(f"[build_dim_customer] Missing required columns: {missing}")
        raise DataCleaningError(f"Missing columns in rcl_customers: {missing}")

    df = df_rcl.copy()
    input_rows = len(df)
    log.info(f"[build_dim_customer] Input rows: {input_rows}")

    null_nk_count = df["customer_unique_id"].isna().sum()
    if null_nk_count > 0:
        log.warning(f"[build_dim_customer] Null natural keys found: {null_nk_count}")

    xx_state_count = (df["customer_state"] == "XX").sum()
    unknown_region_count = (df["customer_region"] == "unknown").sum()

    log.info(f"[build_dim_customer] customer_state='XX' rows: {xx_state_count}")
    log.info(f"[build_dim_customer] customer_region='unknown' rows: {unknown_region_count}")

    df = df.dropna(subset=["customer_unique_id"])
    df["customer_unique_id"] = df["customer_unique_id"].astype(str).str.strip()

    empty_nk_mask = df["customer_unique_id"] == ""
    empty_nk_count = empty_nk_mask.sum()
    if empty_nk_count > 0:
        log.warning(f"[build_dim_customer] Empty natural keys found after trim: {empty_nk_count}")

    df = df[~empty_nk_mask]

    df["customer_region"] = df["customer_region"].fillna("unknown").astype(str).str.strip()
    df["customer_city"] = df["customer_city"].fillna("unknown").astype(str).str.strip()
    df["customer_state"] = df["customer_state"].fillna("XX").astype(str).str.strip().str.upper()

    before_dedup_rows = len(df)
    df = df.drop_duplicates(subset=["customer_unique_id"], keep="first")
    duplicates_removed = before_dedup_rows - len(df)

    if duplicates_removed > 0:
        log.info(f"[build_dim_customer] Duplicates removed on customer_unique_id: {duplicates_removed}")
    else:
        log.info("[build_dim_customer] No duplicates found on customer_unique_id")

    result = df.rename(columns={"customer_unique_id": "natural_key"})[
        [
            "natural_key",
            "customer_region",
            "customer_city",
            "customer_state"
        ]
    ].copy()

    log.info(f"[build_dim_customer] Output rows for dim_customer: {len(result)}")
    log.info("[build_dim_customer] Build completed")

    return result