from sqlalchemy.engine import Connection

from logger.logger import AppLogger
from etl.scripts.extract.read_csv_metadata import read_csv_metadata
from etl.scripts.extract.checkpoint_service import (
    get_or_create_checkpoint,
    mark_checkpoint_running,
    mark_checkpoint_completed,
    mark_checkpoint_failed,
    reset_checkpoint,
)
from etl.scripts.extract.iter_csv_batches import iter_csv_batches
from etl.scripts.extract.batch.process_batch import process_batch

log = AppLogger(name="orchestrator.extract", log_file="orchestrator.log")

def run_extraction(
    conn: Connection,
    csv_path: str,
    selected_columns: list[str],
    batch_size: int,
    target_table: str,
    truncate: bool = False
) -> None:
    log.info(
        f"[extraction_orchestrator] Starting extraction for file={csv_path}, "
        f"target_table={target_table}, batch_size={batch_size}, truncate={truncate}"
    )

    checkpoint = None

    try:
        metadata = read_csv_metadata(csv_path)

        checkpoint = get_or_create_checkpoint(
            conn,
            source_file=metadata.source_file,
            total_rows=metadata.total_rows
        )

        if truncate:
            log.info(
                f"[extraction_orchestrator] Truncate requested for file={csv_path}, resetting checkpoint"
            )
            reset_checkpoint(conn, metadata.source_file)

            checkpoint = get_or_create_checkpoint(
                conn,
                source_file=metadata.source_file,
                total_rows=metadata.total_rows
            )

        if checkpoint.status == "COMPLETED" and not truncate:
            log.info(
                f"[extraction_orchestrator] Extraction skipped for file={csv_path}: "
                f"checkpoint already COMPLETED"
            )
            return

        if checkpoint.status == "FAILED":
            log.info(
                f"[extraction_orchestrator] Checkpoint is FAILED for file={csv_path}, resetting before restart"
            )
            reset_checkpoint(conn, metadata.source_file)

            checkpoint = get_or_create_checkpoint(
                conn,
                source_file=metadata.source_file,
                total_rows=metadata.total_rows
            )

        mark_checkpoint_running(conn, checkpoint.id)

        current_last_row = checkpoint.last_row_extracted

        for chunk in iter_csv_batches(
            csv_path=csv_path,
            selected_columns=selected_columns,
            batch_size=batch_size,
            start_row=current_last_row
        ):
            next_last_row = current_last_row + len(chunk)

            process_batch(
                conn=conn,
                checkpoint_id=checkpoint.id,
                chunk=chunk,
                next_last_row=next_last_row,
                target_table=target_table
            )

            current_last_row = next_last_row

        mark_checkpoint_completed(conn, checkpoint.id)

        log.info(
            f"[extraction_orchestrator] Extraction completed successfully for file={csv_path}"
        )

    except Exception as e:
        if checkpoint is not None:
            try:
                mark_checkpoint_failed(conn, checkpoint.id, str(e))
            except Exception as mark_error:
                log.error(
                    f"[extraction_orchestrator] Failed to mark checkpoint as FAILED "
                    f"for file={csv_path}: {mark_error}"
                )

        log.error(f"[extraction_orchestrator] Extraction failed for file={csv_path}: {e}")
        raise