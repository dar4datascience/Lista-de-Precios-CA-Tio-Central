import json
import pandas as pd

# Load the extracted JSON data
json_file = "tio_central_precios_vol16_v2.json"
with open(json_file, "r") as f:
    all_product_categories = json.load(f)

# Prepare a list to store flattened product data
flattened_data = []

# Process each category entry
for category in all_product_categories:
    category_name = category.get("category_name", "Unknown")  # Handle missing category

    # Ensure products exist and are not empty
    products = category.get("products", [])
    if not products:  # Skip if products list is empty or missing
        continue

    for product in products:
        if not any(product.values()):  # Skip empty product records
            continue

        flattened_data.append({
            "product_category": category_name,
            "COD": product.get("COD"),
            "ARTICULO": product.get("ARTICULO"),
            "DESCRIPCION": product.get("DESCRIPCION"),
            "PRECIO_MAS_ALTO": product.get("PRECIO_MAS_ALTO"),
            "PRECIO_MAS_BAJO": product.get("PRECIO_MAS_BAJO"),
            "PRECIO_POR_KILO": product.get("PRECIO_POR_KILO"),
            "PRECIO_POR_CAJA": product.get("PRECIO_POR_CAJA"),
            "PRECIO_ANTERIOR": product.get("PRECIO_ANTERIOR"),
            "USD": product.get("USD")
        })

# Convert to a DataFrame if there are valid records
if flattened_data:
    df = pd.DataFrame(flattened_data)

    # Save as CSV
    csv_file = "tio_central_precios_vol16_v2.csv"
    df.to_csv(csv_file, index=False, encoding="utf-8")
    
    print(f"CSV file saved as {csv_file}")
else:
    print("No valid product data found. CSV file was not created.")
