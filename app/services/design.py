"""One escaped, script-free document renderer for profiles, previews and PDFs."""
from html import escape
from urllib.parse import urlsplit
import re
from pathlib import Path

from app.schemas import CvDocument, ResumeDesign
from app.services.design_icons import icon

SCREEN_CSS = Path(__file__).with_name("design_screen.css").read_text()


def designed_html(document: CvDocument, design: ResumeDesign, photo: str = '', *, shared_for: str = '') -> str:
    palettes = {
        'forest': ('#245747', '#f1f6f2'), 'navy': ('#203c64', '#f0f4fa'),
        'plum': ('#603c65', '#f7f2f7'), 'terracotta': ('#8b4535', '#faf4ef'),
        'slate': ('#364454', '#f3f5f7'), 'teal': ('#15616a', '#eff7f7'),
    }
    page_color = '#f4f6f8'
    if design.palette in palettes:
        accent, page_color = palettes[design.palette]
        design = design.model_copy(update={'accent': accent})
    photo_size = {'small': 72, 'medium': 112, 'large': 152}[design.photo_size]
    photo_radius = {'round': '50%', 'square': '0', 'rounded': '18%', 'portrait': '40% 40% 16% 16%'}[design.photo_shape]
    e = escape
    contact = document.contact
    roles = []
    for index, role in enumerate(document.experience):
        dates = ' – '.join(filter(None, [role.start, role.end]))
        bullets = ''.join(f'<li>{e(b)}</li>' for b in role.bullets)
        initials = ''.join(word[0] for word in role.employer.split()[:2]).upper() or '—'
        badge = f'<span class="company-badge" data-company-index="{index}" aria-hidden="true">{e(initials)}</span>'
        roles.append(f'<div class="role"><div class="role-heading">{badge}<div><h3>{e(role.title)}</h3><p class="job-meta">{e(role.employer)} <span>{e(dates)}</span></p></div></div><ul>{bullets}</ul></div>')
    schools = ''.join(f'<div class="school"><strong>{e(s.credential)}</strong><p>{e(s.school)} · {e(s.year)}</p></div>' for s in document.education)
    sections = {
        'summary': ('Profile', f'<p>{e(document.summary)}</p>' if document.summary else ''),
        'experience': ('Experience', ''.join(roles)),
        'skills': ('Skills', '<ul class="skills">'+''.join(f'<li>{e(s)}</li>' for s in document.skills)+'</ul>' if document.skills else ''),
        'education': ('Education', schools),
    }
    parts = []
    for name in design.sections:
        title, content = sections[name]
        if content:
            parts.append((name, f'<section class="section {name}"><h2>{icon("role" if name == "experience" else name)}<span>{title}</span></h2>{content}</section>'))
    split = design.template in ('modern', 'creative')
    if split:
        # Section order applies within each column; long experience stays in the main column.
        main = ''.join(html for name, html in parts if name in ('summary', 'experience'))
        side = ''.join(html for name, html in parts if name in ('skills', 'education'))
        content = f'<div class="columns"><aside>{side}</aside><main>{main}</main></div>'
    else:
        content = '<main>'+''.join(html for _, html in parts)+'</main>'
    font = {'serif':'Georgia, "Liberation Serif", serif', 'sans':'Arial, "Liberation Sans", sans-serif', 'editorial':'Georgia, "Liberation Serif", serif', 'humanist':'"Trebuchet MS", Arial, sans-serif', 'book':'Palatino, "Palatino Linotype", Georgia, serif', 'geometric':'Verdana, Geneva, sans-serif', 'mono':'"Courier New", monospace'}[design.font]
    heading = 'Arial, "Liberation Sans", sans-serif' if design.font == 'editorial' else font
    rgb = [int(design.accent[i:i+2], 16) / 255 for i in (1, 3, 5)]
    linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in rgb]
    luminance = sum(v * weight for v, weight in zip(linear, [.2126, .7152, .0722]))
    heading_color = design.accent if 1.05 / (luminance + .05) >= 4.5 else '#20252b'
    banner_text = '#ffffff' if luminance <= .179 else '#111111'
    size = {'small':10,'medium':11,'large':12}[design.text_size]
    space = {'compact':10,'comfortable':17,'airy':24}[design.spacing]
    safe_photo = photo.startswith('data:image/jpeg;base64,') or bool(re.fullmatch(r'https://github\.com/[A-Za-z0-9-]{1,39}\.png\?size=640', photo))
    image = f'<img class="portrait" src="{e(photo, quote=True)}" alt="">' if design.show_photo and safe_photo else ''
    def link(label, href, symbol="link", compact=""):
        text = (f'<span class="contact-short">{e(compact)}</span><span class="contact-full">{e(label)}</span>' if compact else f'<span>{e(label)}</span>')
        return f'<a href="{e(href, quote=True)}" target="_blank" rel="noopener noreferrer">{icon(symbol)}{text}</a>'
    contact_parts = []
    if contact.email:
        contact_parts.append(link(contact.email, 'mailto:' + contact.email, 'mail'))
    if contact.phone:
        contact_parts.append(link(contact.phone, 'tel:' + re.sub(r'[^0-9+]', '', contact.phone), 'phone'))
    if contact.location:
        contact_parts.append(f'<span class="location">{icon("pin")}<span>{e(contact.location)}</span></span>')
    for value in contact.links:
        href = value if '://' in value else 'https://' + value
        try:
            parsed = urlsplit(href)
            safe = parsed.scheme in ('https', 'http') and parsed.hostname and not parsed.username and not parsed.password
        except ValueError:
            safe = False
        host = (parsed.hostname or "").lower() if safe else ""
        symbol = next((brand for brand in ("github", "linkedin") if host == brand + ".com" or host.endswith("." + brand + ".com")), "link")
        path = parsed.path.strip("/").split("/") if safe else []
        compact = ""
        if symbol == "github" and len(path) == 1 and path[0]:
            compact = path[0]
        elif symbol == "linkedin" and len(path) == 2 and path[0] in ("in", "company"):
            compact = path[1]
        contact_parts.append(link(value, href, symbol, compact) if safe else e(value))
    contacts = ''.join(f'<span class="contact-item">{part}</span>' for part in contact_parts)
    screen_body = font
    screen_size = {'small': '15px', 'medium': '16px', 'large': '18px'}[design.text_size]
    screen_gap = {'compact': '16px', 'comfortable': '24px', 'airy': '32px'}[design.spacing]
    headline = document.experience[0].title if document.experience else ''
    context = f'<p class="shared-context"><span>Shared for</span> {e(shared_for)}</p>' if shared_for else ''
    subtitle = f'<p class="professional-title">{e(headline)}</p>' if headline else ''
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(contact.name or 'CV')}</title>
<style>
:root {{ --screen-body:{screen_body}; --heading-font:{heading}; --page-color:{page_color}; --photo-size:{photo_size}px; --photo-radius:{photo_radius}; --screen-size:{screen_size}; --screen-gap:{screen_gap}; --design-accent:{design.accent}; }}
.role-heading {{ display:flex; gap:12px; align-items:flex-start; break-inside:avoid; }}
.role-heading > div {{ min-width:0; }}
.company-badge {{ position:relative; display:inline-flex; align-items:center; justify-content:center; flex:0 0 36px; width:36px; height:36px; border:1px solid #dbe3e8; border-radius:7px; background:#f2f5f7; color:#47525c; font:600 12px/1 Arial,sans-serif; overflow:hidden; }}
.company-badge img {{ position:absolute; inset:0; width:100%; height:100%; object-fit:contain; padding:4px; background:white; }}
.professional-title {{ display:none; }}
.contact-short {{ display:none; }}
.shared-context {{ display:none; }}
.design-icon {{ width:14px; height:14px; vertical-align:middle; margin-right:6px; flex-shrink:0; }}
.contact-item + .contact-item::before {{ content:' · '; }}
@page {{ size:A4; margin:15mm; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:white; color:#20252b; font-family:{font}; font-size:{size}pt; line-height:1.5; overflow-wrap:anywhere; }}
.resume {{ max-width:900px; margin:auto; padding:38px; }}
header {{ border-bottom:2px solid {design.accent}; padding-bottom:22px; margin-bottom:24px; }}
h1 {{ font-family:{heading}; font-size:32pt; line-height:1.12; margin:0 0 12px; letter-spacing:-.035em; }}
h2 {{ font-family:{heading}; color:{heading_color}; font-size:11pt; letter-spacing:.1em; text-transform:uppercase; margin:0 0 10px; border-bottom:1px solid #d9dfe2; padding-bottom:6px; break-after:avoid; }}
h3 {{ font-size:12pt; margin:0; break-after:avoid; }}
p {{ margin:4px 0 10px; }}
.contact {{ font:10pt/1.6 Arial,sans-serif; color:#47525c; }}
.section {{ margin-bottom:{space}px; }}
ul {{ padding-left:18px; margin:6px 0 12px; }} li {{ margin-bottom:5px; }}
.job-meta {{ font-size:10pt; color:#47525c; }} .job-meta span {{ display:block; }}
.role {{ margin-bottom:{space}px; }} .school {{ margin-bottom:12px; }}
.skills {{ list-style:none; padding:0; }} .skills li {{ display:inline; }} .skills li:not(:last-child)::after {{ content:' · '; }}
.portrait {{ width:84px; height:84px; border-radius:50%; object-fit:cover; float:right; margin:0 0 12px 20px; }}
.columns {{ display:flex; gap:30px; align-items:flex-start; }} aside {{ width:27%; flex-shrink:0; }} main {{ min-width:0; flex:1; }}
.modern aside {{ padding-right:20px; border-right:2px solid {design.accent}; }}
.creative header {{ background:{design.accent}; color:{banner_text}; padding:30px; border:0; }}
.creative .contact {{ color:{banner_text}; }}
a {{ color:inherit; text-decoration:underline; text-underline-offset:2px; }} .creative aside {{ background:#edf1f4; padding:18px; }}
.creative h1 {{ font-size:36pt; }}
.minimal h1 {{ font-size:27pt; }} .minimal h2 {{ border:0; letter-spacing:.02em; text-transform:none; }} .minimal header {{ border-bottom:1px solid #d9dfe2; }}
@media screen and (max-width:600px) {{ .resume {{ padding:22px; }} .columns {{ display:block; }} aside {{ width:100%; }} .modern aside {{ border:0; padding:0; }} h1,.creative h1 {{ font-size:26pt; }} .creative header {{ padding:20px; }} }}
@media print {{ .resume {{ padding:0; max-width:none; }} .columns {{ display:block; }} .columns aside {{ float:left; width:27%; }} .columns main {{ margin-left:32%; }} header {{ break-inside:avoid; }} h2,h3 {{ break-after:avoid; }} p,li {{ orphans:2; widows:2; }} body {{ print-color-adjust:exact; }} }}
{SCREEN_CSS}
.portrait {{ width:var(--photo-size); height:var(--photo-size); border-radius:var(--photo-radius); }}
@media screen and (max-width:480px) {{ .portrait {{ width:min(var(--photo-size),120px); height:min(var(--photo-size),120px); }} }}
@media print {{ .portrait {{ width:{round(photo_size * .75)}px; height:{round(photo_size * .75)}px; }} }}
</style></head><body><article class="resume {design.template}"><header>{image}{context}<h1>{e(contact.name or 'CV')}</h1>{subtitle}<p class="contact">{contacts}</p></header>{content}</article></body></html>'''
