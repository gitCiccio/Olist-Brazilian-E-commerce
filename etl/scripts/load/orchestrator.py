from sqlalchemy import create_engine

from etl.scripts.load.load.load_dim_customer import run_load_dim_customer
from etl.scripts.load.load.load_dim_date import run_load_dim_date
from etl.scripts.load.load.load_dim_payment import run_load_dim_payment
from etl.scripts.load.load.load_dim_product import run_load_dim_product
from etl.scripts.load.load.load_dim_seller import run_load_dim_seller
from etl.scripts.load.load.load_fact_sale_item import run_load_fact_sale_item
from logger.logger import AppLogger


log = AppLogger(name="dw.orchestrator", log_file="dw_load.log")

from sqlalchemy import text

def run_dw_pipeline(engine_read, engine_write) -> None:
    log.info("[dw.orchestrator] Pipeline started")

    with engine_write.begin() as conn:
        conn.execute(text("""
            TRUNCATE TABLE
                fact_sale_item,
                dim_payment,
                dim_product,
                dim_seller,
                dim_customer,
                dim_date
            CASCADE
        """))

        run_load_dim_date(engine_read, conn)
        run_load_dim_customer(engine_read, conn)
        run_load_dim_seller(engine_read, conn)
        run_load_dim_product(engine_read, conn)
        run_load_dim_payment(engine_read, conn)
        run_load_fact_sale_item(engine_read, conn)

    log.info("[dw.orchestrator] Pipeline completed")
