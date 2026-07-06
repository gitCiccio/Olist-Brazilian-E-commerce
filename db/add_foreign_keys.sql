-- Add logical foreign key constraints to raw/staging public tables in olist_db

-- orders.customer_id -> customers.customer_id
ALTER TABLE public.orders DROP CONSTRAINT IF EXISTS fk_orders_customer;
ALTER TABLE public.orders
  ADD CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id)
  REFERENCES public.customers (customer_id) ON DELETE SET NULL;

-- order_items.order_id -> orders.order_id
ALTER TABLE public.order_items DROP CONSTRAINT IF EXISTS fk_order_items_order;
ALTER TABLE public.order_items
  ADD CONSTRAINT fk_order_items_order FOREIGN KEY (order_id)
  REFERENCES public.orders (order_id) ON DELETE CASCADE;

-- order_items.product_id -> products.product_id
ALTER TABLE public.order_items DROP CONSTRAINT IF EXISTS fk_order_items_product;
ALTER TABLE public.order_items
  ADD CONSTRAINT fk_order_items_product FOREIGN KEY (product_id)
  REFERENCES public.products (product_id) ON DELETE SET NULL;

-- order_items.seller_id -> sellers.seller_id
ALTER TABLE public.order_items DROP CONSTRAINT IF EXISTS fk_order_items_seller;
ALTER TABLE public.order_items
  ADD CONSTRAINT fk_order_items_seller FOREIGN KEY (seller_id)
  REFERENCES public.sellers (seller_id) ON DELETE SET NULL;

-- order_payments.order_id -> orders.order_id
ALTER TABLE public.order_payments DROP CONSTRAINT IF EXISTS fk_order_payments_order;
ALTER TABLE public.order_payments
  ADD CONSTRAINT fk_order_payments_order FOREIGN KEY (order_id)
  REFERENCES public.orders (order_id) ON DELETE CASCADE;

-- order_reviews.order_id -> orders.order_id
ALTER TABLE public.order_reviews DROP CONSTRAINT IF EXISTS fk_order_reviews_order;
ALTER TABLE public.order_reviews
  ADD CONSTRAINT fk_order_reviews_order FOREIGN KEY (order_id)
  REFERENCES public.orders (order_id) ON DELETE CASCADE;

-- products.product_category_name -> product_category_name_translation.product_category_name
ALTER TABLE public.products DROP CONSTRAINT IF EXISTS fk_products_category;
ALTER TABLE public.products
  ADD CONSTRAINT fk_products_category FOREIGN KEY (product_category_name)
  REFERENCES public.product_category_name_translation (product_category_name) ON DELETE SET NULL;

-- Note: geolocation is left without FK because geolocation_zip_code_prefix is not unique

