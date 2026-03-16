from fastapi import FastAPI

app = FastAPI()   # Create my API application

@app.get("/anklib")     # If someone comes to / and asks for a GET request, run the function below

# @app → attach this to your app
# .get → when someone requests data
# "/" → the root path (like homepage)

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




# Note:
# Note: The full URL that you open in browser to trigger it
# http://127.0.0.1:8000/hello
# http:// → protocol
# 127.0.0.1 → your own computer (localhost)
# :8000 → port where your server is running
# / → the route you defined