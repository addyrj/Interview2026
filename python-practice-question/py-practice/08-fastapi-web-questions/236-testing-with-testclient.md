---

# Q236. Testing with TestClient
# Category: FASTAPI + WEB QUESTIONS
# Difficulty: ⭐⭐

---

## ❓ Question
Write pytest tests for a small FastAPI items API using `TestClient`. Replace the real database dependency with an in-memory fake using `dependency_overrides`, and test the happy path plus 404, 409 and 422.

---

## 💡 Quick Concept (2 lines only)
`TestClient(app)` calls your app in-process (no server, no network). Use `app.dependency_overrides` to swap DBs/auth for fakes, and clear them after each test.
हिंदी: `TestClient` बिना server चलाए app को call करता है; `dependency_overrides` से DB की जगह fake लगाओ।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import pytest  # test runner (can run via python too)
from fastapi import FastAPI, Depends, HTTPException  # app bits
from fastapi.testclient import TestClient  # in-process client
from pydantic import BaseModel  # model

app = FastAPI()  # app under test

class Item(BaseModel):  # body model
    name: str  # name
    price: float  # price

def get_db() -> dict[int, Item]:  # real dependency (pretend: real database)
    raise RuntimeError("real DB not available in tests")  # would fail if not overridden

@app.post("/items/{item_id}", status_code=201)  # create
def create(item_id: int, item: Item, db: dict = Depends(get_db)) -> Item:  # uses dep
    if item_id in db:  # duplicate
        raise HTTPException(409, "exists")  # conflict
    db[item_id] = item  # save
    return item  # echo

@app.get("/items/{item_id}")  # read
def read(item_id: int, db: dict = Depends(get_db)) -> Item:  # uses dep
    if item_id not in db:  # missing
        raise HTTPException(404, "not found")  # 404
    return db[item_id]  # item

# ============================================
# TEST CASES
# ============================================
# ---- the tests ----
@pytest.fixture  # Step 1: fixture builds a fresh client + fake db per test
def client():  # fixture
    fake: dict[int, Item] = {}  # in-memory db
    app.dependency_overrides[get_db] = lambda: fake  # Step 2: swap dependency
    with TestClient(app) as c:  # Step 3: context manager also runs lifespan events
        yield c  # give client to test
    app.dependency_overrides.clear()  # Step 4: always clean up overrides

def test_create_and_read(client):  # happy path
    r = client.post("/items/1", json={"name": "pen", "price": 1.5})  # create
    assert r.status_code == 201  # created
    assert client.get("/items/1").json() == {"name": "pen", "price": 1.5}  # read back

def test_errors(client):  # failure paths
    assert client.get("/items/9").status_code == 404  # missing
    client.post("/items/1", json={"name": "a", "price": 1})  # first create
    assert client.post("/items/1", json={"name": "a", "price": 1}).status_code == 409  # duplicate
    assert client.post("/items/2", json={"name": "a"}).status_code == 422  # invalid body

if __name__ == "__main__":  # run tests when executed directly
    code = pytest.main([__file__, "-q", "-p", "no:cacheprovider"])  # Expected: 2 passed
    print("pytest exit code:", code)  # Expected: 0
```

---

## 🔍 Why This Works (3 lines max)
The fixture builds a fresh fake dict per test so tests don't share state. `dependency_overrides[get_db]` replaces the real dependency everywhere it is used. `with TestClient(app)` also runs lifespan startup/shutdown.
हिंदी: हर test के लिए नया fake DB बनाओ और अंत में overrides साफ़ करो।

---

## ⚡ Alternative Solution
```python
# (same file as above — reuses its imports/names)
# ---- Alternative: async client (httpx + ASGITransport) for async tests ----
import asyncio  # run the async test
import httpx  # async-capable client

async def async_check() -> None:  # async test body
    fake: dict[int, Item] = {}  # fresh fake db
    app.dependency_overrides[get_db] = lambda: fake  # override again
    transport = httpx.ASGITransport(app=app)  # call the ASGI app directly, no network
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:  # async client
        r = await ac.post("/items/5", json={"name": "cup", "price": 3})  # await requests
        print(r.status_code)  # Expected: 201
        print((await ac.get("/items/5")).json())  # Expected: {'name': 'cup', 'price': 3.0}
    app.dependency_overrides.clear()  # cleanup

if __name__ == "__main__":  # only when run directly
    asyncio.run(async_check())  # run it
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: forgetting to clear overrides -> the fake leaks into other test files
app.dependency_overrides[get_db] = lambda: fake
# (no cleanup)

# ❌ Wrong: a module-level shared dict as DB -> tests depend on run order
# ✅ Correct: fixture creates a fresh fake, yields client, then app.dependency_overrides.clear()
```

---

## 🎯 Interview Tip (1 line)
Say: "I test through the HTTP layer with TestClient, override dependencies for DB/auth, and assert status codes plus bodies for success and error paths."

---

## 🔗 Related Questions
→ Q222 (dependencies) | Q221 (CRUD) | Q232 (error handlers) | Q240 (lifespan)
