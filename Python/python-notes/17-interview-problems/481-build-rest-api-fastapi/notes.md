---

# 481. Build REST API (FastAPI)
# हिंदी में: REST API बनाना (FastAPI में CRUD)

Runnable solution with tests: [main.py](./main.py) (run: `python main.py`, verified on Python 3.13 with fastapi + httpx via TestClient; no server needed).

---

## 🔵 Simple Definition (English)
A REST API exposes resources (books, users, orders) as URLs and uses HTTP methods for actions: POST creates, GET reads, PUT/PATCH updates, DELETE removes. FastAPI builds it from type-hinted Python functions and validates data with Pydantic.

## 🔵 सरल परिभाषा (Hindi)
REST API resources (books, users, orders) को URLs के रूप में दिखाती है और HTTP methods से काम कराती है: POST बनाता है, GET पढ़ता है, PUT/PATCH बदलता है, DELETE हटाता है। FastAPI type-hinted Python functions से इसे बनाता है और Pydantic से data validate करता है।

---

## 🔴 Problem it Solves
Frontends, mobile apps and other services need a stable contract to read and change data. Without conventions, every endpoint invents its own URLs, status codes and error shapes. REST plus Pydantic gives predictable URLs, correct status codes (201, 204, 404, 422), automatic validation, and auto-generated docs at `/docs`.

## 🔴 यह क्यों बना? (Hindi)
Frontends, mobile apps और दूसरी services को data पढ़ने-बदलने के लिए स्थिर contract चाहिए। Conventions न हों तो हर endpoint अपने URLs, status codes और error formats बना लेता है। REST और Pydantic से अनुमानित URLs, सही status codes (201, 204, 404, 422), अपने-आप validation और `/docs` पर auto-generated documentation मिलता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define Pydantic models: BookIn (request), Book (response with id)
Step 2 → Put storage behind a repository class (swap memory for a DB later)
Step 3 → Inject the repository with Depends(get_repo) (easy to override in tests)
Step 4 → POST /books      -> 201 Created + body
Step 5 → GET /books       -> list with ?offset=&limit= (validated with Query ge/le)
Step 6 → GET /books/{id}  -> 200 or raise HTTPException(404)
Step 7 → PUT replaces fully; PATCH updates only sent fields (exclude_unset=True)
Step 8 → DELETE /books/{id} -> 204 No Content (404 if missing)
Step 9 → Invalid input is rejected automatically with 422 before your code runs
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Pydantic models बनाओ: BookIn (request), Book (id के साथ response)
Step 2 → Storage को repository class के पीछे रखो (बाद में memory की जगह DB लगाओ)
Step 3 → Repository को Depends(get_repo) से inject करो (tests में बदलना आसान)
Step 4 → POST /books      -> 201 Created + body
Step 5 → GET /books       -> ?offset=&limit= वाली list (Query ge/le से validate)
Step 6 → GET /books/{id}  -> 200 या HTTPException(404) raise करो
Step 7 → PUT पूरा बदलता है; PATCH सिर्फ भेजे गए fields बदलता है (exclude_unset=True)
Step 8 → DELETE /books/{id} -> 204 No Content (न मिले तो 404)
Step 9 → गलत input पर तुम्हारे code से पहले ही अपने-आप 422 मिलता है
```

---

## 🟡 Real World Example
A Zomato-like restaurant service: `POST /restaurants` onboards a restaurant, `GET /restaurants?limit=20&offset=40` powers the listing page, `PATCH /restaurants/7` toggles "open/closed", `DELETE` removes it. The same layout (routes -> service/repository -> DB) is what production teams use.

## 🟡 Real Example Hindi mein
Zomato जैसी restaurant service: `POST /restaurants` से restaurant जुड़ता है, `GET /restaurants?limit=20&offset=40` listing page चलाता है, `PATCH /restaurants/7` "खुला/बंद" बदलता है, `DELETE` हटाता है। Production टीमें यही ढाँचा (routes -> service/repository -> DB) इस्तेमाल करती हैं।

---

## 💻 Code Example — Basic
```python
# Basic CRUD with FastAPI + TestClient
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel

app = FastAPI()                                # the application
db: dict[int, str] = {}                        # id -> title (in-memory)

class BookIn(BaseModel):
    title: str                                 # required string

@app.post("/books", status_code=201)           # create -> 201
def create(b: BookIn) -> dict[str, int | str]:
    new_id: int = len(db) + 1                  # naive id generator
    db[new_id] = b.title                       # store it
    return {"id": new_id, "title": b.title}    # return it

@app.get("/books/{book_id}")                   # read one
def read(book_id: int) -> dict[str, int | str]:
    if book_id not in db:                      # missing?
        raise HTTPException(status_code=404, detail="Book not found")
    return {"id": book_id, "title": db[book_id]}

c = TestClient(app)                            # call the app in-process
print(c.post("/books", json={"title": "Dune"}).status_code)   # create
print(c.get("/books/1").json())                # read it back
print(c.get("/books/9").status_code)           # missing
print(c.post("/books", json={}).status_code)   # invalid body -> 422

# Output:
# 201
# {'id': 1, 'title': 'Dune'}
# 404
# 422
```

## 💻 Code Example — Advanced
```python
# Production style: Pydantic constraints, repository + Depends, pagination, PATCH
# (the complete file with all 5 routes and 11 test calls is main.py)
from typing import Annotated, Optional
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field


class BookIn(BaseModel):
    title: str = Field(min_length=1, max_length=100)   # validated by Pydantic
    price: float = Field(gt=0)                 # must be > 0


class BookPatch(BaseModel):
    title: Optional[str] = Field(None, min_length=1)   # every field optional
    price: Optional[float] = Field(None, gt=0)


class Book(BookIn):
    id: int                                    # response adds the id


class BookRepo:
    def __init__(self) -> None:
        self._data: dict[int, Book] = {}       # storage
        self._next = 1                         # next id

    def add(self, b: BookIn) -> Book:
        book = Book(id=self._next, **b.model_dump())   # build with id
        self._data[book.id] = book
        self._next += 1
        return book

    def get(self, id_: int) -> Optional[Book]:
        return self._data.get(id_)

    def list(self, offset: int, limit: int) -> list[Book]:
        return list(self._data.values())[offset:offset + limit]


_repo = BookRepo()                             # one per process

def get_repo() -> BookRepo:
    return _repo                               # overridable in tests

Repo = Annotated[BookRepo, Depends(get_repo)]  # reusable dependency type
app = FastAPI(title="Books API")


@app.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED)
def create(body: BookIn, repo: Repo) -> Book:
    return repo.add(body)


@app.get("/books", response_model=list[Book])
def list_books(repo: Repo, offset: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100)) -> list[Book]:
    return repo.list(offset, limit)            # bad limit -> 422 automatically


@app.patch("/books/{book_id}", response_model=Book)
def patch(book_id: int, body: BookPatch, repo: Repo) -> Book:
    book = repo.get(book_id)
    if book is None:
        raise HTTPException(404, "Book not found")
    updated = book.model_copy(update=body.model_dump(exclude_unset=True))   # only sent fields
    repo._data[book_id] = updated              # a real repo would expose save()
    return updated


c = TestClient(app)
print(c.post("/books", json={"title": "Dune", "price": 9.5}).json())
print(c.patch("/books/1", json={"price": 12}).json())
print(c.get("/books?limit=1000").status_code)
print(c.post("/books", json={"title": "", "price": -1}).status_code)

# Output:
# {'title': 'Dune', 'price': 9.5, 'id': 1}
# {'title': 'Dune', 'price': 12.0, 'id': 1}
# 422
# 422
```

---

## 🟠 JavaScript vs Python Comparison
Express: manual validation and status codes. FastAPI: types are the validation and the docs. Same routing idea, less boilerplate.

```python
# Python way
@app.post("/books", status_code=201)
def create(b: BookIn) -> Book: ...      # parsed, validated, documented automatically
```
```javascript
// JavaScript way (Express)
app.post("/books", (req, res) => {
  const { title, price } = req.body;
  if (!title || price <= 0) return res.status(422).json({ error: "invalid" });  // manual
  res.status(201).json({ id: 1, title, price });
});
```

---

## 🟠 FastAPI Connection
This topic IS the FastAPI connection. Key parts: `response_model` filters output (e.g. hides password hashes), `Depends` injects the repository/DB session, `status_code` sets the success code, and `HTTPException` produces error responses. To run for real: `uvicorn main:app --reload` and open `/docs`.

```python
# Swap the repository in tests without touching routes
app.dependency_overrides[get_repo] = lambda: BookRepo()   # fresh empty repo per test
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: returning 200 with `{"error": ...}` for failures.
✅ Correct: use proper status codes through `HTTPException` (404, 409, 422).

```python
# Wrong
return {"error": "not found"}
# Right
raise HTTPException(status_code=404, detail="Book not found")
```

❌ Mistake 2: using the same model for input and output (clients could set `id`, and secrets leak).
✅ Correct: separate `BookIn` / `Book` models, set `response_model`.

❌ Mistake 3: PATCH implemented with `model_dump()` (overwrites unsent fields with `None`).
✅ Correct: `model_dump(exclude_unset=True)`.

---

## 🧠 Tricky Interview Question
```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

@app.get("/items/me")
def me() -> dict: return {"who": "me"}

@app.get("/items/{item_id}")
def item(item_id: str) -> dict: return {"who": item_id}

print(TestClient(app).get("/items/me").json())
```
Answer: `{'who': 'me'}`. Routes match in definition order, so the fixed path `/items/me` must be declared BEFORE `/items/{item_id}`; reversed, `me` would be captured as an item_id.

---

## ⚫ Interview Questions + Answers

Q1: PUT vs PATCH?
A1: PUT replaces the whole resource (idempotent); PATCH changes only the sent fields.

Q2: Which status codes for CRUD?
A2: POST 201 (+ `Location`), GET 200, PUT/PATCH 200, DELETE 204, not found 404, validation 422, conflict 409, unauthenticated 401, forbidden 403.

Q3: What is idempotency?
A3: Repeating a request has the same effect as doing it once. GET, PUT, DELETE are idempotent; POST is not (use an idempotency key for payments).

Q4: Offset vs cursor pagination?
A4: Offset is simple but slow and unstable on large/changing data; cursor (keyset) pagination uses "after id X", stays fast and consistent.

Q5: `def` or `async def` for routes?
A5: Use `async def` with async libraries (httpx, asyncpg). A plain `def` runs in a threadpool, which is right for blocking code. Never call blocking code inside `async def`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Clients need a simple, cacheable, language-neutral interface to resources
- CRUD-style domains (orders, users, products)

❌ Avoid when:
- You need real-time two-way streams (use WebSockets/SSE)
- Clients need flexible, nested queries (consider GraphQL)
- Internal high-throughput service calls (consider gRPC)

---

## 📊 Visual Diagram
```
 Client
   |  POST /books {"title": "Dune", "price": 9.5}
   v
 FastAPI router --> Pydantic validates (422 if bad)
   |
   v
 route function --Depends--> BookRepo --> storage (memory / DB)
   |
   v
 response_model filter --> 201 Created + JSON

 Resource map:   /books        GET list   POST create
                 /books/{id}   GET one    PUT replace   PATCH edit   DELETE remove
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| REST | Resources + HTTP verbs | resources और HTTP क्रियाएँ |
| CRUD | Create, Read, Update, Delete | बनाना, पढ़ना, बदलना, हटाना |
| Pydantic | Data validation library | data सत्यापन library |
| Repository | Layer hiding storage details | storage छिपाने वाली परत |
| Idempotent | Same effect when repeated | दोहराने पर वही असर |
| Pagination | Returning data in pages | data को पन्नों में देना |

---

## ⚡ 3-Line Summary
English: REST maps CRUD to HTTP methods and URLs; FastAPI + Pydantic validate and document it for free.
English: Use separate in/out models, a repository via `Depends`, and correct status codes.
English: Paginate lists, use PATCH with `exclude_unset`, and test with `TestClient`.

Hindi: REST, CRUD को HTTP methods और URLs से जोड़ता है; FastAPI + Pydantic validation और docs मुफ्त देते हैं।
Hindi: अलग input/output models, `Depends` से repository और सही status codes इस्तेमाल करो।
Hindi: Lists को paginate करो, PATCH में `exclude_unset` लगाओ, और `TestClient` से test करो।

---

## ➡️ Next Topic
**482. Build Auth System (FastAPI+JWT)** — protect these routes with login, tokens and roles.

---
