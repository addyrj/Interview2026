---

# Q239. API Versioning with Routers
# Category: FastAPI + Web Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Expose `/api/v1/users/{id}` and `/api/v2/users/{id}` from one FastAPI app using `APIRouter`.
v1 returns `{"id", "name"}`; v2 returns a richer shape `{"id", "full_name", "email"}`. Test with `TestClient` (no live server).

---

## 💡 Quick Concept (2 lines only)
Make one `APIRouter` per version and mount each with `app.include_router(router, prefix="/api/v1")`. Old clients keep working while new clients use v2.
हिंदी: हर version का अलग router बनाओ और prefix के साथ include करो — पुराने clients नहीं टूटते।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from fastapi import APIRouter, FastAPI            # Step 1: import router + app classes
from fastapi.testclient import TestClient         # TestClient calls the app in-process

app = FastAPI()                                   # Step 2: create the main app

v1 = APIRouter(prefix="/v1", tags=["v1"])         # Step 3: router for version 1
v2 = APIRouter(prefix="/v2", tags=["v2"])         # router for version 2

@v1.get("/users/{user_id}")                       # GET /api/v1/users/{id}
def get_user_v1(user_id: int) -> dict:            # path param is validated as int
    return {"id": user_id, "name": "Aditya"}      # old, small response shape

@v2.get("/users/{user_id}")                       # GET /api/v2/users/{id}
def get_user_v2(user_id: int) -> dict:            # same path, new version
    return {                                      # new, richer response shape
        "id": user_id,                            # keep id
        "full_name": "Aditya Ranjan",             # name field was renamed
        "email": "a@example.com",                 # new field in v2
    }

app.include_router(v1, prefix="/api")             # Step 4: mount -> /api/v1/...
app.include_router(v2, prefix="/api")             # mount -> /api/v2/...

# ============================================
# TEST CASES
# ============================================
client = TestClient(app)                          # in-process client

r1 = client.get("/api/v1/users/7")                # call v1
print(r1.status_code, r1.json())                  # Expected: 200 {'id': 7, 'name': 'Aditya'}

r2 = client.get("/api/v2/users/7")                # call v2
print(r2.status_code, r2.json())                  # Expected: 200 {'id': 7, 'full_name': 'Aditya Ranjan', 'email': 'a@example.com'}

print(client.get("/api/v3/users/7").status_code)  # Expected: 404 (no such version)
print(client.get("/api/v1/users/abc").status_code)  # Expected: 422 (id must be int)
```

---

## 🔍 Why This Works (3 lines max)
Final path = include_router prefix + router prefix + route path. Each router is an independent module, so v1 code never changes when v2 is added. Unknown versions fall through to 404.
हिंदी: Final URL = include prefix + router prefix + route path — v1 को छुए बिना v2 जुड़ जाता है।

---

## ⚡ Alternative Solution
```python
# Share logic between versions and mount the whole thing as separate sub-apps
from fastapi import FastAPI                       # import app class
from fastapi.testclient import TestClient         # in-process client

def build_v1() -> FastAPI:                        # factory for a v1 sub-app
    sub = FastAPI(title="API v1")                 # own docs page at /api/v1/docs
    @sub.get("/ping")                             # route inside the sub-app
    def ping() -> dict:                           # handler
        return {"version": 1}                     # tell which version answered
    return sub                                    # hand back the sub-app

def build_v2() -> FastAPI:                        # factory for a v2 sub-app
    sub = FastAPI(title="API v2")                 # own docs page at /api/v2/docs
    @sub.get("/ping")                             # same route name
    def ping() -> dict:                           # handler
        return {"version": 2}                     # v2 answer
    return sub                                    # hand back the sub-app

root = FastAPI()                                  # root app
root.mount("/api/v1", build_v1())                 # mount v1 sub-app under prefix
root.mount("/api/v2", build_v2())                 # mount v2 sub-app under prefix

c = TestClient(root)                              # client for the root app
print(c.get("/api/v1/ping").json())               # Expected: {'version': 1}
print(c.get("/api/v2/ping").json())               # Expected: {'version': 2}
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: copy-pasting the same prefix into every route, and one router for all versions
# @app.get("/api/v1/users/{id}")   # repeated string everywhere, easy to typo
# @app.get("/api/v2/users/{id}")   # versions are mixed in one file

# ✅ Correct: one APIRouter per version with prefix=..., then include_router(prefix="/api")
v1 = APIRouter(prefix="/v1")                      # prefix lives in one place only
```

---

## 🎯 Interview Tip (1 line)
Say: "URL-path versioning (`/v1`) is simplest; I keep one router per version, share business logic in a service layer, and deprecate old versions with `deprecated=True`."

---

## 🔗 Related Questions
→ Q233 (response models) | Q236 (TestClient) | Q240 (lifespan events) | Q231 (CORS setup)
