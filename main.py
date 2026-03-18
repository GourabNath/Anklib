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
            <title>Anklib</title>
        </head>
        <body>
            <h2>📚 Anklib - Book Metadata Extractor</h2>

            <input id="fileInput" type="file" accept="image/*">
            <br><br>
            <button onclick="uploadFile()">Extract Metadata</button>

            <h3>Result:</h3>
            <pre id="resultBox">No result yet</pre>

            <script>
                async function uploadFile() {
                    const fileInput = document.getElementById('fileInput');
                    const file = fileInput.files[0];

                    if (!file) {
                        alert("Please select a file");
                        return;
                    }

                    const formData = new FormData();
                    formData.append("file", file);

                    const response = await fetch("/anklib/extract", {
                        method: "POST",
                        body: formData
                    });

                    const data = await response.json();

                    document.getElementById("resultBox").textContent =
                        JSON.stringify(data, null, 2);
                }
            </script>
        </body>
    </html>
    """
