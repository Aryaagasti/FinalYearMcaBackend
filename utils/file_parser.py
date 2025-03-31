# utils/file_parser.py
import PyPDF2
from docx import Document
from io import BytesIO
import time

def parse_resume_file(file):
    """Extract text from a file (PDF or DOCX)."""
    try:
        start_time = time.time()
        
        if file.filename.endswith('.pdf'):
            # Extract text from PDF
            pdf_reader = PyPDF2.PdfReader(file)
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text()
        elif file.filename.endswith('.docx'):
            # Extract text from DOCX
            doc = Document(file)
            text = '\n'.join([para.text for para in doc.paragraphs])
        else:
            # Assume it's a text file
            text = file.read().decode('utf-8', errors='ignore')
        
        end_time = time.time()
        print(f"Time taken to parse resume: {end_time - start_time:.2f} seconds")
        return text
    except Exception as e:
        print(f"Error extracting text from file: {e}")
        return ""
