# REST API (FastAPI): CRUD for books with validation, pagination, proper status codes, tests
from typing import Annotated, Optional
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field


class BookIn(BaseModel):                          # request body (no id)
    title: str = Field(min_length=1, max_length=100)
    author: str = Field(min_length=1)
    price: float = Field(gt=0)


class BookPatch(BaseModel):                       # PATCH: every field optional
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    author: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)


class Book(BookIn):                               # response model adds id
    id: int


class BookRepo:
    """In-memory repository; swap for SQLAlchemy later without touching routes."""
    def __init__(self) -> None:
        self._data: dict[int, Book] = {}
        self._next = 1

    def add(self, b: BookIn) -> Book:
        book = Book(id=self._next, **b.model_dump())
        self._data[book.id] = book
        self._next += 1
        return book

    def get(self, id_: int) -> Optional[Book]:
        return self._data.get(id_)

    def list(self, offset: int, limit: int) -> list[Book]:
        return list(self._data.values())[offset:offset + limit]

    def delete(self, id_: int) -> bool:
        return self._data.pop(id_, None) is not None

    def save(self, book: Book) -> Book:
        self._data[book.id] = book
        return book


_repo = BookRepo()                                # one repo per process


def get_repo() -> BookRepo:                       # dependency (overridable in tests)
    return _repo


Repo = Annotated[BookRepo, Depends(get_repo)]
app = FastAPI(title="Books API")


@app.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_book(body: BookIn, repo: Repo) -> Book:
    return repo.add(body)


@app.get("/books", response_model=list[Book])
def list_books(repo: Repo, offset: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100)) -> list[Book]:
    return repo.list(offset, limit)


@app.get("/books/{book_id}", response_model=Book)
def read_book(book_id: int, repo: Repo) -> Book:
    book = repo.get(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.put("/books/{book_id}", response_model=Book)
def replace_book(book_id: int, body: BookIn, repo: Repo) -> Book:
    if repo.get(book_id) is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return repo.save(Book(id=book_id, **body.model_dump()))


@app.patch("/books/{book_id}", response_model=Book)
def patch_book(book_id: int, body: BookPatch, repo: Repo) -> Book:
    book = repo.get(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    updated = book.model_copy(update=body.model_dump(exclude_unset=True))   # only sent fields
    return repo.save(updated)


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, repo: Repo) -> None:
    if not repo.delete(book_id):
        raise HTTPException(status_code=404, detail="Book not found")


if __name__ == "__main__":
    c = TestClient(app)
    r = c.post("/books", json={"title": "Dune", "author": "Herbert", "price": 9.5})
    assert r.status_code == 201 and r.json()["id"] == 1
    c.post("/books", json={"title": "Emma", "author": "Austen", "price": 5})
    assert len(c.get("/books").json()) == 2
    assert len(c.get("/books?limit=1&offset=1").json()) == 1
    assert c.get("/books/1").json()["title"] == "Dune"
    assert c.get("/books/99").status_code == 404
    assert c.post("/books", json={"title": "", "author": "x", "price": -1}).status_code == 422
    assert c.get("/books?limit=1000").status_code == 422
    assert c.patch("/books/1", json={"price": 12}).json() == {"id": 1, "title": "Dune", "author": "Herbert", "price": 12.0}
    assert c.put("/books/1", json={"title": "Dune2", "author": "H", "price": 1}).json()["title"] == "Dune2"
    assert c.delete("/books/1").status_code == 204
    assert c.delete("/books/1").status_code == 404
    print("all REST API tests passed")
