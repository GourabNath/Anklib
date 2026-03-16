"""
Anklib - Book Metadata Extraction API
"""

from fastapi import FastAPI, File, UploadFile
from openai import OpenAI
import base64
import json

app = FastAPI()
client = OpenAI()


@app.get("/anklib")
def home():
    return {"message": "Welcome to Anklib API 🚀"}


def extract_book_metadata(image_b64: str):

    response = client.responses.create(
        model="gpt-5.2",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "Extract title, author, and publisher from this book image. Return JSON."
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

    except Exception:
        data = {"raw_output": response.output_text}

    return data


@app.post("/anklib/extract")
async def extract(file: UploadFile = File(...)):

    content = await file.read()
    image_b64 = base64.b64encode(content).decode("utf-8")

    result = extract_book_metadata(image_b64)

    return result