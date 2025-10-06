{{ config(materialized='table') }}

SELECT
  id,
  name,
  current_timestamp() AS run_ts
FROM {{ source('dab_training', 'users_source') }}
