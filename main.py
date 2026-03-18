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
    # Serve frontend UI
    return """
    <html>
        <head>
            <title>Anklib</title>
            <style>
                body {
                    font-family: Arial;
                    background-color: #f5f5f5;
                    text-align: center;
                    padding: 40px;
                }

                .container {
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    max-width: 500px;
                    margin: auto;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                }

                button {
    background-color: #4CAF50;
    color: white;

    /* Bigger size for mobile */
    padding: 14px 24px;
    font-size: 16px;
    font-weight: bold;

    border: none;
    border-radius: 8px;

    cursor: pointer;

    /* Make button full-width on small screens */
    width: 100%;
    max-width: 300px;

    /* Add spacing */
    margin-top: 10px;
}

                pre {
    text-align: left;
    background: #f9f9f9;
    padding: 15px;
    border-radius: 8px;
    line-height: 1.6;
}

                img {
                    max-width: 100%;
                    margin-top: 10px;
                }
            </style>
        </head>

        <body>
            <div class="container">
                <h2>📚 Anklib</h2>
                <p>Upload a book image to extract metadata</p>

                <!-- File input with camera support -->
                <input id="fileInput" type="file" accept="image/*" capture="environment" onchange="previewImage()">
                <br><br>

                <!-- Image preview -->
                <img id="preview" style="display:none;" />

                <br>

                <!-- IMPORTANT: added id so JS can control button -->
                <button id="extractBtn" onclick="uploadFile()">Extract Metadata</button>

                <h3>Result:</h3>
                <pre id="resultBox">No result yet</pre>
            </div>

            <script>

                // Preview selected image
                function previewImage() {
                    const file = document.getElementById('fileInput').files[0];
                    const preview = document.getElementById('preview');

                    if (file) {
                        preview.src = URL.createObjectURL(file);
                        preview.style.display = "block";
                    }
                }

                // Main function triggered on button click
                async function uploadFile() {

                    console.log("Button clicked"); // Debug (safe, no popup)

                    const fileInput = document.getElementById('fileInput');
                    const file = fileInput.files[0];
                    const button = document.getElementById("extractBtn");

                    // Prevent empty submission
                    if (!file) {
                        alert("Please select a file");
                        return;
                    }

                    // UI: loading state
                    button.disabled = true;
                    button.textContent = "Processing...";
                    document.getElementById("resultBox").textContent = "Processing...";

                    try {
                        const formData = new FormData();
                        formData.append("file", file);

                        const response = await fetch("/anklib/extract", {
                            method: "POST",
                            body: formData
                        });

                        if (!response.ok) {
                            throw new Error("Server error: " + response.status);
                        }

                        const data = await response.json();

                        // Extract structured data from response
const book = data.data;

// Build clean HTML output (user-friendly instead of JSON)
let output = "";

// Only show fields if they exist (avoids empty clutter)
if (book.title) {
    output += "<b>Title:</b> " + book.title + "<br><br>";
}

if (book.author) {
    output += "<b>Author:</b> " + book.author + "<br><br>";
}

if (book.publisher) {
    output += "<b>Publisher:</b> " + book.publisher + "<br><br>";
}

if (book.isbn) {
    output += "<b>ISBN:</b> " + book.isbn + "<br><br>";
}

if (book.edition) {
    output += "<b>Edition:</b> " + book.edition + "<br><br>";
}

if (book.price) {
    output += "<b>Price:</b> " + book.price + "<br><br>";
}

// Inject formatted HTML into UI
document.getElementById("resultBox").innerHTML = output;

                    } catch (error) {

                        document.getElementById("resultBox").textContent =
                            "❌ Error: " + error.message;

                    } finally {

                        // Reset button
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