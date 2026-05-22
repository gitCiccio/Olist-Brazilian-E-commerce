import os
from psycopg2 import connect
from pandas import DataFrame
from dotenv import load_dotenv
from logger import logger as log
from logger.logger import get_logger

log = get_logger(__name__)

class db_connection:

    # mettiamo l'istanza come una variabile privata
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            log.info("creating new instance")
            cls._instance = object.__new__(cls)
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            load_dotenv()
            self.database_url = os.getenv("DATABASE_URL")
            self.connection = None
            self.cursor = None
            self.initialized = True

    def connect(self):
        pass

    def disconnect(self):
        pass

    def execute(self, query, params=None):
        pass

    def fetch_one(self):
        pass

    def fetch_all(self):
        pass

    def commit(self):
        pass

    def rollback(self):
        pass