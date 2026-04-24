import base64
import io
import textwrap
from PIL import Image, ImageDraw, ImageFont

# ── Font paths available on Linux / Windows fallback ─────────────────────────
_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "arial.ttf",          # Windows
    "Arial.ttf",
]

_FONT_CANDIDATES_REGULAR = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "arial.ttf",
    "Arial.ttf",
]


def _load_font(candidates: list[str], size: int) -> ImageFont.FreeTypeFont:
    """Try each candidate path; fall back to PIL default only as last resort."""
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    # Last-resort: scale-up the built-in bitmap font
    return ImageFont.load_default()


def _draw_text_box(
    draw: ImageDraw.Draw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    box_color: tuple,
    text_color: tuple,
    padding: int = 12,
    max_width_chars: int = 28,
) -> None:
    """
    Draw a semi-transparent rounded rectangle, then render word-wrapped text
    inside it.  Uses only ASCII-safe characters to avoid glyph substitution.
    """
    # Sanitise: keep only printable ASCII so PIL never calls a CJK fallback
    safe_text = text.encode("ascii", errors="ignore").decode("ascii").strip()
    if not safe_text:
        safe_text = text.strip()   # keep original if nothing survives

    wrapped = textwrap.fill(safe_text, width=max_width_chars)
    lines   = wrapped.split("\n")

    # Measure box
    line_h  = font.getbbox("Ay")[3] + 4      # height of one line + leading
    box_w   = max(font.getlength(ln) for ln in lines) + padding * 2
    box_h   = line_h * len(lines) + padding * 2

    x, y = xy
    # Create a temporary RGBA image for the translucent box
    overlay = Image.new("RGBA", draw._image.size, (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    ov_draw.rounded_rectangle(
        [x, y, x + box_w, y + box_h],
        radius=10,
        fill=box_color,
    )
    draw._image.paste(
        Image.alpha_composite(draw._image.convert("RGBA"), overlay).convert("RGB"),
        (0, 0),
    )

    # Re-acquire draw handle after paste
    new_draw = ImageDraw.Draw(draw._image)
    for i, line in enumerate(lines):
        new_draw.text(
            (x + padding, y + padding + i * line_h),
            line,
            fill=text_color,
            font=font,
        )


def overlay_text(image_base64: str, structured_text: str) -> str:
    """
    Decode a base64 PNG, parse structured LLM output, and draw a clean
    English-language infographic overlay with four section boxes.

    Returns the final image as a base64-encoded PNG string.
    """

    # ── Decode ────────────────────────────────────────────────────────────────
    image_data = base64.b64decode(image_base64)
    image = Image.open(io.BytesIO(image_data)).convert("RGB")
    W, H   = image.size

    draw = ImageDraw.Draw(image)

    # ── Fonts ─────────────────────────────────────────────────────────────────
    font_title   = _load_font(_FONT_CANDIDATES,         size=46)
    font_section = _load_font(_FONT_CANDIDATES_REGULAR, size=24)

    # ── Parse structured text ─────────────────────────────────────────────────
    lines    = structured_text.split("\n")
    title    = ""
    sections: list[str] = []

    for line in lines:
        line = line.strip()
        if line.lower().startswith("title:"):
            title = line.split(":", 1)[1].strip()
        elif line.lower().startswith("section") and ":" in line:
            sections.append(line.split(":", 1)[1].strip())

    # ── Title bar ─────────────────────────────────────────────────────────────
    if title:
        title_safe = title.encode("ascii", errors="ignore").decode("ascii").strip() or title
        title_wrapped = textwrap.fill(title_safe, width=50)

        # Semi-transparent dark bar across the top
        bar_overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        bar_draw    = ImageDraw.Draw(bar_overlay)
        bar_draw.rectangle([0, 0, W, 90], fill=(15, 40, 90, 200))
        image = Image.alpha_composite(image.convert("RGBA"), bar_overlay).convert("RGB")
        draw  = ImageDraw.Draw(image)

        draw.text((30, 20), title_wrapped, fill=(255, 255, 255), font=font_title)

    # ── Four quadrant section boxes ───────────────────────────────────────────
    # Layout: 2 columns × 2 rows, with comfortable margins
    margin   = 30
    col_gap  = 20
    row_gap  = 20
    top_offset = 110           # below the title bar

    half_w = (W - margin * 2 - col_gap) // 2
    half_h = (H - top_offset - margin - row_gap) // 2

    positions = [
        (margin,             top_offset),                      # top-left
        (margin + half_w + col_gap, top_offset),               # top-right
        (margin,             top_offset + half_h + row_gap),   # bottom-left
        (margin + half_w + col_gap, top_offset + half_h + row_gap),  # bottom-right
    ]

    # Alternating brand colours (corporate blue palette)
    box_colors = [
        (20,  80, 160, 185),   # deep blue
        (0,  130, 100, 185),   # teal
        (160, 60,  20, 185),   # burnt orange
        (80,  20, 140, 185),   # purple
    ]

    for i, section_text in enumerate(sections[:4]):
        if i >= len(positions):
            break
        _draw_text_box(
            draw=draw,
            xy=positions[i],
            text=section_text,
            font=font_section,
            box_color=box_colors[i],
            text_color=(255, 255, 255),
            padding=14,
            max_width_chars=26,
        )

    # ── Encode & return ───────────────────────────────────────────────────────
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return base64.b64encode(buffer.getvalue()).decode()