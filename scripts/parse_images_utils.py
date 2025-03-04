import json
import os
from pathlib import Path
from tqdm import tqdm
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
from dotenv import load_dotenv
from time import sleep

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    


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

from time import sleep
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to process and store with Google Gemini (with exponential backoff retry)
def process_and_store_with_google_gemini(image_bytes):
    # Prepare the image for Gemini
    image = Image.open(BytesIO(image_bytes))
    
    # Set up the Google Gemini API client using instructor
    client = instructor.from_gemini(
        client=genai.GenerativeModel(
            model_name="models/gemini-1.5-flash",  # Specify model
        ),
        mode=instructor.Mode.GEMINI_JSON,  # Set to Gemini JSON mode
    )

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
        category_name: Optional[
            Literal[
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
        ] = None
        products: Optional[List[Product]] = None

    # Exponential backoff variables
    retry_count = 0
    max_retries = 10
    retry_seconds = 60  # Start with 30 seconds for backoff

    while retry_count < max_retries:
        try:
            # Send the image byte data to Gemini API for analysis
            response = client.messages.create(
                messages=[
                    {"role": "user", "content": "Extract data from the table in this image and infer the product category from the product records found."},
                    {"role": "user", "content": image}  # Pass byte data as content
                ],
                response_model=ProductCategory,
                max_retries=2  # max retries for each call within the client
            )
            return response  # Return the response if the call is successful

        except Exception as ex:  # Catch any exception related to the API call
            logger.error(f"Error during Gemini API call: {str(ex)}")
            retry_count += 1
            if retry_count < max_retries:
                logger.info(f"Retrying in {retry_seconds} seconds...")
                sleep(retry_seconds)  # Wait before retrying
                retry_seconds *= 2  # Exponential backoff (doubling the wait time)
            else:
                logger.error(f"Exceeded maximum retries ({max_retries}) - unable to process the image.")
                raise  # Reraise the last exception after exceeding max retries

def save_image_as_jpg(image_bytes, image_num):
    image = Image.open(BytesIO(image_bytes))
    output_path = f"extracted_images/extracted_image_{image_num}.jpg"
    image.save(output_path, "JPEG")
    print(f"Image saved as {output_path}")
    return output_path

# save results into a dictionary by week
def process_tio_central_pdf(path_2_weekly_pdf):
    
    print(f"Processing {path_2_weekly_pdf}")
    
    # List to store all parsed categories data
    all_product_categories = []

    # Main processing flow
    images = extract_images_from_pdf(path_2_weekly_pdf)

    # Extract and process images separately with a progress bar
    for i, img_bytes in tqdm(enumerate(images), total=len(images), desc="Processing Images"):
        # Apply OCR to the image
        ocr_text = ocr_image(img_bytes)

        if len(ocr_text) > 100:  # Only process if OCR text is NOT empty
            # Process and store each image's OCR text with Google Gemini
            structured_output = process_and_store_with_google_gemini(img_bytes)
            sleep(10)

            # Add the result of the function call to the list
            all_product_categories.append(structured_output.model_dump())
    
    parent_folder = Path(path_2_weekly_pdf).parent
    
    datos_de_semana = parent_folder.name
    
    result = {datos_de_semana: all_product_categories}
    
    output_path = os.path.join(parent_folder,
                               f"precios_semana_{datos_de_semana}.json")
    
    with open(output_path, 'w') as json_file:
        json.dump(result, json_file, indent=4)

    print(f"Data has been written to {output_path}")

