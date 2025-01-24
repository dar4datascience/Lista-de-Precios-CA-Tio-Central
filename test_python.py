from img2table.document import PDF
from img2table.ocr import TesseractOCR

src = "/home/duque/Documents/Lista-de-Precios-CA-Tio-Central/pdfs/lista de precios vol 9.pdf"

pdf = PDF(src, 
          pages=[2,3],
          detect_rotation=False,
          pdf_text_extraction=True)

# Instantiation of the OCR, Tesseract, which requires prior installation
ocr = TesseractOCR(lang="spa")

# Table identification and extraction
pdf_tables = pdf.extract_tables(ocr=ocr,
                                implicit_rows=True,
                                      borderless_tables=False,
                                      min_confidence=50)
