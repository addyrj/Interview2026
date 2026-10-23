---

# 296. FastAPI — Complete Guide
# हिंदी में: FastAPI — पूरी Guide

---

## 🔵 Simple Definition (English)
FastAPI is a modern, async Python web framework for building APIs. Built on Starlette (ASGI) + Pydantic (validation). Key features: automatic OpenAPI/Swagger docs, type-hint-based validation, async/await support, dependency injection, OAuth2/JWT built-in. Fastest Python framework (on par with Node.js/Go for async I/O).

## 🔵 सरल परिभाषा (Hindi)
FastAPI modern async Python web framework है APIs बनाने के लिए। Starlette + Pydantic पर built। Key features: automatic Swagger docs, type-hint validation, async/await, dependency injection, OAuth2/JWT। Python का fastest framework (async I/O में Node.js जितना fast)।

---

## 💻 Code Example — Basic
```python
from fastapi import FastAPI, HTTPException, Query, Path
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="Tariff API",
    description="HS Code classification service",
    version="1.0.0",
)

# ─── Request/Response models ──────────────────────────────────────
class ProductRequest(BaseModel):
    name: str
    description: Optional[str] = None
    weight_kg: float

class TariffResponse(BaseModel):
    hs_code: str
    description: str
    duty_rate: float
    product_name: str

# ─── Path parameters ─────────────────────────────────────────────
@app.get("/tariffs/{hs_code}", response_model=TariffResponse)
async def get_tariff(
    hs_code: str = Path(..., pattern=r"^\d{10}$", description="10-digit HS code")
):
    """Get tariff details by HS code."""
    tariff = await db.get_tariff(hs_code)
    if not tariff:
        raise HTTPException(status_code=404, detail=f"HS code {hs_code} not found")
    return tariff

# ─── Query parameters ────────────────────────────────────────────
@app.get("/tariffs", response_model=list[TariffResponse])
async def search_tariffs(
    q: str = Query(..., min_length=3, description="Search query"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Search tariff codes."""
    results = await db.search(q, limit=limit, offset=offset)
    return results

# ─── POST with request body ──────────────────────────────────────
@app.post("/classify", response_model=TariffResponse, status_code=201)
async def classify_product(product: ProductRequest):
    """Classify a product with an HS code."""
    hs_code = await ai_classify(product.name, product.description)
    return TariffResponse(
        hs_code=hs_code,
        description="Classified by AI",
        duty_rate=0.0,
        product_name=product.name,
    )

# ─── Status codes ────────────────────────────────────────────────
# 200 OK — default for GET
# 201 Created — use status_code=201 for POST that creates
# 204 No Content — DELETE (no response body)
# 400 Bad Request — validation error (auto from Pydantic)
# 401 Unauthorized — missing auth
# 403 Forbidden — auth present but not authorized
# 404 Not Found — resource doesn't exist
# 422 Unprocessable Entity — FastAPI default for validation errors
# 500 Internal Server Error — unhandled exception
```

## 💻 Code Example — Advanced
```python
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import asyncio, json, time

# ─── Lifespan — startup and shutdown ─────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup:
    await database.connect()
    await redis.ping()
    print("App started — DB and Redis connected")
    yield
    # Shutdown:
    await database.disconnect()
    await redis.close()
    print("App stopped")

app = FastAPI(lifespan=lifespan)

# ─── CORS middleware ──────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.example.com"],   # specific origins for production
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    allow_credentials=True,
)

# ─── Custom middleware (logging) ──────────────────────────────────
@app.middleware("http")
async def log_requests(request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = (time.time() - start) * 1000
    print(f"{request.method} {request.url.path} → {response.status_code} ({duration:.0f}ms)")
    return response

# ─── Background tasks ─────────────────────────────────────────────
async def send_notification(user_id: int, message: str):
    await email_service.send(user_id, message)

@app.post("/orders", status_code=201)
async def create_order(order: OrderRequest, background: BackgroundTasks):
    result = await order_service.create(order)
    # Fire and forget — doesn't block response:
    background.add_task(send_notification, order.user_id, "Order created!")
    return result

# ─── Streaming response (Server-Sent Events) ─────────────────────
@app.post("/chat/stream")
async def stream_chat(query: str):
    async def generate():
        async for token in ai_service.stream(query):
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

# ─── Router (organize large apps) ────────────────────────────────
from fastapi import APIRouter

tariffs_router = APIRouter(prefix="/tariffs", tags=["Tariffs"])

@tariffs_router.get("/{code}")
async def get_tariff(code: str, repo: TariffRepo = Depends(get_repo)):
    return await repo.get(code)

@tariffs_router.post("/")
async def create_tariff(data: TariffCreate, repo: TariffRepo = Depends(get_repo)):
    return await repo.create(data)

app.include_router(tariffs_router)
# Also include: app.include_router(users_router, prefix="/v1")

# ─── Exception handlers ───────────────────────────────────────────
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request, exc: ValueError):
    return JSONResponse(status_code=400, content={"error": str(exc)})

@app.exception_handler(Exception)
async def general_error_handler(request, exc: Exception):
    logger.error("Unhandled exception", exc_info=True)
    return JSONResponse(status_code=500, content={"error": "Internal server error"})

# ─── Health check ────────────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health():
    try:
        await db.execute("SELECT 1")
        await redis.ping()
        return {"status": "healthy", "db": "ok", "redis": "ok"}
    except Exception as e:
        raise HTTPException(503, detail={"status": "unhealthy", "error": str(e)})
```

---

## 🟠 JavaScript vs Python Comparison

```python
# FastAPI (Python):
@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Pydantic auto-validates 'user'
    # 422 if validation fails (automatic!)
    new_user = await user_service.create(db, user)
    return new_user  # auto-serialized to UserResponse
```

```javascript
// Express.js (Node.js):
router.post('/users', async (req, res) => {
    try {
        const { error } = userSchema.validate(req.body);  // manual validation
        if (error) return res.status(400).json({ error });
        const user = await userService.create(req.body);
        res.status(201).json(user);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});
```

Key differences:
- FastAPI: validation automatic from type hints (Pydantic). Express: manual (Joi, Zod).
- FastAPI: auto-generates Swagger UI at `/docs`. Express: needs `swagger-jsdoc`.
- FastAPI: async with `await`. Express: also async but no type system.
- FastAPI: `response_model` filters response (removes sensitive fields). Express: manual.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using sync blocking functions in async endpoints
```python
# Wrong — blocks event loop, kills concurrency:
@app.get("/data")
async def get_data():
    time.sleep(2)    # BLOCKS! All other requests wait!
    return {"data": "result"}

# Correct — use await or run_in_threadpool:
from fastapi.concurrency import run_in_threadpool

@app.get("/data")
async def get_data():
    result = await run_in_threadpool(blocking_sync_function)
    return {"data": result}
```

❌ Mistake 2: Returning dict instead of model (no response filtering)
```python
# Wrong — returns ALL fields including password hash!
@app.get("/users/{id}")
async def get_user(id: int, db=Depends(get_db)):
    user = await db.get_user(id)
    return user    # returns everything including sensitive data!

# Correct — response_model filters to only safe fields:
@app.get("/users/{id}", response_model=UserPublicResponse)
async def get_user(id: int, db=Depends(get_db)):
    return await db.get_user(id)   # only UserPublicResponse fields returned
```

---

## 🧠 Tricky Interview Question

**Q**: What is the difference between `@app.get()` and `@app.post()` beyond HTTP method — what happens to routing, validation, and docs?

**Answer**: HTTP method matters for: (1) **Routing** — requests must match the method (`GET /users` ≠ `POST /users`). (2) **Body** — GET requests should have no body (params via query string). POST/PUT/PATCH have request body (validated by Pydantic). (3) **Caching** — GET is cacheable; POST is not. (4) **Idempotency** — GET/PUT/DELETE should be idempotent (same result on repeat). POST is not. (5) **OpenAPI docs** — FastAPI groups by method in `/docs`. REST convention: GET=read, POST=create, PUT=full-update, PATCH=partial, DELETE=remove.

---

## ⚫ Interview Questions + Answers

Q1: How does FastAPI handle request validation automatically?
A1: FastAPI uses Pydantic models as request body type hints. When a request arrives: (1) Parse JSON body → Python dict. (2) Pydantic validates against the model schema (required fields, types, constraints). (3) If invalid: return 422 Unprocessable Entity with detailed error. (4) If valid: create Pydantic object and inject into endpoint function. Path params, query params also validated via type hints + `Path()`/`Query()` constraints. This eliminates manual validation code — declare the schema once, get validation + docs + serialization free.

Q2: What are `Depends()` and dependency injection in FastAPI?
A2: `Depends(func)` tells FastAPI to call `func` and inject its return value into the endpoint. `async def get_db(): async with Session() as session: yield session` — `yield` makes it a context manager (auto-closes after request). `def endpoint(db: Session = Depends(get_db))` — FastAPI calls `get_db()` before the endpoint, injects result, calls cleanup after. Benefits: (1) Shared logic (auth check, DB session). (2) Testable — override with `app.dependency_overrides[get_db] = fake_get_db`. (3) Composable — dependencies can have their own dependencies.

Q3: How do you implement JWT authentication in FastAPI?
A3: `from fastapi.security import OAuth2PasswordBearer; oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")`. Dependency: `async def get_current_user(token: str = Depends(oauth2_scheme)): payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"]); user = await db.get_user(payload["sub"]); return user`. Inject in endpoints: `user: User = Depends(get_current_user)`. Token endpoint: accepts `username/password`, returns `{"access_token": jwt_token, "token_type": "bearer"}`. Store token in `Authorization: Bearer <token>` header.

Q4: What is `response_model` and why is it important?
A4: `response_model=UserPublicResponse` in `@app.get("/users/{id}", response_model=...)` does three things: (1) **Filters** response — only includes fields defined in `UserPublicResponse` (removes `password_hash`, internal fields). (2) **Validates** response data against the model (development safety net). (3) **Documents** — OpenAPI schema shows what the endpoint returns. Without `response_model`: return value is serialized as-is — may leak sensitive data. Always define a separate response model that excludes secrets.

Q5: How does FastAPI's `lifespan` work and what should go in it?
A5: `lifespan` is a context manager that wraps the whole app lifecycle. Code before `yield` runs at startup (before first request); code after `yield` runs at shutdown. Put in startup: DB connection pool creation, Redis client init, ML model loading, cache warming. Put in shutdown: close connections, flush buffers, cleanup temp files. `lifespan` replaced the deprecated `@app.on_event("startup")` / `@app.on_event("shutdown")` decorators. Use `asynccontextmanager` decorator. Startup errors prevent the app from starting — good for fail-fast on misconfiguration.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ASGI | Async Python web standard | Async Python web standard |
| Pydantic | Data validation library | Data validation library |
| Depends() | Dependency injection | Dependency injection |
| response_model | Response filter + schema | Response filter + schema |
| lifespan | App startup/shutdown | App startup/shutdown |
| BackgroundTasks | Fire-and-forget tasks | Fire-and-forget tasks |
| APIRouter | Route organization | Routes organize करना |

---

## ⚡ 3-Line Summary
English: FastAPI = Starlette (ASGI) + Pydantic (validation) — declare types, get validation, serialization, and Swagger docs for free. Use `response_model` to filter sensitive fields, `Depends()` for shared logic (DB session, auth), and `lifespan` for startup/shutdown. Always use `AsyncOpenAI` / `async` DB driver — never block the event loop with sync code.
Hindi: FastAPI = Starlette + Pydantic — types declare करो, validation + Swagger free मिलता है। `response_model` से sensitive fields filter। `Depends()` = shared logic। `lifespan` = startup/shutdown। Sync code से event loop block मत करो।

---

## ➡️ Next Topic
**300. Path + Query Parameters** — Path(), Query(), Header(), Cookie(). **303. Pydantic v2** — validators, config, model_dump. **315. OAuth2 + JWT** — authentication complete.
