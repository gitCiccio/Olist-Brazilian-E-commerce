class ETLException(Exception):
    pass

class DatabaseConnectionError(ETLException):
    pass

class ExtractDataError(ETLException):
    pass

class DataExtractionError(ETLException):
    pass

class LoadDataError(ETLException):
    pass

"""
import sys
from logger import get_logger

logger = get_logger("global")

def global_exception_handler(exc_type, exc_value, exc_traceback):
    logger.critical(
        "Eccezione non gestita!",
        exc_info=(exc_type, exc_value, exc_traceback)
    )

sys.excepthook = global_exception_handler
"""