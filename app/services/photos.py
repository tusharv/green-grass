import io
import re

from PIL import Image, ImageOps, UnidentifiedImageError

MAX_PHOTO_BYTES = 3 * 1024 * 1024
MAX_PHOTO_PIXELS = 40_000_000
PHOTO_SIZE = 640
PHOTO_FORMATS = {"JPEG", "PNG", "WEBP"}

GITHUB_LINK = re.compile(r"^(?:https?://)?(?:www\.)?github\.com/([A-Za-z0-9](?:[A-Za-z0-9-]{0,38}))/?$", re.IGNORECASE)
GITHUB_RESERVED = {"orgs", "features", "topics", "collections", "about", "pricing", "login", "join", "settings"}


class PhotoError(ValueError):
    pass


def square_jpeg(data: bytes) -> bytes:
    """Re-encode an uploaded photo as a square JPEG so no original file or metadata is kept."""
    if not data:
        raise PhotoError("Choose a photo to upload.")
    if len(data) > MAX_PHOTO_BYTES:
        raise PhotoError("This photo is larger than 3 MB.")
    try:
        with Image.open(io.BytesIO(data)) as image:
            if image.format not in PHOTO_FORMATS:
                raise PhotoError("Upload a JPEG, PNG, or WebP photo.")
            width, height = image.size
            if width * height > MAX_PHOTO_PIXELS:
                raise PhotoError("This photo has too many pixels. Use one under 40 megapixels.")
            if width < 96 or height < 96:
                raise PhotoError("This photo is too small. Use one at least 96 pixels wide.")
            image = ImageOps.exif_transpose(image)
            if image.mode in ("RGBA", "LA", "P"):
                image = image.convert("RGBA")
                backdrop = Image.new("RGB", image.size, (255, 255, 255))
                backdrop.paste(image, mask=image.getchannel("A"))
                image = backdrop
            else:
                image = image.convert("RGB")
            square = ImageOps.fit(
                image,
                (PHOTO_SIZE, PHOTO_SIZE),
                method=Image.Resampling.LANCZOS,
                centering=(0.5, 0.4),
            )
    except PhotoError:
        raise
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise PhotoError("That file is not a photo we can read. Upload a JPEG, PNG, or WebP.") from exc
    out = io.BytesIO()
    square.save(out, format="JPEG", quality=86, optimize=True, progressive=True)
    return out.getvalue()


def github_handle(links: list[str] | None) -> str:
    for link in links or []:
        found = GITHUB_LINK.match((link or "").strip())
        if found and found.group(1).lower() not in GITHUB_RESERVED:
            return found.group(1)
    return ""


def github_avatar(handle: str) -> str:
    return f"https://github.com/{handle}.png?size={PHOTO_SIZE}"
