"""
Lo script checkpoint_service gestisce lo stato tecnico del job di estrazione
Verifica lo stato del file: Nuovo, In esecuzione, Completo, da riprendere e l'ultima riga estratta con successo
"""
from sqlalchemy import text

from logger.logger import AppLogger
from exception.exceptions import ExtractDataError
from etl.scripts.extract.models import CheckpointInfo

log = AppLogger(name="checkpoint_service.extract", log_file="checkpoint_service.log")

CHECKPOINT_TABLE = "staging.etl_checkpoint"


def get_or_create_checkpoint(conn, source_file: str, total_rows: int) -> CheckpointInfo:
    log.info(f"[checkpoint_service] get_or_create_checkpoint called with source_file={source_file}, total_rows={total_rows}")

    if conn is None:
        log.error("[checkpoint_service] Database connection is None")
        raise ExtractDataError("Database connection is None")

    if not source_file or not source_file.strip():
        log.error("[checkpoint_service] Source file is empty")
        raise ExtractDataError("Source file is empty")

    if total_rows < 0:
        log.error(f"[checkpoint_service] Invalid total_rows for {source_file}: {total_rows}")
        raise ExtractDataError(f"Invalid total_rows for {source_file}: {total_rows}")

    log.info(f"[checkpoint_service] Looking for checkpoint: {source_file}")

    try:
        row = conn.execute(
            text(f"""
                SELECT id, source_file, total_rows, last_row_extracted, status
                FROM {CHECKPOINT_TABLE}
                WHERE source_file = :source_file
                ORDER BY created_at DESC
                LIMIT 1
            """),
            {"source_file": source_file}
        ).mappings().first()

        if row:
            log.info(
                f"[checkpoint_service] Found checkpoint for {source_file} "
                f"(last_row_extracted={row['last_row_extracted']}, status={row['status']})"
            )

            return CheckpointInfo(
                id=str(row["id"]),
                source_file=row["source_file"],
                total_rows=row["total_rows"],
                last_row_extracted=row["last_row_extracted"],
                status=row["status"]
            )

        log.info(f"[checkpoint_service] No checkpoint found, creating new one for {source_file}")
        created = conn.execute(
            text(f"""
                INSERT INTO {CHECKPOINT_TABLE} (
                    source_file,
                    total_rows,
                    last_row_extracted,
                    status,
                    created_at
                )
                VALUES (:source_file, :total_rows, 0, 'CREATED', NOW())
                RETURNING id, source_file, total_rows, last_row_extracted, status
            """),
            {"source_file": source_file, "total_rows": total_rows}
        ).mappings().first()

        if created is None:
            log.error(f"[checkpoint_service] INSERT returned no row for {source_file}")
            raise ExtractDataError(f"INSERT returned no row for {source_file}")

        return CheckpointInfo(
            id=str(created["id"]),
            source_file=created["source_file"],
            total_rows=created["total_rows"],
            last_row_extracted=created["last_row_extracted"],
            status=created["status"]
        )

    except ExtractDataError:
        raise
    except Exception as e:
        log.error(f"[checkpoint_service] Error while getting or creating checkpoint for {source_file}: {e}")
        raise ExtractDataError(
            f"Error while getting or creating checkpoint for {source_file}: {e}"
        ) from e


def mark_checkpoint_running(conn, checkpoint_id: str) -> None:
    log.info(f"[checkpoint_service] Marking checkpoint {checkpoint_id} as RUNNING")

    if conn is None:
        log.error("[checkpoint_service] Database connection is None")
        raise ExtractDataError("Database connection is None")

    if not checkpoint_id or not checkpoint_id.strip():
        log.error("[checkpoint_service] Checkpoint id is invalid")
        raise ExtractDataError("Checkpoint id is invalid")

    log.info(f"[checkpoint_service] Looking for checkpoint with id: {checkpoint_id}")

    try:
        exist = conn.execute(
            text(f"""
                SELECT status
                FROM {CHECKPOINT_TABLE}
                WHERE id = :checkpoint_id
            """),
            {"checkpoint_id": checkpoint_id}
        ).mappings().first()

        if exist is None:
            log.error(f"[checkpoint_service] No checkpoint found with id: {checkpoint_id}")
            raise ExtractDataError(f"No checkpoint found with id: {checkpoint_id}")

        current_status = exist["status"]
        log.info(f"[checkpoint_service] Found checkpoint with id {checkpoint_id}")

        if current_status != "CREATED":
            log.error(
                f"[checkpoint_service] Unable to mark checkpoint with id {checkpoint_id} "
                f"from status {current_status} to RUNNING"
            )
            raise ExtractDataError(
                f"Unable to mark checkpoint with id {checkpoint_id} "
                f"from status {current_status} to RUNNING"
            )

        conn.execute(
            text(f"""
                UPDATE {CHECKPOINT_TABLE}
                SET status = 'RUNNING',
                    started_at = NOW(),
                    updated_at = NOW()
                WHERE id = :checkpoint_id
            """),
            {"checkpoint_id": checkpoint_id}
        )

        log.info(
            f"[checkpoint_service] Marked checkpoint with id {checkpoint_id} "
            f"from {current_status} to RUNNING"
        )

    except ExtractDataError:
        raise
    except Exception as e:
        log.error(f"[checkpoint_service] Error while getting checkpoint with id {checkpoint_id}: {e}")
        raise ExtractDataError(
            f"Error while getting checkpoint with id {checkpoint_id}: {e}"
        ) from e


def update_checkpoint_progress(conn, checkpoint_id: str, last_row: int) -> None:
    log.info(f"[checkpoint_service] Updating checkpoint {checkpoint_id}")

    if conn is None:
        log.error("[checkpoint_service] Database connection is None")
        raise ExtractDataError("Database connection is None")

    if not checkpoint_id or not checkpoint_id.strip():
        log.error("[checkpoint_service] Checkpoint id is invalid")
        raise ExtractDataError("Checkpoint id is invalid")

    if last_row < 0:
        log.error(f"[checkpoint_service] Invalid last_row for checkpoint {checkpoint_id}: {last_row}")
        raise ExtractDataError(f"Invalid last_row for checkpoint {checkpoint_id}: {last_row}")

    log.info(f"[checkpoint_service] Looking for checkpoint with id: {checkpoint_id}")

    try:
        exist = conn.execute(
            text(f"""
                SELECT status, last_row_extracted
                FROM {CHECKPOINT_TABLE}
                WHERE id = :checkpoint_id
            """),
            {"checkpoint_id": checkpoint_id}
        ).mappings().first()

        if exist is None:
            log.error(f"[checkpoint_service] No checkpoint found with id: {checkpoint_id}")
            raise ExtractDataError(f"No checkpoint found with id: {checkpoint_id}")

        current_status = exist["status"]
        current_last_row = exist["last_row_extracted"]

        log.info(f"[checkpoint_service] Found checkpoint with id {checkpoint_id}")

        if current_status != "RUNNING":
            log.error(
                f"[checkpoint_service] Unable to update checkpoint {checkpoint_id} "
                f"because status is {current_status} instead of RUNNING"
            )
            raise ExtractDataError(
                f"Unable to update checkpoint {checkpoint_id} "
                f"because status is {current_status} instead of RUNNING"
            )

        if last_row < current_last_row:
            log.error(
                f"[checkpoint_service] Invalid progress for checkpoint {checkpoint_id}: "
                f"last_row {last_row} < current_last_row {current_last_row}"
            )
            raise ExtractDataError(
                f"Invalid progress for checkpoint {checkpoint_id}: "
                f"last_row {last_row} < current_last_row {current_last_row}"
            )

        conn.execute(
            text(f"""
                UPDATE {CHECKPOINT_TABLE}
                SET last_row_extracted = :last_row,
                    updated_at = NOW(),
                    last_committed_at = NOW()
                WHERE id = :checkpoint_id
            """),
            {"checkpoint_id": checkpoint_id, "last_row": last_row}
        )

        log.info(
            f"[checkpoint_service] Updated checkpoint with id {checkpoint_id} "
            f"from last_row_extracted {current_last_row} to last_row {last_row}"
        )

    except ExtractDataError:
        raise
    except Exception as e:
        log.error(f"[checkpoint_service] Error while updating checkpoint with id {checkpoint_id}: {e}")
        raise ExtractDataError(
            f"Error while updating checkpoint with id {checkpoint_id}: {e}"
        ) from e


def mark_checkpoint_completed(conn, checkpoint_id: str) -> None:
    log.info(f"[checkpoint_service] Marking checkpoint {checkpoint_id} as COMPLETED")

    if conn is None:
        log.error("[checkpoint_service] Database connection is None")
        raise ExtractDataError("Database connection is None")

    if not checkpoint_id or not checkpoint_id.strip():
        log.error("[checkpoint_service] Checkpoint id is invalid")
        raise ExtractDataError("Checkpoint id is invalid")

    log.info(f"[checkpoint_service] Looking for checkpoint with id: {checkpoint_id}")

    try:
        exist = conn.execute(
            text(f"""
                SELECT status
                FROM {CHECKPOINT_TABLE}
                WHERE id = :checkpoint_id
            """),
            {"checkpoint_id": checkpoint_id}
        ).mappings().first()

        if exist is None:
            log.error(f"[checkpoint_service] No checkpoint found with id: {checkpoint_id}")
            raise ExtractDataError(f"No checkpoint found with id: {checkpoint_id}")

        current_status = exist["status"]
        log.info(f"[checkpoint_service] Found checkpoint with id {checkpoint_id}")

        if current_status != "RUNNING":
            log.error(
                f"[checkpoint_service] Unable to mark checkpoint with id {checkpoint_id} "
                f"from status {current_status} to COMPLETED"
            )
            raise ExtractDataError(
                f"Unable to mark checkpoint with id {checkpoint_id} "
                f"from status {current_status} to COMPLETED"
            )

        conn.execute(
            text(f"""
                UPDATE {CHECKPOINT_TABLE}
                SET status = 'COMPLETED',
                    completed_at = NOW(),
                    updated_at = NOW()
                WHERE id = :checkpoint_id
            """),
            {"checkpoint_id": checkpoint_id}
        )

        log.info(
            f"[checkpoint_service] Marked checkpoint with id {checkpoint_id} "
            f"from {current_status} to COMPLETED"
        )

    except ExtractDataError:
        raise
    except Exception as e:
        log.error(f"[checkpoint_service] Error while getting checkpoint with id {checkpoint_id}: {e}")
        raise ExtractDataError(
            f"Error while getting checkpoint with id {checkpoint_id}: {e}"
        ) from e


def mark_checkpoint_failed(conn, checkpoint_id: str, error_message: str | None = None) -> None:
    log.info(f"[checkpoint_service] Marking checkpoint {checkpoint_id} as FAILED")

    if conn is None:
        log.error("[checkpoint_service] Database connection is None")
        raise ExtractDataError("Database connection is None")

    if not checkpoint_id or not checkpoint_id.strip():
        log.error("[checkpoint_service] Checkpoint id is invalid")
        raise ExtractDataError("Checkpoint id is invalid")

    log.info(f"[checkpoint_service] Looking for checkpoint with id: {checkpoint_id}")

    try:
        exist = conn.execute(
            text(f"""
                SELECT status
                FROM {CHECKPOINT_TABLE}
                WHERE id = :checkpoint_id
            """),
            {"checkpoint_id": checkpoint_id}
        ).mappings().first()

        if exist is None:
            log.error(f"[checkpoint_service] No checkpoint found with id: {checkpoint_id}")
            raise ExtractDataError(f"No checkpoint found with id: {checkpoint_id}")

        current_status = exist["status"]
        log.info(f"[checkpoint_service] Found checkpoint with id {checkpoint_id}")

        if current_status not in ["CREATED", "RUNNING"]:
            log.error(
                f"[checkpoint_service] Unable to mark checkpoint with id {checkpoint_id} "
                f"from status {current_status} to FAILED"
            )
            raise ExtractDataError(
                f"Unable to mark checkpoint with id {checkpoint_id} "
                f"from status {current_status} to FAILED"
            )

        conn.execute(
            text(f"""
                UPDATE {CHECKPOINT_TABLE}
                SET status = 'FAILED',
                    error_message = :error_message,
                    failed_at = NOW(),
                    updated_at = NOW()
                WHERE id = :checkpoint_id
            """),
            {"checkpoint_id": checkpoint_id, "error_message": error_message}
        )

        log.info(
            f"[checkpoint_service] Marked checkpoint with id {checkpoint_id} "
            f"from {current_status} to FAILED"
        )

    except ExtractDataError:
        raise
    except Exception as e:
        log.error(f"[checkpoint_service] Error while getting checkpoint with id {checkpoint_id}: {e}")
        raise ExtractDataError(
            f"Error while getting checkpoint with id {checkpoint_id}: {e}"
        ) from e


def reset_checkpoint(conn, source_file: str) -> None:
    log.info(f"[checkpoint_service] Resetting checkpoint for source file: {source_file}")

    if conn is None:
        log.error("[checkpoint_service] Database connection is None")
        raise ExtractDataError("Database connection is None")

    if not source_file or not source_file.strip():
        log.error("[checkpoint_service] Source file is invalid")
        raise ExtractDataError("Source file is invalid")

    log.info(f"[checkpoint_service] Looking for checkpoint for source file: {source_file}")

    try:
        exist = conn.execute(
            text(f"""
                SELECT id, status
                FROM {CHECKPOINT_TABLE}
                WHERE source_file = :source_file
                ORDER BY created_at DESC
                LIMIT 1
            """),
            {"source_file": source_file}
        ).mappings().first()

        if exist is None:
            log.error(f"[checkpoint_service] No checkpoint found for source file: {source_file}")
            raise ExtractDataError(f"No checkpoint found for source file: {source_file}")

        current_status = exist["status"]
        checkpoint_id = exist["id"]

        log.info(f"[checkpoint_service] Found checkpoint {checkpoint_id} for source file: {source_file}")

        if current_status == "CREATED":
            log.error(
                f"[checkpoint_service] Unable to reset checkpoint {checkpoint_id}: "
                f"already in CREATED status"
            )
            raise ExtractDataError(
                f"Unable to reset checkpoint {checkpoint_id}: already in CREATED status"
            )

        conn.execute(
            text(f"""
                UPDATE {CHECKPOINT_TABLE}
                SET status = 'CREATED',
                    last_row_extracted = 0,
                    error_message = NULL,
                    completed_at = NULL,
                    failed_at = NULL,
                    last_committed_at = NULL,
                    updated_at = NOW()
                WHERE id = :checkpoint_id
            """),
            {"checkpoint_id": str(checkpoint_id)}
        )

        log.info(
            f"[checkpoint_service] Reset checkpoint {checkpoint_id} "
            f"from {current_status} to CREATED"
        )

    except ExtractDataError:
        raise
    except Exception as e:
        log.error(f"[checkpoint_service] Error while resetting checkpoint for source file {source_file}: {e}")
        raise ExtractDataError(
            f"Error while resetting checkpoint for source file {source_file}: {e}"
        ) from e