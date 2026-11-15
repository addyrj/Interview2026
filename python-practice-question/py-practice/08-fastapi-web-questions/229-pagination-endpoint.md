---

# Q229. Pagination endpoint
# Category: FASTAPI + WEB QUESTIONS
# Difficulty: ⭐

---

## ❓ Question
Build `GET /items?page=&size=` returning `items, total, page, size, pages`. Validate `page >= 1` and `size` between 1 and 10. Then show cursor (keyset) pagination as an alternative.

---

## 💡 Quick Concept (2 lines only)
Offset pagination = `LIMIT size OFFSET (page-1)*size`; simple but slow and unstable on big/changing tables. Cursor pagination (`WHERE id > last`) is fast and stable.
हिंदी: Offset pagination आसान है, पर बड़ी table पर cursor (`id > last`) तेज़ और सुरक्षित है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from typing import Annotated  # for Query metadata
from fastapi import FastAPI, Query  # app + query validation
from fastapi.testclient import TestClient  # client
from pydantic import BaseModel  # response model

app = FastAPI()  # app
DB = [{"id": i, "name": f"item{i}"} for i in range(1, 26)]  # 25 fake rows

class Page(BaseModel):  # response envelope
    items: list[dict]  # rows of this page
    total: int  # total rows overall
    page: int  # current page
    size: int  # page size
    pages: int  # total pages

@app.get("/items", response_model=Page)  # endpoint
async def list_items(
    page: Annotated[int, Query(ge=1)] = 1,  # page >= 1
    size: Annotated[int, Query(ge=1, le=10)] = 5,  # 1..10 per page (cap protects DB)
) -> Page:  # typed return
    total = len(DB)  # count rows
    start = (page - 1) * size  # offset formula
    rows = DB[start:start + size]  # slice = LIMIT/OFFSET
    return Page(items=rows, total=total, page=page, size=size, pages=-(-total // size))  # ceil division

# ============================================
# TEST CASES
# ============================================
client = TestClient(app)  # client
r = client.get("/items", params={"page": 2, "size": 10}).json()  # page 2
print([x["id"] for x in r["items"]], r["total"], r["pages"])  # Expected: [11, 12, 13, 14, 15, 16, 17, 18, 19, 20] 25 3
print(client.get("/items", params={"page": 3, "size": 10}).json()["items"][-1])  # Expected: {'id': 25, 'name': 'item25'}
print(client.get("/items", params={"page": 9}).json()["items"])  # Expected: [] (past the end)
print(client.get("/items", params={"size": 100}).status_code)  # Expected: 422 (size > 10)
```

---

## 🔍 Why This Works (3 lines max)
`Query(ge=1, le=10)` makes FastAPI reject bad values with 422 and caps the page size to protect the DB. Pages are `ceil(total / size)` — written as `-(-total // size)`. Past-the-end pages return an empty list.
हिंदी: `Query(ge=1, le=10)` गलत value पर 422 देता है; max size लगाना ज़रूरी है।

---

## ⚡ Alternative Solution
```python
# (same file as above — reuses its imports/names)
# ---- Alternative: cursor (keyset) pagination ----
app2 = FastAPI()  # app

@app2.get("/feed")  # endpoint
async def feed(after: int = 0, limit: Annotated[int, Query(ge=1, le=10)] = 5) -> dict:  # cursor = last seen id
    rows = [r for r in DB if r["id"] > after][:limit]  # WHERE id > after LIMIT n
    nxt = rows[-1]["id"] if len(rows) == limit else None  # next cursor or None at end
    return {"items": [r["id"] for r in rows], "next": nxt}  # response

c2 = TestClient(app2)  # client
print(c2.get("/feed", params={"limit": 5}).json())  # Expected: {'items': [1, 2, 3, 4, 5], 'next': 5}
print(c2.get("/feed", params={"after": 22, "limit": 5}).json())  # Expected: {'items': [23, 24, 25], 'next': None}
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: no upper limit on size -> client asks size=1_000_000 and kills the DB
async def list_items(page: int = 1, size: int = 100000): ...

# ❌ Wrong: offset = page * size (page starts at 1 -> skips the first page)
start = page * size
# ✅ Correct: start = (page - 1) * size   and   size: Query(ge=1, le=10)
```

---

## 🎯 Interview Tip (1 line)
Say: "Offset is simple but O(offset) and drifts when rows change; for feeds I use keyset/cursor pagination on an indexed column."

---

## 🔗 Related Questions
→ Q182 (pagination helper) | Q221 (CRUD) | Q223 (validation) | Q233 (response models)
