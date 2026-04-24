"""
prompts.py
==========
The LLM generates TWO things in one call:

  1. EXPLANATION — Title + 4 sections (shown in the UI as text)
  2. VISUAL BRIEF — detailed image generation instructions derived
     from understanding the concept (colors, scene, objects, style)

The visual brief is extracted and passed directly to the image model.
"""


def build_text_prompt(concept: str) -> str:
    return f"""You are an expert insurance educator and creative visual director.

Your job is to explain the insurance concept "{concept}" AND write a detailed
visual brief that an AI image model will use to generate a concept illustration.

Return ONLY this exact format with no extra commentary, no markdown, no symbols:

Title:
<short concept title, max 6 English words>

Section1:
<key educational point 1 — one clear sentence, 8 to 14 words>

Section2:
<key educational point 2 — one clear sentence, 8 to 14 words>

Section3:
<key educational point 3 — one clear sentence, 8 to 14 words>

Section4:
<key educational point 4 — one clear sentence, 8 to 14 words>

ColorTheme:
<one word: blue OR green OR red OR orange OR purple>

ImageSubject:
<The main subject of the illustration — what physical objects or people should be shown, 10 to 20 words>

ImageScene:
<The setting and background — where this takes place visually, 10 to 20 words>

ImageAction:
<What is happening in the scene — movement, interaction, process being shown, 10 to 20 words>

ImageStyle:
<Art style and mood — e.g. flat vector, corporate illustration, infographic, photorealistic, 3D render>

ImageDetails:
<Specific visual details unique to this concept — shapes, symbols, colors, composition, 15 to 25 words>

Rules:
- Plain English only, no markdown, no special characters
- Each Image field must be specific to "{concept}" — not generic insurance phrases
- ColorTheme must be exactly one of: blue, green, red, orange, purple
- All Image fields describe ONLY visual elements — no text or words in the image
- Make the image fields vivid, specific, and concept-accurate
"""


def build_image_prompt(concept: str, visual_meta: dict | None = None) -> str:
    """
    Assembles the full image generation prompt from the LLM visual brief.
    Uses all 5 image fields to create a rich, concept-specific prompt.
    """
    if not visual_meta or not visual_meta.get("image_subject"):
        # Generic fallback
        return (
            f"Professional digital illustration about {concept} insurance concept. "
            "Flat vector style, corporate blue palette, clean white background. "
            "Icons: shield, document, people, money flows. No text, no letters."
        )

    subject = visual_meta.get("image_subject", "")
    scene   = visual_meta.get("image_scene", "")
    action  = visual_meta.get("image_action", "")
    style   = visual_meta.get("image_style", "flat vector illustration")
    details = visual_meta.get("image_details", "")
    color   = visual_meta.get("color_theme", "blue")

    color_palette = {
        "blue":   "corporate navy blue, sky blue, white — professional and trustworthy",
        "green":  "forest green, emerald, light cream — growth, safety, nature",
        "red":    "deep crimson, warm red, white — urgency, risk, alert",
        "orange": "warm amber, burnt orange, cream — energy, caution, warmth",
        "purple": "rich purple, violet, soft lavender — authority, wisdom, trust",
    }.get(color, "corporate blue and white")

    return f"""Digital illustration for insurance concept: {concept}

Subject: {subject}
Scene: {scene}
Action: {action}
Style: {style}
Color palette: {color_palette}
Key details: {details}

Requirements:
- Highly detailed, professional quality illustration
- Concept-specific imagery that clearly represents {concept}
- {style} aesthetic throughout
- No text, no letters, no numbers, no words anywhere in the image
- No watermarks, no signatures, no foreign characters
- Clean composition with strong visual storytelling
- High resolution, sharp edges, vibrant colors

Negative: text, words, letters, typography, watermark, blur, low resolution, dark gloomy mood"""


def parse_visual_meta(structured_text: str) -> dict:
    """
    Extracts both explanation fields and the full visual brief
    from the LLM output. Returns a dict with all parsed fields.
    """
    import re

    meta = {
        "color_theme":   "blue",
        "image_subject": "",
        "image_scene":   "",
        "image_action":  "",
        "image_style":   "flat vector illustration, corporate design",
        "image_details": "",
    }

    VALID_THEMES = {"blue", "green", "red", "orange", "purple"}

    current_key  = None
    current_lines = []

    def flush():
        if not current_key or not current_lines:
            return
        val = " ".join(current_lines).strip()
        val = re.sub(r"\*{1,2}(.*?)\*{1,2}", r"\1", val).strip()
        if not val:
            return
        if current_key == "colortheme" and val.lower() in VALID_THEMES:
            meta["color_theme"] = val.lower()
        elif current_key == "imagesubject":
            meta["image_subject"] = val
        elif current_key == "imagescene":
            meta["image_scene"] = val
        elif current_key == "imageaction":
            meta["image_action"] = val
        elif current_key == "imagestyle":
            meta["image_style"] = val
        elif current_key == "imagedetails":
            meta["image_details"] = val

    KNOWN_KEYS = {
        "colortheme", "imagesubject", "imagescene",
        "imageaction", "imagestyle", "imagedetails",
        # these are explanation fields — skip them
        "title", "section1", "section2", "section3", "section4",
    }

    for raw_line in structured_text.split("\n"):
        line = raw_line.strip()
        if not line:
            continue
        clean = re.sub(r"\*{1,2}(.*?)\*{1,2}", r"\1", line).strip()
        m = re.match(r"^([A-Za-z0-9 _]+?)\s*:\s*(.*)", clean)
        if m:
            key_raw    = m.group(1).strip().lower().replace(" ", "")
            inline_val = m.group(2).strip()
            if key_raw in KNOWN_KEYS:
                flush()
                current_key   = key_raw
                current_lines = [inline_val] if inline_val else []
                continue
            flush()
            current_key   = None
            current_lines = []
            continue
        if current_key:
            current_lines.append(clean)

    flush()
    return meta