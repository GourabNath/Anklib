from fastapi import FastAPI, File, UploadFile

app = FastAPI()   # Create my API application

@app.get("/anklib")     # If someone comes to / and asks for a GET request, run the function below

# @app → attach this to your app
# .get → when someone requests data
# "/anklib" → the root path (like homepage)

def home():
    """
    Health check endpoint

    This helps us verify:
    - Server is running
    - Routing works

    URL:
    http://127.0.0.1:8000/anklib
    """
    return {"message": "Book Extractor API is running"}



@app.post("/ankita/extract")
async def extract(file: UploadFile = File(...)):  # The function is doing I/O work (reading a file, calling APIs later)
	content = await file.read()
	return {
		"filename": file.filename,
		"size": len(content)
		}


# Notes on Async:
# What is I/O? Reading file, calling GPT, database calls. These are slow operations.
# Why async helps? Instead of: “Wait here until file read finishes.” It says: “While waiting, go handle other requests”