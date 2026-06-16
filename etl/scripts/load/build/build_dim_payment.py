import pandas as pd

from logger.logger import AppLogger
from exception.exceptions import DataCleaningError

log = AppLogger(name="dw.build_dim_payment", log_file="dw_load.log")

VALID_PAYMENT_TYPES = {
    "credit_card",
    "debit_card",
    "voucher",
    "ticket",
    "not_defined"
}


def normalize_payment_type(value: str) -> str:
    if pd.isna(value):
        return "not_defined"

    value = str(value).strip().lower()

    mapping = {
        "credit_card": "credit_card",
        "debit_card": "debit_card",
        "voucher": "voucher",
        "boleto": "ticket",
        "ticket": "ticket",
        "not_defined": "not_defined"
    }

    normalized = mapping.get(value, "not_defined")
    return normalized if normalized in VALID_PAYMENT_TYPES else "not_defined"


def build_dim_payment(df_rcl: pd.DataFrame) -> pd.DataFrame:
    log.info("[build_dim_payment] Build started")

    if df_rcl is None:
        log.error("[build_dim_payment] Input dataframe is None")
        raise DataCleaningError("rcl_payments dataframe is None")

    if df_rcl.empty:
        log.error("[build_dim_payment] Input dataframe is empty")
        raise DataCleaningError("rcl_payments dataframe is empty")

    required_cols = [
        "payment_type",
        "payment_installments"
    ]

    missing = [c for c in required_cols if c not in df_rcl.columns]
    if missing:
        log.error(f"[build_dim_payment] Missing required columns: {missing}")
        raise DataCleaningError(f"Missing columns in rcl_payments: {missing}")

    df = df_rcl.copy()
    input_rows = len(df)
    log.info(f"[build_dim_payment] Input rows: {input_rows}")

    df["payment_type"] = df["payment_type"].apply(normalize_payment_type)
    df["payment_installments"] = pd.to_numeric(
        df["payment_installments"], errors="coerce"
    ).fillna(0).astype(int)

    negative_installments = (df["payment_installments"] < 0).sum()
    if negative_installments > 0:
        log.warning(f"[build_dim_payment] Negative installments found: {negative_installments}")
        df.loc[df["payment_installments"] < 0, "payment_installments"] = 0

    not_defined_count = (df["payment_type"] == "not_defined").sum()
    if not_defined_count > 0:
        log.warning(f"[build_dim_payment] payment_type normalized to 'not_defined': {not_defined_count}")

    before_dedup_rows = len(df)
    df = df.drop_duplicates(subset=["payment_type", "payment_installments"], keep="first")
    duplicates_removed = before_dedup_rows - len(df)

    if duplicates_removed > 0:
        log.info(
            "[build_dim_payment] Duplicates removed on (payment_type, payment_installments): "
            f"{duplicates_removed}"
        )
    else:
        log.info("[build_dim_payment] No duplicates found on payment dimension business key")

    result = df[[
        "payment_type",
        "payment_installments"
    ]].copy()

    log.info(f"[build_dim_payment] Output rows for dim_payment: {len(result)}")
    log.info("[build_dim_payment] Build completed")

    return result