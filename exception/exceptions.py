import sys
import traceback
from logger.logger import get_logger

log = get_logger(__name__)

class ETLException(Exception):
    """Classe base per tutte le eccezioni della pipeline ETL."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)  # passa il messaggio a Exception


class DatabaseConnectionError(ETLException):
    def __init__(self, reason: str):
        # 'reason' è la causa originale (es. str(e) dal psycopg2)
        super().__init__(f"Database connection error, caused by: {reason}")


class ExtractDataError(ETLException):
    def __init__(self, reason: str):
        super().__init__(f"Extract data error, caused by: {reason}")


class DataCleaningError(ETLException):
    def __init__(self, reason: str):
        super().__init__(f"Data cleaning error, caused by: {reason}")


class LoadDataError(ETLException):
    def __init__(self, reason: str):
        super().__init__(f"Load data error, caused by: {reason}")

def global_exception_handler(exc_type, exc_value, exc_tb):
    # if the program is closed by a keyboard input
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return

    # ETL exceptions management
    if issubclass(exc_type, DatabaseConnectionError):
        log.critical(f"[DB] connection failed: {exc_value}")
    elif issubclass(exc_type, ExtractDataError):
        log.critical(f"[EXTRACT] extraction error: {exc_value}")
    elif issubclass(exc_type, DataCleaningError):
        log.critical(f"[CLEAN] cleaning error: {exc_value}")
    elif issubclass(exc_type, LoadDataError):
        log.critical(f"[LOAD] load data error: {exc_value}")
    elif issubclass(exc_type, ETLException):
        log.critical(f"[ETL] ETL pipeline error: {exc_value}")
    else:
        log.critical(
            "Unknow error: ",
            exc_info=(exc_type, exc_value, exc_tb)
        )

    log.critical("Full traceback: \n" + "" .join(
        traceback.format_exception(exc_type, exc_value, exc_tb)
    ))

sys.excepthook = global_exception_handler