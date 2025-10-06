CREATE TABLE IF NOT EXISTS ${catalog_name}.dab_s.users_sql AS
SELECT id, name FROM ${catalog_name}.dab_b.users
;
