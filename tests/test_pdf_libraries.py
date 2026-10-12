from app.services import pdf


def test_macos_adds_homebrew_and_preserves_configured_paths(monkeypatch):
    monkeypatch.setattr(pdf.sys, 'platform', 'darwin')
    monkeypatch.setenv('DYLD_FALLBACK_LIBRARY_PATH', '/custom/lib')
    monkeypatch.setattr(pdf.Path, 'is_file', lambda path: str(path).startswith('/opt/homebrew/'))
    pdf._configure_pdf_libraries()
    pdf._configure_pdf_libraries()
    assert pdf.os.environ['DYLD_FALLBACK_LIBRARY_PATH'] == '/custom/lib:/opt/homebrew/lib'


def test_linux_library_configuration_is_unchanged(monkeypatch):
    monkeypatch.setattr(pdf.sys, 'platform', 'linux')
    monkeypatch.delenv('DYLD_FALLBACK_LIBRARY_PATH', raising=False)
    pdf._configure_pdf_libraries()
    assert 'DYLD_FALLBACK_LIBRARY_PATH' not in pdf.os.environ
