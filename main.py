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

# Initialize FastAPI application
app = FastAPI()

# Initialize OpenAI client (uses API key from environment)
client = OpenAI()


@app.get("/anklib")
def home():
    """
    Health check endpoint

    Purpose:
    - Verify API is running
    - Simple test route

    URL:
    http://127.0.0.1:8000/anklib
    """
    return {"message": "Welcome to Anklib API 🚀"}


def extract_book_metadata(image_b64: str):
    """
    Calls GPT to extract book metadata from an image

    Parameters:
    - image_b64 (str): Base64 encoded image string

    Returns:
    - dict: Extracted metadata (title, author, publisher)
    """

    # Send request to GPT with both text instruction and image
    response = client.responses.create(
        model="gpt-5.2",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        # Instruction to the model
                        "type": "input_text",
                        "text": "Extract title, author, and publisher from this book image. Return JSON."
                    },
                    {
                        # Image passed as base64 data URL
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{image_b64}"
                    }
                ]
            }
        ]
    )

    # Attempt to parse model output into JSON
    try:
        # Remove extra whitespace
        text = response.output_text.strip()

        # Remove markdown formatting if model returns ```json ... ```
        if text.startswith("```"):
            text = text.replace("```json", "").replace("```", "").strip()

        # Convert string → dictionary
        data = json.loads(text)

    except Exception:
        # Fallback: return raw output if parsing fails
        data = {"raw_output": response.output_text}

    return data


@app.post("/anklib/extract")
async def extract(file: UploadFile = File(...)):
    """
    Main endpoint for book metadata extraction

    Input:
    - file: Uploaded image (book cover / ISBN page)

    Workflow:
    1. Read uploaded file
    2. Convert image to base64
    3. Send to LLM for extraction
    4. Return structured metadata
    """

    # Step 1: Read file content as bytes
    content = await file.read()

    # Step 2: Convert bytes → base64 string (required for GPT input)
    image_b64 = base64.b64encode(content).decode("utf-8")

    # Step 3: Extract metadata using helper function
    result = extract_book_metadata(image_b64)

    # Step 4: Return structured response
    return result