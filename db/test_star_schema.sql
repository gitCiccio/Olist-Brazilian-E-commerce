\c olist_dw

SELECT current_database(), current_schema();

SELECT
    table_schema,
    table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_type = 'BASE TABLE'
  AND table_name IN (
      'dim_product',
      'dim_date',
      'dim_payment',
      'dim_customer',
      'dim_seller',
      'fact_sale_item',
      'fact_order'
  )
ORDER BY table_name;

SELECT 'dim_product' AS table_name, COUNT(*) AS total_rows FROM public.dim_product
UNION ALL
SELECT 'dim_date', COUNT(*) FROM public.dim_date
UNION ALL
SELECT 'dim_payment', COUNT(*) FROM public.dim_payment
UNION ALL
SELECT 'dim_customer', COUNT(*) FROM public.dim_customer
UNION ALL
SELECT 'dim_seller', COUNT(*) FROM public.dim_seller
UNION ALL
SELECT 'fact_sale_item', COUNT(*) FROM public.fact_sale_item
UNION ALL
SELECT 'fact_order', COUNT(*) FROM public.fact_order;

SELECT
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (WHERE surrogate_key IS NULL) AS null_surrogate_key,
    COUNT(*) FILTER (WHERE natural_key IS NULL) AS null_natural_key,
    COUNT(*) FILTER (WHERE customer_region IS NULL) AS null_customer_region,
    COUNT(*) FILTER (WHERE customer_city IS NULL) AS null_customer_city,
    COUNT(*) FILTER (WHERE customer_state IS NULL) AS null_customer_state,
    COUNT(*) FILTER (WHERE valid_from IS NULL) AS null_valid_from,
    COUNT(*) FILTER (WHERE is_current IS NULL) AS null_is_current
FROM public.dim_customer;

SELECT
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (WHERE surrogate_key IS NULL) AS null_surrogate_key,
    COUNT(*) FILTER (WHERE natural_key IS NULL) AS null_natural_key,
    COUNT(*) FILTER (WHERE seller_region IS NULL) AS null_seller_region,
    COUNT(*) FILTER (WHERE seller_city IS NULL) AS null_seller_city,
    COUNT(*) FILTER (WHERE seller_state IS NULL) AS null_seller_state,
    COUNT(*) FILTER (WHERE valid_from IS NULL) AS null_valid_from,
    COUNT(*) FILTER (WHERE is_current IS NULL) AS null_is_current
FROM public.dim_seller;

SELECT
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (WHERE surrogate_key IS NULL) AS null_surrogate_key,
    COUNT(*) FILTER (WHERE natural_key IS NULL) AS null_natural_key,
    COUNT(*) FILTER (WHERE category_name_en IS NULL) AS null_category_name_en
FROM public.dim_product;

SELECT
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (WHERE surrogate_key IS NULL) AS null_surrogate_key,
    COUNT(*) FILTER (WHERE natural_key IS NULL) AS null_natural_key,
    COUNT(*) FILTER (WHERE full_date IS NULL) AS null_full_date,
    COUNT(*) FILTER (WHERE day IS NULL) AS null_day,
    COUNT(*) FILTER (WHERE month IS NULL) AS null_month,
    COUNT(*) FILTER (WHERE quarter IS NULL) AS null_quarter,
    COUNT(*) FILTER (WHERE year IS NULL) AS null_year,
    COUNT(*) FILTER (WHERE day_of_week IS NULL) AS null_day_of_week,
    COUNT(*) FILTER (WHERE week_of_year IS NULL) AS null_week_of_year,
    COUNT(*) FILTER (WHERE is_weekend IS NULL) AS null_is_weekend
FROM public.dim_date;

SELECT
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (WHERE surrogate_key IS NULL) AS null_surrogate_key,
    COUNT(*) FILTER (WHERE payment_type IS NULL) AS null_payment_type,
    COUNT(*) FILTER (WHERE payment_installments IS NULL) AS null_payment_installments
FROM public.dim_payment;

SELECT
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (WHERE surrogate_key IS NULL) AS null_surrogate_key,
    COUNT(*) FILTER (WHERE natural_key IS NULL) AS null_natural_key,
    COUNT(*) FILTER (WHERE order_id IS NULL) AS null_order_id,
    COUNT(*) FILTER (WHERE order_item_id IS NULL) AS null_order_item_id,
    COUNT(*) FILTER (WHERE order_status IS NULL) AS null_order_status,
    COUNT(*) FILTER (WHERE item_count IS NULL) AS null_item_count,
    COUNT(*) FILTER (WHERE price IS NULL) AS null_price,
    COUNT(*) FILTER (WHERE freight_value IS NULL) AS null_freight_value,
    COUNT(*) FILTER (WHERE product_key IS NULL) AS null_product_key,
    COUNT(*) FILTER (WHERE customer_key IS NULL) AS null_customer_key,
    COUNT(*) FILTER (WHERE seller_key IS NULL) AS null_seller_key,
    COUNT(*) FILTER (WHERE purchase_date_key IS NULL) AS null_purchase_date_key
FROM public.fact_sale_item;

SELECT
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (WHERE surrogate_key IS NULL) AS null_surrogate_key,
    COUNT(*) FILTER (WHERE natural_key IS NULL) AS null_natural_key,
    COUNT(*) FILTER (WHERE order_id IS NULL) AS null_order_id,
    COUNT(*) FILTER (WHERE order_status IS NULL) AS null_order_status,
    COUNT(*) FILTER (WHERE payment_value IS NULL) AS null_payment_value,
    COUNT(*) FILTER (WHERE review_score IS NULL) AS null_review_score,
    COUNT(*) FILTER (WHERE delivery_days IS NULL) AS null_delivery_days,
    COUNT(*) FILTER (WHERE customer_key IS NULL) AS null_customer_key,
    COUNT(*) FILTER (WHERE payment_key IS NULL) AS null_payment_key,
    COUNT(*) FILTER (WHERE purchase_date_key IS NULL) AS null_purchase_date_key
FROM public.fact_order;

SELECT surrogate_key, COUNT(*) AS cnt
FROM public.dim_customer
GROUP BY surrogate_key
HAVING COUNT(*) > 1;

SELECT surrogate_key, COUNT(*) AS cnt
FROM public.dim_seller
GROUP BY surrogate_key
HAVING COUNT(*) > 1;

SELECT surrogate_key, COUNT(*) AS cnt
FROM public.dim_product
GROUP BY surrogate_key
HAVING COUNT(*) > 1;

SELECT surrogate_key, COUNT(*) AS cnt
FROM public.dim_date
GROUP BY surrogate_key
HAVING COUNT(*) > 1;

SELECT surrogate_key, COUNT(*) AS cnt
FROM public.dim_payment
GROUP BY surrogate_key
HAVING COUNT(*) > 1;

SELECT natural_key, COUNT(*) AS cnt
FROM public.dim_customer
GROUP BY natural_key
HAVING COUNT(*) > 1
ORDER BY cnt DESC, natural_key;

SELECT natural_key, COUNT(*) AS current_rows
FROM public.dim_customer
WHERE is_current = TRUE
GROUP BY natural_key
HAVING COUNT(*) > 1;

SELECT natural_key, COUNT(*) AS current_rows
FROM public.dim_seller
WHERE is_current = TRUE
GROUP BY natural_key
HAVING COUNT(*) > 1;

SELECT natural_key, COUNT(*) AS cnt
FROM public.dim_product
GROUP BY natural_key
HAVING COUNT(*) > 1;

SELECT natural_key, COUNT(*) AS cnt
FROM public.dim_date
GROUP BY natural_key
HAVING COUNT(*) > 1;

SELECT payment_type, payment_installments, COUNT(*) AS cnt
FROM public.dim_payment
GROUP BY payment_type, payment_installments
HAVING COUNT(*) > 1;

SELECT natural_key, COUNT(*) AS cnt
FROM public.fact_sale_item
GROUP BY natural_key
HAVING COUNT(*) > 1;

SELECT order_id, order_item_id, COUNT(*) AS cnt
FROM public.fact_sale_item
GROUP BY order_id, order_item_id
HAVING COUNT(*) > 1
ORDER BY cnt DESC, order_id, order_item_id;

SELECT natural_key, COUNT(*) AS cnt
FROM public.fact_order
GROUP BY natural_key
HAVING COUNT(*) > 1;

SELECT order_id, COUNT(*) AS cnt
FROM public.fact_order
GROUP BY order_id
HAVING COUNT(*) > 1;

SELECT COUNT(*) AS missing_product_fk
FROM public.fact_sale_item f
LEFT JOIN public.dim_product d
    ON f.product_key = d.surrogate_key
WHERE d.surrogate_key IS NULL;

SELECT COUNT(*) AS missing_customer_fk
FROM public.fact_sale_item f
LEFT JOIN public.dim_customer d
    ON f.customer_key = d.surrogate_key
WHERE d.surrogate_key IS NULL;

SELECT COUNT(*) AS missing_seller_fk
FROM public.fact_sale_item f
LEFT JOIN public.dim_seller d
    ON f.seller_key = d.surrogate_key
WHERE d.surrogate_key IS NULL;

SELECT COUNT(*) AS missing_purchase_date_fk
FROM public.fact_sale_item f
LEFT JOIN public.dim_date d
    ON f.purchase_date_key = d.surrogate_key
WHERE d.surrogate_key IS NULL;

SELECT COUNT(*) AS missing_customer_fk
FROM public.fact_order f
LEFT JOIN public.dim_customer d
    ON f.customer_key = d.surrogate_key
WHERE d.surrogate_key IS NULL;

SELECT COUNT(*) AS missing_payment_fk
FROM public.fact_order f
LEFT JOIN public.dim_payment d
    ON f.payment_key = d.surrogate_key
WHERE f.payment_key IS NOT NULL
  AND d.surrogate_key IS NULL;

SELECT COUNT(*) AS missing_purchase_date_fk
FROM public.fact_order f
LEFT JOIN public.dim_date d
    ON f.purchase_date_key = d.surrogate_key
WHERE d.surrogate_key IS NULL;

SELECT customer_state, COUNT(*) AS cnt
FROM public.dim_customer
GROUP BY customer_state
HAVING customer_state IS NULL
   OR LENGTH(TRIM(customer_state)) <> 2
ORDER BY cnt DESC;

SELECT seller_state, COUNT(*) AS cnt
FROM public.dim_seller
GROUP BY seller_state
HAVING seller_state IS NULL
   OR LENGTH(TRIM(seller_state)) <> 2
ORDER BY cnt DESC;

SELECT customer_region, COUNT(*) AS cnt
FROM public.dim_customer
GROUP BY customer_region
ORDER BY cnt DESC;

SELECT seller_region, COUNT(*) AS cnt
FROM public.dim_seller
GROUP BY seller_region
ORDER BY cnt DESC;

SELECT
    COUNT(*) FILTER (WHERE review_score IS NULL) AS null_review_score,
    COUNT(*) FILTER (WHERE review_score < 1 OR review_score > 5) AS invalid_review_score
FROM public.fact_order;

SELECT
    COUNT(*) FILTER (WHERE payment_value IS NULL) AS null_payment_value,
    COUNT(*) FILTER (WHERE payment_value < 0) AS negative_payment_value
FROM public.fact_order;

SELECT
    COUNT(*) FILTER (WHERE price < 0) AS negative_price,
    COUNT(*) FILTER (WHERE freight_value < 0) AS negative_freight_value
FROM public.fact_sale_item;

SELECT
    COUNT(*) FILTER (WHERE delivery_days < 0) AS negative_delivery_days
FROM public.fact_order;

SELECT 'dim_customer_null_natural_key' AS check_name,
       COUNT(*) AS bad_rows
FROM public.dim_customer
WHERE natural_key IS NULL OR TRIM(natural_key) = ''

UNION ALL
SELECT 'dim_customer_multi_current',
       COUNT(*)
FROM (
    SELECT natural_key
    FROM public.dim_customer
    WHERE is_current = TRUE
    GROUP BY natural_key
    HAVING COUNT(*) > 1
) t

UNION ALL
SELECT 'dim_seller_null_natural_key',
       COUNT(*)
FROM public.dim_seller
WHERE natural_key IS NULL OR TRIM(natural_key) = ''

UNION ALL
SELECT 'dim_seller_multi_current',
       COUNT(*)
FROM (
    SELECT natural_key
    FROM public.dim_seller
    WHERE is_current = TRUE
    GROUP BY natural_key
    HAVING COUNT(*) > 1
) t

UNION ALL
SELECT 'fact_sale_item_missing_customer_fk',
       COUNT(*)
FROM public.fact_sale_item f
LEFT JOIN public.dim_customer d ON f.customer_key = d.surrogate_key
WHERE d.surrogate_key IS NULL

UNION ALL
SELECT 'fact_sale_item_missing_seller_fk',
       COUNT(*)
FROM public.fact_sale_item f
LEFT JOIN public.dim_seller d ON f.seller_key = d.surrogate_key
WHERE d.surrogate_key IS NULL

UNION ALL
SELECT 'fact_sale_item_missing_product_fk',
       COUNT(*)
FROM public.fact_sale_item f
LEFT JOIN public.dim_product d ON f.product_key = d.surrogate_key
WHERE d.surrogate_key IS NULL

UNION ALL
SELECT 'fact_order_missing_customer_fk',
       COUNT(*)
FROM public.fact_order f
LEFT JOIN public.dim_customer d ON f.customer_key = d.surrogate_key
WHERE d.surrogate_key IS NULL

UNION ALL
SELECT 'fact_order_missing_payment_fk',
       COUNT(*)
FROM public.fact_order f
LEFT JOIN public.dim_payment d ON f.payment_key = d.surrogate_key
WHERE f.payment_key IS NOT NULL
  AND d.surrogate_key IS NULL

UNION ALL
SELECT 'fact_order_invalid_review_score',
       COUNT(*)
FROM public.fact_order
WHERE review_score IS NOT NULL
  AND (review_score < 1 OR review_score > 5)

UNION ALL
SELECT 'fact_order_negative_payment_value',
       COUNT(*)
FROM public.fact_order
WHERE payment_value < 0;