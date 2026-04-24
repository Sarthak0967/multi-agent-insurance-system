"""
image_generator.py
==================
Uses the LLM's visual brief (5 image fields) to generate a
concept-specific AI image. Returns the raw image — no overlays.

Modes (IMAGE_MODE in .env):
  hf      → HuggingFace FLUX.1-schnell (free, needs HF_API_KEY)
  sdxl    → Stability AI SDXL (paid, needs STABILITY_API_KEY)
  pillow  → Geometric placeholder (no API key needed, always works)
"""

import os, io, base64, requests
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
from visualizer.prompts import build_image_prompt, parse_visual_meta

load_dotenv()

HF_API_KEY        = os.getenv("HF_API_KEY", "")
print(HF_API_KEY)
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY", "")
MODE              = os.getenv("IMAGE_MODE", "hf")

FONT_BOLD = [
    "C:/Windows/Fonts/arialbd.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
FONT_REG = [
    "C:/Windows/Fonts/arial.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

def _font(paths, size):
    for p in paths:
        try: return ImageFont.truetype(p, size)
        except: pass
    return ImageFont.load_default()

def _sanitize(t):
    return t.encode("ascii", "ignore").decode("ascii").strip()

def _pil_to_b64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


def _fetch_hf(prompt: str) -> Image.Image | None:
    """
    Free image generation using Pollinations AI.
    No API key required.
    """

    try:
        from urllib.parse import quote

        encoded_prompt = quote(prompt)

        url = (
            f"https://image.pollinations.ai/prompt/"
            f"{encoded_prompt}"
            "?width=1024&height=1024"
        )

        print("[Pollinations] Generating image...")

        resp = requests.get(
            url,
            timeout=180,
        )

        if resp.status_code == 200:
            print("[Pollinations] Image generated successfully")

            return Image.open(
                io.BytesIO(resp.content)
            ).convert("RGB")

        print(f"[Pollinations ERROR] {resp.status_code}")

    except Exception as e:
        print(f"[Pollinations Exception] {e}")

    return None


def _fetch_sdxl(prompt: str) -> Image.Image | None:
    """Stability AI SDXL — paid."""
    if not STABILITY_API_KEY:
        return None
    try:
        resp = requests.post(
            "https://api.stability.ai/v1/generation/"
            "stable-diffusion-xl-1024-v1-0/text-to-image",
            headers={"Accept": "application/json",
                     "Content-Type": "application/json",
                     "Authorization": f"Bearer {STABILITY_API_KEY}"},
            json={
                "text_prompts": [
                    {"text": prompt, "weight": 1.0},
                    {"text": "text letters words watermark blur low quality",
                     "weight": -1.0},
                ],
                "cfg_scale": 7, "height": 1024, "width": 1024,
                "steps": 30, "samples": 1, "style_preset": "digital-art",
            },
            timeout=120,
        )
        if resp.status_code == 200:
            b64 = resp.json()["artifacts"][0]["base64"]
            return Image.open(io.BytesIO(base64.b64decode(b64))).convert("RGB")
        print(f"[SDXL] {resp.status_code}: {resp.text[:150]}")
    except Exception as e:
        print(f"[SDXL] error: {e}")
    return None


def _pillow_fallback(concept: str, visual_meta: dict) -> Image.Image:
    """Clean geometric placeholder when no API key is available."""
    import math, textwrap

    W, H = 1024, 1024
    theme = visual_meta.get("color_theme", "blue")

    THEME = {
        "blue":   {"bg": (228,238,255), "hdr": (15,50,120),  "mid": (60,110,200)},
        "green":  {"bg": (228,248,234), "hdr": (10,80,50),   "mid": (40,140,80)},
        "red":    {"bg": (255,230,230), "hdr": (130,15,15),  "mid": (200,50,50)},
        "orange": {"bg": (255,243,220), "hdr": (150,70,5),   "mid": (220,130,30)},
        "purple": {"bg": (238,230,255), "hdr": (60,15,110),  "mid": (120,60,190)},
    }
    t = THEME.get(theme, THEME["blue"])

    img  = Image.new("RGB", (W, H), t["bg"])
    draw = ImageDraw.Draw(img)

    fT   = _font(FONT_BOLD, 52)
    fMed = _font(FONT_BOLD, 24)
    fSm  = _font(FONT_REG,  20)

    # Header
    draw.rectangle([0,0,W,120], fill=t["hdr"])
    draw.rectangle([0,115,W,120], fill=t["mid"])
    title = _sanitize(concept)[:50]
    tw = draw.textbbox((0,0), title, font=fT)[2]
    draw.text((max(30,(W-tw)//2), 28), title, font=fT, fill=(255,255,255))

    # Subject & scene text from LLM
    subject = _sanitize(visual_meta.get("image_subject",""))[:80]
    scene   = _sanitize(visual_meta.get("image_scene",""))[:80]
    action  = _sanitize(visual_meta.get("image_action",""))[:80]

    y = 140
    for label, val in [("Subject", subject), ("Scene", scene), ("Action", action)]:
        if val:
            draw.text((40, y), f"{label}:", font=fMed, fill=t["hdr"])
            for line in textwrap.wrap(val, width=70):
                y += 28
                draw.text((40, y), line, font=fSm, fill=(60,60,80))
            y += 20

    # Four decorative quadrants
    GT, GG, PAD = max(y+20, 340), 16, 30
    SW = (W-PAD*2-GG)//2
    SH = (H-GT-PAD-GG)//2

    for i, (x0,y0) in enumerate([
        (PAD,GT),(PAD+SW+GG,GT),
        (PAD,GT+SH+GG),(PAD+SW+GG,GT+SH+GG)
    ]):
        x1,y1 = x0+SW, y0+SH
        draw.rounded_rectangle([x0,y0,x1,y1], radius=18,
                                fill=tuple(min(255,c+30) for c in t["bg"]),
                                outline=t["mid"], width=2)
        draw.rounded_rectangle([x0,y0,x1,y0+60], radius=18, fill=t["hdr"])
        draw.rectangle([x0,y0+42,x1,y0+60], fill=t["hdr"])
        draw.text((x0+20,y0+16), f"Key point {i+1}", font=fMed, fill=(255,255,255))
        for k in range(3):
            yw = y0+76+k*38
            draw.rounded_rectangle(
                [x0+16,yw,x0+16+int((SW-32)*[0.8,0.95,0.6][k]),yw+20],
                radius=10, fill=t["mid"])

    # Footer
    draw.rectangle([0,H-38,W,H], fill=t["hdr"])
    draw.text((30,H-27), "Insurance GenAI · Groq LLaMA 3.3", font=fMed,
              fill=(140,180,240))

    return img


def generate_image(concept: str, structured_text: str) -> str:
    """
    1. Parse the LLM's visual brief from structured_text
    2. Build a rich, concept-specific image prompt from it
    3. Call the AI image model (HF / SDXL / Pillow fallback)
    4. Return raw image as data URI — no overlay, no drawing on top
    """
    # Extract visual brief written by the LLM
    visual_meta  = parse_visual_meta(structured_text)

    # Build image prompt from all 5 visual brief fields
    image_prompt = build_image_prompt(concept, visual_meta)

    print(f"\n[image_generator] Concept: {concept}")
    print(f"[image_generator] Subject: {visual_meta.get('image_subject','')}")
    print(f"[image_generator] Scene:   {visual_meta.get('image_scene','')}")
    print(f"[image_generator] Style:   {visual_meta.get('image_style','')}")
    print(f"[image_generator] Prompt snippet: {image_prompt[:200]}...")

    img = None
    if MODE == "hf":
        img = _fetch_hf(image_prompt)
    elif MODE == "sdxl":
        img = _fetch_sdxl(image_prompt)

    if img is None:
        print(f"[image_generator] Falling back to Pillow placeholder")
        img = _pillow_fallback(concept, visual_meta)

    return f"data:image/png;base64,{_pil_to_b64(img)}"