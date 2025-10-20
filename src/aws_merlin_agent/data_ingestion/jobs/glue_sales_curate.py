from __future__ import annotations

import argparse

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date


def transform(input_path: str, output_path: str) -> None:
    """
    Glue ETL job that reads raw seller payloads, normalizes schema, and writes Parquet partitions.

    Expected input is newline-delimited JSON produced by the ingestion Lambda.
    """
    spark = SparkSession.builder.appName("MerlinSalesCurate").getOrCreate()

    df = spark.read.json(input_path)
    curated_df = (
        df.withColumn("sale_date", to_date(col("date")))
        .withColumnRenamed("net_revenue", "net_revenue_usd")
        .withColumnRenamed("ad_spend", "ad_spend_usd")
    )

    curated_df.write.mode("overwrite").partitionBy("sale_date").parquet(output_path)
    spark.stop()


def main() -> None:
    parser = argparse.ArgumentParser(description="MERLIN Glue ETL for sales payloads.")
    parser.add_argument("--input", required=True, help="S3 path to landing zone JSON (e.g., s3://bucket/landing/*)")
    parser.add_argument("--output", required=True, help="S3 path to curated Parquet dataset")
    args = parser.parse_args()
    transform(args.input, args.output)


if __name__ == "__main__":
    main()
