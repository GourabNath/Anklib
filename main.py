from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, JSONResponse
from services.extractor import extract_book_metadata
from utils.image import encode_image
from services.sheets import save_to_sheets  # 🆕 NEW

# Initialize FastAPI app
app = FastAPI()


@app.get("/anklib")
def home():
    """
    Description:
        Health check endpoint to verify that the API is running.

    Parameters:
        None

    Returns:
        dict: Simple welcome message.
    """
    return {"message": "Welcome to Anklib API"}


@app.post("/anklib/extract")
async def extract(file: UploadFile = File(...)):
    """
    Description:
        Accepts an image file, converts it to base64, and extracts
        book metadata using an LLM-based service.

    Parameters:
        file (UploadFile): Uploaded image file.

    Returns:
        dict:
            - status: success/error
            - data: extracted metadata (if successful)
    """

    # Validate file type
    if not file.content_type.startswith("image/"):
        return {"error": "Only image files are supported"}

    try:
        # Read file as bytes
        content = await file.read()

        # Convert image to base64
        image_b64 = encode_image(content)

        # Call LLM extractor
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


# 🆕 NEW ENDPOINT: Save extracted metadata in google sheets
@app.post("/anklib/confirm")
async def confirm(request: Request):
    """
    Description:
        Receives user-edited metadata and saves it to Google Sheets.
    """
    data = await request.json()

    # 🆕 Save to Google Sheets
    save_to_sheets(data)

    return {"status": "saved"}


# Handles user-confirmed / edited metadata
@app.post("/anklib/confirm")
async def confirm(request: Request):
    """
    Description:
        Receives user-reviewed (and possibly edited) metadata from the UI.
        This acts as the human-in-the-loop validation layer.

    Parameters:
        request (Request): Incoming request containing JSON payload.

    Returns:
        dict: Confirmation status.
    """
    # Extract JSON payload from request
    data = await request.json()

    # 🆕 For now: log the confirmed data (placeholder for DB / Sheets)
    print("✅ Confirmed Data:", data)

    return {"status": "saved"}


@app.get("/", response_class=HTMLResponse)
def ui():
    """
    Description:
        Serves the frontend UI for:
        - Uploading an image
        - Viewing extracted metadata
        - Editing metadata
        - Confirming and saving data

    Parameters:
        None

    Returns:
        HTMLResponse: UI page
    """
    return """
    <html>
        <head>
            <title>Anklib</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">

            <style>
                body {
                    font-family: Arial;
                    background: #f5f5f5;
                    text-align: center;
                    padding: 20px;
                }

                .container {
                    background: white;
                    padding: 25px;
                    border-radius: 12px;
                    max-width: 500px;
                    margin: auto;
                }

                button {
                    background: #4CAF50;
                    color: white;
                    padding: 14px;
                    border: none;
                    border-radius: 8px;
                    width: 100%;
                    margin-top: 10px;
                    cursor: pointer;
                }

                .upload-btn {
                    display: block;
                    background: #2196F3;
                    color: white;
                    padding: 14px;
                    border-radius: 8px;
                    cursor: pointer;
                    margin-top: 10px;
                }

                input {
                    width: 100%;
                    padding: 8px;
                    margin-top: 5px;
                    border-radius: 6px;
                    border: 1px solid #ccc;
                }

                .field-block {
                    margin-bottom: 15px;
                    text-align: left;
                }

                .field-label {
                    font-size: 12px;
                    color: #777;
                }
            </style>
        </head>

        <body>
            <div class="container">
                <h2>📚 Anklib</h2>

                <!-- Upload button -->
                <label for="fileInput" class="upload-btn">
                    📸 Upload Image
                </label>

                <!-- Hidden file input -->
                <input id="fileInput" type="file" accept="image/*"
                       onchange="handleFileSelect()" style="display:none;">

                <!-- Image preview -->
                <img id="preview" style="display:none; max-width:100%; margin-top:10px;" />

                <!-- Extract trigger -->
                <button id="extractBtn" onclick="uploadFile()">Extract Metadata</button>

                <!-- 🆕 Editable metadata container -->
                <div id="resultBox" style="margin-top:20px;"></div>

                <!-- 🆕 Confirm button (hidden initially) -->
                <button id="confirmBtn" onclick="confirmData()" style="display:none;">
                    Confirm & Save
                </button>
            </div>

            <script>

                /**
                 * Description:
                 *     Displays preview of selected image.
                 */
                function handleFileSelect() {
                    const file = document.getElementById('fileInput').files[0];
                    const preview = document.getElementById('preview');

                    if (file) {
                        preview.src = URL.createObjectURL(file);
                        preview.style.display = "block";
                    }
                }

                /**
                 * Description:
                 *     Sends image to backend, receives extracted metadata,
                 *     and renders editable fields.
                 */
                async function uploadFile() {

                    const file = document.getElementById('fileInput').files[0];

                    if (!file) {
                        alert("Select a file");
                        return;
                    }

                    const formData = new FormData();
                    formData.append("file", file);

                    const res = await fetch("/anklib/extract", {
                        method: "POST",
                        body: formData
                    });

                    const data = await res.json();
                    const book = data.data;

                    // 🆕 Creates editable input fields instead of static text
                    function field(label, value) {
                        return `
                            <div class="field-block">
                                <div class="field-label">${label}</div>
                                <input id="${label}" value="${value || ""}">
                            </div>
                        `;
                    }

                    let html = "";

                    // 🆕 Render editable fields
                    html += field("Title", book.title);
                    html += field("Author", book.author);
                    html += field("Publisher", book.publisher);
                    html += field("ISBN", book.isbn);
                    html += field("Edition", book.edition);
                    html += field("Price", book.price);

                    document.getElementById("resultBox").innerHTML = html;

                    // 🆕 Show confirm button after extraction
                    document.getElementById("confirmBtn").style.display = "block";
                }


                /**
                 * Description:
                 *     Collects user-edited values from input fields.
                 */
                function collectData() {
                    return {
                        title: document.getElementById("Title")?.value,
                        author: document.getElementById("Author")?.value,
                        publisher: document.getElementById("Publisher")?.value,
                        isbn: document.getElementById("ISBN")?.value,
                        edition: document.getElementById("Edition")?.value,
                        price: document.getElementById("Price")?.value
                    };
                }


                /**
                 * Description:
                 *     Sends user-confirmed metadata to backend.
                 */
                async function confirmData() {

                    const payload = collectData();

                    const res = await fetch("/anklib/confirm", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify(payload)
                    });

                    const result = await res.json();

                    alert("✅ Saved successfully!");
                }

            </script>
        </body>
    </html>
    """


# Entry point to run app locally
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)