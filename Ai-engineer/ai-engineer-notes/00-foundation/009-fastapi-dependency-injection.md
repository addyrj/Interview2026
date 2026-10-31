---

# 009. FastAPI Dependency Injection
# हिंदी में: FastAPI Dependency Injection

---

## 🔵 Simple Definition (English)
Dependency Injection (DI) means a route declares what it needs (an LLM client, a DB session, the current user) with `Depends(...)`, and FastAPI builds and passes it in. The route does not create these things itself. This makes code reusable, testable and clean.

## 🔵 सरल परिभाषा (Hindi)
Dependency Injection (DI) में route `Depends(...)` से बताता है कि उसे क्या चाहिए (LLM client, DB session, current user), और FastAPI उसे बनाकर दे देता है। Route खुद ये चीज़ें नहीं बनाता। इससे code reusable, testable और साफ़ रहता है।

---

## 🔴 Problem it Solves
Without DI, every route creates its own OpenAI client, opens its own DB connection and re-checks the API key. That duplicates code, wastes connections and makes tests hard (you cannot swap the real LLM for a fake). DI centralises creation and cleanup, and tests can override dependencies.

## 🔴 यह क्यों बना? (Hindi)
DI के बिना हर route अपना OpenAI client बनाता है, अपना DB connection खोलता है और API key दोबारा check करता है। इससे code दोहराता है, connections बर्बाद होते हैं और tests मुश्किल हो जाते हैं (असली LLM की जगह fake नहीं लगा सकते)। DI creation और cleanup एक जगह रखता है, और tests dependencies override कर सकते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write a dependency: a function (sync or async) that returns or yields a value
Step 2 → In the route: `svc: Service = Depends(get_service)`
Step 3 → On each request FastAPI calls get_service() (it may itself Depends on other things → a tree)
Step 4 → Results are cached per request, so the same dependency is built once per request
Step 5 → If the dependency uses `yield`, code after yield runs after the response (cleanup)
Step 6 → An exception in a dependency (HTTPException) stops the route (auth, rate limit)
Step 7 → In tests: app.dependency_overrides[get_service] = fake_service
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Dependency लिखो: ऐसा function (sync या async) जो value return या yield करे
Step 2 → Route में: `svc: Service = Depends(get_service)`
Step 3 → हर request पर FastAPI get_service() चलाता है (यह खुद भी दूसरी Depends पर निर्भर हो सकता है → tree)
Step 4 → Results प्रति request cache होते हैं, यानी एक request में dependency एक बार बनती है
Step 5 → `yield` वाली dependency में yield के बाद का code response के बाद चलता है (cleanup)
Step 6 → Dependency में exception (HTTPException) route को रोक देता है (auth, rate limit)
Step 7 → Tests में: app.dependency_overrides[get_service] = fake_service
```

---

## 🟡 Real World Example
**Tariff Classification System**: Dependencies: `get_settings` (env config), `get_llm` (shared async LLM client), `get_db` (DB session with cleanup), `get_current_user` (checks API key), `rate_limit` (per-user token budget). The `/classify` route simply lists them. In tests we override `get_llm` with a fake that returns a fixed HS code and costs no tokens.

**Zomato AI**: `get_current_user` identifies the diner so the recommender can use their past orders.

## 🟡 Real Example Hindi mein
**Tariff System**: Dependencies: `get_settings` (env config), `get_llm` (shared async LLM client), `get_db` (cleanup वाला DB session), `get_current_user` (API key check), `rate_limit` (प्रति user token budget)। `/classify` route बस इन्हें list करता है। Tests में `get_llm` को fake से override करते हैं जो fixed HS code देता है और tokens खर्च नहीं करता।

**Zomato AI**: `get_current_user` diner को पहचानता है ताकि recommender उसके पुराने orders use कर सके।

---

## 💻 Code Example — Basic
```python
# Basic dependency injection - needs fastapi + httpx for the test client
from fastapi import Depends, FastAPI, Header, HTTPException  # DI tools
from fastapi.testclient import TestClient  # in-process testing

app = FastAPI()  # app


def get_api_key(x_api_key: str = Header(default="")) -> str:  # dependency reading a header
    if x_api_key != "secret":  # simple check
        raise HTTPException(status_code=401, detail="bad api key")  # stops the route
    return x_api_key  # value passed to the route


class FakeLLM:  # stands in for a real client
    def answer(self, q: str) -> str:  # returns canned text
        return f"HS 8517 for {q}"  # fake


def get_llm() -> FakeLLM:  # dependency providing the client
    return FakeLLM()  # new object (or a shared one in real apps)


@app.get("/ask")  # route
def ask(q: str, key: str = Depends(get_api_key), llm: FakeLLM = Depends(get_llm)) -> dict[str, str]:  # two deps
    return {"answer": llm.answer(q)}  # use injected objects


client = TestClient(app)  # create test client
print(client.get("/ask?q=phone").status_code)  # 401, dependency blocked it
print(client.get("/ask?q=phone", headers={"x-api-key": "secret"}).json())  # works
```

## 💻 Code Example — Advanced
```python
# Production DI: lifespan-created shared client, yield-dependency for DB session, settings,
# per-user token budget, class-based dependency, and test override
import asyncio  # async tools
from contextlib import asynccontextmanager  # lifespan helper
from typing import Annotated, AsyncIterator  # typing

from fastapi import Depends, FastAPI, HTTPException, Request  # FastAPI pieces
from fastapi.testclient import TestClient  # tests
from pydantic import BaseModel  # body model


class Settings(BaseModel):  # configuration object
    model: str = "gpt-4o-mini"  # model name
    daily_token_budget: int = 1000  # tiny budget for the demo


class LLMClient:  # shared client wrapper (real code would wrap AsyncOpenAI)
    async def complete(self, prompt: str) -> tuple[str, int]:  # returns (text, tokens)
        await asyncio.sleep(0.01)  # pretend network
        return "8517.13", 400  # fake answer + token usage


class Session:  # fake DB session with cleanup
    closed = False  # state flag

    async def close(self) -> None:  # cleanup
        self.closed = True  # mark closed


@asynccontextmanager  # lifespan: runs once at startup/shutdown
async def lifespan(app: FastAPI) -> AsyncIterator[None]:  # startup and shutdown hook
    app.state.llm = LLMClient()  # created ONCE, shared by all requests
    app.state.usage = {}  # user -> tokens used today
    yield  # app is running
    # shutdown cleanup (close clients) would go here


app = FastAPI(lifespan=lifespan)  # app with lifespan


def get_settings() -> Settings:  # settings dependency
    return Settings()  # cheap to build


def get_llm(request: Request) -> LLMClient:  # reads the shared client from app.state
    return request.app.state.llm  # same object every request


async def get_session() -> AsyncIterator[Session]:  # yield dependency
    session = Session()  # open
    try:  # ensure cleanup
        yield session  # route runs here
    finally:  # always executes after the response
        await session.close()  # release the connection


def get_user(request: Request) -> str:  # identify caller
    user = request.headers.get("x-user")  # header lookup
    if not user:  # missing
        raise HTTPException(status_code=401, detail="x-user header required")  # reject
    return user  # user id


class BudgetGuard:  # class-based dependency (callable object)
    def __init__(self, cost_estimate: int) -> None:  # configuration
        self.cost_estimate = cost_estimate  # tokens to reserve

    def __call__(self, request: Request, user: Annotated[str, Depends(get_user)],
                 settings: Annotated[Settings, Depends(get_settings)]) -> str:  # nested deps
        used = request.app.state.usage.get(user, 0)  # tokens used so far
        if used + self.cost_estimate > settings.daily_token_budget:  # would exceed?
            raise HTTPException(status_code=429, detail="daily token budget exceeded")  # block before paying
        return user  # allowed


class In(BaseModel):  # body
    description: str  # product text


@app.post("/classify")  # route with many dependencies
async def classify(
    body: In,  # request body
    request: Request,  # raw request to update usage
    user: Annotated[str, Depends(BudgetGuard(cost_estimate=400))],  # budget check
    llm: Annotated[LLMClient, Depends(get_llm)],  # shared client
    session: Annotated[Session, Depends(get_session)],  # per-request session
) -> dict[str, str | int]:  # response
    text, tokens = await llm.complete(body.description)  # call model
    request.app.state.usage[user] = request.app.state.usage.get(user, 0) + tokens  # record spend
    return {"hs_code": text, "tokens": tokens}  # result


if __name__ == "__main__":  # self-test
    with TestClient(app) as c:  # context manager runs lifespan
        h = {"x-user": "alice"}  # header
        print(c.post("/classify", json={"description": "phone"}, headers=h).json())  # ok
        print(c.post("/classify", json={"description": "phone"}, headers=h).json())  # ok (800 used)
        print(c.post("/classify", json={"description": "phone"}, headers=h).status_code)  # 429
        print(c.post("/classify", json={"description": "phone"}).status_code)  # 401

        class Fake(LLMClient):  # test double
            async def complete(self, prompt: str) -> tuple[str, int]:  # no tokens spent
                return "TEST", 0  # constant
        app.dependency_overrides[get_llm] = lambda: Fake()  # override in tests
        print(c.post("/classify", json={"description": "x"}, headers={"x-user": "bob"}).json())  # TEST
```

---

## 🟠 FastAPI Integration
DI is a core FastAPI feature. Use `Annotated[T, Depends(fn)]` (current recommended style), put cross-cutting checks (auth, rate limit) in `dependencies=[Depends(...)]` on a router so every route is protected, and build expensive clients once in `lifespan`.

```python
# Router-level dependency protects every route inside
from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException  # tools


def require_key(x_api_key: str = Header(default="")) -> None:  # checks every request
    if x_api_key != "secret":  # invalid
        raise HTTPException(401, "invalid key")  # stop


router = APIRouter(prefix="/admin", dependencies=[Depends(require_key)])  # applies to all routes below


@router.get("/stats")  # route without its own auth code
async def stats() -> dict[str, int]:  # handler
    return {"requests": 42}  # data


app = FastAPI()  # app
app.include_router(router)  # mount
```

---

## 🔗 LangChain / LangGraph Connection
Build the chain or compiled graph once and inject it, instead of rebuilding per request. The compiled LangGraph app is thread-safe for `ainvoke`; pass per-user data via `config={"configurable": {"thread_id": user}}`.

```python
# Inject a prebuilt chain (needs API key to actually run)
from fastapi import Depends, FastAPI, Request  # DI
from langchain_core.prompts import ChatPromptTemplate  # prompt
from langchain_openai import ChatOpenAI  # model


def build_chain():  # built once at startup
    return ChatPromptTemplate.from_template("HS code for {item}") | ChatOpenAI(model="gpt-4o-mini")  # LCEL


def get_chain(request: Request):  # dependency
    return request.app.state.chain  # read the shared chain


app = FastAPI()  # app
app.state.chain = build_chain()  # store at import/startup


@app.get("/hs")  # route
async def hs(item: str, chain=Depends(get_chain)) -> dict[str, str]:  # injected chain
    return {"answer": str((await chain.ainvoke({"item": item})).content)}  # call it
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Creating the client inside the dependency on every request
✅ Correct: create it once (lifespan) and return the shared instance.

```python
# Wrong: new connection pool per request
def get_llm():
    return AsyncOpenAI()
# Right
def get_llm(request: Request):
    return request.app.state.llm
```

❌ Mistake 2: Forgetting cleanup (leaking DB sessions)
✅ Correct: use `yield` with `try/finally`.

```python
# Wrong: session never closed
def get_db():
    return Session()
# Right
def get_db():
    s = Session()
    try:
        yield s
    finally:
        s.close()
```

❌ Mistake 3: Using global variables for per-user state. A dependency should derive state from the request (headers, token).

---

## 🧠 Tricky Interview Question

**Q**: "A dependency `get_user` is used by the route and by `BudgetGuard`. Does it run twice per request? And what if you want it to run every time?"

**Answer**: By default FastAPI caches dependency results within one request (`use_cache=True`), so `get_user` runs once and both get the same value. If you need a fresh call each time (for example, a function that returns a random id or timestamp), use `Depends(get_user, use_cache=False)`. Caching is per request, not across requests, so a shared client must live in `app.state` or a module-level singleton instead.

---

## ⚫ Interview Questions + Answers

Q1: What is `Depends` used for? (Easy)
A1: It tells FastAPI to call a function and pass its result to the route. It is used for auth, DB sessions, config, shared clients, and common parameters.

Q2: How do you replace a dependency in tests? (Easy)
A2: `app.dependency_overrides[real_dep] = fake_dep`, then clear it after the test. This lets you test routes without calling the real LLM or database.

Q3: What does a dependency with `yield` do? (Medium)
A3: Code before `yield` runs before the route (setup) and the yielded value is injected. Code after `yield` runs after the response is sent (teardown), even if the route raised, when written in `try/finally`. Used for DB sessions and locks.

Q4: Where should an expensive LLM client be created? (Medium)
A4: Once at startup using `lifespan` (or a module-level singleton), stored on `app.state` or returned by a dependency. Reusing it keeps HTTP connection pools warm and avoids per-request setup latency.

Q5: How would you implement per-tenant rate limiting by tokens using DI? (Hard)
A5: A dependency reads the tenant from the auth token, estimates input tokens (tiktoken), and does an atomic Redis operation (Lua script or `INCRBY` plus `EXPIRE`) on a per-day key. If over budget, raise 429 before any LLM call. After the call, a second step (a background task or the `finally` of a yield-dependency) adds the actual `usage.total_tokens`. Fail policy for a Redis outage must be chosen: fail-open protects availability, fail-closed protects budget.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Sharing clients, settings, DB sessions across routes
- Authentication and authorisation checks
- You want easy test overrides

❌ Avoid when:
- A simple pure helper function is enough (just call it)
- You hide heavy I/O in deeply nested dependencies and lose track of latency
- You need state across requests (use `app.state` or an external store, not per-request dependencies)

---

## 📊 Visual Diagram
```
 request ──► route classify(body, user=Depends(BudgetGuard), llm=Depends(get_llm), db=Depends(get_session))
                              │                │                  │              │
                              ▼                ▼                  ▼              ▼
                     get_user ─► settings   app.state.llm     open session ──► yield
                        │ 401?       │ 429?                                        │
                        └────────────┴── pass ──► route body runs ──► response ──► close session
 tests: app.dependency_overrides[get_llm] = Fake   (no tokens, no network)
```

---

## 💰 Cost Impact
DI itself is free, but it is the best place to protect spend: a budget dependency rejects over-limit users before any tokens are used; an auth dependency blocks anonymous traffic; a shared client avoids repeated connection setup. Test overrides mean CI runs call a fake LLM, so tests cost zero tokens. Example: if abuse or bugs would otherwise cause 5K extra calls of 700 tokens per day, the guard prevents 3.5M tokens, about $0.5/day on gpt-4o-mini input pricing and much more on larger models.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Dependency | Something a route needs | route को चाहिए चीज़ |
| Depends | Marks an injected dependency | injection चिह्नित करता है |
| Lifespan | Startup and shutdown hook | startup/shutdown hook |
| dependency_overrides | Replace dependency in tests | tests में बदलना |
| yield dependency | Setup + cleanup dependency | setup + cleanup वाली dependency |
| app.state | Shared app-level storage | app-level साझा storage |
| use_cache | Reuse result within a request | request में result दोबारा use |
| Singleton | One shared instance | एक साझा instance |

---

## ⚡ 3-Line Summary
English: `Depends` lets routes receive shared resources (LLM client, DB session, user) built and cleaned up by FastAPI. Create expensive clients once in `lifespan`, use `yield` for cleanup, and override dependencies in tests. Put auth and token budgets in dependencies to block bad calls before they cost tokens.
Hindi: `Depends` से routes को shared resources (LLM client, DB session, user) मिलते हैं जिन्हें FastAPI बनाता और साफ़ करता है। महंगे clients `lifespan` में एक बार बनाओ, cleanup के लिए `yield` लो, और tests में dependencies override करो। Auth और token budget dependencies में रखो ताकि गलत calls पर tokens खर्च न हों।

---

## ➡️ Next Topic
**010. FastAPI Background Tasks** — after the response is returned, we run slow work (logging usage, saving results) without making the user wait.
