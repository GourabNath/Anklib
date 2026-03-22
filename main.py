from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from services.extractor import extract_book_metadata
from utils.image import encode_image

# Initialize FastAPI app instance
app = FastAPI()


@app.get("/anklib")
def home():
    # Simple health check endpoint to verify API is running
    return {"message": "Welcome to Anklib API"}


@app.post("/anklib/extract")
async def extract(file: UploadFile = File(...)):

    # Validate that the uploaded file is an image
    if not file.content_type.startswith("image/"):
        return {"error": "Only image files are supported"}

    try:
        # Read the uploaded file content as bytes
        content = await file.read()

        # Convert image bytes into base64 string (required for LLM processing)
        image_b64 = encode_image(content)

        # Call extraction service (likely an LLM) to get book metadata
        result = extract_book_metadata(image_b64)

        # Return structured success response
        return {
            "status": "success",
            "data": result
        }

    except Exception as e:
        # Catch and return any runtime errors
        return {
            "status": "error",
            "message": str(e)
        }



@app.get("/", response_class=HTMLResponse)
def ui():
    # Serve a simple frontend UI for interacting with the API
    return """
    <html>
        <head>
            <title>Anklib</title>

            <!-- Ensures proper scaling on mobile devices -->
            <meta name="viewport" content="width=device-width, initial-scale=1.0">

            <style>
                /* Base page styling */
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f5f5f5;
                    text-align: center;
                    padding: 20px;
                }

                /* Card container for UI */
                .container {
                    background: white;
                    padding: 25px;
                    border-radius: 12px;
                    max-width: 500px;
                    margin: auto;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                }

                /* Green action button (Extract Metadata) */
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

                /* Disabled button state */
                button:disabled {
                    background-color: #999;
                }

                /* Blue upload button (custom file input trigger) */
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

                /* Hover effect for upload button */
                .upload-btn:hover {
                    background-color: #1976D2;
                }

                /* Displays selected file name */
                .file-name {
                    margin-top: 10px;
                    font-size: 14px;
                    color: #555;
                }

                /* Image preview styling */
                img {
                    max-width: 100%;
                    margin-top: 10px;
                    border-radius: 5px;
                }

                /* Result container */
                #resultBox {
                    text-align: center;
                    background: #f9f9f9;
                    padding: 20px;
                    border-radius: 10px;
                    margin-top: 10px;
                }

                /* Each metadata field block */
                .field-block {
                    margin-bottom: 20px;
                }

                /* Field label (e.g., Title, Author) */
                .field-label {
                    font-size: 14px;
                    font-weight: bold;
                    color: #777;
                }

                /* Field value (actual data) */
                .field-value {
                    font-size: 16px;
                    font-weight: 500;
                    color: #222;
                    margin-top: 1px;

                    /* Handle long text wrapping */
                    word-wrap: break-word;
                    overflow-wrap: break-word;
                }
            </style>
        </head>

        <body>
            <div class="container">
                <h2>📚 Anklib</h2>
                <p>Upload a book image to extract metadata</p>

                <!-- Custom styled upload button -->
                <label for="fileInput" class="upload-btn">
                    📸 Choose or Capture Image
                </label>

                <!-- Hidden file input -->
                <input id="fileInput" type="file" accept="image/*" capture="environment"
                       onchange="handleFileSelect()" style="display:none;">

                <!-- Displays selected file name -->
                <div id="fileName" class="file-name">No file selected</div>

                <!-- Image preview -->
                <img id="preview" style="display:none;" />

                <!-- Trigger extraction -->
                <button id="extractBtn" onclick="uploadFile()">Extract Metadata</button>

                
                <!-- Result display container -->
                <div id="resultBox">No result yet</div>
            </div>

            <script>

                // Handles file selection and preview rendering
                function handleFileSelect() {
                    const file = document.getElementById('fileInput').files[0];
                    const preview = document.getElementById('preview');
                    const fileName = document.getElementById('fileName');

                    if (file) {
                        // Create temporary URL for preview
                        preview.src = URL.createObjectURL(file);
                        preview.style.display = "block";

                        // Show file name
                        fileName.textContent = "Selected: " + file.name;
                    }
                }

                // Handles file upload and API call
                async function uploadFile() {

                    const fileInput = document.getElementById('fileInput');
                    const file = fileInput.files[0];
                    const button = document.getElementById("extractBtn");

                    // Ensure a file is selected
                    if (!file) {
                        alert("Please select a file");
                        return;
                    }

                    // Update UI to loading state
                    button.disabled = true;
                    button.textContent = "Processing...";
                    document.getElementById("resultBox").textContent = "Processing...";

                    try {
                        // Prepare form data for POST request
                        const formData = new FormData();
                        formData.append("file", file);

                        // Call backend extraction API
                        const response = await fetch(window.location.origin + "/anklib/extract", {
                            method: "POST",
                            body: formData
                        });

                        // Handle HTTP errors
                        if (!response.ok) {
                            throw new Error("Server error: " + response.status);
                        }

                        // Parse JSON response
                        const data = await response.json();
                        const book = data.data;

                        // Helper function to generate HTML blocks for each field
                        function createField(label, value) {
                            return `
                                <div class="field-block">
                                    <div class="field-label">${label}</div>
                                    <div class="field-value">${value}</div>
                                </div>
                            `;
                        }

                        let output = "";

                        // Dynamically add only available fields
                        if (book.title) output += createField("Title", book.title);
                        if (book.author) output += createField("Author", book.author);
                        if (book.publisher) output += createField("Publisher", book.publisher);
                        if (book.isbn) output += createField("ISBN", book.isbn);
                        if (book.edition) output += createField("Edition", book.edition);
                        if (book.price) output += createField("Price", book.price);

                        // Render result in UI
                        document.getElementById("resultBox").innerHTML = output;

                    } catch (error) {

                        // Display error message in UI
                        document.getElementById("resultBox").textContent =
                            "❌ Error: " + error.message;

                    } finally {

                        // Reset button state
                        button.disabled = false;
                        button.textContent = "Extract Metadata";
                    }
                }

            </script>

        </body>
    </html>
    """


# Entry point for running the app locally using Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)