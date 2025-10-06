# SQL Job Template

Use este diretório como base para criar jobs SQL mais complexos. Os passos sugeridos:

1. Copie `examples/sql-query/resources/sql_query_job.yml` para `resources/jobs/` do seu bundle e renomeie o job.
2. Ajuste o `query.file_path` para apontar para seus scripts SQL (podem estar nesta pasta ou em outra estrutura).
3. Configure parâmetros adicionais do `sql_task`:
   - `alert_id` para disparar alertas existentes.
   - `timeout_seconds` para impor limite de execução.
   - `retry_on_timeout` / `max_retries` conforme necessidade.
4. Certifique-se de definir `var.sql_warehouse_id` no `databricks.yml` com o ID do SQL Warehouse serverless usado pelo job.
5. Valide (`databricks bundle validate`) e execute (`databricks bundle run`) o novo job.

O arquivo `sql/refresh_users.sql` do exemplo anterior pode ser reutilizado aqui como ponto de partida.
