import json
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional, Literal, List
import instructor
import google.generativeai as genai
from PIL import Image
import pytesseract
from io import BytesIO
import fitz  # PyMuPDF
from google.genai import types

import PIL.Image

# Function to apply OCR on an image
def ocr_image(image_bytes):
    image = Image.open(BytesIO(image_bytes))
    text = pytesseract.image_to_string(image).strip()  # Remove leading/trailing whitespace
    return text


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

# Function to process and store with Google Gemini (single call)
def process_and_store_with_google_gemini(image_bytes):
    # Prepare the image for Gemini
    image = Image.open(BytesIO(image_bytes))

    # Convert image to byte data for the API
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format="PNG")
    
    # Set up the Google Gemini API client using instructor
    client = instructor.from_gemini(
        client=genai.GenerativeModel(
            model_name="models/gemini-1.5-flash",  # Specify model
        ),
        mode=instructor.Mode.GEMINI_JSON,  # Set to Gemini JSON mode
    )


    # Define allowed categories
    AllowedCategories = Literal[
        "Frutas y Verduras",
        "Flores y Hortalizas",
        "Zona de Subasta Gourmet",
        "Especias, Semillas y Chiles Secos",
        "Pescados y Mariscos",
        "Cárnicos",
        "Cárnicos para Taquerías",
        "Cremería y Salchichonería",
        "Botanas",
        "Avícola",
        "Abarrotes"
    ]

    # Define the product data model
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

    # Define the category model with restricted category names
    class ProductCategory(BaseModel):
        category_name: Optional[AllowedCategories] = None
        products: Optional[List[Product]] = None


    # Send the image byte data to Gemini API for analysis
    response = client.messages.create(
        messages=[
            {"role": "user", "content": "Extract data from the table in this image and infer the product category from the product records found."},
            {"role": "user", "content": image}  # Pass byte data as content
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
    return output_path
