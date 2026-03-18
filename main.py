from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from services.extractor import extract_book_metadata
from utils.image import encode_image

# Initialize FastAPI app
app = FastAPI()


@app.get("/anklib")
def home():
    # Health check endpoint
    return {"message": "Welcome to Anklib API"}


@app.post("/anklib/extract")
async def extract(file: UploadFile = File(...)):

    # Ensure uploaded file is an image
    if not file.content_type.startswith("image/"):
        return {"error": "Only image files are supported"}

    try:
        # Read file bytes
        content = await file.read()

        # Convert image to base64
        image_b64 = encode_image(content)

        # Extract metadata using LLM service
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

            <meta name="viewport" content="width=device-width, initial-scale=1.0">

            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f5f5f5;
                    text-align: center;
                    padding: 20px;
                }

                .container {
                    background: white;
                    padding: 25px;
                    border-radius: 12px;
                    max-width: 500px;
                    margin: auto;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                }

                /* Green button */
                button {
                    background-color: #4CAF50;
                    color: white;
                    padding: 16px;
                    font-size: 18px;
                    font-weight: bold;
                    border: none;
                    border-radius: 10px;
                    width: 100%;
                    max-width: 400px;
                    margin-top: 15px;
                    cursor: pointer;
                }

                button:disabled {
                    background-color: #999;
                }

                /* Blue upload button */
                .upload-btn {
                    display: block;
                    background-color: #2196F3;
                    color: white;
                    padding: 16px;
                    font-size: 18px;
                    font-weight: bold;
                    border-radius: 10px;
                    cursor: pointer;
                    width: 100%;
                    max-width: 400px;
                    margin: 15px auto 0 auto;
                    box-sizing: border-box;
                }

                .upload-btn:hover {
                    background-color: #1976D2;
                }

                .file-name {
                    margin-top: 10px;
                    font-size: 14px;
                    color: #555;
                }

                img {
                    max-width: 100%;
                    margin-top: 10px;
                    border-radius: 5px;
                }

                /* ✅ Result box (NEW STYLE) */
                #resultBox {
                    text-align: center;
                    background: #f9f9f9;
                    padding: 20px;
                    border-radius: 10px;
                    margin-top: 10px;
                }

                /* Each field block */
                .field-block {
                    margin-bottom: 20px;
                }

                /* Label (Title, Author...) */
                .field-label {
                    font-size: 14px;
                    font-weight: bold;
                    color: #777;
                }

                /* Value */
                .field-value {
                    font-size: 18px;
                    font-weight: 500;
                    color: #222;
                    margin-top: 5px;

                    /* Ensure long text wraps properly */
                    word-wrap: break-word;
                    overflow-wrap: break-word;
                }
            </style>
        </head>

        <body>
            <div class="container">
                <h2>📚 Anklib</h2>
                <p>Upload a book image to extract metadata</p>

                <label for="fileInput" class="upload-btn">
                    📸 Choose or Capture Image
                </label>

                <input id="fileInput" type="file" accept="image/*" capture="environment"
                       onchange="handleFileSelect()" style="display:none;">

                <div id="fileName" class="file-name">No file selected</div>

                <img id="preview" style="display:none;" />

                <button id="extractBtn" onclick="uploadFile()">Extract Metadata</button>

                <h3>Result:</h3>
                <!-- ✅ switched from <pre> to <div> -->
                <div id="resultBox">No result yet</div>
            </div>

            <script>

                function handleFileSelect() {
                    const file = document.getElementById('fileInput').files[0];
                    const preview = document.getElementById('preview');
                    const fileName = document.getElementById('fileName');

                    if (file) {
                        preview.src = URL.createObjectURL(file);
                        preview.style.display = "block";
                        fileName.textContent = "Selected: " + file.name;
                    }
                }

                async function uploadFile() {

                    const fileInput = document.getElementById('fileInput');
                    const file = fileInput.files[0];
                    const button = document.getElementById("extractBtn");

                    if (!file) {
                        alert("Please select a file");
                        return;
                    }

                    button.disabled = true;
                    button.textContent = "Processing...";
                    document.getElementById("resultBox").textContent = "Processing...";

                    try {
                        const formData = new FormData();
                        formData.append("file", file);

                        const response = await fetch(window.location.origin + "/anklib/extract", {
                            method: "POST",
                            body: formData
                        });

                        if (!response.ok) {
                            throw new Error("Server error: " + response.status);
                        }

                        const data = await response.json();
                        const book = data.data;

                        // Helper to create field blocks
                        function createField(label, value) {
                            return `
                                <div class="field-block">
                                    <div class="field-label">${label}</div>
                                    <div class="field-value">${value}</div>
                                </div>
                            `;
                        }

                        let output = "";

                        if (book.title) output += createField("Title", book.title);
                        if (book.author) output += createField("Author", book.author);
                        if (book.publisher) output += createField("Publisher", book.publisher);
                        if (book.isbn) output += createField("ISBN", book.isbn);
                        if (book.edition) output += createField("Edition", book.edition);
                        if (book.price) output += createField("Price", book.price);

                        document.getElementById("resultBox").innerHTML = output;

                    } catch (error) {

                        document.getElementById("resultBox").textContent =
                            "❌ Error: " + error.message;

                    } finally {

                        button.disabled = false;
                        button.textContent = "Extract Metadata";
                    }
                }

            </script>

        </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)