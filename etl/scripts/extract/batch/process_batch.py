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
from etl.scripts.extract.batch.load_batch_to_staging import load_to_staging
from etl.scripts.extract.checkpoint_service import update_checkpoint_progress

log = AppLogger(name="batch_processor.extract", log_file="batch_processor.log")

def process_batch(
    conn: Connection,
    checkpoint_id: str,
    chunk: pd.DataFrame,
    next_last_row: int,
    target_table: str
) -> None:
    """
    Tratta un singolo batch come un'unità transazionale atomica (blocco di lavoro).
    Carica i dati nello staging e aggiorna il progresso del checkpoint 
    all'interno di una transazione annidata (savepoint). In caso di errore, 
    entrambe le operazioni vengono annullate per garantire consistenza.

    :param conn: Connessione al database.
    :param checkpoint_id: ID del checkpoint corrente.
    :param chunk: Il DataFrame Pandas contenente i dati del batch corrente.
    :param next_last_row: Il numero di riga a cui aggiornare il checkpoint dopo il caricamento.
    :param target_table: Nome della tabella di destinazione nello staging.
    """
    log.info(
        f"[batch_processor] Processing batch for checkpoint_id={checkpoint_id} "
        f"with {len(chunk)} rows up to row {next_last_row}"
    )

    if conn is None:
        raise ExtractDataError("Database connection is None")
    if not checkpoint_id or not checkpoint_id.strip():
        raise ExtractDataError("Checkpoint id is invalid")
    if chunk is None or chunk.empty:
        raise ExtractDataError(f"Empty batch for checkpoint_id={checkpoint_id}")
    if next_last_row < 0:
        raise ExtractDataError(
            f"Invalid next_last_row for checkpoint_id={checkpoint_id}: {next_last_row}"
        )

    try:
        with conn.begin_nested():
            load_to_staging(conn, chunk, target_table)
            update_checkpoint_progress(conn, checkpoint_id, next_last_row)

        log.info(
            f"[batch_processor] Batch processed successfully for checkpoint_id={checkpoint_id} "
            f"up to row {next_last_row}"
        )

    except ExtractDataError:
        raise
    except Exception as e:
        log.error(
            f"[batch_processor] Error while processing batch for checkpoint_id={checkpoint_id}: {e}"
        )
        raise ExtractDataError(
            f"Error while processing batch for checkpoint_id={checkpoint_id}: {e}"
        ) from e