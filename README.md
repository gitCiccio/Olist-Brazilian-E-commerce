# Olist Brazilian E-commerce

## Panoramica del Progetto

**Olist** è il più grande marketplace aggregatore del Brasile. Non vende prodotti propri — fa da intermediario tra piccole e medie imprese brasiliane (SMB) e i grandi marketplace come Mercado Livre e Amazon Brasil. Con un unico contratto, un venditore ottiene visibilità su tutte le piattaforme contemporaneamente.

***

## Cosa Contiene il Dataset

Il dataset raccoglie **100.000 ordini reali** effettuati tra il **2016 e il 2018** su marketplace brasiliani. Ogni ordine può essere analizzato da diverse angolazioni:

- **Stato dell'ordine** — approvato, spedito, consegnato, cancellato
- **Prezzi e spese di spedizione** — valore del prodotto e costo logistico
- **Metodi di pagamento** — carta di credito, boleto, voucher, debito
- **Localizzazione del cliente** — stato e città di destinazione
- **Attributi del prodotto** — categoria, peso, dimensioni
- **Recensioni dei clienti** — punteggio da 1 a 5 stelle e commento testuale

***

## Clienti

I clienti sono i **consumatori finali brasiliani** che acquistano online tramite i marketplace partner di Olist.

- La maggioranza si trova nello stato di **São Paulo (SP)** — oltre 40.000 ordini tra 2016 e 2018, anche perché Olist ha sede lì
- La distribuzione geografica è concentrata nella **zona sud-orientale del Brasile** (SP, RJ, MG)
- Spesa media per ordine: circa **125 Real brasiliani** (~25€)

***

## Venditori

I venditori sono **piccole e medie imprese brasiliane (PMI)** che utilizzano Olist come vetrina per raggiungere più piattaforme.

- Oltre **45.000 venditori attivi** sulla piattaforma
- Non gestiscono la logistica in autonomia — si affidano ai **partner logistici di Olist**
- Concentrati prevalentemente negli stati di **SP, PR, MG**
- Vendono prodotti fisici appartenenti a qualsiasi categoria

***

## Prodotti e Categorie

Il catalogo copre **71 categorie** di prodotti fisici, tutte con nome originale in portoghese tradotto in inglese tramite la tabella `category_translation`.

| Categoria (EN) | Categoria (PT) | Caratteristica |
|---|---|---|
| Bed, Bath & Table | cama_mesa_banho | La più venduta in volume |
| Beauty & Health | beleza_saude | Alto volume di ordini |
| Sports & Leisure | esporte_lazer | Molto popolare |
| Computers & Accessories | informatica_acessorios | Alto valore medio per ordine |
| Furniture & Decor | moveis_decoracao | Alto valore medio per ordine |
| Housewares | utilidades_domesticas | Alto volume di ordini |

***

## Aree Geografiche

Il dataset copre **tutti i 27 stati brasiliani**, con concentrazione nelle aree:

| Area | Stati | Note |
|---|---|---|
| **Sud-est** | SP, RJ, MG, ES | Zona più ricca, maggioranza degli ordini e venditori |
| **Sud** | PR, RS, SC | Alta presenza di venditori |
| **Nord-est** | BA, CE, PE | Crescita rapida nel periodo 2016–2018 |
| **Nord / Centro-ovest** | AM, GO, DF... | Presenza ridotta ma in crescita |

La tabella `geolocation` collega ogni **CEP (codice postale)** a coordinate geografiche (lat/lng), città e stato.

***

## Pagamenti

Ogni ordine può essere pagato con **uno o più metodi** combinati (es. parte con carta, parte con voucher):

- **Carta di credito** (`credit_card`) — metodo dominante, fino a 12 rate mensili
- **Boleto bancário** (`boleto`) — equivalente brasiliano del pagamento in contanti/bonifico
- **Voucher** (`voucher`) — buoni sconto applicati all'ordine
- **Carta di debito** (`debit_card`) — pagamento immediato

***

## Recensioni

Dopo ogni consegna, il cliente riceve una notifica e può lasciare una recensione:

- **Punteggio** da 1 a 5 stelle (`review_score`)
- **Titolo** e **commento testuale** opzionali, in portoghese
- **Data di creazione** della recensione e **data di risposta** del venditore
- Prodotti con tempi di consegna rispettati tendono ad avere punteggi mediamente più alti

***

## Schema del Database Riconciliato

Il database riconciliato è composto da **9 tabelle** che rispecchiano fedelmente la struttura del dataset originale:

| Tabella | Descrizione | Righe (approx.) |
|---|---|---|
| `customers` | Clienti che hanno effettuato ordini | ~99.000 |
| `sellers` | Venditori attivi sulla piattaforma | ~3.000 |
| `products` | Catalogo prodotti | ~33.000 |
| `category_translation` | Dizionario categorie PT → EN | 71 |
| `geolocation` | Coordinate geografiche per CAP | ~1.000.000 |
| `orders` | Ordini effettuati (tabella centrale) | ~100.000 |
| `order_items` | Articoli per ogni ordine | ~115.000 |
| `order_payments` | Pagamenti per ogni ordine | ~104.000 |
| `order_reviews` | Recensioni dei clienti | ~99.000 |

***

## Stack Tecnologico

| Componente | Tecnologia |
|---|---|
| Database | PostgreSQL 16 (Docker) |
| ORM | SQLAlchemy 2.x |
| Linguaggio | Python 3.11 |
| Gestione dipendenze | pip + requirements.txt |
| Configurazione | python-dotenv (.env) |
| IDE | PyCharm |
| Containerizzazione | Docker + Docker Compose |

***

## Struttura del Progetto

```
dw_exam_project/
├── docker-compose.yml         # Configurazione Docker (PostgreSQL)
├── .env                       # Credenziali database (non committare!)
├── .gitignore
├── requirements.txt
├── db/
│   ├── __init__.py
│   ├── models.py              # Tabelle SQLAlchemy (Fase 1.3)
│   └── create_db.py           # Script creazione DB
├── data/
│   └── raw/                   # CSV originali Olist
├── etl/
│   └── load_raw.py            # Caricamento CSV → DB (Fase 2.1)
└── cleaning/
    └── data_quality.py        # Data cleaning (Fase 2.2)
```