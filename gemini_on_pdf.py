import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from io import BytesIO
import google.generativeai as genai
import os

from app_utils import load_dotenv

load_dotenv()

# Set up the Google Gemini API client
# client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

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
    text = pytesseract.image_to_string(image)
    return text

# Function to save extracted images as .jpg
def save_image_as_jpg(image_bytes, image_num):
    image = Image.open(BytesIO(image_bytes))
    output_path = f"extracted_images/extracted_image_{image_num}.jpg"
    image.save(output_path, "JPEG")
    print(f"Image saved as {output_path}")

# Function to use Google Gemini for content generation or refinement
def process_with_google_gemini(ocr_text):
    response = client.models.generate_content(
        model="gemini-1.5-flash-002",  # You can use different models like "gemini-2.0-flash"
        contents=ocr_text
    )
    return response.text

# Main processing flow
pdf_path = "lista de precios Vol. 16.pdf"
images = extract_images_from_pdf(pdf_path)

# Save images and apply OCR on them
for i, img_bytes in enumerate(images):
    # Save the image as JPG
    save_image_as_jpg(img_bytes, i + 1)
    
    # Apply OCR to the image
    ocr_text = ocr_image(img_bytes)
    print(f"Extracted Text from Image {i + 1} (OCR):")
    print(ocr_text)

    # Optionally, process the OCR text with Google Gemini (uncomment if needed)
    # response_text = process_with_google_gemini(ocr_text)
    # print(f"Processed Content from Google Gemini:")
    # print(response_text)

# among the images found sound are not tables but images for the style of the pdf
# llm aware to make sure it doesnt consider these.

# Metadata: quien "cortesia" saber precios de ciertos productos
# los precios de cortesia nos dicen QUE LOCAL OFRECE ESOS PRECIOS


# are columns the same for sections? not always may change per category
# enumarete sections to associate with order of tables
# frutas y verduras
# FLores y hortalizas
# zona de subasta gourmet
# especias, semillas y chiles secos
# pescados y mariscos
# carnicos
# CARNICOS PARA TAQUERIAS
# cremeria y salchichoneria
# botanas
# avicola
# abarrotes
#

# del archivo pdf parece que estan registrando 543 productos
