import duckdb
from pathlib import Path

# create a connection to a file called 'file.db'
#conn = duckdb.connect("ca_precios_tio_central.db")
#duckdb.sql("SELECT * FROM 'example.json'")

def process_json_with_duckdb(json_path: str) -> duckdb.DuckDBPyConnection:

    # Connect to DuckDB (in-memory for now)
    con = duckdb.connect(":memory:")
    
    # Processing
    print(json_path)
    
    # get week number to catch column name
    week_recorded = json_path.parent.name
    
    # Process the JSON entirely within DuckDB
    processed_query = f"""
---CREATE TABLE test_df_{week_recorded} AS 
    WITH base_table AS (
    SELECT UNNEST("{week_recorded}", recursive := true) 
    FROM read_json('{json_path}')
    ),
    expanded_table AS (
    SELECT 
    {week_recorded} AS week_recorded,
    category_name,
    UNNEST(products, recursive := true)
    FROM base_table
    ), 
    cleaned_data AS (
    -- First CTE: Handle cases like "190  > 972" or "190  < 972" to just the first number
    SELECT 
        week_recorded::INT64 AS week_recorded,
        category_name,
        COD AS codigo_de_articulo,
        ARTICULO AS articulo,
        DESCRIPCION AS descripcion,
        -- Clean up price columns by removing > and < and keeping only the first number
        REGEXP_REPLACE(PRECIO_MAS_ALTO, '(^\d+)(\s*[<>]+.*)', '\1') AS PRECIO_MAS_ALTO,
        REGEXP_REPLACE(PRECIO_MAS_BAJO, '(^\d+)(\s*[<>]+.*)', '\1') AS PRECIO_MAS_BAJO,
        REGEXP_REPLACE(PRECIO_POR_KILO, '(^\d+)(\s*[<>]+.*)', '\1') AS PRECIO_POR_KILO,
        REGEXP_REPLACE(PRECIO_POR_CAJA, '(^\d+)(\s*[<>]+.*)', '\1') AS PRECIO_POR_CAJA,
        REGEXP_REPLACE(PRECIO_ANTERIOR, '(^\d+)(\s*[<>]+.*)', '\1') AS PRECIO_ANTERIOR,
        REGEXP_REPLACE(USD, '(^\d+)(\s*[<>]+.*)', '\1') AS USD
    FROM expanded_table
),
final_cleaned_data AS (
    -- Second CTE: Remove unwanted symbols and "agotado" and clean numbers for conversion to DOUBLE
    SELECT
        week_recorded,
        category_name,
        codigo_de_articulo,
        articulo,
        descripcion,
        
        -- Apply transformations and ensure we only have valid numbers, replacing invalid entries with NULL
        TRY_CAST(
            NULLIF(
                TRIM(
                    REGEXP_REPLACE(
                        REGEXP_REPLACE(
                            REGEXP_REPLACE(PRECIO_MAS_ALTO, '[$,<>=>]', '', 'g'), -- Remove $, <, >, = signs
                            '(?i)agotado', ''  -- Remove "agotado" text (case insensitive)
                        ), 
                        '\s+', ' '  -- Replace multiple spaces with a single space
                    )
                ), 
            '') AS DOUBLE) AS PRECIO_MAS_ALTO,

        TRY_CAST(
            NULLIF(
                TRIM(
                    REGEXP_REPLACE(
                        REGEXP_REPLACE(
                            REGEXP_REPLACE(PRECIO_MAS_BAJO, '[$,<>=>]', '', 'g'), 
                            '(?i)agotado', ''
                        ), 
                        '\s+', ' '
                    )
                ), 
            '') AS DOUBLE) AS PRECIO_MAS_BAJO,

        TRY_CAST(
            NULLIF(
                TRIM(
                    REGEXP_REPLACE(
                        REGEXP_REPLACE(
                            REGEXP_REPLACE(PRECIO_POR_KILO, '[$,<>=>]', '', 'g'), 
                            '(?i)agotado', ''
                        ), 
                        '\s+', ' '
                    )
                ), 
            '') AS DOUBLE) AS PRECIO_POR_KILO,

        TRY_CAST(
            NULLIF(
                TRIM(
                    REGEXP_REPLACE(
                        REGEXP_REPLACE(
                            REGEXP_REPLACE(PRECIO_POR_CAJA, '[$,<>=>]', '', 'g'), 
                            '(?i)agotado', ''
                        ), 
                        '\s+', ' '
                    )
                ), 
            '') AS DOUBLE) AS PRECIO_POR_CAJA,

        TRY_CAST(
            NULLIF(
                TRIM(
                    REGEXP_REPLACE(
                        REGEXP_REPLACE(
                            REGEXP_REPLACE(PRECIO_ANTERIOR, '[$,<>=>]', '', 'g'), 
                            '(?i)agotado', ''
                        ), 
                        '\s+', ' '
                    )
                ), 
            '') AS DOUBLE) AS PRECIO_ANTERIOR,

        TRY_CAST(
            NULLIF(
                TRIM(
                    REGEXP_REPLACE(
                        REGEXP_REPLACE(
                            REGEXP_REPLACE(USD, '[$,<>=>]', '', 'g'), 
                            '(?i)agotado', ''
                        ), 
                        '\s+', ' '
                    )
                ), 
            '') AS DOUBLE) AS precio_usd

    FROM cleaned_data
)

SELECT * FROM final_cleaned_data
    """
    ejemplo_lista_ca = duckdb.sql(processed_query)
    
    result = duckdb.sql(f"SELECT * FROM ejemplo_lista_ca")
    print(result)
    result.write_parquet(
              "lista_de_precios_ca_tio_central.parquet", 
        compression="SNAPPY",        # Use Snappy compression 
        append=True,      
        partition_by=["week_recorded"] # Partition the data by "week_recorded" column
        )
    #print(con.fetchone())

    return ejemplo_lista_ca  # Return connection to allow further queries


# Specify the root folder where you want to start searching
root_folder = Path('lista_de_precios_por_semana')

# Use rglob to recursively find all .json files
precios_ca_json_files = list(root_folder.rglob('*.json'))

for json in precios_ca_json_files:
    process_json_with_duckdb(json)
    
    #print(result)
    
    
# final_result.write_parquet(
#           "example.parquet", 
#     compression="SNAPPY",        # Use Snappy compression
#     overwrite=False,         
#     partition_by=["week_recorded"] # Partition the data by "week_recorded" column
#     )

