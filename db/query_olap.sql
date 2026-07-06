\c olist_dw;

-- ============================================================
-- KPI 1 - Fatturato per mese
-- fact: fact_sale_item
-- misura: SUM(price)
-- ============================================================
SELECT
    d.year,
    d.month,
    DATE_TRUNC('month', d.full_date)::date AS month_date,
    SUM(fsi.price) AS revenue_items_only,
    SUM(fsi.price + fsi.freight_value) AS revenue_including_freight,
    COUNT(*) AS sold_items
FROM fact_sale_item fsi
JOIN dim_date d
    ON fsi.purchase_date_key = d.surrogate_key
GROUP BY
    d.year,
    d.month,
    DATE_TRUNC('month', d.full_date)
ORDER BY
    d.year,
    d.month;


-- ============================================================
-- KPI 2 - Fatturato per trimestre
-- ============================================================
SELECT
    d.year,
    d.quarter,
    SUM(fsi.price) AS revenue_items_only,
    SUM(fsi.price + fsi.freight_value) AS revenue_including_freight,
    COUNT(*) AS sold_items
FROM fact_sale_item fsi
JOIN dim_date d
    ON fsi.purchase_date_key = d.surrogate_key
GROUP BY
    d.year,
    d.quarter
ORDER BY
    d.year,
    d.quarter;


-- ============================================================
-- KPI 3 - Fatturato per anno
-- ============================================================
SELECT
    d.year,
    SUM(fsi.price) AS revenue_items_only,
    SUM(fsi.price + fsi.freight_value) AS revenue_including_freight,
    COUNT(*) AS sold_items
FROM fact_sale_item fsi
JOIN dim_date d
    ON fsi.purchase_date_key = d.surrogate_key
GROUP BY
    d.year
ORDER BY
    d.year;


-- ============================================================
-- KPI 4 - Fatturato per regione cliente
-- ============================================================
SELECT
    dc.customer_region,
    SUM(fsi.price) AS revenue_items_only,
    SUM(fsi.price + fsi.freight_value) AS revenue_including_freight,
    COUNT(DISTINCT fsi.order_id) AS orders_count,
    COUNT(*) AS sold_items
FROM fact_sale_item fsi
JOIN dim_customer dc
    ON fsi.customer_key = dc.surrogate_key
WHERE dc.is_current = TRUE
GROUP BY
    dc.customer_region
ORDER BY
    revenue_items_only DESC;


-- ============================================================
-- KPI 5 - Fatturato per stato cliente
-- drill-down geografico cliente
-- ============================================================
SELECT
    dc.customer_region,
    dc.customer_state,
    SUM(fsi.price) AS revenue_items_only,
    COUNT(DISTINCT fsi.order_id) AS orders_count
FROM fact_sale_item fsi
JOIN dim_customer dc
    ON fsi.customer_key = dc.surrogate_key
WHERE dc.is_current = TRUE
GROUP BY
    dc.customer_region,
    dc.customer_state
ORDER BY
    dc.customer_region,
    revenue_items_only DESC;


-- ============================================================
-- KPI 6 - Fatturato per città cliente
-- drill-down geografico cliente
-- ============================================================
SELECT
    dc.customer_region,
    dc.customer_state,
    dc.customer_city,
    SUM(fsi.price) AS revenue_items_only,
    COUNT(DISTINCT fsi.order_id) AS orders_count
FROM fact_sale_item fsi
JOIN dim_customer dc
    ON fsi.customer_key = dc.surrogate_key
WHERE dc.is_current = TRUE
GROUP BY
    dc.customer_region,
    dc.customer_state,
    dc.customer_city
ORDER BY
    revenue_items_only DESC;


-- ============================================================
-- KPI 7 - Fatturato per categoria prodotto
-- ============================================================
SELECT
    dp.category_name_en,
    SUM(fsi.price) AS revenue_items_only,
    SUM(fsi.price + fsi.freight_value) AS revenue_including_freight,
    COUNT(*) AS sold_items,
    COUNT(DISTINCT fsi.order_id) AS orders_count
FROM fact_sale_item fsi
JOIN dim_product dp
    ON fsi.product_key = dp.surrogate_key
GROUP BY
    dp.category_name_en
ORDER BY
    revenue_items_only DESC;


-- ============================================================
-- KPI 8 - Fatturato mensile per categoria prodotto
-- utile per storytelling temporale del mix prodotti
-- ============================================================
SELECT
    d.year,
    d.month,
    dp.category_name_en,
    SUM(fsi.price) AS revenue_items_only,
    COUNT(*) AS sold_items
FROM fact_sale_item fsi
JOIN dim_date d
    ON fsi.purchase_date_key = d.surrogate_key
JOIN dim_product dp
    ON fsi.product_key = dp.surrogate_key
GROUP BY
    d.year,
    d.month,
    dp.category_name_en
ORDER BY
    d.year,
    d.month,
    revenue_items_only DESC;


-- ============================================================
-- KPI 9 - Top seller per ricavi
-- ============================================================
SELECT
    ds.natural_key AS seller_id,
    ds.seller_region,
    ds.seller_state,
    ds.seller_city,
    SUM(fsi.price) AS revenue_items_only,
    SUM(fsi.price + fsi.freight_value) AS revenue_including_freight,
    COUNT(DISTINCT fsi.order_id) AS orders_count,
    COUNT(*) AS sold_items
FROM fact_sale_item fsi
JOIN dim_seller ds
    ON fsi.seller_key = ds.surrogate_key
WHERE ds.is_current = TRUE
GROUP BY
    ds.natural_key,
    ds.seller_region,
    ds.seller_state,
    ds.seller_city
ORDER BY
    revenue_items_only DESC
LIMIT 20;


-- ============================================================
-- KPI 10 - Numero ordini per mese
-- fact: fact_order
-- ============================================================
SELECT
    d.year,
    d.month,
    DATE_TRUNC('month', d.full_date)::date AS month_date,
    COUNT(*) AS orders_count
FROM fact_order fo
JOIN dim_date d
    ON fo.purchase_date_key = d.surrogate_key
GROUP BY
    d.year,
    d.month,
    DATE_TRUNC('month', d.full_date)
ORDER BY
    d.year,
    d.month;


-- ============================================================
-- KPI 11 - Numero ordini per stato ordine e mese
-- ============================================================
SELECT
    d.year,
    d.month,
    fo.order_status,
    COUNT(*) AS orders_count
FROM fact_order fo
JOIN dim_date d
    ON fo.purchase_date_key = d.surrogate_key
GROUP BY
    d.year,
    d.month,
    fo.order_status
ORDER BY
    d.year,
    d.month,
    orders_count DESC;


-- ============================================================
-- KPI 12 - Ticket medio per ordine
-- payment_value è corretto qui perché la granularità è ordine
-- ============================================================
SELECT
    d.year,
    d.month,
    ROUND(AVG(fo.payment_value), 2) AS avg_ticket,
    ROUND(SUM(fo.payment_value), 2) AS total_order_value,
    COUNT(*) AS orders_count
FROM fact_order fo
JOIN dim_date d
    ON fo.purchase_date_key = d.surrogate_key
GROUP BY
    d.year,
    d.month
ORDER BY
    d.year,
    d.month;


-- ============================================================
-- KPI 13 - Ticket medio per regione cliente
-- ============================================================
SELECT
    dc.customer_region,
    ROUND(AVG(fo.payment_value), 2) AS avg_ticket,
    ROUND(SUM(fo.payment_value), 2) AS total_order_value,
    COUNT(*) AS orders_count
FROM fact_order fo
JOIN dim_customer dc
    ON fo.customer_key = dc.surrogate_key
WHERE dc.is_current = TRUE
GROUP BY
    dc.customer_region
ORDER BY
    avg_ticket DESC;


-- ============================================================
-- KPI 14 - Tempo medio di consegna
-- solo ordini consegnati
-- ============================================================
SELECT
    d.year,
    d.month,
    ROUND(AVG(fo.delivery_days), 2) AS avg_delivery_days,
    MIN(fo.delivery_days) AS min_delivery_days,
    MAX(fo.delivery_days) AS max_delivery_days,
    COUNT(*) AS delivered_orders
FROM fact_order fo
JOIN dim_date d
    ON fo.purchase_date_key = d.surrogate_key
WHERE fo.order_status = 'delivered'
  AND fo.delivery_days IS NOT NULL
GROUP BY
    d.year,
    d.month
ORDER BY
    d.year,
    d.month;


-- ============================================================
-- KPI 15 - Tempo medio di consegna per regione cliente
-- ============================================================
SELECT
    dc.customer_region,
    ROUND(AVG(fo.delivery_days), 2) AS avg_delivery_days,
    COUNT(*) AS delivered_orders
FROM fact_order fo
JOIN dim_customer dc
    ON fo.customer_key = dc.surrogate_key
WHERE fo.order_status = 'delivered'
  AND fo.delivery_days IS NOT NULL
  AND dc.is_current = TRUE
GROUP BY
    dc.customer_region
ORDER BY
    avg_delivery_days DESC;


-- ============================================================
-- KPI 16 - Review score medio per regione cliente
-- ============================================================
SELECT
    dc.customer_region,
    ROUND(AVG(fo.review_score), 2) AS avg_review_score,
    COUNT(*) AS reviewed_orders
FROM fact_order fo
JOIN dim_customer dc
    ON fo.customer_key = dc.surrogate_key
WHERE fo.review_score IS NOT NULL
  AND dc.is_current = TRUE
GROUP BY
    dc.customer_region
ORDER BY
    avg_review_score DESC;


-- ============================================================
-- KPI 17 - Review score medio per mese
-- ============================================================
SELECT
    d.year,
    d.month,
    ROUND(AVG(fo.review_score), 2) AS avg_review_score,
    COUNT(*) AS reviewed_orders
FROM fact_order fo
JOIN dim_date d
    ON fo.purchase_date_key = d.surrogate_key
WHERE fo.review_score IS NOT NULL
GROUP BY
    d.year,
    d.month
ORDER BY
    d.year,
    d.month;


-- ============================================================
-- KPI 18 - Distribuzione metodi di pagamento
-- ============================================================
SELECT
    dp.payment_type,
    COUNT(*) AS orders_count,
    ROUND(SUM(fo.payment_value), 2) AS total_payment_value,
    ROUND(AVG(fo.payment_value), 2) AS avg_payment_value
FROM fact_order fo
JOIN dim_payment dp
    ON fo.payment_key = dp.surrogate_key
GROUP BY
    dp.payment_type
ORDER BY
    total_payment_value DESC;


-- ============================================================
-- KPI 19 - Distribuzione per metodi di pagamento e rate
-- ============================================================
SELECT
    dp.payment_type,
    dp.payment_installments,
    dprod.category_name_en,
    COUNT(DISTINCT fo.order_id) AS orders_count,
    ROUND(SUM(fsi.price), 2) AS total_revenue,
    ROUND(AVG(fsi.price), 2) AS avg_item_revenue
FROM fact_order fo
-- Join cruciale tra la testata dell'ordine e le sue singole righe prodotto
JOIN fact_sale_item fsi
    ON fo.order_id = fsi.order_id
-- Join per i metodi di pagamento
JOIN dim_payment dp
    ON fo.payment_key = dp.surrogate_key
-- Join per le categorie dei prodotti
JOIN dim_product dprod
    ON fsi.product_key = dprod.surrogate_key
WHERE fo.order_status = 'delivered'
GROUP BY
    dp.payment_type,
    dp.payment_installments,
    dprod.category_name_en
ORDER BY
    total_revenue DESC;


-- ============================================================
-- KPI 20 - Analisi geografica cliente-venditore
-- regione cliente x regione seller
-- ============================================================
SELECT
    dc.customer_region,
    ds.seller_region,
    COUNT(DISTINCT fsi.order_id) AS orders_count,
    COUNT(*) AS sold_items,
    SUM(fsi.price) AS revenue_items_only
FROM fact_sale_item fsi
JOIN dim_customer dc
    ON fsi.customer_key = dc.surrogate_key
JOIN dim_seller ds
    ON fsi.seller_key = ds.surrogate_key
WHERE dc.is_current = TRUE
  AND ds.is_current = TRUE
GROUP BY
    dc.customer_region,
    ds.seller_region
ORDER BY
    revenue_items_only DESC;


-- ============================================================
-- KPI 21 - Stato cliente x stato seller
-- drill-down della relazione geografica
-- ============================================================
SELECT
    dc.customer_state,
    ds.seller_state,
    COUNT(DISTINCT fsi.order_id) AS orders_count,
    SUM(fsi.price) AS revenue_items_only
FROM fact_sale_item fsi
JOIN dim_customer dc
    ON fsi.customer_key = dc.surrogate_key
JOIN dim_seller ds
    ON fsi.seller_key = ds.surrogate_key
WHERE dc.is_current = TRUE
  AND ds.is_current = TRUE
GROUP BY
    dc.customer_state,
    ds.seller_state
ORDER BY
    revenue_items_only DESC;


-- ============================================================
-- KPI 22 - Seller top per categoria prodotto
-- ============================================================
SELECT
    dp.category_name_en,
    ds.natural_key AS seller_id,
    ds.seller_state,
    SUM(fsi.price) AS revenue_items_only,
    COUNT(*) AS sold_items
FROM fact_sale_item fsi
JOIN dim_product dp
    ON fsi.product_key = dp.surrogate_key
JOIN dim_seller ds
    ON fsi.seller_key = ds.surrogate_key
WHERE ds.is_current = TRUE
GROUP BY
    dp.category_name_en,
    ds.natural_key,
    ds.seller_state
ORDER BY
    dp.category_name_en,
    revenue_items_only DESC;


SELECT
    d_purch.year AS year,
    d_purch.month AS month,
    c.customer_state AS customer_state,
    p.category_name_en AS category_name_en,
    SUM(f.price) AS total_revenue,
    AVG(d_deliv.full_date - d_purch.full_date) AS avg_delivery_days
FROM fact_sale_item f
-- Join per la data di acquisto (per anno e mese)
JOIN dim_date d_purch
    ON f.purchase_date_key = d_purch.surrogate_key
-- Join per la data di consegna (per calcolare i giorni di spedizione)
JOIN dim_date d_deliv
    ON f.delivered_date_key = d_deliv.surrogate_key
-- Join per i dati geografici del cliente
JOIN dim_customer c
    ON f.customer_key = c.surrogate_key
-- Join per le categorie dei prodotti
JOIN dim_product p
    ON f.product_key = p.surrogate_key
WHERE f.order_status = 'delivered'
  AND f.delivered_date_key IS NOT NULL
GROUP BY
    d_purch.year,
    d_purch.month,
    c.customer_state,
    p.category_name_en;


