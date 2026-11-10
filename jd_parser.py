import os
from resume_parser import extract_text_from_pdf, extract_text_from_docx, extract_text_from_txt

def parse_jd(uploaded_file_or_text):
    """
    Parses Job Description from either a file upload or raw text.
    """
    if isinstance(uploaded_file_or_text, str):
        return uploaded_file_or_text
    
    if uploaded_file_or_text is None:
        return ""

    file_type = uploaded_file_or_text.name.split('.')[-1].lower()
    
    if file_type == 'pdf':
        return extract_text_from_pdf(uploaded_file_or_text)
    elif file_type == 'docx':
        return extract_text_from_docx(uploaded_file_or_text)
    elif file_type == 'txt':
        return extract_text_from_txt(uploaded_file_or_text)
    else:
        return "Unsupported file format for JD."
