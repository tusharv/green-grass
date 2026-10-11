from html import escape

from app.schemas import CvDocument


def _section(title: str, body: str) -> str:
    if not body:
        return ""
    return f"<h2>{escape(title)}</h2>{body}"


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
    h1 {{ font-size: 22pt; margin: 0; font-weight: 700; letter-spacing: -0.03em; }}
    .contact {{ margin: 4px 0 0; color: #5c5348; font-family: "Liberation Sans", sans-serif; font-size: 10pt; }}
    .rule {{ border: 0; border-top: 1px solid #1a1a1a; margin: 10px 0 4px; }}
    h2 {{
      font-family: "Liberation Sans", sans-serif;
      font-size: 9pt;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      font-weight: 700;
      border-bottom: 1px solid #d9d2c5;
      margin: 14px 0 8px;
      padding-bottom: 3px;
    }}
    p {{ margin: 0 0 6px; }}
    .role-line {{ display: flex; justify-content: space-between; gap: 12px; font-size: 12pt; margin: 0; }}
    .employer {{ margin: 0 0 4px; }}
    ul {{ margin: 4px 0 10px; padding-left: 1.1em; }}
    li {{ margin: 2px 0; }}
  </style>
</head>
<body>
  <h1>{escape(contact.name or "CV")}</h1>
  <p class="contact">{contact_line}</p>
  <hr class="rule">
  {_section("Summary", f"<p>{escape(document.summary)}</p>" if document.summary else "")}
  {_section("Experience", "".join(roles))}
  {_section("Skills", f"<p>{skills}</p>" if skills else "")}
  {_section("Education", "".join(schools))}
</body>
</html>"""


def render_pdf(document: CvDocument) -> bytes:
    html = document_html(document)
    try:
        from weasyprint import HTML
    except OSError as exc:
        raise RuntimeError(
            "PDF rendering needs the system libraries in the Docker image."
        ) from exc
    return HTML(string=html).write_pdf()
