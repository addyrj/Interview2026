---

# Q232. Global error handlers
# Category: FASTAPI + WEB QUESTIONS
# Difficulty: ⭐⭐

---

## ❓ Question
Make every error in a FastAPI app return the same JSON shape `{"error": {"code", "message"}}`: a custom `AppError`, `HTTPException` (including 404/405), validation errors (422) and unexpected crashes (500, without leaking details).

---

## 💡 Quick Concept (2 lines only)
Use `@app.exception_handler(ExcType)` to turn exceptions into responses. Register Starlette's `HTTPException` (not just FastAPI's) so 404/405 are covered too.
हिंदी: `exception_handler` से हर error का एक जैसा JSON format बनाओ; 500 में internal details कभी मत दिखाओ।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from fastapi import FastAPI, Request, HTTPException  # web types
from fastapi.exceptions import RequestValidationError  # pydantic/validation errors
from fastapi.responses import JSONResponse  # custom response
from fastapi.testclient import TestClient  # client
from starlette.exceptions import HTTPException as StarletteHTTPException  # also covers 404/405

class AppError(Exception):  # our own domain exception
    def __init__(self, code: str, message: str, status: int = 400) -> None:  # fields
        self.code, self.message, self.status = code, message, status  # store

app = FastAPI()  # app

@app.exception_handler(AppError)  # Step 1: handle our custom error
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:  # handler
    return JSONResponse({"error": {"code": exc.code, "message": exc.message}}, status_code=exc.status)  # uniform shape

@app.exception_handler(StarletteHTTPException)  # Step 2: HTTPException + 404 + 405
async def http_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:  # handler
    return JSONResponse({"error": {"code": "http_error", "message": str(exc.detail)}}, status_code=exc.status_code)  # same shape

@app.exception_handler(RequestValidationError)  # Step 3: 422 validation errors
async def validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:  # handler
    fields = [".".join(str(p) for p in e["loc"]) for e in exc.errors()]  # which fields failed
    return JSONResponse({"error": {"code": "validation", "message": f"invalid: {fields}"}}, status_code=422)  # clean message

@app.exception_handler(Exception)  # Step 4: catch-all (becomes 500)
async def crash_handler(request: Request, exc: Exception) -> JSONResponse:  # handler
    return JSONResponse({"error": {"code": "internal", "message": "something went wrong"}}, status_code=500)  # hide internals

@app.get("/users/{uid}")  # route
async def get_user(uid: int) -> dict[str, int]:  # uid must be int
    if uid == 0:  # custom failure
        raise AppError("not_found", "user 0 missing", 404)  # our error
    if uid == 99:  # http failure
        raise HTTPException(403, "forbidden")  # builtin error
    if uid == 500:  # bug
        raise RuntimeError("boom secret")  # unexpected
    return {"id": uid}  # success

# ============================================
# TEST CASES
# ============================================
client = TestClient(app, raise_server_exceptions=False)  # False: let 500 handler respond
print(client.get("/users/0").status_code, client.get("/users/0").json())  # Expected: 404 {'error': {'code': 'not_found', 'message': 'user 0 missing'}}
print(client.get("/users/99").json())  # Expected: {'error': {'code': 'http_error', 'message': 'forbidden'}}
print(client.get("/users/abc").json())  # Expected: {'error': {'code': 'validation', 'message': "invalid: ['path.uid']"}}
print(client.get("/nope").json())  # Expected: {'error': {'code': 'http_error', 'message': 'Not Found'}}
print(client.get("/users/500").json())  # Expected: {'error': {'code': 'internal', 'message': 'something went wrong'}}
```

---

## 🔍 Why This Works (3 lines max)
FastAPI looks up the handler by exception class (most specific first), so `AppError`, `RequestValidationError` and the catch-all `Exception` each get their own. `raise_server_exceptions=False` makes TestClient return the 500 response instead of re-raising.
हिंदी: Handler exception class से चुना जाता है; test में `raise_server_exceptions=False` रखो ताकि 500 response दिखे।

---

## ⚡ Alternative Solution
```python
# (same file as above — reuses its imports/names)
# ---- Alternative: register handlers via dict in constructor ----
app2 = FastAPI(exception_handlers={AppError: app_error_handler})  # handlers passed at creation

@app2.get("/")  # route
async def r() -> None:  # handler
    raise AppError("x", "y", 418)  # raise

print(TestClient(app2).get("/").status_code)  # Expected: 418
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: registering FastAPI's HTTPException only -> router 404/405 (Starlette's) keep the old format
from fastapi import HTTPException
@app.exception_handler(HTTPException)

# ✅ Correct: handle starlette.exceptions.HTTPException (parent class of both)
from starlette.exceptions import HTTPException as StarletteHTTPException

# ❌ Wrong: returning str(exc) from the 500 handler -> leaks stack info / SQL / secrets
# ✅ Correct: log exc server-side, return a generic message
```

---

## 🎯 Interview Tip (1 line)
Say: "One error envelope for the whole API: domain exceptions, HTTP errors, validation and a catch-all that logs but never leaks internals."

---

## 🔗 Related Questions
→ Q223 (validation) | Q233 (status codes) | Q225 (middleware) | Q130 (too-broad except)
