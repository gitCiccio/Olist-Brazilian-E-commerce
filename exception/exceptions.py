import sys
import traceback
from types import TracebackType

from logger.logger import AppLogger

log = AppLogger(name="exception.extract", log_file="exceptions.log")

class ETLException(Exception):
    """Classe base per tutte le eccezioni della pipeline ETL."""
    def __init__(self, message: str, cause: Exception | None = None):
        self.message = message
        self.cause = cause
        super().__init__(self.message)
        self.__cause__ = cause


class DatabaseConnectionError(ETLException):
    def __init__(self, reason: str, cause: Exception | None = None):
        """
        Inizializza l'errore di connessione al database.
        :param reason: Stringa che descrive la causa scatenante (es. errore psycopg2).
        """
        # 'reason' è la causa originale (es. str(e) dal psycopg2)
        super().__init__(f"Database connection error, caused by: {reason}", cause)


class ExtractDataError(ETLException):
    def __init__(self, reason: str,  cause: Exception | None = None):
        """
        Inizializza l'errore che si verifica durante la fase di Extract.
        """
        super().__init__(f"Extract data error, caused by: {reason}", cause)


class DataCleaningError(ETLException):
    def __init__(self, reason: str,  cause: Exception | None = None):
        """
        Inizializza l'errore che si verifica durante la fase di pulizia dei dati (Transform).
        """
        super().__init__(f"Data cleaning error, caused by: {reason}", cause)


class LoadDataError(ETLException):
    def __init__(self, reason: str,  cause: Exception | None = None):
        """
        Inizializza l'errore che si verifica durante la fase di Load (caricamento finale).
        """
        super().__init__(f"Load data error, caused by: {reason}", cause)

_PREFIX_MAP = {
    DatabaseConnectionError: "[DB]",
    ExtractDataError:        "[EXTRACT]",
    DataCleaningError:       "[CLEAN]",
    LoadDataError:           "[LOAD]",
    ETLException:            "[ETL]",
}

def global_exception_handler(
    exc_type: type,
    exc_value: BaseException,
    exc_tb: TracebackType | None = None,
) -> None:
    """
    Gestore globale delle eccezioni non catturate nell'applicazione.
    Ignora `KeyboardInterrupt` per permettere l'uscita pulita con Ctrl+C.
    Registra a livello 'CRITICAL' qualsiasi altra eccezione, applicando un 
    prefisso in base al tipo di eccezione definita.
    """
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return

    prefix = next(
        (p for cls, p in _PREFIX_MAP.items() if issubclass(exc_type, cls)),
        "[UNKNOWN]",
    )

    log.critical(
        "%s %s",
        prefix,
        exc_value,
        exc_info=(exc_type, exc_value, exc_tb),
    )

sys.excepthook = global_exception_handler