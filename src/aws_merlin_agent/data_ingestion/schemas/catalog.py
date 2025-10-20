from __future__ import annotations

from aws_merlin_agent.config.settings import EnvironmentSettings


def sales_fact_sql() -> str:
    """Return the Athena DDL for the curated sales fact table."""
    settings = EnvironmentSettings.load()
    return f"""
    CREATE EXTERNAL TABLE IF NOT EXISTS sales_fact (
        seller_id string,
        sku string,
        date string,
        units_sold int,
        net_revenue_usd double,
        ad_spend_usd double,
        inventory_on_hand int
    )
    PARTITIONED BY (sale_date date)
    STORED AS PARQUET
    LOCATION 's3://{settings.curated_bucket}/sales_fact/';
    """
