import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

def export_dw_to_csv():
    # Carica le variabili d'ambiente dal file .env
    load_dotenv()
    
    # Recupera le credenziali del database
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5433")
    dw_db = os.getenv("POSTGRES_DW_DB", "olist_dw")
    
    # Crea la cartella 'exports' se non esiste
    export_dir = "exports"
    os.makedirs(export_dir, exist_ok=True)
    
    # Connessione al database Data Warehouse
    print(f"[*] Connessione al database DW: {dw_db} (Host: {host}:{port})")
    engine_dw = create_engine(
        f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dw_db}"
    )
    
    # Tabelle dello Star Schema da esportare
    tables = [
        "dim_product",
        "dim_date",
        "dim_payment",
        "dim_customer",
        "dim_seller",
        "fact_sale_item"
    ]
    
    print("[*] Inizio esportazione dei dati...")
    try:
        for table in tables:
            print(f"    -> Estrazione della tabella: {table}...")
            query = f"SELECT * FROM {table}"
            df = pd.read_sql(query, engine_dw)
            
            output_file = os.path.join(export_dir, f"{table}.csv")
            df.to_csv(output_file, index=False, encoding='utf-8')
            print(f"       Salvato {len(df)} righe in {output_file}")
            
        print("[*] Esportazione completata con successo!")
        
    except Exception as e:
        print(f"[!] Errore durante l'esportazione: {e}")

if __name__ == "__main__":
    export_dw_to_csv()
