from parse_images_utils import *

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# List to store all parsed categories data
all_product_categories = []

# Main processing flow
pdf_path = "lista_de_precios_Vol_16.pdf"
images = extract_images_from_pdf(pdf_path)

# Extract and process images separately
for i, img_bytes in enumerate(images):
    # Save the image as JPG
    image_path = save_image_as_jpg(img_bytes, i + 1)
    
    # Apply OCR to the image
    ocr_text = ocr_image(img_bytes)

    if ocr_text:  # Only process if OCR text is NOT empty
        print(f"Extracted Text from Image {i + 1} (OCR):\n{ocr_text}\n")

        # Process and store each image's OCR text with Google Gemini
        structured_output = process_and_store_with_google_gemini(img_bytes)

        # Add the result of the function call to the list
        all_product_categories.append(structured_output.model_dump())


# Write all extracted and parsed data to a JSON file
output_file = "tio_central_precios_vol16_v2.json"
with open(output_file, "w") as json_file:
    json.dump(all_product_categories, json_file, indent=4)

print(f"Data has been stored in {output_file}")
