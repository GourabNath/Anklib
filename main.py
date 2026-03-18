from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from services.extractor import extract_book_metadata
from utils.image import encode_image

# Initialize FastAPI application (entry point of the API)
app = FastAPI()


@app.get("/anklib")
def home():
    # Simple health check endpoint to verify API is running
    return {"message": "Welcome to Anklib API"}


@app.post("/anklib/extract")
async def extract(file: UploadFile = File(...)):

    # Validate that the uploaded file is an image
    # Prevents sending unsupported file types to the LLM pipeline
    if not file.content_type.startswith("image/"):
        return {"error": "Only image files are supported"}

    try:
        # Read uploaded image bytes (needed before encoding for LLM input)
        content = await file.read()

        # Convert image bytes → base64 string (required for OpenAI image input)
        image_b64 = encode_image(content)

        # Call extraction service (LLM handles metadata extraction)
        result = extract_book_metadata(image_b64)

        # Return structured response to frontend
        return {
            "status": "success",
            "data": result
        }

    except Exception as e:
        # Catch unexpected errors and return safe error response
        # Prevents API crash and helps debugging
        return {
            "status": "error",
            "message": str(e)
        }



@app.get("/", response_class=HTMLResponse)
def ui():
    # Serves a simple frontend UI directly from FastAPI
    # Allows users to upload images and view results without separate frontend app
    return """
    <html>
        <head>
            <title>Anklib</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
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
                    padding: 10px 20px;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                }

                button:hover {
                    background-color: #45a049;
                }

                pre {
                    text-align: left;
                    background: #eee;
                    padding: 10px;
                    border-radius: 5px;
                    overflow-x: auto;
                }

                img {
                    max-width: 100%;
                    margin-top: 10px;
                    border-radius: 5px;
                }
            </style>
        </head>

        <body>
            <div class="container">
                <h2>📚 Anklib</h2>
                <p>Upload a book image to extract metadata</p>

                <!-- File input allows selecting image from device or camera (mobile-friendly) -->
                <input id="fileInput" type="file" accept="image/*" onchange="previewImage()">
                <br><br>

                <!-- Preview selected image before upload -->
                <img id="preview" style="display:none;" />

                <br>
                <!-- Trigger extraction without page reload -->
                <button onclick="uploadFile()">Extract Metadata</button>

                <h3>Result:</h3>
                <!-- Display formatted JSON response -->
                <pre id="resultBox">No result yet</pre>
            </div>

            <script>
                function previewImage() {
                    // Show preview of selected image for better user experience
                    const file = document.getElementById('fileInput').files[0];
                    const preview = document.getElementById('preview');

                    if (file) {
                        preview.src = URL.createObjectURL(file);
                        preview.style.display = "block";
                    }
                }

                async function uploadFile() {
    // Get the file input element
    const fileInput = document.getElementById('fileInput');

    // Get the selected file (first file from input)
    const file = fileInput.files[0];

    // Get the button element to control its state (disable/enable)
    const button = document.querySelector("button");

    // Guard clause: stop if no file is selected
    if (!file) {
        alert("Please select a file");
        return;
    }

    // Prepare form data for sending file to backend
    const formData = new FormData();
    formData.append("file", file);

    // UI FEEDBACK: indicate processing has started
    button.disabled = true;                 // prevent multiple clicks
    button.textContent = "Processing...";   // update button text

    // Show immediate feedback in result box
    document.getElementById("resultBox").textContent = "Processing...";

    // Send POST request to backend endpoint
    const response = await fetch("/anklib/extract", {
        method: "POST",
        body: formData
    });

    // Parse JSON response from backend
    const data = await response.json();

    // Display formatted JSON result in UI
    document.getElementById("resultBox").textContent =
        JSON.stringify(data, null, 2);

    // RESET UI: restore button to original state
    button.disabled = false;
    button.textContent = "Extract Metadata";
}
            </script>
        </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)