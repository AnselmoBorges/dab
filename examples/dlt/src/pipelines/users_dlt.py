# Databricks notebook source

import dlt
from pyspark.sql.functions import current_timestamp

CATALOG_NAME = spark.conf.get("catalog_name", "dab_dev")

@dlt.table(comment="Bronze users ingested via DLT")
def bronze_users():
    return spark.table(f"{CATALOG_NAME}.dab_b.users")

@dlt.table(comment="Gold users with ingestion timestamp")
def gold_users():
    df = dlt.read("bronze_users")
    return df.withColumn("loaded_at", current_timestamp())
