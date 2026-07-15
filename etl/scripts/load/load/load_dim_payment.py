import pandas as pd
from sqlalchemy import text

from etl.scripts.data_quality.dq_dim_payment import run_dq_dim_payment
from etl.scripts.load.build.build_dim_payment import build_dim_payment
from logger.logger import AppLogger
from exception.exceptions import ExtractDataError, LoadDataError

log = AppLogger(name="dw.load_dim_payment", log_file="dw_load.log")


def extract_rcl_payments(engine) -> pd.DataFrame:
    """
    Estrae i dati dei pagamenti (tipo e numero di rate) dall'area reconciled.

    :param engine: Connessione al database (schema reconciled).
    :return: DataFrame Pandas con le combinazioni di pagamenti.
    """
    log.info("[load_dim_payment] Extract from rcl_payments started")

    if engine is None:
        log.error("[load_dim_payment] Database engine is None")
        raise ExtractDataError("Database engine is None")

    query = """
        SELECT
            payment_type,
            payment_installments
        FROM reconciled.rcl_order_payments
    """

    try:
        df_rcl = pd.read_sql(query, engine)
        log.info(f"[load_dim_payment] Rows extracted from rcl_order_payments: {len(df_rcl)}")
        return df_rcl

    except Exception as e:
        log.error(f"[load_dim_payment] Error during extract from rcl_order_payments: {e}")
        raise ExtractDataError(f"Error extracting rcl_order_payments: {e}") from e


def load_dim_payment_table(conn, dim_payment: pd.DataFrame) -> None:
    """
    Carica le tipologie di pagamento nella tabella `dim_payment` del Data Warehouse.
    Nota: la TRUNCATE della tabella è gestita dall'orchestratore, qui avviene solo l'inserimento in append.

    :param conn: Connessione al database (schema public/dwh).
    :param dim_payment: DataFrame Pandas con le chiavi surrogate e i dati pronti per il DWH.
    """
    log.info("[load_dim_payment] Load into dim_payment started")

    if conn is None:
        log.error("[load_dim_payment] Database connection is None")
        raise LoadDataError("Database connection is None")

    if dim_payment is None:
        log.error("[load_dim_payment] dim_payment dataframe is None")
        raise LoadDataError("dim_payment dataframe is None")

    if dim_payment.empty:
        log.error("[load_dim_payment] dim_payment dataframe is empty")
        raise LoadDataError("dim_payment dataframe is empty")

    required_cols = [
        "payment_type",
        "payment_installments"
    ]
    missing = [c for c in required_cols if c not in dim_payment.columns]
    if missing:
        log.error(f"[load_dim_payment] Missing required columns in dim_payment: {missing}")
        raise LoadDataError(f"Missing required columns in dim_payment: {missing}")

    try:
        log.info(f"[load_dim_payment] Inserting rows into dim_payment: {len(dim_payment)}")
        dim_payment.to_sql(
            "dim_payment",
            con=conn,
            if_exists="append",
            index=False,
            method="multi"
        )

        log.info("[load_dim_payment] Load into dim_payment completed")

    except Exception as e:
        log.error(f"[load_dim_payment] Error during load into dim_payment: {e}")
        raise LoadDataError(f"Error loading dim_payment: {e}") from e


def run_load_dim_payment(engine, conn) -> None:
    """
    Esegue l'intero flusso di caricamento per `dim_payment`:
    1. Extract delle combinazioni uniche (tipo pagamento, rate) da reconciled.
    2. Build (assegnazione della surrogate key).
    3. Load nel DWH.
    4. Esecuzione dei controlli di Data Quality (DQ) post-caricamento.

    :param engine: Connessione in lettura (reconciled).
    :param conn: Connessione in scrittura (dwh).
    """
    log.info("[load_dim_payment] Pipeline started")

    df_rcl = extract_rcl_payments(engine)
    dim_payment = build_dim_payment(df_rcl)
    load_dim_payment_table(conn, dim_payment)

    dq_path = run_dq_dim_payment(
        source_df=df_rcl,
        transformed_df=dim_payment,
        engine_dw=conn
    )
    log.info(f"[load_dim_payment] DQ report saved: {dq_path}")
    log.info("[load_dim_payment] Pipeline completed")