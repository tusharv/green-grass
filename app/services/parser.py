import io
from pathlib import Path

from docx import Document
from pypdf import PdfReader

from app.config import MAX_CV_CHARS


class UploadError(Exception):
    pass


ALLOWED = {".pdf", ".docx"}


def extract_text(filename: str, data: bytes, max_bytes: int) -> str:
    if not filename:
        raise UploadError("Choose a PDF or DOCX file.")
    if len(data) > max_bytes:
        raise UploadError("This file is larger than 5 MB.")
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED:
        raise UploadError("Upload a PDF or DOCX.")
    if suffix == ".pdf":
        text = _pdf_text(data)
    else:
        text = _docx_text(data)
    text = "\n".join(line.rstrip() for line in text.splitlines()).strip()
    if len(text) < 40:
        raise UploadError(
            "This file has no readable text. Upload a text PDF or a DOCX, not a scan."
        )
    if len(text) > MAX_CV_CHARS:
        raise UploadError("This CV is too long to read. Shorten it and upload again.")
    return text


def _pdf_text(data: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(data))
    except Exception as exc:
        raise UploadError("This PDF could not be read.") from exc
    parts: list[str] = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n".join(parts)


def _docx_text(data: bytes) -> str:
    try:
        document = Document(io.BytesIO(data))
    except Exception as exc:
        raise UploadError("This DOCX could not be read.") from exc
    return "\n".join(paragraph.text for paragraph in document.paragraphs)
