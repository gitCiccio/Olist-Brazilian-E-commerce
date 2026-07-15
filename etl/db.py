import os
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_values
from exception.exceptions import DatabaseConnectionError
from logger.logger import AppLogger

log = AppLogger(name="db.extract", log_file="db.log")

class db_connection:

    # mettiamo l'istanza come una variabile privata
    _instance = None

    def __new__(cls):
        """
        Garantisce che la classe db_connection sia un Singleton.
        Crea e restituisce un'unica istanza condivisa per l'intera applicazione.
        """
        if cls._instance is None:
            log.info(f"Creating new instance of {cls.__name__}")
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Inizializza l'istanza caricando le variabili d'ambiente necessarie (URL e Nome del DB).
        Imposta il flag `initialized` per evitare di ripetere l'operazione nelle chiamate successive.
        """
        if not hasattr(self, 'initialized'):
            load_dotenv()
            self.database_url = os.getenv("DATABASE_URL")
            self.database_name = os.getenv("DATABASE_NAME")
            self.connection = None
            self.cursor = None
            self.initialized = True

    def connect(self):
        """
        Apre una connessione verso il database Postgres e inizializza un cursore 
        (RealDictCursor) che restituisce i risultati sotto forma di dizionari.
        Se la connessione è già attiva, non fa nulla.
        """
        if self.connection is not None and not self.connection.closed:
            log.debug(f"Connection to {self.database_url} already opened")
            return self
        try:
            log.info(f"Connecting to {self.database_url}")
            self.connection = psycopg2.connect(self.database_url)
            self.cursor = self.connection.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor
            )
            log.info(f"Successfully connected to {self.database_url}")
            return self
        except psycopg2.OperationalError as e:
            log.error(f"Unable to connect to {self.database_name}: {e}")
            raise DatabaseConnectionError(f"Connection failed: {e}") from e

    def disconnect(self):
        """
        Chiude in modo sicuro il cursore e la connessione al database, 
        liberando le risorse di rete e di sistema.
        """
        try:
            if self.cursor and not self.cursor.closed:
                self.cursor.close()
            if self.connection and not self.connection.closed:
                self.connection.close()
                log.info(f"Successfully disconnected from {self.database_url}")
        except psycopg2.OperationalError as e:
            log.error(f"Unable to disconnect from {self.database_name}: {e}")
            # Aggiungere eccezione per disconettersi dal db
        finally:
            self.connection = None
            self.cursor = None

    # context manager
    def __enter__(self):
        """
        Fornisce il supporto al Context Manager (sintassi `with db_connection() as db:`).
        Invoca automaticamente `connect()`.
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Chiusura del Context Manager.
        Esegue la commit della transazione se non ci sono stati errori.
        In caso contrario, esegue il rollback. Alla fine si disconnette sempre.
        """
        if exc_type is None:
            self.commit()
        else:
            log.warning(f"Exception caught ({exc_type.__name__}), rolling back.")
            self.rollback()
        self.disconnect()
        return False

    # SQL operations

    def execute(self, query, params=None):
        """
        Esegue una singola istruzione SQL (es. SELECT, INSERT, UPDATE, DELETE).
        Il parametro `params` consente di passare variabili in modo sicuro per 
        prevenire la SQL injection.
        """
        try:
            self.cursor.execute(query, params)
            return self
        except psycopg2.OperationalError as e:
            log.error(f"Query failed: {e}\nQuery: {query}\nParams: {params}")
            raise

    def execute_batch(self, query: str, data: list[tuple], page_size: int = 1000):
        """
        Inserimento bulk efficiente con execute_values (psycopg2).
        Usato nel load.py per i batch ETL.

        Esempio query:
          INSERT INTO dim_product (natural_key, category_name_en)
          VALUES %s
          ON CONFLICT (natural_key) DO UPDATE SET ...
        """
        try:
            execute_values(self.cursor, query, data, page_size=page_size)
            return self
        except psycopg2.Error as e:
            log.error(f"Batch execute failed: {e}")
            raise


    def fetch_one(self) -> dict | None:
        """
        Recupera il primo record dal risultato dell'ultima query eseguita.
        Restituisce un dizionario le cui chiavi sono i nomi delle colonne.
        """
        return self.cursor.fetchone()

    def fetch_all(self):
        """
        Recupera tutti i record prodotti dall'ultima query eseguita.
        Restituisce una lista di dizionari.
        """
        return self.cursor.fetchall()

    def commit(self):
        """
        Conferma la transazione corrente, salvando permanentemente 
        le modifiche apportate sul database.
        """
        try:
            self.connection.commit()
            log.debug("Transaction committed.")
        except psycopg2.Error as e:
            log.error(f"Commit failed: {e}")
            raise

    def rollback(self):
        """
        Annulla la transazione corrente. Qualsiasi modifica non sottoposta 
        a commit viene scartata per mantenere la coerenza dei dati.
        """
        try:
            self.connection.rollback()
            log.warning("Transaction rolled back.")
        except psycopg2.Error as e:
            log.error(f"Rollback failed: {e}")
            raise