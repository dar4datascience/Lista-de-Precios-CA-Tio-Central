import json
import os
from dotenv import load_dotenv
from pydantic import BaseModel
import instructor
import google.generativeai as genai
from PIL import Image
import pytesseract
from io import BytesIO
import fitz  # PyMuPDF

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
# Set up the Google Gemini API client
client = instructor.from_gemini(
    client=genai.GenerativeModel(
        model_name="models/gemini-1.5-flash-latest",
        
    ),
    mode=instructor.Mode.GEMINI_JSON,
)

from typing import Optional
from pydantic import BaseModel

# Define the product data model using Pydantic with optional fields
class Product(BaseModel):
    COD: Optional[str] = None
    ARTICULO: Optional[str] = None
    DESCRIPCION: Optional[str] = None
    PRECIO_MAS_ALTO: Optional[str] = None
    PRECIO_MAS_BAJO: Optional[str] = None
    PRECIO_POR_KILO: Optional[str] = None
    PRECIO_POR_CAJA: Optional[str] = None
    PRECIO_ANTERIOR: Optional[str] = None
    USD: Optional[str] = None

class ProductCategory(BaseModel):
    category_name: Optional[str] = None
    products: Optional[list[Product]] = None

# Function to extract images from a PDF
def extract_images_from_pdf(pdf_path):
    pdf_document = fitz.open(pdf_path)
    images = []
    
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        image_list = page.get_images(full=True)
        
        for image_index, img in enumerate(image_list):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            images.append(image_bytes)
    
    return images

# Function to apply OCR on an image
def ocr_image(image_bytes):
    image = Image.open(BytesIO(image_bytes))
    text = pytesseract.image_to_string(image).strip()  # Remove leading/trailing whitespace
    return text

# Function to process and store with Google Gemini (single call)
def process_and_store_with_google_gemini(ocr_text):
    prompt = f"""
    You are tasked with extracting and storing data from OCR text that contains product categories and related pricing information. The categories include:
    frutas y verduras, FLores y hortalizas, zona de subasta gourmet, especias, semillas y chiles secos, 
    pescados y mariscos, carnicos, CARNICOS PARA TAQUERIAS, cremeria y salchichoneria, botanas, avicola, abarrotes.

    Each product category contains the following columns:
    - COD
    - ARTICULO
    - DESCRIPCION
    - PRECIO MAS ALTO
    - PRECIO MAS BAJO
    - PRECIO POR KILO
    - PRECIO POR CAJA
    - PRECIO ANTERIOR
    - USD

    The "PRECIO" columns are in **MXN (Mexican Pesos)**. Your task is to parse the extracted OCR text, extract the relevant details, and store the information in a structured format. 
    For each product category, store the following data:
    - The name of the category
    - A list of products in the category with each product's attributes (COD, ARTICULO, DESCRIPCION, PRECIO MAS ALTO, PRECIO MAS BAJO, PRECIO POR KILO, PRECIO POR CAJA, PRECIO ANTERIOR, USD)

    Please process the following OCR extracted text:
    {ocr_text}
    """

    response = client.messages.create(
        messages=[
            {"role": "user", "content": prompt}
        ],
        response_model=ProductCategory,
        max_retries=3
    )
    
    return response

def save_image_as_jpg(image_bytes, image_num):
    image = Image.open(BytesIO(image_bytes))
    output_path = f"extracted_images/extracted_image_{image_num}.jpg"
    image.save(output_path, "JPEG")
    print(f"Image saved as {output_path}")

# List to store all parsed categories data
all_product_categories = []

# Main processing flow
pdf_path = "lista_de_precios_Vol_16.pdf"
images = extract_images_from_pdf(pdf_path)

# Extract OCR texts from all images and process them separately
for i, img_bytes in enumerate(images):
    # Save the image as JPG
    save_image_as_jpg(img_bytes, i + 1)
    
    # Apply OCR to the image
    ocr_text = ocr_image(img_bytes)

    if ocr_text:  # Only process if OCR text is NOT empty
        print(f"Extracted Text from Image {i + 1} (OCR):\n{ocr_text}\n")

        # Process and store each image's OCR text with Google Gemini
        structured_output = process_and_store_with_google_gemini(ocr_text)

        # Add the result of the function call to the list
        all_product_categories.append(structured_output.model_dump())

# Write all extracted and parsed data to a JSON file
output_file = "tio_central_precios_vol16.json"
with open(output_file, "w") as json_file:
    json.dump(all_product_categories, json_file, indent=4)

print(f"Data has been stored in {output_file}")
