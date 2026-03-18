from openai import OpenAI
import json
import re

client = OpenAI()

def clean_isbn(isbn):
    if not isbn:
        return None
    return re.sub(r"[^0-9Xx]", "", isbn)


def extract_book_metadata(image_b64: str):

    response = client.responses.create(
        model="gpt-5.2",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": """
You are extracting structured metadata from a book image.

Extract the following fields:
- title
- author
- publisher
- isbn
- edition
- price


Rules:
- Return ONLY valid JSON (no markdown, no explanations)
- If a field is not visible, return null
- Do not guess or hallucinate
- Prefer clearly printed text (ignore blur/noise)
- If multiple authors exist, return as a comma-separated string

Field-specific rules:
- isbn: Extract ISBN-10 or ISBN-13 (numbers only, remove dashes/spaces)
- edition: Capture edition info like "2nd Edition", "Third Edition"
- price: Capture price with currency if visible (e.g., "₹499", "$20")

Output format:
{
  "title": "...",
  "author": "...",
  "publisher": "...",
  "isbn": "...",
  "edition": "...",
  "price": "..."
}
"""
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{image_b64}"
                    }
                ]
            }
        ]
    )

    try:
        text = response.output_text.strip()

        if text.startswith("```"):
            text = text.replace("```json", "").replace("```", "").strip()

        data = json.loads(text)

        # Ensure all fields exist
        for field in ["title", "author", "publisher", "isbn", "edition", "price"]:
            data.setdefault(field, None)

        # Normalize ISBN
        data["isbn"] = clean_isbn(data.get("isbn"))

    except Exception:
        data = {"raw_output": response.output_text}

    return data
