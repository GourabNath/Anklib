"""
Anklib - Book Metadata Extraction API

Step 2:
- Accept image upload
- Convert image to base64
- Send image to GPT (LLM)
- Extract structured metadata (title, author, publisher)
- Return clean JSON response
"""

from fastapi import FastAPI, File, UploadFile
from openai import OpenAI
import base64
import json

# Initialize FastAPI app
app = FastAPI()

# Initialize OpenAI client
client = OpenAI()


@app.get("/anklib")
def home():
    """
    Health check endpoint

    URL:
    http://127.0.0.1:8000/anklib
    """
    return {"message": "Welcome to Anklib API 🚀"}


def extract_book_metadata(image_b64: str):
    """
    Helper function to call GPT and extract book metadata

    Parameters:
    - image_b64 (str): Base64 encoded image string

    Returns:
    - dict: Extracted metadata (title, author, publisher)
    """

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

    # Convert response to JSON safely
    try:
        data = json.loads(response.output_text)
    except Exception:
        data = {"raw_output": response.output_text}

    return data


@app.post("/anklib/extract")
async def extract(file: UploadFile = File(...)):
    """
    Main endpoint to handle image upload and metadata extraction

    Steps:
    1. Read uploaded image file
    2. Convert image to base64
    3. Send to LLM for extraction
    4. Return structured JSON
    """

    # Step 1: Read file as bytes
    content = await file.read()

    # Step 2: Convert bytes to base64 string
    image_b64 = base64.b64encode(content).decode("utf-8")

    # Step 3: Extract metadata using helper function
    result = extract_book_metadata(image_b64)

    # Step 4: Return result
    return result