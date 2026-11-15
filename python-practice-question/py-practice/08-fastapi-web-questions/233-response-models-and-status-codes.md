---

# Q233. Response models and status codes
# Category: FASTAPI + WEB QUESTIONS
# Difficulty: ⭐

---

## ❓ Question
Build a user API where the input model has a `password` but the response never does (`response_model`). Return `201` on create, `204` with no body on delete, and `404` for a missing user.

---

## 💡 Quick Concept (2 lines only)
`response_model` filters and validates what leaves the API (hides secrets, documents the schema). `status_code=` sets the success code; use `HTTPException` or a `Response` for errors.
हिंदी: `response_model` से password जैसे fields बाहर नहीं जाते; सही status code (201/204/404) देना ज़रूरी है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from fastapi import FastAPI, Response, status  # status constants
from fastapi.testclient import TestClient  # client
from pydantic import BaseModel  # models

class UserIn(BaseModel):  # what the client SENDS
    name: str  # public field
    password: str  # secret field

class UserOut(BaseModel):  # what the client RECEIVES
    id: int  # generated id
    name: str  # public field (no password!)

app = FastAPI()  # app
USERS: dict[int, dict] = {}  # fake db

@app.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)  # Step 1: filter output + 201
async def create(u: UserIn) -> dict:  # returns full dict incl. password
    uid = len(USERS) + 1  # new id
    USERS[uid] = {"id": uid, **u.model_dump()}  # store everything
    return USERS[uid]  # response_model strips password

@app.get("/users/{uid}", response_model=UserOut, responses={404: {"description": "Not found"}})  # document 404
async def read(uid: int, response: Response) -> dict | Response:  # may return early
    if uid not in USERS:  # missing
        return Response(status_code=404)  # bypasses response_model validation
    return USERS[uid]  # filtered again

@app.delete("/users/{uid}", status_code=status.HTTP_204_NO_CONTENT)  # 204 = no body
async def delete(uid: int) -> None:  # return nothing
    USERS.pop(uid, None)  # idempotent delete

# ============================================
# TEST CASES
# ============================================
client = TestClient(app)  # client
r = client.post("/users", json={"name": "ann", "password": "s3cret"})  # create
print(r.status_code, r.json())  # Expected: 201 {'id': 1, 'name': 'ann'}
print(client.get("/users/1").json())  # Expected: {'id': 1, 'name': 'ann'}
print(client.get("/users/7").status_code)  # Expected: 404
d = client.delete("/users/1")  # delete
print(d.status_code, repr(d.content))  # Expected: 204 b''
print(client.post("/users", json={"name": "x"}).status_code)  # Expected: 422 (password missing)
```

---

## 🔍 Why This Works (3 lines max)
The route returns a dict containing `password`, but `response_model=UserOut` serialises only `id` and `name`. 204 must have an empty body, so the route returns `None`. Using separate In/Out models is the standard way to avoid leaking fields.
हिंदी: Input और Output के अलग models रखो — return में dict पूरा हो तब भी बाहर सिर्फ `UserOut` के fields जाते हैं।

---

## ⚡ Alternative Solution
```python
# (same file as above — reuses its imports/names)
# ---- Alternative: response_model_exclude_unset / by return annotation ----
app2 = FastAPI()  # app

class Item(BaseModel):  # model with defaults
    name: str  # required
    note: str | None = None  # optional

@app2.get("/i", response_model_exclude_unset=True)  # drop fields never set
async def i() -> Item:  # return annotation acts as response model too
    return Item(name="pen")  # note is unset

print(TestClient(app2).get("/i").json())  # Expected: {'name': 'pen'}
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: returning the same model used for input -> password is sent back to the client
@app.post("/users")
async def create(u: UserIn) -> UserIn: ...

# ❌ Wrong: status 200 for create and a JSON body for delete (should be 201 / 204)

# ✅ Correct: separate UserIn / UserOut, response_model=UserOut, status_code=201 / 204
```

---

## 🎯 Interview Tip (1 line)
Say: "Separate input and output models, set explicit status codes (201 create, 204 delete, 404 missing), and response_model as the safety net against leaks."

---

## 🔗 Related Questions
→ Q221 (CRUD) | Q223 (Pydantic) | Q232 (error handlers) | Q229 (pagination)
