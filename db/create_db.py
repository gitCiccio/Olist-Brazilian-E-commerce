import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from models import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def create_database():
    print(f"Connessione a: {DATABASE_URL}")
    engine = create_engine(str(DATABASE_URL), echo=False)

    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        print(f"✅ Connesso! {result.fetchone()[0]}\n")
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS reconciled"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS warehouse"))
        conn.commit()
        print("✅ Schemi creati: reconciled, warehouse\n")

    Base.metadata.create_all(engine)
    print("✅ Tabelle create:")
    for t in Base.metadata.tables.keys():
        print(f"   → {t}")

if __name__ == "__main__":
    create_database()