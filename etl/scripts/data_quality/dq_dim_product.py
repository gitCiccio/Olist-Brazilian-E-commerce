from etl.scripts.data_quality.dq_utils import build_dq_report, save_dq_report


def run_dq_dim_product(source_df, transformed_df, engine_dw):
    """
    Esegue i controlli di Data Quality per la dimensione 'dim_product'.
    - Verifica la presenza e la non nullità del `product_id` (chiave di business/naturale).
    - Controlla l'assenza di duplicati sulla chiave naturale nel DataFrame trasformato.

    :param source_df: DataFrame dei dati prodotti grezzi.
    :param transformed_df: DataFrame dei prodotti formattati.
    :param engine_dw: Connessione al Data Warehouse per verificare le righe caricate.
    :return: Il percorso al file di report JSON generato.
    """
    report = build_dq_report(
        job_name="dq_dim_product",
        source_df=source_df,
        transformed_df=transformed_df,
        engine_dw=engine_dw,
        loaded_table_name="dim_product",
        required_columns_source=["product_id"],
        required_columns_transformed=["natural_key"],
        business_key_columns_source=["product_id"],
        business_key_columns_transformed=["natural_key"]
    )
    return save_dq_report(report)