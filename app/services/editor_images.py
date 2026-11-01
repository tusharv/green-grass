"""Small, metadata-free company logos; uploaded originals are never retained."""
import base64
import binascii
import io

from PIL import Image, ImageOps, UnidentifiedImageError

MAX_LOGO_BYTES = 3 * 1024 * 1024
LOGO_PREFIX = 'data:image/png;base64,'


def logo_image(data: bytes, crop: bool = False) -> str:
    if not data or len(data) > MAX_LOGO_BYTES:
        raise ValueError('Choose a company logo under 3 MB.')
    try:
        with Image.open(io.BytesIO(data)) as original:
            if original.format not in {'PNG', 'JPEG', 'WEBP'}:
                raise ValueError('Upload a PNG, JPEG or WebP company logo.')
            if original.width * original.height > 16_000_000:
                raise ValueError('Use a company logo under 16 megapixels.')
            image = ImageOps.exif_transpose(original).convert('RGBA')
            if crop:
                image = ImageOps.fit(image, (256, 256), Image.Resampling.LANCZOS)
            else:
                image.thumbnail((256, 256), Image.Resampling.LANCZOS)
            canvas = Image.new('RGBA', (256, 256), (255, 255, 255, 0))
            canvas.paste(image, ((256 - image.width) // 2, (256 - image.height) // 2))
            output = io.BytesIO()
            canvas.save(output, format='PNG')
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise ValueError('That image could not be read. Upload a PNG, JPEG or WebP.') from exc
    return LOGO_PREFIX + base64.b64encode(output.getvalue()).decode('ascii')


def validate_logos(value: dict[str, str]) -> dict[str, str]:
    if len(value) > 50:
        raise ValueError('Use at most 50 company logos.')
    result = {}
    for employer, url in value.items():
        key = ' '.join(employer.lower().split())
        if not key or len(key) > 200:
            raise ValueError('Choose an employer before uploading a logo.')
        if not url:
            result[key] = ''  # Explicit removal suppresses automatic lookup.
            continue
        if not url.startswith(LOGO_PREFIX) or len(url) > 400_000:
            raise ValueError('Upload the logo image instead of a remote image link.')
        try:
            raw = base64.b64decode(url[len(LOGO_PREFIX):], validate=True)
        except (ValueError, binascii.Error) as exc:
            raise ValueError('That company logo is invalid.') from exc
        result[key] = logo_image(raw)
    return result
