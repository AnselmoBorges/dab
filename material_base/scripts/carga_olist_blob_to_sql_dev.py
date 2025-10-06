import os
import pandas as pd
import sqlalchemy
from urllib.parse import quote_plus

# Configurações do Azure SQL DEV
SQL_SERVER = 'sqlrescuedev.database.windows.net'
SQL_DATABASE = 'rescue'
SQL_USERNAME = 'engenharia'
SQL_PASSWORD = '1qaz@WSX3edc'
SQL_SCHEMA = 'olist'

# SAS Key e URL do Blob Storage
SAS_KEY = 'sp=r&st=2025-10-05T00:46:11Z&se=2025-10-05T09:01:11Z&spr=https&sv=2024-11-04&sr=c&sig=LJcu6qdO%2BLQxIbRnFG7un2zQQ7scSj%2FPSSxBhihFvoM%3D'
BLOB_URL = 'https://sarescuedev.blob.core.windows.net/staging/olist'

# Lista de arquivos CSV
csv_files = [
    'customers.csv',
    'geolocation.csv',
    'order_items.csv',
    'order_payments.csv',
    'order_reviews.csv',
    'orders.csv',
    'product_category_name_translation.csv',
    'products.csv',
    'sellers.csv'
]

# String de conexão SQLAlchemy
conn_str = f"mssql+pyodbc://{SQL_USERNAME}:{quote_plus(SQL_PASSWORD)}@{SQL_SERVER}:1433/{SQL_DATABASE}?driver=ODBC+Driver+17+for+SQL+Server"
engine = sqlalchemy.create_engine(conn_str)

with engine.connect() as conn:
    conn.execute(sqlalchemy.text(f"IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = '{SQL_SCHEMA}') CREATE SCHEMA {SQL_SCHEMA};"))
    conn.execute(sqlalchemy.text(f"IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = '{SQL_SCHEMA_README}') CREATE SCHEMA {SQL_SCHEMA_README};"))

for csv_file in csv_files:
    print(f'Processando {csv_file}...')
    url = f"{BLOB_URL}/{csv_file}?{SAS_KEY}"
    df = pd.read_csv(url)
    table_name = csv_file.replace('.csv', '')
    # Cria tabela se não existir, tipos automáticos
    df.to_sql(table_name, engine, schema=SQL_SCHEMA, if_exists='replace', index=False)
    print(f'Tabela {SQL_SCHEMA}.{table_name} criada e dados inseridos.')

print('Carga concluída no DEV!')
