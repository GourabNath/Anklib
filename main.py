from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from services.extractor import extract_book_metadata
from utils.image import encode_image

app = FastAPI()


@app.get("/anklib")
def home():
    return {"message": "Welcome to Anklib API"}


@app.post("/anklib/extract")
async def extract(file: UploadFile = File(...)):

    if not file.content_type.startswith("image/"):
        return {"error": "Only image files are supported"}

    try:
        content = await file.read()
        image_b64 = encode_image(content)

        result = extract_book_metadata(image_b64)

        return {
            "status": "success",
            "data": result
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }



@app.get("/", response_class=HTMLResponse)
def ui():
    return """
    <html>
        <head>
            <title>Anklib - Book Extractor</title>
        </head>
        <body>
            <h2>📚 Anklib - Book Metadata Extractor</h2>

            <form action="/anklib/extract" enctype="multipart/form-data" method="post">
                <input name="file" type="file" accept="image/*" required>
                <br><br>
                <button type="submit">Extract Metadata</button>
            </form>

            <p>Upload a book image and get structured metadata.</p>
        </body>
    </html>
    """

