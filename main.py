from db import *
from etl.db import db_connection


def main():
    db = db_connection()

    with db as connection:
        connection.execute("SELECT version()").fetch_one()