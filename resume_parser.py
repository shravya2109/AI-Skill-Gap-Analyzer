import os
import PyPDF2
import docx

def extract_text_from_pdf(file):
    """Extract text from a PDF file."""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def extract_text_from_docx(file):
    """Extract text from a DOCX file."""
    try:
        doc = docx.Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        return f"Error reading DOCX: {str(e)}"

def extract_text_from_txt(file):
    """Extract text from a TXT file."""
    try:
        return file.read().decode("utf-8")
    except Exception as e:
        return f"Error reading TXT: {str(e)}"

def parse_resume(uploaded_file):
    """
    Main function to parse uploaded resume file.
    Returns extracted text as string.
    """
    if uploaded_file is None:
        return ""
    
    file_type = uploaded_file.name.split('.')[-1].lower()
    
    if file_type == 'pdf':
        return extract_text_from_pdf(uploaded_file)
    elif file_type == 'docx':
        return extract_text_from_docx(uploaded_file)
    elif file_type == 'txt':
        return extract_text_from_txt(uploaded_file)
    else:
        return "Unsupported file format. Please upload PDF, DOCX, or TXT."
