import os

import psycopg2
from psycopg2 import connect
from pandas import DataFrame
from dotenv import load_dotenv

from exception import exceptions
from logger import logger as log
from logger.logger import get_logger
from exception import *

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
            self.database_name = os.getenv("DATABASE_NAME")
            self.connection = None
            self.cursor = None
            self.initialized = True

    def connect(self):
        try:
            self.connection = psycopg2.connect(self.database_url)
            self.cursor = self.connection.cursor()
        except psycopg2.OperationalError as e:
            log.error(f"Unable to connect to {self.database_name}, error: {e}")
            raise exceptions.DatabaseConnectionError from e

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