import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from supabase import create_client, Client

# --- Configuration ---
# In production, use environment variables!
URL = "https://bdrwzxqucaefpwxyjqvv.supabase.co"
KEY = "sb_publishable_rpTK6BCBOdUZC8O5TKIbcw_gAtloIGs"
SECRET_BEARER_TOKEN = "passwordassignment6"

supabase: Client = create_client(URL, KEY)
app = FastAPI(title="Bookstore API", description="Relational Database CRUD with Supabase")

# --- Schemas (Type Hints) ---
class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    published_year: int
    is_available: bool = True

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    is_available: Optional[bool] = None

# --- Security Dependency ---
async def verify_token(authorization: str = Header(...)):
    if authorization != f"Bearer {SECRET_BEARER_TOKEN}":
        raise HTTPException(status_code=403, detail="Invalid or missing Bearer Token")

# --- Routes ---

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/books", response_model=List[dict])
def get_books():
    response = supabase.table("books").select("*").execute()
    return response.data

@app.post("/books", status_code=201)
def create_book(book: BookCreate, token: str = Depends(verify_token)):
    response = supabase.table("books").insert(book.dict()).execute()
    return response.data

@app.put("/books/{book_id}")
def update_book(book_id: int, book: BookCreate, token: str = Depends(verify_token)):
    response = supabase.table("books").update(book.dict()).eq("id", book_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Book not found")
    return response.data

@app.patch("/books/{book_id}")
def patch_book(book_id: int, book: BookUpdate, token: str = Depends(verify_token)):
    update_data = {k: v for k, v in book.dict().items() if v is not None}
    response = supabase.table("books").update(update_data).eq("id", book_id).execute()
    return response.data

@app.delete("/books/{book_id}")
def delete_book(book_id: int, token: str = Depends(verify_token)):
    response = supabase.table("books").delete().eq("id", book_id).execute()
    return {"message": f"Book {book_id} deleted"}
