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
                        "text": """<YOUR UPDATED PROMPT HERE>"""
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