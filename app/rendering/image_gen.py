"""Image generation — fetches real photos from loremflickr + adds text overlay."""

from __future__ import annotations

import textwrap
import warnings
from pathlib import Path
from typing import Any

import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter


warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)


def _fetch_photo(keywords: str, width: int = 1280, height: int = 720) -> bytes | None:
    """Fetch a real photo from loremflickr by keywords."""
    # Clean keywords for URL
    clean = keywords.replace(" ", ",").replace(":", "").lower()[:50]
    url = f"https://loremflickr.com/{width}/{height}/{clean}"
    try:
        resp = requests.get(url, verify=False, timeout=15, allow_redirects=True)
        if resp.status_code == 200 and "image" in resp.headers.get("content-type", ""):
            return resp.content
    except Exception:
        pass
    return None


def generate_scene_image(
    title: str,
    description: str,
    output_path: str,
    style: str = "default",
    width: int = 1280,
    height: int = 720,
    scene_number: int = 1,
    topic: str = "",
) -> str:
    """Generate a scene image: fetch real photo + add text overlay.
    
    Fetches a relevant photo from the web and overlays the scene title.
    Falls back to a solid-color card if photo fetch fails.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Build search keywords from title/description/topic
    keywords = " ".join([topic, title, description])[:80]

    # Try to fetch a real photo
    photo_bytes = _fetch_photo(keywords, width, height)

    if photo_bytes:
        import io
        img = Image.open(io.BytesIO(photo_bytes)).convert("RGB")
        img = img.resize((width, height), Image.LANCZOS)
        # Darken image slightly for text readability
        darkened = img.point(lambda p: int(p * 0.6))
        img = darkened
    else:
        # Fallback: solid color
        PALETTES = {
            "cinematic": (15, 15, 30),
            "pixar": (40, 60, 120),
            "documentary": (25, 25, 25),
            "default": (20, 20, 35),
        }
        bg = PALETTES.get(style, (20, 20, 35))
        img = Image.new("RGB", (width, height), bg)

    draw = ImageDraw.Draw(img)

    # Load fonts
    try:
        font_sm = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
        font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 42)
        font_body = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
    except (OSError, IOError):
        font_sm = ImageFont.load_default()
        font_title = ImageFont.load_default()
        font_body = ImageFont.load_default()

    # Semi-transparent overlay bar at bottom for text
    overlay = Image.new("RGBA", (width, 220), (0, 0, 0, 160))
    img = img.convert("RGBA")
    img.paste(overlay, (0, height - 220), overlay)

    draw = ImageDraw.Draw(img)

    # Scene badge
    draw.text((40, height - 200), f"SCENE {scene_number}", fill=(180, 180, 180), font=font_sm)

    # Title
    wrapped_title = textwrap.fill(title, width=45)
    draw.multiline_text((40, height - 170), wrapped_title, fill=(255, 255, 255), font=font_title)

    # Description (smaller, below title)
    desc_short = description[:100] + "..." if len(description) > 100 else description
    draw.text((40, height - 60), desc_short, fill=(200, 200, 200), font=font_sm)

    # Save as RGB
    img = img.convert("RGB")
    img.save(output_path, "PNG")
    return output_path
