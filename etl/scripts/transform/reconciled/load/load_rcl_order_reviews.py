import pandas as pd
from sqlalchemy import text

from logger.logger import AppLogger
from exception.exceptions import ExtractDataError, LoadDataError

log = AppLogger(name="rcl.order_reviews.load", log_file="rcl_order_reviews.log")


def extract_order_reviews_from_staging(engine) -> pd.DataFrame:
    """
    Estrae tutti i record delle recensioni dalla tabella `stg_order_reviews` (area di staging).
    
    :param engine: Connessione al database di staging.
    :return: DataFrame Pandas con i dati estratti.
    """
    log.info("[load_rcl_order_reviews] Extract from order_reviews started")

    if engine is None:
        log.error("[load_rcl_order_reviews] Database engine is None")
        raise ExtractDataError("Database engine is None")

    query = """
        SELECT
            review_id,
            order_id,
            review_score,
            review_comment_title,
            review_comment_message,
            review_creation_date,
            review_answer_timestamp
        FROM staging.stg_order_reviews
    """

    try:
        df = pd.read_sql(query, engine)
        log.info(f"[load_rcl_order_reviews] Rows extracted: {len(df)}")
        return df
    except Exception as e:
        log.error(f"[load_rcl_order_reviews] Error during extract: {e}")
        raise ExtractDataError(f"Error extracting order_reviews: {e}") from e


def load_rcl_order_reviews_table(conn, df_rcl: pd.DataFrame) -> None:
    """
    Carica i dati delle recensioni trasformati nella tabella `rcl_order_reviews` dell'area reconciled.
    Esegue prima una TRUNCATE per garantire l'idempotenza.

    :param conn: Connessione al database (reconciled).
    :param df_rcl: DataFrame Pandas con i dati puliti.
    """
    log.info("[load_rcl_order_reviews] Load into rcl_order_reviews started")

    if conn is None:
        log.error("[load_rcl_order_reviews] Database connection is None")
        raise LoadDataError("Database connection is None")

    if df_rcl is None or df_rcl.empty:
        log.error("[load_rcl_order_reviews] dataframe is empty or None")
        raise LoadDataError("rcl_order_reviews dataframe is empty or None")

    try:
        conn.execute(text("TRUNCATE TABLE reconciled.rcl_order_reviews"))
        df_rcl.to_sql("rcl_order_reviews", con=conn, schema="reconciled", if_exists="append", index=False, method="multi")
        log.info(f"[load_rcl_order_reviews] Loaded rows: {len(df_rcl)}")
    except Exception as e:
        log.error(f"[load_rcl_order_reviews] Error during load: {e}")
        raise LoadDataError(f"Error loading rcl_order_reviews: {e}") from e