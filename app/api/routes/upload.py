# Indian Law RAG Chatbot - File Upload Routes
"""
Endpoints for uploading and processing case documents.
Supports PDF, DOCX, and TXT files.
"""

import logging
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["Upload"])


class UploadResponse(BaseModel):
    """Response schema for file upload."""
    success: bool
    file_id: str
    filename: str
    file_type: str
    text_content: str
    text_length: int
    message: str


# Supported file types
ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.doc', '.docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file using PyMuPDF."""
    try:
        import fitz  # PyMuPDF
        
        doc = fitz.open(stream=file_content, filetype="pdf")
        text_parts = []
        
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text_parts.append(page.get_text())
        
        doc.close()
        return "\n\n".join(text_parts)
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to extract text from PDF: {str(e)}"
        )


def extract_text_from_txt(file_content: bytes) -> str:
    """Extract text from TXT file."""
    try:
        # Try UTF-8 first, then fallback to latin-1
        try:
            return file_content.decode('utf-8')
        except UnicodeDecodeError:
            return file_content.decode('latin-1')
    except Exception as e:
        logger.error(f"TXT extraction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to read text file: {str(e)}"
        )


def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file."""
    try:
        import io
        from zipfile import ZipFile
        from xml.etree import ElementTree
        
        # DOCX is a ZIP file with XML content
        with ZipFile(io.BytesIO(file_content)) as zf:
            xml_content = zf.read('word/document.xml')
            tree = ElementTree.fromstring(xml_content)
            
            # Extract text from all paragraph elements
            namespaces = {
                'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
            }
            
            text_parts = []
            for paragraph in tree.findall('.//w:p', namespaces):
                texts = paragraph.findall('.//w:t', namespaces)
                para_text = ''.join([t.text or '' for t in texts])
                if para_text.strip():
                    text_parts.append(para_text)
            
            return '\n\n'.join(text_parts)
    except Exception as e:
        logger.error(f"DOCX extraction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to extract text from DOCX: {str(e)}"
        )


@router.post("", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...)
):
    """
    Upload a case document for analysis.
    
    Supported formats:
    - PDF (.pdf)
    - Text (.txt)
    - Word Document (.doc, .docx)
    
    Args:
        file: The uploaded file
        
    Returns:
        UploadResponse: Contains extracted text and file metadata
    """
    # Validate file extension
    filename = file.filename or "unknown"
    file_ext = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
    
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{file_ext}' not supported. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content
    file_content = await file.read()
    
    # Check file size
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)} MB"
        )
    
    # Extract text based on file type
    if file_ext == '.pdf':
        text_content = extract_text_from_pdf(file_content)
        file_type = 'PDF'
    elif file_ext == '.txt':
        text_content = extract_text_from_txt(file_content)
        file_type = 'TXT'
    elif file_ext in ['.doc', '.docx']:
        text_content = extract_text_from_docx(file_content)
        file_type = 'DOCX'
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file_ext}"
        )
    
    # Validate extracted text
    if not text_content.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No text content could be extracted from the file"
        )
    
    # Generate file ID
    file_id = str(uuid4())
    
    logger.info(f"Uploaded file: {filename} ({file_type}), extracted {len(text_content)} chars")
    
    return UploadResponse(
        success=True,
        file_id=file_id,
        filename=filename,
        file_type=file_type,
        text_content=text_content,
        text_length=len(text_content),
        message=f"Successfully extracted {len(text_content)} characters from {filename}"
    )
