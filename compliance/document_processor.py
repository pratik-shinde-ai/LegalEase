import PyPDF2
import docx
from PIL import Image
import pytesseract
import io
import fitz  # PyMuPDF

def extract_text_from_pdf(file_path):
    text = ''
    try:
        pdf_document = fitz.open(file_path)
    except Exception as e:
        raise ValueError(f"Error opening PDF file: {e}")

    for page_num in range(len(pdf_document)):
        try:
            page = pdf_document[page_num]
            text += page.get_text()
            
            # Extract images from the PDF page
            for img in page.get_images(full=True):
                xref = img[0]
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]
                image = Image.open(io.BytesIO(image_bytes))
                text += '\n' + pytesseract.image_to_string(image)
        except Exception as e:
            print(f"Error processing page {page_num}: {e}")
            continue

    pdf_document.close()
    return text

def extract_text_from_docx(file_path):
    text = ''
    try:
        doc = docx.Document(file_path)
    except Exception as e:
        raise ValueError(f"Error opening DOCX file: {e}")

    for para in doc.paragraphs:
        text += para.text + '\n'

    # Extract images from DOCX
    for rel in doc.part.rels.values():
        try:
            if "image" in rel.target_ref:
                image_part = rel.target_part
                image = Image.open(io.BytesIO(image_part.blob))
                text += '\n' + pytesseract.image_to_string(image)
        except Exception as e:
            print(f"Error processing image in DOCX: {e}")
            continue

    return text

def process_document(file_path):
    if file_path.endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        return extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format")
