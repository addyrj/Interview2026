---

# 311. Dependency Injection in FastAPI — Complete Guide
# हिंदी में: FastAPI में Dependency Injection — पूरी Guide

---

## 🔵 Simple Definition (English)
FastAPI's `Depends()` is a dependency injection system — you declare what a route needs (DB connection, current user, pagination params), and FastAPI automatically provides it. Dependencies are reusable functions that run before the route handler and pass their return value to it.

## 🔵 सरल परिभाषा (Hindi)
FastAPI का `Depends()` dependency injection system है — आप declare करते हो कि route को क्या चाहिए (DB connection, current user, pagination), और FastAPI automatically provide करता है। Dependencies reusable functions हैं जो route handler से पहले run होती हैं।

---

## 🔴 Problem it Solves
Without DI: every route duplicates auth check, DB session creation, pagination parsing. Change the auth logic → edit every route. Test a route → need real DB. With `Depends()`: auth is one function, DB is one function — inject anywhere, mock in tests.

## 🔴 यह क्यों बना? (Hindi)
Depends() के बिना: हर route में auth check, DB session, pagination copy-paste। Auth logic change = हर route edit। Test = real DB चाहिए। `Depends()` से: auth एक function, DB एक function — कहीं भी inject करो, tests में mock करो।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define dependency as a regular or async function
Step 2 → Use Depends(your_function) in route parameter
Step 3 → FastAPI sees Depends() → calls your_function first
Step 4 → Return value of your_function is passed to route as parameter
Step 5 → If dependency raises HTTPException → route never runs
Step 6 → Dependencies can have their own dependencies (sub-dependencies)
Step 7 → yield dependencies → code after yield runs as cleanup (DB session close)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Dependency function define करो
Step 2 → Route parameter में Depends(function) use करो
Step 3 → FastAPI Depends() देखता है → पहले आपकी function call करता है
Step 4 → Function का return value route को parameter के रूप में मिलता है
Step 5 → Dependency HTTPException raise करे → route run ही नहीं होता
Step 6 → Dependencies के अपने dependencies हो सकते हैं (sub-dependencies)
Step 7 → yield dependency → yield के बाद code cleanup में run होता है
```

---

## 🟡 Real World Example
Razorpay API: every endpoint needs (1) auth token validated, (2) DB session, (3) rate limit check. With dependencies, declare these once and `Depends()` them everywhere. Change from JWT to API key auth → change ONE dependency function, all routes updated automatically.

## 🟡 Real Example Hindi mein
Razorpay API: हर endpoint को (1) auth token check, (2) DB session, (3) rate limit चाहिए। Dependencies से एक बार declare करो। JWT से API key auth change → एक function change = सभी routes automatically update।

---

## 💻 Code Example — Basic
```python
# Basic dependency injection patterns
from fastapi import FastAPI, Depends, HTTPException, status
from typing import Annotated

app = FastAPI()

# DEPENDENCY 1: Pagination parameters (reusable across all list routes)
def pagination_params(
    page: int = 1,
    page_size: int = 20
) -> dict:
    """Validates and returns pagination parameters."""
    if page < 1:
        raise HTTPException(status_code=400, detail="page must be >= 1")
    if page_size > 100:
        raise HTTPException(status_code=400, detail="max page_size is 100")
    offset = (page - 1) * page_size
    return {"limit": page_size, "offset": offset, "page": page}

# DEPENDENCY 2: Simple header-based auth
def require_api_key(x_api_key: str = Header(None)) -> str:
    """Validates API key from request header."""
    valid_keys = {"secret-key-123", "secret-key-456"}  # use DB/Redis in production
    if x_api_key not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return x_api_key

# Annotated type — modern FastAPI style (Python 3.9+)
PaginationDep = Annotated[dict, Depends(pagination_params)]
ApiKeyDep = Annotated[str, Depends(require_api_key)]

@app.get("/products")
def list_products(
    pagination: PaginationDep,     # automatically injected!
    api_key: ApiKeyDep,            # auth checked automatically!
    category: str | None = None    # regular query param
):
    # pagination = {"limit": 20, "offset": 0, "page": 1} — ready to use
    return {
        "page": pagination["page"],
        "limit": pagination["limit"],
        "offset": pagination["offset"],
        "category": category
    }
```

## 💻 Code Example — Advanced
```python
# Production patterns: DB sessions, JWT auth, role-based access
from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Annotated, AsyncGenerator
from datetime import datetime

# --- DATABASE DEPENDENCY ---
DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/mydb"
engine = create_async_engine(DATABASE_URL, pool_size=10)
AsyncSessionFactory = async_sessionmaker(engine, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Yields a DB session and ensures it's closed after request.
    yield dependency = code before yield runs first, code after yield runs as cleanup.
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session              # ← session is passed to route
            await session.commit()    # commit if no exception
        except Exception:
            await session.rollback()  # rollback on error
            raise
        # session.close() called automatically by async with

DbDep = Annotated[AsyncSession, Depends(get_db)]

# --- AUTH DEPENDENCY ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

class TokenData(BaseModel):
    user_id: int
    email: str
    role: str

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DbDep                        # dependency depends on another dependency!
) -> TokenData:
    """Validates JWT and returns the current user. Sub-dependencies work!"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
        email: str = payload.get("email", "")
        role: str = payload.get("role", "user")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Optionally verify user still exists in DB
        # user = await db.get(User, user_id)
        # if not user: raise HTTPException(401, "User not found")
        
        return TokenData(user_id=user_id, email=email, role=role)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

CurrentUser = Annotated[TokenData, Depends(get_current_user)]

# --- ROLE-BASED ACCESS ---
def require_role(required_role: str):
    """Factory that creates role-checking dependencies."""
    async def check_role(current_user: CurrentUser) -> TokenData:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role: {required_role}"
            )
        return current_user
    return check_role

AdminUser = Annotated[TokenData, Depends(require_role("admin"))]

# --- ROUTES USING DEPENDENCIES ---
app = FastAPI()

@app.get("/me")
async def get_profile(current_user: CurrentUser, db: DbDep):
    """Any authenticated user."""
    return {"user_id": current_user.user_id, "email": current_user.email}

@app.delete("/users/{user_id}")
async def delete_user(user_id: int, admin: AdminUser, db: DbDep):
    """Admin only."""
    # admin is automatically validated as role='admin'
    # db session is automatically provided and cleaned up
    return {"deleted": user_id}

@app.get("/health")
async def health_check(db: DbDep):
    """No auth needed — just DB check."""
    await db.execute(text("SELECT 1"))
    return {"status": "ok"}
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python FastAPI: DI with Depends()
from fastapi import FastAPI, Depends

def get_db():
    db = DatabaseSession()
    try:
        yield db
    finally:
        db.close()

@app.get("/users")
def get_users(db = Depends(get_db)):    # FastAPI injects db
    return db.query(User).all()
```

```javascript
// JavaScript NestJS: DI with decorators (similar concept)
import { Injectable, Controller, Get } from '@nestjs/common';

@Injectable()
class DatabaseService {
    query(sql: string) { /* ... */ }
}

@Controller('users')
class UsersController {
    constructor(private db: DatabaseService) {}  // NestJS injects!
    
    @Get()
    getUsers() {
        return this.db.query('SELECT * FROM users');
    }
}

// Express (no built-in DI):
// Must manually inject: const db = new DatabaseService();
// router.get('/users', (req, res) => { db.query(...) });
// No automatic lifecycle, no automatic cleanup

// FastAPI's Depends() is simpler than NestJS — no decorators needed,
// just declare in function signature
```

---

## 🟠 FastAPI Connection — Global Dependencies

```python
# Apply dependencies to ALL routes in a router or app
from fastapi import FastAPI, APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer

# Option 1: router-level dependency (all routes in this router need auth)
router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_role("admin"))]  # ← ALL routes require admin
)

@router.get("/users")                 # ← automatically requires admin
async def list_all_users(db: DbDep):
    pass

@router.delete("/user/{user_id}")     # ← automatically requires admin
async def delete_user(user_id: int, db: DbDep):
    pass

# Option 2: app-level dependency (ALL routes in the app)
app = FastAPI(
    dependencies=[Depends(require_api_key)]   # ← every route requires API key
)

# Option 3: middleware (slightly different — doesn't get DI benefits)
# Use Depends() over middleware when you need the dependency's return value in the route
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Returning DB session instead of yielding
```python
# Wrong — session never closed!
async def get_db():
    session = AsyncSessionFactory()
    return session              # ← no cleanup! Connection leaks!

# Correct — use yield:
async def get_db():
    async with AsyncSessionFactory() as session:
        yield session           # ← after yield, async with closes session
```

❌ Mistake 2: Calling dependency function directly (bypasses FastAPI's DI)
```python
# Wrong — get_db() called manually, not injected
@app.get("/users")
async def get_users():
    db = get_db()               # ← this returns a generator object, not a session!
    users = await db.execute("SELECT * FROM users")

# Correct — let FastAPI inject it via Depends():
@app.get("/users")
async def get_users(db: DbDep): # FastAPI calls get_db() and passes the yielded session
    users = await db.execute(select(User))
```

❌ Mistake 3: Mutable default in dependency
```python
# Wrong — shared mutable state across requests!
def get_settings(config: dict = {}):   # ← dict shared across all calls!
    config["debug"] = True
    return config

# Correct — create new object each time:
def get_settings() -> dict:
    return {"debug": True, "env": "prod"}   # fresh dict every call
```

---

## 🧠 Tricky Interview Question

```python
from fastapi import FastAPI, Depends

def dep_a() -> str:
    print("dep_a called")
    return "A"

def dep_b(a: str = Depends(dep_a)) -> str:
    print(f"dep_b called, got: {a}")
    return f"B({a})"

def dep_c(a: str = Depends(dep_a)) -> str:
    print(f"dep_c called, got: {a}")
    return f"C({a})"

app = FastAPI()

@app.get("/test")
def endpoint(b: str = Depends(dep_b), c: str = Depends(dep_c)):
    return {"b": b, "c": c}
```
What happens when `/test` is called? How many times is `dep_a` called?
Answer: `dep_a` is called **ONCE**, not twice. FastAPI caches dependency results within a single request — if the same dependency appears multiple times in the dependency graph, it's resolved once and the result is reused. This is called dependency caching (controlled by `use_cache=True` default in `Depends()`). You can disable with `Depends(dep_a, use_cache=False)` if you need fresh calls.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `Depends()` and middleware?
A1: `Depends()` is for route-specific dependencies — injected only when needed, returns a value the route can use, participates in the type system, easy to mock in tests. Middleware applies to ALL requests before routing, can't return values to routes, runs regardless of route. Use `Depends()` for: auth, DB sessions, pagination, rate limiting per route. Use middleware for: logging all requests, adding headers, CORS.

Q2: How do you test a route that uses `Depends()`?
A2: Override the dependency in `TestClient`. FastAPI's `app.dependency_overrides[original_dep] = mock_dep` replaces the dependency for testing. This lets you inject a fake DB session, a mock user, etc. without a real DB connection:
```python
app.dependency_overrides[get_db] = lambda: fake_db_session
app.dependency_overrides[get_current_user] = lambda: TokenData(user_id=1, role="admin")
client = TestClient(app)
response = client.get("/admin/users")
```

Q3: What is a `yield` dependency vs a regular `return` dependency?
A3: `yield` dependency (generator function): the code before `yield` is setup, the yielded value is the injected dependency, the code after `yield` runs as cleanup after the request completes. Use for DB sessions, file handles, any resource needing cleanup. `return` dependency: simpler, just returns a value. Use for pure transformations (pagination params, config values).

Q4: Can dependencies have their own dependencies?
A4: Yes — sub-dependencies. FastAPI builds a dependency graph and resolves it in the right order. `get_current_user` can `Depends(get_db)` and `Depends(oauth2_scheme)`. FastAPI calls them all, caches results, and injects them in the right order. There's no explicit limit to nesting depth.

Q5: What is `Annotated` and how does it improve dependency injection?
A5: `Annotated[Type, Depends(func)]` is a modern (Python 3.9+) way to declare dependencies using type hints. `DbDep = Annotated[AsyncSession, Depends(get_db)]` — then use `db: DbDep` in routes. Benefits: cleaner syntax (no default value needed), reusable type alias across many routes, works better with type checkers than `db = Depends(get_db)`.

---

## 🔷 When to Use + When Not to Use

✅ Use Depends() for:
- DB session management (yield pattern with cleanup)
- Authentication and authorization (JWT validation, role checks)
- Common query parameter parsing (pagination, filters, sorting)
- Rate limiting per user/route
- Cache setup, external service clients
- Any logic shared across 2+ routes

❌ Avoid Depends() for:
- Logic specific to one route — just write it inline
- Very heavy computation that runs on every request (cache it instead)
- When middleware is more appropriate (logging ALL requests)

---

## 📊 Visual Diagram
```
Request → /admin/users
         │
         ├─→ Depends(get_db)           → db session (yield, cleanup after)
         │
         ├─→ Depends(require_role("admin"))
         │         │
         │         └─→ Depends(get_current_user)   (sub-dependency!)
         │                   │
         │                   └─→ Depends(oauth2_scheme)  → JWT token from header
         │                   └─→ Depends(get_db)         → SAME db session (cached!)
         │
         ↓
    Route handler(db, admin_user)
    
FastAPI resolves the graph, calls each dependency ONCE (cached),
injects results in the right order.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Depends() | FastAPI's DI mechanism | Dependency inject करने का तरीका |
| yield dependency | Dependency with cleanup code | Setup + cleanup वाली dependency |
| sub-dependency | Dependency that depends on another | Dependency की dependency |
| dependency caching | Same dep called once per request | एक request में एक बार call |
| dependency override | Replace dep in tests | Tests में mock dependency लगाओ |
| Annotated | Type hint + metadata combined | Type hint + Depends एक साथ |

---

## ⚡ 3-Line Summary
English: FastAPI's `Depends()` injects reusable functions (DB session, auth, pagination) into routes automatically. `yield` dependencies handle setup and cleanup. FastAPI caches dependency results within a request — same dependency resolved once even if used by multiple sub-dependencies.
Hindi: `Depends()` reusable functions (DB, auth, pagination) को routes में automatically inject करता है। `yield` dependency setup और cleanup handle करती है। FastAPI एक request में same dependency एक बार resolve करता है।

---

## ➡️ Next Topic
**312. Dependencies — Complete Guide** — class-based dependencies, parametrized dependencies, global router-level dependencies, and dependency testing patterns.
