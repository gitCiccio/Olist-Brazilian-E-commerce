import pandas as pd
from sqlalchemy import text

from logger.logger import AppLogger
from exception.exceptions import ExtractDataError, LoadDataError

log = AppLogger(name="rcl.order_payments.load", log_file="rcl_order_payments.log")


def extract_order_payments_from_staging(engine) -> pd.DataFrame:
    """
    Estrae tutti i record dei pagamenti dalla tabella `stg_order_payments` (area di staging).
    
    :param engine: Connessione al database di staging.
    :return: DataFrame Pandas con i dati estratti.
    """
    log.info("[load_rcl_order_payments] Extract from order_payments started")

    if engine is None:
        log.error("[load_rcl_order_payments] Database engine is None")
        raise ExtractDataError("Database engine is None")

    query = """
        SELECT
            order_id,
            payment_sequential,
            payment_type,
            payment_installments,
            payment_value
        FROM staging.stg_order_payments
    """

    try:
        df = pd.read_sql(query, engine)
        log.info(f"[load_rcl_order_payments] Rows extracted: {len(df)}")
        return df
    except Exception as e:
        log.error(f"[load_rcl_order_payments] Error during extract: {e}")
        raise ExtractDataError(f"Error extracting order_payments: {e}") from e


def load_rcl_order_payments_table(conn, df_rcl: pd.DataFrame) -> None:
    """
    Carica i dati dei pagamenti trasformati nella tabella `rcl_order_payments` dell'area reconciled.
    Esegue prima una TRUNCATE per garantire l'idempotenza.

    :param conn: Connessione al database (reconciled).
    :param df_rcl: DataFrame Pandas con i dati puliti.
    """
    log.info("[load_rcl_order_payments] Load into rcl_order_payments started")

    if conn is None:
        log.error("[load_rcl_order_payments] Database connection is None")
        raise LoadDataError("Database connection is None")

    if df_rcl is None or df_rcl.empty:
        log.error("[load_rcl_order_payments] dataframe is empty or None")
        raise LoadDataError("rcl_order_payments dataframe is empty or None")

    try:
        conn.execute(text("TRUNCATE TABLE reconciled.rcl_order_payments"))
        df_rcl.to_sql("rcl_order_payments", con=conn, schema="reconciled", if_exists="append", index=False, method="multi")
        log.info(f"[load_rcl_order_payments] Loaded rows: {len(df_rcl)}")
    except Exception as e:
        log.error(f"[load_rcl_order_payments] Error during load: {e}")
        raise LoadDataError(f"Error loading rcl_order_payments: {e}") from e