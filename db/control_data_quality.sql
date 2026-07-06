-- ============================================================================
-- DATA QUALITY CONTROL SUITE - 3 Layer ETL Architecture
-- ============================================================================
-- Esegui questo script per verificare la coerenza dei dati tra staging e reconciled

-- ============================================================================
-- PARTE 1: OVERVIEW INFRASTRUTTURA
-- ============================================================================

-- 1.1) Lista dei database
SELECT 'DATABASE OVERVIEW' as section;
\l

-- 1.2) Schema nel database reconciled
SELECT 'RECONCILED DB SCHEMAS' as section;
\c olist_reconciled
\dn

-- 1.3) Tabelle nel database staging
SELECT 'STAGING DB TABLES' as section;
\c olist_staging
\dt public.*

-- 1.4) Tabelle nel database reconciled
SELECT 'RECONCILED DB TABLES' as section;
\c olist_reconciled
\dt reconciled.*

-- 1.5) Tabelle nel database DW
SELECT 'DATA WAREHOUSE TABLES' as section;
\c olist_dw
\dt public.dim_* public.fact_*

-- ============================================================================
-- PARTE 2: CONTEGGIO RIGHE - STAGING vs RECONCILED
-- ============================================================================

SELECT '=== STAGING: CARDINALITÀ TABELLE RAW ===' as header;
\c olist_staging

SELECT
  'public.customers' as table_name,
  COUNT(*) as row_count
FROM public.customers
UNION ALL
SELECT 'public.sellers', COUNT(*) FROM public.sellers
UNION ALL
SELECT 'public.orders', COUNT(*) FROM public.orders
UNION ALL
SELECT 'public.order_items', COUNT(*) FROM public.order_items
UNION ALL
SELECT 'public.order_payments', COUNT(*) FROM public.order_payments
UNION ALL
SELECT 'public.order_reviews', COUNT(*) FROM public.order_reviews
UNION ALL
SELECT 'public.products', COUNT(*) FROM public.products
UNION ALL
SELECT 'public.product_category_name_translation', COUNT(*) FROM public.product_category_name_translation
UNION ALL
SELECT 'public.geolocation', COUNT(*) FROM public.geolocation
ORDER BY table_name;

SELECT '=== RECONCILED: CARDINALITÀ TABELLE RCL ===' as header;
\c olist_reconciled

SELECT
  'reconciled.rcl_customers' as table_name,
  COUNT(*) as row_count
FROM reconciled.rcl_customers
UNION ALL
SELECT 'reconciled.rcl_sellers', COUNT(*) FROM reconciled.rcl_sellers
UNION ALL
SELECT 'reconciled.rcl_orders', COUNT(*) FROM reconciled.rcl_orders
UNION ALL
SELECT 'reconciled.rcl_order_items', COUNT(*) FROM reconciled.rcl_order_items
UNION ALL
SELECT 'reconciled.rcl_order_payments', COUNT(*) FROM reconciled.rcl_order_payments
UNION ALL
SELECT 'reconciled.rcl_order_reviews', COUNT(*) FROM reconciled.rcl_order_reviews
UNION ALL
SELECT 'reconciled.rcl_products', COUNT(*) FROM reconciled.rcl_products
UNION ALL
SELECT 'reconciled.rcl_product_category_translation', COUNT(*) FROM reconciled.rcl_product_category_translation
UNION ALL
SELECT 'reconciled.rcl_geolocation', COUNT(*) FROM reconciled.rcl_geolocation
ORDER BY table_name;

-- ============================================================================
-- PARTE 3: CONFRONTO CARDINALITÀ (Expected vs Actual)
-- ============================================================================

SELECT '=== CONFRONTO CARDINALITÀ ===' as header;

-- Customers: staging raw vs reconciled
SELECT
  'customers' as entity,
  (SELECT COUNT(*) FROM olist_staging.public.customers) as staging_count,
  (SELECT COUNT(*) FROM olist_reconciled.reconciled.rcl_customers) as reconciled_count,
  (SELECT COUNT(*) FROM olist_staging.public.customers) -
  (SELECT COUNT(*) FROM olist_reconciled.reconciled.rcl_customers) as delta_rows,
  CASE
    WHEN (SELECT COUNT(*) FROM olist_staging.public.customers) =
         (SELECT COUNT(*) FROM olist_reconciled.reconciled.rcl_customers)
    THEN 'OK'
    ELSE 'WARNING: Cardinalità diversa!'
  END as status

UNION ALL

-- Sellers
SELECT
  'sellers' as entity,
  (SELECT COUNT(*) FROM olist_staging.public.sellers) as staging_count,
  (SELECT COUNT(*) FROM olist_reconciled.reconciled.rcl_sellers) as reconciled_count,
  (SELECT COUNT(*) FROM olist_staging.public.sellers) -
  (SELECT COUNT(*) FROM olist_reconciled.reconciled.rcl_sellers) as delta,
  CASE
    WHEN (SELECT COUNT(*) FROM olist_staging.public.sellers) =
         (SELECT COUNT(*) FROM olist_reconciled.reconciled.rcl_sellers)
    THEN 'OK'
    ELSE 'WARNING'
  END

UNION ALL

-- Orders
SELECT
  'orders',
  (SELECT COUNT(*) FROM olist_staging.public.orders),
  (SELECT COUNT(*) FROM olist_reconciled.reconciled.rcl_orders),
  (SELECT COUNT(*) FROM olist_staging.public.orders) -
  (SELECT COUNT(*) FROM olist_reconciled.reconciled.rcl_orders),
  CASE
    WHEN (SELECT COUNT(*) FROM olist_staging.public.orders) =
         (SELECT COUNT(*) FROM olist_reconciled.reconciled.rcl_orders)
    THEN 'OK'
    ELSE 'WARNING'
  END

UNION ALL

-- Order Items
SELECT
  'order_items',
  (SELECT COUNT(*) FROM olist_staging.public.order_items),
  (SELECT COUNT(*) FROM olist_reconciled.reconciled.rcl_order_items),
  (SELECT COUNT(*) FROM olist_staging.public.order_items) -
  (SELECT COUNT(*) FROM olist_reconciled.reconciled.rcl_order_items),
  CASE
    WHEN (SELECT COUNT(*) FROM olist_staging.public.order_items) =
         (SELECT COUNT(*) FROM olist_reconciled.reconciled.rcl_order_items)
    THEN 'OK'
    ELSE 'WARNING'
  END

UNION ALL

-- Order Payments
SELECT
  'order_payments',
  (SELECT COUNT(*) FROM olist_staging.public.order_payments),
  (SELECT COUNT(*) FROM olist_reconciled.reconciled.rcl_order_payments),
  (SELECT COUNT(*) FROM olist_staging.public.order_payments) -
  (SELECT COUNT(*) FROM olist_reconciled.reconciled.rcl_order_payments),
  CASE
    WHEN (SELECT COUNT(*) FROM olist_staging.public.order_payments) =
         (SELECT COUNT(*) FROM olist_reconciled.reconciled.rcl_order_payments)
    THEN 'OK'
    ELSE 'WARNING'
  END

UNION ALL

-- Order Reviews
SELECT
  'order_reviews',
  (SELECT COUNT(*) FROM olist_staging.public.order_reviews),
  (SELECT COUNT(*) FROM olist_reconciled.reconciled.rcl_order_reviews),
  (SELECT COUNT(*) FROM olist_staging.public.order_reviews) -
  (SELECT COUNT(*) FROM olist_reconciled.reconciled.rcl_order_reviews),
  CASE
    WHEN (SELECT COUNT(*) FROM olist_staging.public.order_reviews) =
         (SELECT COUNT(*) FROM olist_reconciled.reconciled.rcl_order_reviews)
    THEN 'OK'
    ELSE 'WARNING'
  END

UNION ALL

-- Products
SELECT
  'products',
  (SELECT COUNT(*) FROM olist_staging.public.products),
  (SELECT COUNT(*) FROM olist_reconciled.reconciled.rcl_products),
  (SELECT COUNT(*) FROM olist_staging.public.products) -
  (SELECT COUNT(*) FROM olist_reconciled.reconciled.rcl_products),
  CASE
    WHEN (SELECT COUNT(*) FROM olist_staging.public.products) =
         (SELECT COUNT(*) FROM olist_reconciled.reconciled.rcl_products)
    THEN 'OK'
    ELSE 'WARNING'
  END

UNION ALL

-- Product Category Translation
SELECT
  'product_category_translation',
  (SELECT COUNT(*) FROM olist_staging.public.product_category_name_translation),
  (SELECT COUNT(*) FROM olist_reconciled.reconciled.rcl_product_category_translation),
  (SELECT COUNT(*) FROM olist_staging.public.product_category_name_translation) -
  (SELECT COUNT(*) FROM olist_reconciled.reconciled.rcl_product_category_translation),
  CASE
    WHEN (SELECT COUNT(*) FROM olist_staging.public.product_category_name_translation) =
         (SELECT COUNT(*) FROM olist_reconciled.reconciled.rcl_product_category_translation)
    THEN 'OK'
    ELSE 'WARNING'
  END

UNION ALL

-- Geolocation
SELECT
  'geolocation',
  (SELECT COUNT(*) FROM olist_staging.public.geolocation),
  (SELECT COUNT(*) FROM olist_reconciled.reconciled.rcl_geolocation),
  (SELECT COUNT(*) FROM olist_staging.public.geolocation) -
  (SELECT COUNT(*) FROM olist_reconciled.reconciled.rcl_geolocation),
  CASE
    WHEN (SELECT COUNT(*) FROM olist_staging.public.geolocation) =
         (SELECT COUNT(*) FROM olist_reconciled.reconciled.rcl_geolocation)
    THEN 'OK'
    ELSE 'WARNING'
  END
;

-- ============================================================================
-- PARTE 4: CONTROLLI SPECIFICI DI QUALITÀ DATI
-- ============================================================================

SELECT '=== PAYMENT_TYPE VALIDATION ===' as header;
\c olist_reconciled

-- Validazione payment_type in reconciled
SELECT
  payment_type,
  COUNT(*) as count,
  CASE
    WHEN payment_type IN ('credit_card', 'debit_card', 'voucher', 'ticket', 'not_defined')
    THEN 'VALID'
    ELSE 'INVALID'
  END as status
FROM reconciled.rcl_order_payments
GROUP BY payment_type
ORDER BY count DESC;

SELECT '=== REVIEW_SCORE VALIDATION ===' as header;

-- Review score deve essere tra 1 e 5 oppure NULL
SELECT
  'Valid scores (1-5)' as status,
  COUNT(*) as count
FROM reconciled.rcl_order_reviews
WHERE review_score >= 1 AND review_score <= 5

UNION ALL

SELECT
  'NULL scores',
  COUNT(*)
FROM reconciled.rcl_order_reviews
WHERE review_score IS NULL

UNION ALL

SELECT
  'INVALID scores (out of range)',
  COUNT(*)
FROM reconciled.rcl_order_reviews
WHERE review_score < 1 OR review_score > 5;

SELECT '=== CUSTOMER ID UNIQUENESS ===' as header;

-- Verificare che customer_id e customer_unique_id siano coerenti
SELECT
  'Customers with NULL customer_unique_id' as check_type,
  COUNT(*) as count
FROM reconciled.rcl_customers
WHERE customer_unique_id IS NULL

UNION ALL

SELECT
  'Expected customer count',
  COUNT(DISTINCT customer_id)
FROM reconciled.rcl_customers;

SELECT '=== DUPLICATES CHECK ===' as header;

-- Verificare duplicati in reconciled (non dovrebbero existere)
SELECT
  'Duplicate customer_ids' as check_type,
  COUNT(*) as duplicate_count
FROM (
  SELECT customer_id
  FROM reconciled.rcl_customers
  GROUP BY customer_id
  HAVING COUNT(*) > 1
) duplicates

UNION ALL

SELECT
  'Duplicate seller_ids',
  COUNT(*)
FROM (
  SELECT seller_id
  FROM reconciled.rcl_sellers
  GROUP BY seller_id
  HAVING COUNT(*) > 1
) duplicates

UNION ALL

SELECT
  'Duplicate order_ids',
  COUNT(*)
FROM (
  SELECT order_id
  FROM reconciled.rcl_orders
  GROUP BY order_id
  HAVING COUNT(*) > 1
) duplicates

UNION ALL

SELECT
  'Duplicate product_ids',
  COUNT(*)
FROM (
  SELECT product_id
  FROM reconciled.rcl_products
  GROUP BY product_id
  HAVING COUNT(*) > 1
) duplicates;

SELECT '=== ORDER STATUS VALIDATION ===' as header;

-- Order status deve avere valori specifici
SELECT
  order_status,
  COUNT(*) as count
FROM reconciled.rcl_orders
GROUP BY order_status
ORDER BY count DESC;

SELECT '=== STATE CODES VALIDATION ===' as header;

-- State codes devono essere sempre validi o 'XX' (per invalid)
SELECT
  'Valid state codes (2 chars, uppercase)' as status,
  COUNT(*) as count
FROM reconciled.rcl_customers
WHERE customer_state ~ '^[A-Z]{2}$'

UNION ALL

SELECT
  'INVALID state codes',
  COUNT(*)
FROM reconciled.rcl_customers
WHERE customer_state !~ '^[A-Z]{2}$';

SELECT '=== PRICE VALIDATION ===' as header;

-- Prezzi negli order_items devono essere positivi o zero
SELECT
  'Valid prices (>= 0)' as status,
  COUNT(*) as count
FROM reconciled.rcl_order_items
WHERE price >= 0

UNION ALL

SELECT
  'INVALID prices (< 0 or NULL)',
  COUNT(*)
FROM reconciled.rcl_order_items
WHERE price < 0 OR price IS NULL;

SELECT '=== REFERENTIAL INTEGRITY SPOT CHECKS ===' as header;

-- Check: order_id in order_items deve esistere in orders
SELECT
  'order_items with non-existent order_ids' as check_type,
  COUNT(*) as count
FROM reconciled.rcl_order_items oi
WHERE NOT EXISTS (
  SELECT 1 FROM reconciled.rcl_orders o
  WHERE o.order_id = oi.order_id
)

UNION ALL

-- Check: product_id in order_items deve esistere in products
SELECT
  'order_items with non-existent product_ids',
  COUNT(*)
FROM reconciled.rcl_order_items oi
WHERE NOT EXISTS (
  SELECT 1 FROM reconciled.rcl_products p
  WHERE p.product_id = oi.product_id
)

UNION ALL

-- Check: seller_id in order_items deve esistere in sellers
SELECT
  'order_items with non-existent seller_ids',
  COUNT(*)
FROM reconciled.rcl_order_items oi
WHERE NOT EXISTS (
  SELECT 1 FROM reconciled.rcl_sellers s
  WHERE s.seller_id = oi.seller_id
);

SELECT '=== NULL VALUES SUMMARY ===' as header;

-- Riepilogo dei NULL per colonne critiche
SELECT
  'rcl_customers.customer_state IS NULL' as check_type,
  COUNT(*) as null_count
FROM reconciled.rcl_customers
WHERE customer_state IS NULL

UNION ALL

SELECT
  'rcl_orders.order_status IS NULL',
  COUNT(*)
FROM reconciled.rcl_orders
WHERE order_status IS NULL

UNION ALL

SELECT
  'rcl_order_items.price IS NULL',
  COUNT(*)
FROM reconciled.rcl_order_items
WHERE price IS NULL

UNION ALL

SELECT
  'rcl_order_reviews.review_score IS NULL',
  COUNT(*)
FROM reconciled.rcl_order_reviews
WHERE review_score IS NULL;

SELECT '=== CONTROL SCRIPT COMPLETED ===' as header;

