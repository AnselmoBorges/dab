# Databricks notebook source
# DBTITLE 1,Configura widgets de entrada
dbutils.widgets.text("catalog_name", "dab_dev", "Catalog Name")
dbutils.widgets.text("user_id", "3", "User ID")
dbutils.widgets.text("user_name", "Anselmo", "User Name")

# COMMAND ----------
# DBTITLE 1,Obtém valores informados
catalog_name = dbutils.widgets.get("catalog_name")
user_id = int(dbutils.widgets.get("user_id"))
user_name = dbutils.widgets.get("user_name")
print(f"Using Catalog: {catalog_name}")
print(f"Inserting user_id={user_id}, user_name={user_name}")

# COMMAND ----------
# DBTITLE 1,Cria tabela e insere dados de exemplo + parâmetro
spark.sql(
    f"CREATE TABLE IF NOT EXISTS {catalog_name}.dab_b.users (id INT, name STRING)"
)
spark.sql(
    f"INSERT OVERWRITE {catalog_name}.dab_b.users VALUES (1, 'Alice'), (2, 'Bob')"
)
spark.sql(
    f"INSERT INTO {catalog_name}.dab_b.users VALUES ({user_id}, '{user_name}')"
)

# COMMAND ----------
# DBTITLE 1,Lê os dados inseridos
result_df = spark.sql(f"SELECT * FROM {catalog_name}.dab_b.users ORDER BY id")
display(result_df)
