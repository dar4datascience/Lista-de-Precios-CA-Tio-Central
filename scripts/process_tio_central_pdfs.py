from scripts.parse_images_utils import process_tio_central_pdf
from pathlib import Path

# Get all PDFs
lista_de_precios_por_semana = Path("lista_de_precios_por_semana")
lista_de_precios_por_semana_pdf_files = list(lista_de_precios_por_semana.rglob("*.pdf"))

# Run function in a regular for loop
for pdf_file in lista_de_precios_por_semana_pdf_files:
    process_tio_central_pdf(pdf_file)

print("Processing completed!")
