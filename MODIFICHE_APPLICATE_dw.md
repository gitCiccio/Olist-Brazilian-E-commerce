# Modifiche applicate e decisioni di modifica

## Modifiche già applicate o definite con chiarezza

### 1. `dim_customer`

La `dim_customer` è stata ripensata per usare `customer_unique_id` come `natural_key`, perché nel dataset Olist è questo l'identificatore che rappresenta il cliente reale e non il singolo ordine.[web:6]
La funzione `transform_dim_customers` è stata adeguata per deduplicare su `customer_unique_id` invece che su `customer_id`.[web:6]
Sono state inoltre aggiunte le normalizzazioni su città e stato e la derivazione dell'attributo `customer_region` a partire da `customer_state`.[file:3]

### 2. Gerarchia geografica cliente

La dimensione cliente ora è pensata con una gerarchia geografica completa:

- `customer_region`
- `customer_state`
- `customer_city`

Questa scelta è stata fatta per supportare navigazione analitica, aggregazioni geografiche e drill-down nelle dashboard.[file:3]

### 3. `dim_seller`

Anche la `dim_seller` è stata riallineata alla stessa logica della dimensione cliente, con aggiunta dell'attributo `seller_region` derivato da `seller_state`.[file:3]
La funzione `transform_dim_sellers` è stata verificata e corretta nella parte di derivazione della regione, evitando di sovrascrivere il valore mappato con lo stato originale.[file:3]

### 4. Predisposizione SCD

Nel DDL di `dim_customer` e `dim_seller` sono stati previsti i campi:

- `valid_from`
- `valid_to`
- `is_current`

Questi campi preparano le dimensioni a una gestione compatibile con SCD Type 2, anche se il dataset statico Olist non richiede davvero un tracciamento storico incrementale completo.[web:41][web:50][web:6]
Per rendere questa scelta possibile, è stato anche deciso di togliere il vincolo `UNIQUE` dalla `natural_key` delle dimensioni coinvolte.[web:41]

## Correzioni individuate ma da completare

### 1. Coerenza tra `dim_customer` e fact table

Anche se `dim_customer` ora usa `customer_unique_id`, alcuni passaggi del flusso ETL portano ancora avanti `customer_id` fino alla fact table.[web:6]
Questa incoerenza deve essere risolta, altrimenti il join tra fact e `dim_customer` rischia di produrre chiavi esterne mancanti o errate.[web:6][file:3]

### 2. `transform_dim_payment`

È stato identificato un problema logico tra `PAYMENT_MAPPING` e `VALID_PAYMENT_TYPES`: mappare `boleto -> ticket` e poi validare contro un insieme che non contiene `ticket` porta quei record a diventare `not_defined`.[web:6]
La soluzione è scegliere una sola convenzione e mantenerla coerente in tutto il progetto.[web:6]

### 3. `transform_review_info`

La trasformazione delle review calcola una media con un decimale, ma il DDL della fact usa `review_score SMALLINT`.[file:3]
Questa discrepanza deve essere risolta decidendo se mantenere la precisione decimale nel DW oppure arrotondare il valore prima del load.[file:3]

### 4. `payment_value` nella fact

È stato confermato che `payment_value` non è coerente con una fact a granularità `order_item`, perché rappresenta il totale ordine e non il totale del singolo item.[web:43][web:6]
Questa misura deve essere rimossa, ridefinita o ripartita proporzionalmente se si vuole mantenerla senza introdurre errori di aggregazione.[web:43]

## DDL aggiornato a livello concettuale

Le due dimensioni principali sono state ripensate in questa forma logica.

```sql
CREATE TABLE dim_customer (
    surrogate_key   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    natural_key     VARCHAR(255) NOT NULL,
    customer_region VARCHAR(50) NOT NULL,
    customer_city   VARCHAR(255) NOT NULL,
    customer_state  CHAR(2) NOT NULL,
    valid_from      DATE NOT NULL DEFAULT CURRENT_DATE,
    valid_to        DATE,
    is_current      BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE dim_seller (
    surrogate_key   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    natural_key     VARCHAR(255) NOT NULL,
    seller_region   VARCHAR(50) NOT NULL,
    seller_city     VARCHAR(255) NOT NULL,
    seller_state    CHAR(2) NOT NULL,
    valid_from      DATE NOT NULL DEFAULT CURRENT_DATE,
    valid_to        DATE,
    is_current      BOOLEAN NOT NULL DEFAULT TRUE
);
```

## Mapping geografico introdotto

Per derivare `customer_region` e `seller_region` è stato definito un mapping tra sigla dello stato brasiliano e macro-regione geografica, così da trasformare gli stati in un livello superiore di aggregazione utile alla business intelligence.[file:3]
Questo consente analisi del tipo regione -> stato -> città, particolarmente utili in Tableau o in strumenti OLAP.[file:3]

## Prossimi interventi consigliati

L'ordine di lavoro suggerito dopo queste modifiche è il seguente:

1. allineare `transform_fact_table` e `load_fact_table` al nuovo uso di `customer_unique_id`;[web:6]
2. decidere definitivamente la strategia su `payment_value`;[web:43]
3. correggere la dimensione pagamenti mantenendo coerenza tra mapping e valori ammessi;[web:6]
4. arricchire `dim_date` con attributi come `day_of_week`, `week_of_year` e `is_weekend`;[file:3]
5. introdurre il reconciled layer come livello intermedio stabile tra staging e DW.[file:3]
