"""
Lo script process_batch serve a trasformare un singolo batch in un blocco di lavoro atomico
Permette di gestire in modo corretto le transazioni
Le sue funzionalità sono:
    - Caricamento dei chunk nello staging
    - Aggiornamento del checkpoint
    - Commit della transazione del batch
"""
import pandas as pd
from sqlalchemy.engine import Connection

from logger.logger import AppLogger
from exception.exceptions import ExtractDataError
from etl.extract.batch.load_batch_to_staging import load_to_staging
from etl.extract.checkpoint_service import update_checkpoint_progress

log = AppLogger(name="batch_processor.extract", log_file="batch_processor.log")

def process_batch(
    conn: Connection,
    checkpoint_id: str,
    chunk: pd.DataFrame,
    next_last_row: int,
    target_table: str
) -> None:
    log.info(
        f"[batch_processor] Processing batch for checkpoint_id={checkpoint_id} "
        f"with {len(chunk)} rows up to row {next_last_row}"
    )

    if conn is None:
        log.error("[batch_processor] Database connection is None")
        raise ExtractDataError("Database connection is None")

    if not checkpoint_id or not checkpoint_id.strip():
        log.error("[batch_processor] Checkpoint id is invalid")
        raise ExtractDataError("Checkpoint id is invalid")

    if chunk is None or chunk.empty:
        log.error(f"[batch_processor] Empty batch for checkpoint_id={checkpoint_id}")
        raise ExtractDataError(f"Empty batch for checkpoint_id={checkpoint_id}")

    if next_last_row < 0:
        log.error(f"[batch_processor] Invalid next_last_row for checkpoint_id={checkpoint_id}: {next_last_row}")
        raise ExtractDataError(
            f"Invalid next_last_row for checkpoint_id={checkpoint_id}: {next_last_row}"
        )
    try:
        load_to_staging(conn, chunk, target_table)
        update_checkpoint_progress(conn, checkpoint_id, next_last_row)
        conn.commit()

        log.info(
            f"[batch_processor] Batch committed successfully for checkpoint_id={checkpoint_id} "
            f"up to row {next_last_row}"
        )

    except ExtractDataError:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        log.error(
            f"[batch_processor] Error while processing batch for checkpoint_id={checkpoint_id}: {e}"
        )
        raise ExtractDataError(
            f"Error while processing batch for checkpoint_id={checkpoint_id}: {e}"
        ) from e