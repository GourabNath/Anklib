from pydantic import BaseModel
from typing import Optional

class BookMetadata(BaseModel):
    title: Optional[str]
    author: Optional[str]
    publisher: Optional[str]
    isbn: Optional[str]
    edition: Optional[str]
    price: Optional[str]