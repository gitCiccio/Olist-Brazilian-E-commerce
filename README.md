# Olist Brazilian E-commerce Data Warehouse

## Panoramica del Progetto

**Olist** è il più grande marketplace aggregatore del Brasile. Questo progetto consiste nella costruzione di un **Data Warehouse (Star Schema)** partendo dal dataset pubblico di Olist.
L'obiettivo è stato sviluppare una pipeline **ETL (Extract, Transform, Load)** robusta in Python, che ingerisca grandi moli di dati grezzi (CSV), li pulisca in un livello intermedio (Reconciled) e li carichi nel Data Warehouse finale su PostgreSQL, applicando inoltre rigorosi controlli di **Data Quality**.

---

## Architettura della Pipeline ETL

Il progetto implementa un'architettura multi-livello governata da un orchestratore centrale (`main.py`):

1. **Extract (Staging Area)**
   - Lettura dei file CSV grezzi tramite l'utilizzo di chunk in Pandas (per ottimizzare la memoria).
   - Inserimento rapido nello schema `staging`.
   - Meccanismo di Checkpoint per tolleranza agli errori e ripresa delle estrazioni interrotte senza ripartire da zero.

2. **Transform (Reconciled Layer)**
   - Estrazione dallo schema staging.
   - Pulizia, normalizzazione delle stringhe (es. lowercasing, rimozione accenti), conversione coerente dei tipi di dato e gestione dei valori nulli.
   - Salvataggio nello schema `reconciled`, che rappresenta una "Golden Copy" relazionale del database transazionale originale.

3. **Load (Data Warehouse / Star Schema)**
   - Trasformazione dai modelli relazionali a modelli puramente analitici (Star Schema).
   - Generazione di chiavi naturali composite o derivate (`natural_key`).
   - Caricamento nello schema `dwh` organizzato in **Fact tables** (es. `fact_sale_item`) e **Dimension tables** (es. `dim_customer`, `dim_product`).

4. **Data Quality**
   - Modulo dedicato alla validazione post-caricamento nel Data Warehouse.
   - Controlli strict su: completezza (assenza di nulli non previsti), validità dei domini (es. codici stati brasiliani, tipologie pagamenti), unicità delle business keys e limiti numerici.
   - Generazione di report JSON dettagliati per singola tabella e di un file riassuntivo (Data Quality Metrics CSV) nella cartella `exports/` (o all'interno di `data_quality/reports`).

---

## Cosa Contiene il Dataset

Il dataset originale raccoglie oltre **100.000 ordini reali** effettuati tra il **2016 e il 2018** su marketplace partner di Olist in Brasile. Offre diverse prospettive di analisi:

- **Clienti**: distribuiti prevalentemente nella zona sud-orientale (es. São Paulo).
- **Venditori**: Piccole e medie imprese brasiliane (PMI).
- **Ordini e Pagamenti**: Dallo stato della consegna (approvato, spedito, ecc.) al metodo di pagamento (carta di credito, boleto, voucher).
- **Prodotti**: Catalogo di 71 categorie (con dizionario di traduzione inglese-portoghese).
- **Recensioni**: Punteggio (1-5 stelle) e commenti testuali lasciati dai consumatori post-vendita.

---

## Modello Dati

Il progetto crea dinamicamente tre schemi principali sul database PostgreSQL.

### 1. Schema Reconciled (Relazionale)
Rispecchia la struttura originale e normalizzata del dataset:
- **Anagrafiche:** `customers`, `sellers`, `products`, `category_translation`, `geolocation`
- **Dati Transazionali:** `orders` (centrale), `order_items`, `order_payments`, `order_reviews`

### 2. Schema DWH (Star Schema)
Progettato e denormalizzato per massimizzare le performance di query analitiche e dashboarding:
- **Dimensioni**: `dim_customer`, `dim_seller`, `dim_product`, `dim_payment`, `dim_date`
- **Fatti**: `fact_order` (misurazioni aggregate sull'ordine), `fact_sale_item` (dettaglio granulare delle singole vendite)

---

## Stack Tecnologico

| Componente | Tecnologia |
|---|---|
| **Database** | PostgreSQL 16 (Docker Multi-Schema: staging, reconciled, dwh) |
| **Connessione DB** | SQLAlchemy (Core per l'Engine) + psycopg2-binary |
| **Linguaggio** | Python 3.11 |
| **Data Processing** | Pandas |
| **Gestione Dipendenze** | pip + requirements.txt |
| **Configurazione** | python-dotenv (.env) |
| **IDE** | PyCharm |
| **Containerizzazione** | Docker + Docker Compose |

---

## Struttura del Progetto

```text
brazilian_e_commerce_dw/
├── docker-compose.yml         # Configurazione Docker (PostgreSQL multi-schema)
├── .env                       # Credenziali database (non committato)
├── .gitignore
├── requirements.txt           # Dipendenze del progetto
├── main.py                    # Entry point (Orchestratore) principale della pipeline ETL
├── db/                        # Script SQL per la creazione dei DB layer
│   ├── staging_area.sql       
│   ├── reconciled_layer.sql   
│   └── create_star_schema.sql 
├── data/
│   └── raw/                   # Cartella destinata ai CSV originali Olist (ignorati da Git)
├── etl/
│   ├── sources.py             # Definizione metadati (tipi di colonna e file mapping)
│   └── scripts/               # Core Logics della pipeline suddiviso in fasi
│       ├── extract/           # Lettura CSV -> Staging (Chunking + Checkpoints)
│       ├── transform/         # Pulizia Dati -> Reconciled
│       ├── load/              # Popolamento Dimensioni e Fatti -> Star Schema
│       └── data_quality/      # Validazioni post-caricamento e Reportistica DQ
├── exports/                   # Eventuali report finali o output esportati
├── exception/                 # Gestori custom per le eccezioni ETL
├── logger/                    # Gestore centralizzato per i file di log
└── project_documentation/     # Documentazione architetturale estesa e note di progetto
```

---

## Come Eseguire il Progetto

1. **Popolare i Dati Raw:**
   Scaricare i CSV dal dataset pubblico di Olist e posizionarli all'interno della cartella `data/raw/`.

2. **Avviare il Database:**
   Assicurati di avere Docker e Docker Compose installati, quindi da terminale:
   ```bash
   docker-compose up -d
   ```

3. **Configurare l'Ambiente Python:**
   ```bash
   python -m venv .venv
   
   # Su Windows:
   .venv\Scripts\activate
   # Su Linux/Mac:
   source .venv/bin/activate
   
   pip install -r requirements.txt
   ```

4. **Configurare le Variabili d'Ambiente:**
   Crea un file `.env` nella root prendendo a modello le tue credenziali (coerenti con `docker-compose.yml`). Esempio:
   ```env
   DB_HOST=localhost
   DB_PORT=5433
   DB_NAME=postgres
   DB_USER=postgres
   DB_PASS=password
   ```

5. **Avviare la Pipeline ETL:**
   Basta eseguire l'orchestratore. Il progetto lancerà automaticamente in sequenza la creazione delle tabelle SQL, le fasi di Extract, Transform, Load e la fase di Data Quality.
   ```bash
   python main.py
   ```
   *Nota: L'esecuzione completa potrebbe richiedere alcuni minuti a causa dell'ingente volume di dati (es. oltre 1 milione di righe per la tabella geolocation).*