import duckdb
from pathlib import Path

# Persistent DuckDB Connection
db_path = "ca_precios_tio_central.duckdb"
con = duckdb.connect(db_path)

# Create a persistent table to store all data across JSON files
con.execute("""
CREATE OR REPLACE TABLE precios_tio_central (
    week_recorded BIGINT,
    category_name STRING,
    codigo_de_articulo STRING, 
    articulo STRING,
    descripcion STRING,
    PRECIO_MAS_ALTO BIGINT, 
    PRECIO_MAS_BAJO BIGINT,
    PRECIO_POR_KILO BIGINT,
    PRECIO_POR_CAJA BIGINT, 
    PRECIO_ANTERIOR BIGINT,
    precio_usd BIGINT
);
""")

def process_json_with_duckdb(json_path: Path, con: duckdb.DuckDBPyConnection):
    week_recorded = json_path.parent.name

    processed_query = f"""
    WITH base_table AS (
        SELECT UNNEST("{week_recorded}", recursive := true) 
        FROM read_json('{json_path}')
    ),
    expanded_table AS (
        SELECT 
            '{week_recorded}' AS week_recorded,
            category_name,
            UNNEST(products, recursive := true)
        FROM base_table
    ), 
    cleaned_data AS (
        SELECT 
            week_recorded::INT64 AS week_recorded,
            category_name,
            COD AS codigo_de_articulo,
            ARTICULO AS articulo,
            DESCRIPCION AS descripcion,
            REGEXP_REPLACE(PRECIO_MAS_ALTO, '(^\d+)(\s*[<>]+.*)', '\1') AS PRECIO_MAS_ALTO,
            REGEXP_REPLACE(PRECIO_MAS_BAJO, '(^\d+)(\s*[<>]+.*)', '\1') AS PRECIO_MAS_BAJO,
            REGEXP_REPLACE(PRECIO_POR_KILO, '(^\d+)(\s*[<>]+.*)', '\1') AS PRECIO_POR_KILO,
            REGEXP_REPLACE(PRECIO_POR_CAJA, '(^\d+)(\s*[<>]+.*)', '\1') AS PRECIO_POR_CAJA,
            REGEXP_REPLACE(PRECIO_ANTERIOR, '(^\d+)(\s*[<>]+.*)', '\1') AS PRECIO_ANTERIOR,
            REGEXP_REPLACE(USD, '(^\d+)(\s*[<>]+.*)', '\1') AS USD
        FROM expanded_table
    ),
    final_cleaned_data AS (
        SELECT
            week_recorded,
            category_name,
            codigo_de_articulo,
            articulo,
            descripcion,
            TRY_CAST(NULLIF(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(REGEXP_REPLACE(PRECIO_MAS_ALTO, '[$,<>=>]', '', 'g'), '(?i)agotado', ''), '\s+', ' ')), '') AS DOUBLE) AS PRECIO_MAS_ALTO,
            TRY_CAST(NULLIF(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(REGEXP_REPLACE(PRECIO_MAS_BAJO, '[$,<>=>]', '', 'g'), '(?i)agotado', ''), '\s+', ' ')), '') AS DOUBLE) AS PRECIO_MAS_BAJO,
            TRY_CAST(NULLIF(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(REGEXP_REPLACE(PRECIO_POR_KILO, '[$,<>=>]', '', 'g'), '(?i)agotado', ''), '\s+', ' ')), '') AS DOUBLE) AS PRECIO_POR_KILO,
            TRY_CAST(NULLIF(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(REGEXP_REPLACE(PRECIO_POR_CAJA, '[$,<>=>]', '', 'g'), '(?i)agotado', ''), '\s+', ' ')), '') AS DOUBLE) AS PRECIO_POR_CAJA,
            TRY_CAST(NULLIF(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(REGEXP_REPLACE(PRECIO_ANTERIOR, '[$,<>=>]', '', 'g'), '(?i)agotado', ''), '\s+', ' ')), '') AS DOUBLE) AS PRECIO_ANTERIOR,
            TRY_CAST(NULLIF(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(REGEXP_REPLACE(USD, '[$,<>=>]', '', 'g'), '(?i)agotado', ''), '\s+', ' ')), '') AS DOUBLE) AS precio_usd
        FROM cleaned_data
    )

    INSERT INTO precios_tio_central 
    SELECT * FROM final_cleaned_data;
    """

    con.execute(processed_query)

# Process all JSON files and append data
root_folder = Path('lista_de_precios_por_semana')
precios_ca_json_files = list(root_folder.rglob('*.json'))

for json_file in precios_ca_json_files:
    print(f"Processing.... {json_file}")
    process_json_with_duckdb(json_file, con)

# Write all data to a single Parquet file after processing
con.execute("""
    COPY (SELECT * FROM precios_tio_central) 
    TO 'lista_de_precios_ca_tio_central.parquet' 
    (FORMAT PARQUET, COMPRESSION 'SNAPPY')
""")

# Close the connection
con.close()
