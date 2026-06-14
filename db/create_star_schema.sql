\c olist_star_schema;

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- DIMENSIONI
-- ============================================================

CREATE TABLE dim_product (
    surrogate_key       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    natural_key         VARCHAR(255) NOT NULL UNIQUE,
    category_name_en    VARCHAR(255) NOT NULL
);

CREATE TABLE dim_date (
    surrogate_key       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    natural_key         INTEGER NOT NULL UNIQUE,
    full_date           DATE NOT NULL UNIQUE,
    day                 SMALLINT NOT NULL,
    month               SMALLINT NOT NULL,
    quarter             SMALLINT NOT NULL,
    year                SMALLINT NOT NULL,
    day_of_week         SMALLINT NOT NULL,
    week_of_year        SMALLINT NOT NULL,
    is_weekend          BOOLEAN NOT NULL
);

CREATE TABLE dim_payment (
    surrogate_key           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_type            VARCHAR(100) NOT NULL,
    payment_installments    SMALLINT NOT NULL,
    CONSTRAINT uq_dim_payment UNIQUE (payment_type, payment_installments)
);

CREATE TABLE dim_customer (
    surrogate_key       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    natural_key         VARCHAR(255) NOT NULL,           -- customer_unique_id
    customer_region     VARCHAR(50) NOT NULL,
    customer_city       VARCHAR(255) NOT NULL,
    customer_state      CHAR(2) NOT NULL,
    valid_from          DATE NOT NULL DEFAULT CURRENT_DATE,
    valid_to            DATE,
    is_current          BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE dim_seller (
    surrogate_key       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    natural_key         VARCHAR(255) NOT NULL,           -- seller_id
    seller_region       VARCHAR(50) NOT NULL,
    seller_city         VARCHAR(255) NOT NULL,
    seller_state        CHAR(2) NOT NULL,
    valid_from          DATE NOT NULL DEFAULT CURRENT_DATE,
    valid_to            DATE,
    is_current          BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE fact_sale_item (
    surrogate_key               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    natural_key                 VARCHAR(255) NOT NULL UNIQUE, -- order_id || '-' || order_item_id
    order_id                    VARCHAR(255) NOT NULL,
    order_item_id               SMALLINT NOT NULL,
    order_status                VARCHAR(50) NOT NULL,
    item_count                  SMALLINT NOT NULL DEFAULT 1,
    price                       DECIMAL(10,2) NOT NULL,
    freight_value               DECIMAL(10,2) NOT NULL,
    delivery_days               SMALLINT,

    product_key                 UUID NOT NULL,
    customer_key                UUID NOT NULL,
    seller_key                  UUID NOT NULL,
    payment_key                 UUID,
    purchase_date_key           UUID NOT NULL,
    shipping_limit_date_key     UUID,
    delivered_date_key          UUID,
    estimated_delivery_date_key UUID,

    CONSTRAINT fk_product                  FOREIGN KEY (product_key) REFERENCES dim_product(surrogate_key),
    CONSTRAINT fk_customer                 FOREIGN KEY (customer_key) REFERENCES dim_customer(surrogate_key),
    CONSTRAINT fk_seller                   FOREIGN KEY (seller_key) REFERENCES dim_seller(surrogate_key),
    CONSTRAINT fk_payment                  FOREIGN KEY (payment_key) REFERENCES dim_payment(surrogate_key),
    CONSTRAINT fk_purchase_date            FOREIGN KEY (purchase_date_key) REFERENCES dim_date(surrogate_key),
    CONSTRAINT fk_shipping_limit_date      FOREIGN KEY (shipping_limit_date_key) REFERENCES dim_date(surrogate_key),
    CONSTRAINT fk_delivered_date           FOREIGN KEY (delivered_date_key) REFERENCES dim_date(surrogate_key),
    CONSTRAINT fk_estimated_delivery_date  FOREIGN KEY (estimated_delivery_date_key) REFERENCES dim_date(surrogate_key)
);

-- Fact secondaria opzionale, ma consigliata per misure a livello ordine
CREATE TABLE fact_order (
    surrogate_key               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    natural_key                 VARCHAR(255) NOT NULL UNIQUE, -- order_id
    order_id                    VARCHAR(255) NOT NULL,
    order_status                VARCHAR(50) NOT NULL,
    payment_value               DECIMAL(10,2) NOT NULL,
    review_score                DECIMAL(3,1),
    delivery_days               SMALLINT,

    customer_key                UUID NOT NULL,
    payment_key                 UUID,
    purchase_date_key           UUID NOT NULL,
    delivered_date_key          UUID,
    estimated_delivery_date_key UUID,

    CONSTRAINT fk_order_customer                FOREIGN KEY (customer_key) REFERENCES dim_customer(surrogate_key),
    CONSTRAINT fk_order_payment                 FOREIGN KEY (payment_key) REFERENCES dim_payment(surrogate_key),
    CONSTRAINT fk_order_purchase_date           FOREIGN KEY (purchase_date_key) REFERENCES dim_date(surrogate_key),
    CONSTRAINT fk_order_delivered_date          FOREIGN KEY (delivered_date_key) REFERENCES dim_date(surrogate_key),
    CONSTRAINT fk_order_estimated_delivery_date FOREIGN KEY (estimated_delivery_date_key) REFERENCES dim_date(surrogate_key)
);

CREATE TABLE etl_checkpoint (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_file VARCHAR(255) NOT NULL,
    last_row_extracted INT NOT NULL,
    total_rows INT NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('CREATED', 'RUNNING', 'FAILED', 'COMPLETED')),
    error_message TEXT,
    created_at TIMESTAMP NOT NULL,
    started_at TIMESTAMP,
    updated_at TIMESTAMP,
    failed_at TIMESTAMP,
    completed_at TIMESTAMP,
    last_committed_at TIMESTAMP
);

CREATE INDEX idx_etl_checkpoint_source
    ON etl_checkpoint (source_file, status, started_at DESC);

-- SCD2: un solo record corrente per natural key
CREATE UNIQUE INDEX uq_dim_customer_current
    ON dim_customer (natural_key)
    WHERE is_current = TRUE;

CREATE UNIQUE INDEX uq_dim_seller_current
    ON dim_seller (natural_key)
    WHERE is_current = TRUE;