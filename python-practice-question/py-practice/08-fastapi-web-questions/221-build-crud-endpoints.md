---

# Q221. Build CRUD endpoints
# Category: FASTAPI + WEB QUESTIONS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build Create / Read / Update / Delete endpoints for an `Item` using FastAPI with an in-memory dict. Use proper status codes (201, 204, 404) and response models. Test with `TestClient`.

```python
POST /items   GET /items   GET /items/{id}   PUT /items/{id}   DELETE /items/{id}
```

---

## 💡 Quick Concept (2 lines only)
One path per resource, HTTP verbs for the action, Pydantic models for input/output, `HTTPException` for errors.
हिंदी: Resource के लिए एक URL, verbs से action, Pydantic से validation, और error के लिए HTTPException।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

from fastapi import FastAPI, HTTPException        # app + error helper
from fastapi.testclient import TestClient         # in-process client (no server)
from pydantic import BaseModel                    # request/response schemas

app = FastAPI()                                   # create app
db: dict[int, dict] = {}                          # in-memory "table"
next_id = 1                                       # auto-increment id


class ItemIn(BaseModel):                          # input schema (no id)
    name: str                                     # required
    price: float                                  # required


class Item(ItemIn):                               # output schema = input + id
    id: int                                       # server-generated


@app.post("/items", response_model=Item, status_code=201)  # Create
def create(item: ItemIn) -> dict:
    global next_id                                # modify counter
    row = {"id": next_id, **item.model_dump()}    # build row
    db[next_id] = row                             # store it
    next_id += 1                                  # bump id
    return row                                    # FastAPI validates against Item


@app.get("/items", response_model=list[Item])     # Read all
def list_items() -> list[dict]:
    return list(db.values())                      # all rows


@app.get("/items/{item_id}", response_model=Item) # Read one
def get_item(item_id: int) -> dict:
    if item_id not in db:                         # missing?
        raise HTTPException(404, "Item not found")  # 404 response
    return db[item_id]                            # found


@app.put("/items/{item_id}", response_model=Item) # Update (replace)
def update(item_id: int, item: ItemIn) -> dict:
    if item_id not in db:                         # missing?
        raise HTTPException(404, "Item not found")  # 404 response
    db[item_id] = {"id": item_id, **item.model_dump()}  # overwrite
    return db[item_id]                            # updated row


@app.delete("/items/{item_id}", status_code=204)  # Delete
def delete(item_id: int) -> None:
    if db.pop(item_id, None) is None:             # nothing to delete?
        raise HTTPException(404, "Item not found")  # 404 response


# ---------- TEST CASES ----------
c = TestClient(app)                               # test client
r = c.post("/items", json={"name": "pen", "price": 2.5})
print(r.status_code, r.json())                    # create
print(c.get("/items/1").json())                   # read one
print(c.put("/items/1", json={"name": "pen", "price": 3}).json())  # update
print(c.get("/items").json())                     # list
print(c.delete("/items/1").status_code)           # delete
print(c.get("/items/1").status_code, c.get("/items/1").json())  # gone

# ============================================
# OUTPUT (real run, Python 3.13):
# ============================================

# 201 {'name': 'pen', 'price': 2.5, 'id': 1}
# {'name': 'pen', 'price': 2.5, 'id': 1}
# {'name': 'pen', 'price': 3.0, 'id': 1}
# [{'name': 'pen', 'price': 3.0, 'id': 1}]
# 204
# 404 {'detail': 'Item not found'}
```

---

## 🔍 Why This Works (3 lines max)
`ItemIn` has no `id`, `Item` adds it, so clients cannot choose ids and responses are filtered by `response_model`. Missing rows raise `HTTPException(404)`. Note: recent Starlette versions print a deprecation warning about `httpx` in `TestClient` (harmless).
हिंदी: ItemIn (id नहीं) और Item (id के साथ) अलग रखो; missing पर 404, create पर 201, delete पर 204।

---

## ⚡ Alternative Solution
```python
from fastapi import FastAPI                       # app
from fastapi.testclient import TestClient         # test client
from pydantic import BaseModel                    # schema

app = FastAPI()                                   # create app
item = {"name": "pen", "price": 2.5, "stock": 10} # one stored row


class ItemPatch(BaseModel):                       # every field optional
    name: str | None = None                       # may be omitted
    price: float | None = None                    # may be omitted
    stock: int | None = None                      # may be omitted


@app.patch("/item")                               # PATCH = partial update
def patch(body: ItemPatch) -> dict:
    changes = body.model_dump(exclude_unset=True) # ONLY fields the client sent
    item.update(changes)                          # merge into stored row
    return item                                   # updated row


c = TestClient(app)                               # test client
print(c.patch("/item", json={"price": 9.0}).json())     # only price changes
print(c.patch("/item", json={"stock": None}).json())    # explicit null IS kept (unset vs None)

# ============================================
# OUTPUT (real run, Python 3.13):
# ============================================

# {'name': 'pen', 'price': 9.0, 'stock': 10}
# {'name': 'pen', 'price': 9.0, 'stock': None}
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: returning 200 with an error body, and one model for input + output
@app.get("/items/{item_id}")
def get_item(item_id: int):
    return db.get(item_id, {"error": "not found"})   # status is still 200!

# ✅ Correct: raise HTTPException(404, "Item not found")
```

---

## 🎯 Interview Tip (1 line)
Say: "Separate input/output schemas, correct status codes, and 404 via HTTPException; swap the dict for a DB session via Depends."

---

## 🔗 Related Questions
→ Q222 (dependency injection) | Q223 (Pydantic validation) | Q233 (response models) | Q236 (TestClient)
