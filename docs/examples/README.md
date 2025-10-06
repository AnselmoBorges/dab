# Exemplos de Jobs com Databricks Asset Bundles

Este diretório complementa o guia principal com exemplos práticos de recursos que podem ser descritos via Asset Bundles. Cada pasta contém artefatos prontos (código + YAML) e instruções resumidas para adaptação.

> **Importante:** os arquivos `resources/*.yml` aqui não são carregados automaticamente pelo bundle principal. Copie-os (ou referencie-os via `include`) e ajuste as variáveis necessárias antes de executar.

## Estrutura

```
examples/
├── python-notebook/
├── dbt/
├── sql-query/
├── sql-job/
└── dlt/
```

## 1. Notebook Python (`examples/python-notebook`)
- Notebook: `src/notebooks/users_ingest.py`.
- Job: `resources/notebook_job.yml` (tarefa `notebook_task`, compute serverless via fila).
- Como usar:
  1. Copie o YAML para `resources/jobs/` do seu bundle.
  2. Garanta que `var.catalog_name` esteja definido.
  3. Execute `databricks bundle run notebook_job_example -t dev`.

## 2. DBT (`examples/dbt`)
- Projeto: `dbt_project.yml` + modelos em `src/models/`.
- Job: `resources/dbt_job.yml` com `dbt_task` e `warehouse_id` parametrizado (`${var.sql_warehouse_id}`).
- Ajustes necessários:
  - Adicionar `sql_warehouse_id` ao `databricks.yml` (ID de um SQL Warehouse serverless).
  - Definir variáveis de ambiente para o `profiles.yml` conforme o padrão da equipe.
- Execução: `databricks bundle run dbt_job_example -t dev --params sql_warehouse_id=<warehouse-id>`.

## 3. SQL Query (`examples/sql-query`)
- Script SQL: `sql/refresh_users.sql` (usa variável `catalog_name`).
- Job: `resources/sql_query_job.yml` com `sql_task` apontando para o arquivo e `warehouse_id` parametrizado.
- Requer `var.sql_warehouse_id` no `databricks.yml`.

## 4. SQL Job (`examples/sql-job`)
- Base para jobs SQL que combinam múltiplas queries ou tarefas sequenciais (por exemplo, dashboards, alertas ou cargas batch).
- Duplique o exemplo de `sql-query` e ajuste nomes, arquivos SQL, alertas e `warehouse_id` conforme a necessidade.

## 5. Pipelines DLT (`examples/dlt`)
- Pipeline: `resources/dlt_pipeline.yml` descreve um pipeline Delta Live Tables com duas tabelas (bronze → gold).
- Notebook DLT: `src/pipelines/users_dlt.py` (usa APIs `dlt.table`).
- Ajustes:
  - Adicione `resources/pipelines/*.yml` ao `include` do seu bundle.
  - Valide o runtime suportado (`spark_version` / `node_type_id`) para serverless DLT.
  - Comandos sugeridos: `databricks bundle deploy -t dev --only pipelines/users_dlt_pipeline` e, depois, `databricks bundle run pipelines/users_dlt_pipeline -t dev`.

## Recomendações Gerais
- Sempre execute `databricks bundle validate -t <target>` após copiar um exemplo.
- Prefira variáveis (`${var.*}`) para hosts, catálogos e IDs de compute.
- Para SQL Warehouses, trate os IDs como segredos (Azure DevOps Variable Group/Key Vault).
- Versione adaptações locais para garantir rastreabilidade.
