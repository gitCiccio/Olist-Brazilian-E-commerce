from etl.scripts.data_quality.dq_utils import build_dq_report, save_dq_report


def run_dq_fact_sale_item(source_df, transformed_df, engine_dw):
    """
    Esegue i controlli di Data Quality per la fact table 'fact_sale_item'.
    - Verifica la completezza delle chiavi di ordine, item e riferimenti dimensionali.
    - Controlla l'unicità della chiave naturale composta (`order_id` + `order_item_id`).
    - Valida i range numerici di prezzi e costi di trasporto (non negativi).

    :param source_df: DataFrame dei dati item grezzi.
    :param transformed_df: DataFrame dei dati item trasformati.
    :param engine_dw: Connessione al Data Warehouse.
    :return: Il percorso al file di report JSON generato.
    """
    report = build_dq_report(
        job_name="dq_fact_sale_item",
        source_df=source_df,
        transformed_df=transformed_df,
        engine_dw=engine_dw,
        loaded_table_name="fact_sale_item",
        required_columns_source=[
            "order_id", "order_item_id", "product_natural_key",
            "customer_natural_key", "seller_natural_key", "purchase_date"
        ],
        required_columns_transformed=[
            "natural_key", "order_id", "order_item_id", "product_natural_key",
            "customer_natural_key", "seller_natural_key", "purchase_date"
        ],
        business_key_columns_source=["order_id", "order_item_id"],
        business_key_columns_transformed=["natural_key"],
        numeric_ranges_transformed={
            "price": {"min": 0, "max": None},
            "freight_value": {"min": 0, "max": None},
            "item_count": {"min": 1, "max": None}
        }
    )
    return save_dq_report(report)