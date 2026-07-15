import pandas as pd

from exception.exceptions import DataCleaningError
from logger.logger import AppLogger

log = AppLogger(name="rcl.order_reviews.build", log_file="rcl_order_reviews.log")


def build_rcl_order_reviews(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Esegue la pulizia e l'arricchimento dei dati delle recensioni degli ordini.
    - Valida il punteggio della recensione (review_score) verificando che sia tra 1 e 5.
    - Sostituisce eventuali valori nulli nei campi testuali (titolo e messaggio) con stringhe vuote.
    - Converte le date in formato datetime.
    - Elimina eventuali duplicati esatti.

    :param dataframe: DataFrame Pandas contenente i dati raw delle recensioni dallo staging.
    :return: DataFrame Pandas pulito e formattato per l'area reconciled.
    """
    log.info("[build_rcl_order_reviews] Build started")

    if dataframe is None:
        log.error("[build_rcl_order_reviews] Input dataframe is None")
        raise DataCleaningError("Order reviews dataframe is None")

    if dataframe.empty:
        log.error("[build_rcl_order_reviews] Input dataframe is empty")
        raise DataCleaningError("Order reviews dataframe is empty")

    df = dataframe.copy()

    df = df.rename(columns={
        # alias futuri, se dovessero servire
        # "review_answer_date": "review_answer_timestamp",
    })

    required_cols = [
        "review_id",
        "order_id",
        "review_score",
        "review_comment_title",
        "review_comment_message",
        "review_creation_date",
        "review_answer_timestamp"
    ]

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        log.error(f"[build_rcl_order_reviews] Missing required columns: {missing}")
        raise DataCleaningError(f"Missing required columns: {missing}")

    df["review_id"] = df["review_id"].astype(str).str.strip()
    df["order_id"] = df["order_id"].astype(str).str.strip()
    df["review_score"] = pd.to_numeric(df["review_score"], errors="coerce")
    df["review_score_valid_flag"] = df["review_score"].between(1, 5, inclusive="both")

    df["review_comment_title"] = (
        df["review_comment_title"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["review_comment_message"] = (
        df["review_comment_message"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["review_creation_date"] = pd.to_datetime(df["review_creation_date"], errors="coerce")
    df["review_answer_timestamp"] = pd.to_datetime(df["review_answer_timestamp"], errors="coerce")

    before = len(df)
    df = df.drop_duplicates()
    log.info(f"[build_rcl_order_reviews] Exact duplicates removed: {before - len(df)}")
    log.info(f"[build_rcl_order_reviews] Output rows: {len(df)}")

    return df[[
        "review_id",
        "order_id",
        "review_score",
        "review_comment_title",
        "review_comment_message",
        "review_creation_date",
        "review_answer_timestamp",
        "review_score_valid_flag"
    ]]