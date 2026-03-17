import base64

def encode_image(content: bytes) -> str:
    return base64.b64encode(content).decode("utf-8")