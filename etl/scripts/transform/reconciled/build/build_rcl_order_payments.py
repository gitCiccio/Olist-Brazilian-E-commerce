import pandas as pd

from exception.exceptions import DataCleaningError
from logger.logger import AppLogger

log = AppLogger(name="rcl.order_payments.build", log_file="rcl_order_payments.log")

PAYMENT_MAPPING = {
    "credit_card": "credit_card",
    "debit_card": "debit_card",
    "voucher": "voucher",
    "boleto": "ticket"
}

VALID_PAYMENT_TYPES = {
    "credit_card",
    "debit_card",
    "voucher",
    "ticket",
    "not_defined"
}


def build_rcl_order_payments(dataframe: pd.DataFrame) -> pd.DataFrame:
    log.info("[build_rcl_order_payments] Build started")

    if dataframe is None:
        log.error("[build_rcl_order_payments] Input dataframe is None")
        raise DataCleaningError("Order payments dataframe is None")

    if dataframe.empty:
        log.error("[build_rcl_order_payments] Input dataframe is empty")
        raise DataCleaningError("Order payments dataframe is empty")

    df = dataframe.copy()

    required_cols = [
        "order_id",
        "payment_sequential",
        "payment_type",
        "payment_installments",
        "payment_value"
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        log.error(f"[build_rcl_order_payments] Missing required columns: {missing}")
        raise DataCleaningError(f"Missing required columns: {missing}")

    df["order_id"] = df["order_id"].astype(str).str.strip()

    df["payment_type"] = (
        df["payment_type"]
        .fillna("not_defined")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df["payment_type"] = df["payment_type"].map(PAYMENT_MAPPING).fillna(df["payment_type"])
    df.loc[~df["payment_type"].isin(VALID_PAYMENT_TYPES), "payment_type"] = "not_defined"

    df["payment_sequential"] = pd.to_numeric(df["payment_sequential"], errors="coerce")
    df["payment_installments"] = pd.to_numeric(df["payment_installments"], errors="coerce")
    df["payment_value"] = pd.to_numeric(df["payment_value"], errors="coerce")

    before = len(df)
    df = df.drop_duplicates()
    log.info(f"[build_rcl_order_payments] Exact duplicates removed: {before - len(df)}")
    log.info(f"[build_rcl_order_payments] Output rows: {len(df)}")

    return df[required_cols]