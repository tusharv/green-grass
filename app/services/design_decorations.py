"""Small, self-contained vector ornaments shared by screen and print."""
from urllib.parse import quote
from base64 import b64encode
from functools import lru_cache
from pathlib import Path
from io import BytesIO

from PIL import Image, ImageOps


def corner_images(template: str, accent: str = '#245747') -> tuple[str, str]:
    ink = accent if len(accent) == 7 and accent.startswith('#') and all(c in '0123456789abcdefABCDEF' for c in accent[1:]) else '#245747'
    opacity = '0.18' if template == 'modern' else '0.38'
    if template == 'modern':
        shapes = ''.join(
            f'<path d="M-30 {-110+i*18}C50 {50+i*18} 200 {-100+i*18} 270 {i*18}S200 {170+i*18} 380 {210+i*18}"/>'
            for i in range(11)
        )
    elif template == 'classic':
        shapes = ''.join(
            f'<path d="M{95+i*10} 0V{75+i*10}Q{95+i*10} {110+i*10} {130+i*10} {110+i*10}H340"/>'
            for i in range(5)
        )
    elif template == 'creative':
        shapes = ''.join(f'<circle cx="350" cy="10" r="{90+i*21}"/>' for i in range(9))
    else:
        shapes = '<path d="M205 0V70H340M225 0V50H340M245 0V30H340"/><path d="M285 100H320M302.5 82.5V117.5"/>'

    def image(transform=''):
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="340" height="400" viewBox="0 0 340 400">'
               f'<g transform="{transform}" fill="none" stroke="{ink}" stroke-opacity="{opacity}" stroke-width="1.05">{shapes}</g></svg>')
        return 'url("data:image/svg+xml,' + quote(svg, safe='') + '")'

    return image(), image('translate(340 400) rotate(180)')


@lru_cache(maxsize=64)
def theme_background(template: str, accent: str = '#245747') -> dict[str, str] | None:
    """Cache small raster pieces, keeping browser CSS values below size limits.

    Crop without resizing: CSS sets width and leaves height automatic. The
    classic spine tiles vertically instead of stretching. Pillow is already
    used for profile photos; no external asset requests are required.
    """
    specs = {
        'classic': ('executive.png',
                    [(20, 0, 40, 80), (795, 1231, 260, 260)],
                    'left top,right bottom', '12px auto,150px auto',
                    '3mm auto,38mm auto', 'repeat-y,no-repeat'),
        'modern': ('modern.png',
                   [(674, 0, 380, 360), (0, 1112, 400, 380)],
                   'right top,left bottom', '26% auto,26% auto',
                   '55mm auto,55mm auto', 'no-repeat'),
        'creative': ('botanical.png',
                     [(0, 0, 380, 390), (695, 1051, 360, 440)],
                     'left top,right bottom', '26% auto,26% auto',
                     '55mm auto,55mm auto', 'no-repeat'),
    }
    if template not in specs:
        return None
    filename, windows, position, screen_size, print_size, repeat = specs[template]
    images = []
    with Image.open(Path(__file__).with_name('assets') / 'cv-backgrounds' / filename) as source:
        for x, y, width, height in windows:
            crop = source.crop((x, y, x + width, y + height))
            # Turn white paper into transparency and preserve the drawing's
            # shading as alpha. The selected accent supplies every visible hue.
            opacity = ImageOps.invert(ImageOps.grayscale(crop)).point(
                lambda value: min(150, max(0, value - 6)))
            piece = Image.new('RGBA', crop.size, accent)
            piece.putalpha(opacity)
            output = BytesIO()
            piece.save(output, format='PNG', optimize=True)
            encoded = b64encode(output.getvalue()).decode('ascii')
            images.append(f'url("data:image/png;base64,{encoded}")')
    return {'images': ','.join(images), 'position': position,
            'screen_size': screen_size, 'print_size': print_size, 'repeat': repeat}
