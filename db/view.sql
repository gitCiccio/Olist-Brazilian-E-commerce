\c olist_dw;

CREATE OR REPLACE VIEW vw_kpi_revenue_month AS
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
    d.year, d.month, DATE_TRUNC('month', d.full_date);

CREATE OR REPLACE VIEW vw_kpi_revenue_customer_region AS
SELECT
    dc.customer_region,
    SUM(fsi.price) AS revenue_items_only,
    SUM(fsi.price + fsi.freight_value) AS revenue_including_freight,
    COUNT(DISTINCT fsi.order_id) AS orders_count
FROM fact_sale_item fsi
JOIN dim_customer dc
    ON fsi.customer_key = dc.surrogate_key
WHERE dc.is_current = TRUE
GROUP BY
    dc.customer_region;

CREATE OR REPLACE VIEW vw_kpi_revenue_category AS
SELECT
    dp.category_name_en,
    SUM(fsi.price) AS revenue_items_only,
    COUNT(DISTINCT fsi.order_id) AS orders_count
FROM fact_sale_item fsi
JOIN dim_product dp
    ON fsi.product_key = dp.surrogate_key
GROUP BY
    dp.category_name_en;

CREATE OR REPLACE VIEW vw_kpi_avg_ticket_month AS
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
    d.year, d.month;

CREATE OR REPLACE VIEW vw_kpi_delivery_month AS
SELECT
    d.year,
    d.month,
    ROUND(AVG(fo.delivery_days), 2) AS avg_delivery_days,
    COUNT(*) AS delivered_orders
FROM fact_order fo
JOIN dim_date d
    ON fo.purchase_date_key = d.surrogate_key
WHERE fo.order_status = 'delivered'
  AND fo.delivery_days IS NOT NULL
GROUP BY
    d.year, d.month;