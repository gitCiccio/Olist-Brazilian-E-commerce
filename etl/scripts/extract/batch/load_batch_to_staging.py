import pandas as pd
from sqlalchemy.engine import Connection

from logger.logger import AppLogger
from exception.exceptions import ExtractDataError

log = AppLogger(name="staging_loader.extract", log_file="staging_loader.log")

def load_to_staging(conn: Connection, chunk: pd.DataFrame, target_table: str) -> None:
    log.info(
        f"[staging_loader] Loading batch into {target_table} "
        f"with {len(chunk)} rows"
    )

    if conn is None:
        log.error("[staging_loader] Database connection is None")
        raise ExtractDataError("Database connection is None")

    if chunk is None:
        log.error(f"[staging_loader] Chunk is None for target table: {target_table}")
        raise ExtractDataError(f"Chunk is None for target table: {target_table}")

    if chunk.empty:
        log.error(f"[staging_loader] Chunk is empty for target table: {target_table}")
        raise ExtractDataError(f"Chunk is empty for target table: {target_table}")

    if not target_table or not target_table.strip():
        log.error("[staging_loader] Target table is invalid")
        raise ExtractDataError("Target table is invalid")

    try:
        chunk.to_sql(
            name=target_table,
            con=conn,
            if_exists="append",
            index=False
        )

        log.info(
            f"[staging_loader] Loaded {len(chunk)} rows into {target_table}"
        )

    except Exception as e:
        log.error(
            f"[staging_loader] Error while loading batch into {target_table}: {e}"
        )
        raise ExtractDataError(
            f"Error while loading batch into {target_table}: {e}"
        ) from e