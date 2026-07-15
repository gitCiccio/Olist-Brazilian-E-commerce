import logging
import sys


class _Colors:
    RESET = "\033[0m"
    DEBUG = "\033[36m"  # Cyan
    INFO = "\033[32m"  # Verde
    WARNING = "\033[33m"  # Giallo
    ERROR = "\033[31m"  # Rosso
    CRITICAL = "\033[1;35m"  # Magenta bold

class _ColoredFormatter(logging.Formatter):
    LEVEL_COLORS = {
        logging.DEBUG: _Colors.DEBUG,
        logging.INFO: _Colors.INFO,
        logging.WARNING: _Colors.WARNING,
        logging.ERROR: _Colors.ERROR,
        logging.CRITICAL: _Colors.CRITICAL,
    }

    def format(self, record: logging.LogRecord) -> str:
        """
        Formatta il log record inserendo i codici ANSI per i colori 
        in base al livello (es. Verde per INFO, Rosso per ERROR).
        """
        color = self.LEVEL_COLORS.get(record.levelno, _Colors.RESET)
        record.levelname = f"{color}{record.levelname:<8}{_Colors.RESET}"
        return super().format(record)


class AppLogger:
    _FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    _DATE_FMT = "%Y-%m-%d %H:%M:%S"

    def __init__(
        self,
        name: str,
        level: int = logging.DEBUG,
        log_file: str | None = "app.log",
    ) -> None:
        """
        Inizializza un logger personalizzato.
        Crea due handler: uno per la console (con output colorato) 
        e uno per un file (testo normale).
        """
        self._logger = logging.getLogger(name)

        # Evita di aggiungere handler duplicati
        if self._logger.handlers:
            return

        self._logger.setLevel(level)

        # Handler console con colori
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(_ColoredFormatter(self._FORMAT, self._DATE_FMT))
        self._logger.addHandler(console_handler)

        # Handler file senza colori (i codici ANSI sporcherebbero il file)
        if log_file:
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(
                logging.Formatter(self._FORMAT, self._DATE_FMT)
            )
            self._logger.addHandler(file_handler)

    # Espone i metodi standard
    def debug(self, msg: str, *args, **kwargs) -> None:
        """Stampa un messaggio a livello DEBUG, utile per diagnosticare in fase di sviluppo."""
        self._logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs) -> None:
        """Stampa un messaggio a livello INFO, usato per tracciare il normale flusso esecutivo."""
        self._logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs) -> None:
        """Stampa un messaggio a livello WARNING, indica situazioni anomale non bloccanti."""
        self._logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs) -> None:
        """Stampa un messaggio a livello ERROR, indica il fallimento di un'operazione specifica."""
        self._logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs) -> None:
        """Stampa un messaggio a livello CRITICAL, usato per errori gravissimi o crash globali."""
        self._logger.critical(msg, *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs) -> None:
        """Logga un errore includendo automaticamente lo stack trace."""
        self._logger.exception(msg, *args, **kwargs)