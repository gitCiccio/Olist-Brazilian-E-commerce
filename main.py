import pandas as pd

from db import *
from etl.db import db_connection
from etl.trasform import transform_dim_sellers, transform_dim_payment, transform_dim_customers, transform_dim_date
from logger.logger import AppLogger
from sources import SOURCES

log = AppLogger(name="main.extract", log_file="main.log")

if __name__ == "__main__":
    log.info("Init program")


    """# Test
    df_sellers = pd.read_csv(SOURCES["dim_seller"]["file"])
    seller_cities = df["seller_city"].unique().tolist()
    seller_states = df["seller_state"].unique().tolist()
    print(seller_cities)
    print(seller_states)

    df_customers = pd.read_csv(SOURCES["dim_customer"]["file"])
    customer_cities = df["customer_city"].unique().tolist()
    customer_states = df["customer_state"].unique().tolist()
    print(customer_cities)
    print(customer_states)
"""
"""
 df_payment = extract_csv(SOURCES["dim_payment"]["file"])
    transform_dim_payment(df_payment)

    df_sellers = extract_csv(SOURCES["dim_seller"]["file"])
    transform_dim_sellers(df_sellers)

    df_customers = extract_csv(SOURCES["dim_customer"]["file"])
    transform_dim_customers(df_customers)

    df_date = extract_csv(SOURCES["dim_date"]["file"])
    transform_dim_date(df_date)

    df_product = extract_csv(SOURCES["dim_product"]["file"])
    # transform_dim_product(df_product)
"""

df = pd.read_csv(SOURCES['review_info']['file'])

# Conta quante review ha ogni order_id
order_counts = df.groupby('order_id').size().reset_index(name='review_count')

# Quanti ordini hanno più di una review?
duplicated_orders = order_counts[order_counts['review_count'] > 1]

print(f"Ordini totali         : {len(order_counts)}")
print(f"Ordini con >1 review  : {len(duplicated_orders)}")
print(f"\nDistribuzione review per ordine:")
print(order_counts['review_count'].value_counts().sort_index())

# Se vuoi vedere i casi duplicati
if len(duplicated_orders) > 0:
    print(f"\nEsempio ordini duplicati:")
    print(df[df['order_id'].isin(duplicated_orders['order_id'].head(3))]
          [['order_id', 'review_score']].sort_values('order_id'))