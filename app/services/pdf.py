from html import escape
import os
import sys
from pathlib import Path

from app.schemas import CvDocument, ResumeDesign
from app.services.design import designed_html
from app.services.design_icons import icon


def _section(title: str, body: str, symbol: str) -> str:
    if not body:
        return ""
    mark = icon(symbol).replace('stroke="currentColor"', 'stroke="#1a1a1a"')
    return f"<h2>{mark}<span>{escape(title)}</span></h2>{body}"


def document_html(document: CvDocument) -> str:
    contact = document.contact
    bits = [bit for bit in [contact.email, contact.phone, contact.location, *contact.links] if bit]
    contact_line = " · ".join(escape(bit) for bit in bits)
    skills = " · ".join(escape(skill) for skill in document.skills)
    roles = []
    for role in document.experience:
        dates = " – ".join(part for part in [role.start, role.end] if part)
        bullets = "".join(f"<li>{escape(bullet)}</li>" for bullet in role.bullets)
        date_html = f"<span>{escape(dates)}</span>" if dates else ""
        roles.append(
            "<section class='role'>"
            f"<p class='role-line'><strong>{escape(role.title)}</strong>{date_html}</p>"
            f"<p class='employer'><em>{escape(role.employer)}</em></p>"
            f"<ul>{bullets}</ul></section>"
        )
    schools = []
    for school in document.education:
        line = ", ".join(
            escape(part) for part in [school.credential, school.school, school.year] if part
        )
        if line:
            schools.append(f"<p>{line}</p>")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{escape(contact.name or "CV")}</title>
  <style>
    @page {{ margin: 16mm; }}
    body {{
      font-family: "Liberation Serif", "Times New Roman", serif;
      color: #1a1a1a;
      background: #fbfaf6;
      font-size: 11pt;
      line-height: 1.4;
    }}
    h1 {{ font-size: 26pt; margin: 0; font-weight: 700; letter-spacing: -0.03em; line-height: 1.1; }}
    .contact {{ margin: 6px 0 0; color: #5c5348; font-family: "Liberation Sans", sans-serif; font-size: 10pt; }}
    .rule {{ border: 0; border-top: 1px solid #1a1a1a; margin: 12px 0 2px; }}
    h2 {{
      display: flex;
      align-items: center;
      gap: 6px;
      font-family: "Liberation Sans", sans-serif;
      font-size: 9pt;
      letter-spacing: 0.16em;
      text-transform: uppercase;
      font-weight: 700;
      border-bottom: 1px solid #d9d2c5;
      margin: 16px 0 8px;
      padding-bottom: 4px;
    }}
    h2 .design-icon {{ width: 13px; height: 13px; flex: 0 0 auto; }}
    p {{ margin: 0 0 6px; }}
    .role {{ margin: 0 0 12px; }}
    .role-line {{ display: flex; justify-content: space-between; align-items: baseline; gap: 16px; font-size: 12pt; margin: 0; }}
    .role-line span {{ font-family: "Liberation Sans", sans-serif; font-size: 10pt; font-weight: 600; color: #5c5348; font-variant-numeric: tabular-nums; }}
    .employer {{ margin: 1px 0 4px; font-family: "Liberation Sans", sans-serif; }}
    ul {{ margin: 4px 0 8px; padding-left: 1.15em; }}
    li {{ margin: 2px 0; }}
    li::marker {{ color: #5c5348; }}
  </style>
</head>
<body>
  <h1>{escape(contact.name or "CV")}</h1>
  <p class="contact">{contact_line}</p>
  <hr class="rule">
  {_section("Summary", f"<p>{escape(document.summary)}</p>" if document.summary else "", "summary")}
  {_section("Experience", "".join(roles), "role")}
  {_section("Skills", f"<p>{skills}</p>" if skills else "", "skills")}
  {_section("Education", "".join(schools), "education")}
</body>
</html>"""


def _configure_pdf_libraries() -> None:
    """Help macOS locate Homebrew libraries without changing Linux deployments."""
    if sys.platform != 'darwin':
        return
    paths = [p for p in os.environ.get('DYLD_FALLBACK_LIBRARY_PATH', '').split(':') if p]
    for directory in ('/opt/homebrew/lib', '/usr/local/lib'):
        if (Path(directory) / 'libpango-1.0.dylib').is_file() and directory not in paths:
            paths.append(directory)
    if paths:
        os.environ['DYLD_FALLBACK_LIBRARY_PATH'] = ':'.join(paths)


def render_pdf(document: CvDocument, design: ResumeDesign | None = None, photo: str = "") -> bytes:
    html = designed_html(document, design, photo) if design else document_html(document)
    _configure_pdf_libraries()
    try:
        from weasyprint import HTML
    except OSError as exc:
        raise RuntimeError(
            "PDF rendering libraries could not be loaded. On macOS, install Pango with "
            "brew install pango. On Linux, use the project Docker image."
        ) from exc
    return HTML(string=html).write_pdf()
