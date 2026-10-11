import io

from docx import Document
from pypdf import PdfWriter

from app.services.parser import UploadError, extract_text


def _docx(text: str) -> bytes:
    buffer = io.BytesIO()
    document = Document()
    document.add_paragraph(text)
    document.save(buffer)
    return buffer.getvalue()


LONG = "Ada Lovelace built analytical engines and wrote notes on computation. " * 2


def test_docx_text_is_extracted():
    text = extract_text("ada.docx", _docx(LONG), 5 * 1024 * 1024)
    assert "Ada Lovelace" in text


def test_rejects_other_file_types():
    try:
        extract_text("notes.txt", b"hello world " * 10, 5 * 1024 * 1024)
    except UploadError as exc:
        assert "PDF or DOCX" in str(exc)
    else:
        raise AssertionError("txt was accepted")


def test_rejects_oversize_file():
    try:
        extract_text("ada.pdf", b"x" * (5 * 1024 * 1024 + 1), 5 * 1024 * 1024)
    except UploadError as exc:
        assert "5 MB" in str(exc)
    else:
        raise AssertionError("oversize file was accepted")


def test_rejects_scanned_pdf():
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    buffer = io.BytesIO()
    writer.write(buffer)
    try:
        extract_text("scan.pdf", buffer.getvalue(), 5 * 1024 * 1024)
    except UploadError as exc:
        assert "scan" in str(exc).lower()
    else:
        raise AssertionError("blank pdf was accepted")
