import PyPDF2
from docx import Document
import time

def parse_resume_file(file):
    """Extract text from a file (PDF or DOCX) with improved error handling."""
    try:
        start_time = time.time()
        text = ""

        if file.filename.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        elif file.filename.endswith('.docx'):
            doc = Document(file)
            text = '\n'.join([para.text for para in doc.paragraphs if para.text.strip()])
        else:
            text = file.read().decode('utf-8', errors='ignore')

        end_time = time.time()
        print(f"Time taken to parse resume: {end_time - start_time:.2f} seconds")
        
        if not text.strip():
            raise ValueError("Failed to extract text from resume. Ensure the document is not empty or scanned.")

        return text.strip()

    except Exception as e:
        print(f"Error extracting text from file: {e}")
        return ""
