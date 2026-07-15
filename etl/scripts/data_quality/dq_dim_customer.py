from etl.scripts.data_quality.dq_utils import build_dq_report, save_dq_report


def run_dq_dim_customer(source_df, transformed_df, engine_dw):
    """
    Esegue i controlli di Data Quality per la dimensione 'dim_customer'.
    - Verifica la completezza delle colonne obbligatorie (id, regione, città, stato).
    - Controlla l'unicità della business key (`customer_unique_id` prima e `natural_key` poi).
    - Valida i domini di `customer_state` affinché contengano solo le sigle corrette degli stati brasiliani o 'XX'.

    :param source_df: DataFrame dei dati estratti da reconciled.
    :param transformed_df: DataFrame dei dati trasformati prima del caricamento.
    :param engine_dw: Connessione al Data Warehouse per verificare le righe caricate.
    :return: Il percorso al file di report JSON generato.
    """
    report = build_dq_report(
        job_name="dq_dim_customer",
        source_df=source_df,
        transformed_df=transformed_df,
        engine_dw=engine_dw,
        loaded_table_name="dim_customer",
        required_columns_source=["customer_unique_id", "customer_region", "customer_city", "customer_state"],
        required_columns_transformed=["natural_key", "customer_region", "customer_city", "customer_state"],
        business_key_columns_source=["customer_unique_id"],
        business_key_columns_transformed=["natural_key"],
        allowed_values_transformed={
            "customer_state": [
                "AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG",
                "PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO","XX"
            ]
        }
    )
    return save_dq_report(report)