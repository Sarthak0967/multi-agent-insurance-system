import os
from groq import Groq
from dotenv import load_dotenv
from visualizer.prompts import build_text_prompt

load_dotenv()

_api_key = os.getenv("GROQ_API_KEY")
if not _api_key:
    raise EnvironmentError("GROQ_API_KEY environment variable is not set")

client = Groq(api_key=_api_key)

def generate_text(concept: str) -> str:
    """
    Calls Groq LLaMA 3.3 to produce:
      - Structured explanation  (Title + Section 1-4)
      - Full visual brief       (ImageSubject, ImageScene, ImageAction,
                                 ImageStyle, ImageDetails, ColorTheme)

    The visual brief is used by image_generator.py to build a
    rich, concept-specific image prompt — not a generic one.
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert insurance educator and creative visual director. "
                    "If the concept is not related to insurance you should not attempt to create an explanation or visual brief and reply with text as follows: 'The provided concept is outside the scope of insurance. Please provide a valid insurance-related concept for explanation and visualization.' "
                    "Always respond in plain English only. "
                    "Never use markdown, foreign characters, or symbols. "
                    "Follow the exact structured format provided precisely — "
                    "every field must be filled with specific, concept-relevant content."
                ),
            },
            {
                "role": "user",
                "content": build_text_prompt(concept),
            },
        ],
        temperature=0.6,   # slightly higher for richer visual descriptions
        max_tokens=600,    # enough room for all 9 fields
    )
    return response.choices[0].message.content