# Databricks notebook source

# COMMAND ----------
dbutils.widgets.text("catalog_name", "dab_dev", "Catalog Name")

# COMMAND ----------
catalog_name = dbutils.widgets.get("catalog_name")

# COMMAND ----------
spark.sql(
    f"CREATE TABLE IF NOT EXISTS {catalog_name}.dab_b.users_notebook (id INT, name STRING)"
)
spark.sql(
    f"INSERT OVERWRITE {catalog_name}.dab_b.users_notebook VALUES (1, 'Alice'), (2, 'Bob')"
)

# COMMAND ----------
out_df = spark.sql(f"SELECT * FROM {catalog_name}.dab_b.users_notebook ORDER BY id")
display(out_df)
