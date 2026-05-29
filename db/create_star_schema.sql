-- CREATE DATABASE olist_star_schema;

\c olist_star_schema;

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- DIMENSIONI
-- ============================================================

CREATE TABLE dim_product (
    surrogate_key       UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    natural_key         VARCHAR(255) NOT NULL UNIQUE,
    category_name_pt    VARCHAR(255),
    category_name_en    VARCHAR(255) NOT NULL
);

CREATE TABLE dim_date (
    surrogate_key   UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    natural_key     INTEGER NOT NULL UNIQUE,
    full_date       DATE    NOT NULL UNIQUE,
    day             SMALLINT NOT NULL,
    month           SMALLINT NOT NULL,
    quarter         SMALLINT NOT NULL,
    year            SMALLINT NOT NULL
);

CREATE TABLE dim_payment (
    surrogate_key       UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_type        VARCHAR(100) NOT NULL
);

CREATE TABLE dim_customer (
    surrogate_key       UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    natural_key         VARCHAR(255) NOT NULL UNIQUE,
    customer_unique_id  VARCHAR(255) NOT NULL,
    customer_city       VARCHAR(255) NOT NULL,
    customer_state      CHAR(2)      NOT NULL
);

CREATE TABLE dim_seller (
    surrogate_key   UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    natural_key     VARCHAR(255) NOT NULL UNIQUE,
    seller_city     VARCHAR(255) NOT NULL,
    seller_state    CHAR(2)      NOT NULL
);

-- ============================================================
-- FATTO
-- ============================================================

CREATE TABLE fact_sell (
    surrogate_key   UUID           PRIMARY KEY DEFAULT gen_random_uuid(),
    natural_key        VARCHAR(255)   NOT NULL UNIQUE,
    order_item_id   SMALLINT       NOT NULL,
    price           DECIMAL(10, 2) NOT NULL,
    freight_value   DECIMAL(10, 2) NOT NULL,
    payment_value   DECIMAL(10, 2) NOT NULL,
    review_score    SMALLINT       CHECK (review_score BETWEEN 1 AND 5),
    delivery_days   SMALLINT,
    product_id      UUID NOT NULL,
    date_id         UUID NOT NULL,
    payment_id      UUID NOT NULL,
    customer_id     UUID NOT NULL,
    seller_id       UUID NOT NULL,

    CONSTRAINT fk_product  FOREIGN KEY (product_id)  REFERENCES dim_product  (surrogate_key),
    CONSTRAINT fk_date     FOREIGN KEY (date_id)     REFERENCES dim_date     (surrogate_key),
    CONSTRAINT fk_payment  FOREIGN KEY (payment_id)  REFERENCES dim_payment  (surrogate_key),
    CONSTRAINT fk_customer FOREIGN KEY (customer_id) REFERENCES dim_customer (surrogate_key),
    CONSTRAINT fk_seller   FOREIGN KEY (seller_id)   REFERENCES dim_seller   (surrogate_key)
);

CREATE TABLE etl_checkpoint (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_file VARCHAR(255) NOT NULL,
    last_row_extracted INT NOT NULL,
    total_rows INT NOT NULL,
    status VARCHAR(50) NOT NULL check ( status in ('RUNNING', 'FAILED', 'COMPLETED')),
    started_at TIMESTAMP DEFAULT NOW() NOT NULL,
    blocked_at TIMESTAMP,
    completed_at TIMESTAMP,
    last_committed_at TIMESTAMP
);

CREATE INDEX idx_etl_checkpoint_source ON etl_checkpoint (source_file, status, started_at DESC);