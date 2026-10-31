---

# 007. FastAPI Route Creation
# हिंदी में: FastAPI Route बनाना

---

## 🔵 Simple Definition (English)
A route connects an HTTP method and URL (like `POST /classify`) to a Python function. FastAPI reads the function's type hints to parse the request, validate it and produce docs automatically. Routes are the front door of every AI service.

## 🔵 सरल परिभाषा (Hindi)
Route एक HTTP method और URL (जैसे `POST /classify`) को Python function से जोड़ता है। FastAPI function के type hints पढ़कर request parse, validate और docs अपने आप बनाता है। हर AI service का front door routes ही हैं।

---

## 🔴 Problem it Solves
Before frameworks like FastAPI you wrote manual parsing: read raw body, check fields, convert types, build error replies, and write docs by hand. That is slow and error-prone. FastAPI gives validation, serialisation, async support and Swagger docs from a few lines.

## 🔴 यह क्यों बना? (Hindi)
FastAPI जैसे frameworks से पहले manual parsing करनी पड़ती थी: raw body पढ़ो, fields check करो, types बदलो, error replies बनाओ, docs हाथ से लिखो। यह धीमा और गलतियों वाला था। FastAPI कुछ lines में validation, serialisation, async support और Swagger docs देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → app = FastAPI() creates the application
Step 2 → @app.get / @app.post("/path") registers a function as a handler
Step 3 → Client sends HTTP request; the router matches method + path
Step 4 → Path params (/items/{id}), query params (?top_k=3) and JSON body are parsed using type hints
Step 5 → Invalid input returns 422 automatically; valid input is passed to your function
Step 6 → Your function returns a dict/model; FastAPI converts it to JSON (filtered by response_model)
Step 7 → /docs (Swagger) and /openapi.json are generated for free
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → app = FastAPI() application बनाता है
Step 2 → @app.get / @app.post("/path") function को handler के रूप में register करता है
Step 3 → Client HTTP request भेजता है; router method + path match करता है
Step 4 → Path params (/items/{id}), query params (?top_k=3) और JSON body type hints से parse होते हैं
Step 5 → गलत input पर अपने आप 422; सही input आपके function को मिलता है
Step 6 → Function dict/model return करता है; FastAPI उसे JSON बनाता है (response_model से filter)
Step 7 → /docs (Swagger) और /openapi.json मुफ़्त में बन जाते हैं
```

---

## 🟡 Real World Example
**Tariff Classification System**: Routes: `POST /classify` (one product), `POST /classify/batch`, `GET /codes/{hs_code}` (look up one code), `GET /health` (for the load balancer). Clients such as the customs web app call these.

**Zomato AI**: `POST /search` takes a natural-language query ("spicy veg dinner under 300") and returns restaurants; `GET /restaurants/{id}` returns details.

## 🟡 Real Example Hindi mein
**Tariff System**: Routes: `POST /classify` (एक product), `POST /classify/batch`, `GET /codes/{hs_code}` (एक code देखना), `GET /health` (load balancer के लिए)। Customs web app इन्हें call करता है।

**Zomato AI**: `POST /search` natural-language query लेता है ("300 से कम में तीखा veg dinner") और restaurants देता है; `GET /restaurants/{id}` details देता है।

---

## 💻 Code Example — Basic
```python
# Basic FastAPI app (pip install fastapi uvicorn). Run: uvicorn main:app --reload
from fastapi import FastAPI  # the framework
from pydantic import BaseModel  # request body model

app = FastAPI(title="Tariff API")  # create the application


class ClassifyIn(BaseModel):  # JSON body shape
    description: str  # required product description


@app.get("/health")  # GET route, no input
async def health() -> dict[str, str]:  # return type hint
    return {"status": "ok"}  # becomes JSON


@app.get("/codes/{hs_code}")  # path parameter in braces
async def get_code(hs_code: str, verbose: bool = False) -> dict:  # verbose is a query param (?verbose=true)
    info = {"hs_code": hs_code, "chapter": hs_code[:2]}  # tiny fake lookup
    if verbose:  # optional extra detail
        info["note"] = "chapter = first two digits"  # add detail
    return info  # JSON response


@app.post("/classify")  # POST route with JSON body
async def classify(body: ClassifyIn) -> dict:  # body parsed + validated by pydantic
    return {"input": body.description, "hs_code": "8517.13"}  # fake model answer


# Quick self-test without a server, using the built-in test client:
if __name__ == "__main__":  # only when run directly
    from fastapi.testclient import TestClient  # needs httpx installed
    client = TestClient(app)  # in-process client
    print(client.get("/health").json())  # {'status': 'ok'}
    print(client.get("/codes/8517?verbose=true").json())  # path + query param
    print(client.post("/classify", json={"description": "phone"}).json())  # body
    print(client.post("/classify", json={}).status_code)  # 422 validation error
```

## 💻 Code Example — Advanced
```python
# Production routes: APIRouter, tags, status codes, response_model, async LLM call, error handling
import asyncio  # async tools
from fastapi import APIRouter, FastAPI, HTTPException, Path, status  # core pieces
from pydantic import BaseModel, Field  # models

router = APIRouter(prefix="/v1", tags=["classification"])  # groups routes under /v1


class ClassifyIn(BaseModel):  # input
    description: str = Field(min_length=3, max_length=2000, examples=["Android smartphone 128GB"])  # bounded size = bounded tokens
    country: str = Field(default="IN", pattern=r"^[A-Z]{2}$")  # 2-letter code


class ClassifyOut(BaseModel):  # output
    hs_code: str  # result code
    confidence: float  # 0..1
    tokens_used: int  # for cost tracking


async def llm_classify(text: str) -> ClassifyOut:  # mock for a real LLM call
    await asyncio.sleep(0.05)  # pretend latency
    if "forbidden" in text:  # simulate provider failure
        raise ConnectionError("provider down")  # transient error
    return ClassifyOut(hs_code="8517.13", confidence=0.82, tokens_used=640)  # fake result


@router.post("/classify", response_model=ClassifyOut, status_code=status.HTTP_200_OK,
             summary="Classify one product", responses={502: {"description": "LLM provider failed"}})
async def classify(body: ClassifyIn) -> ClassifyOut:  # async handler
    try:  # guard external call
        return await llm_classify(body.description)  # await the LLM
    except ConnectionError as exc:  # provider failure
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))  # clear error


@router.get("/codes/{hs_code}", response_model=dict)  # path parameter
async def get_code(
    hs_code: str = Path(pattern=r"^\d{4}", description="HS code"),  # path param validated by regex
) -> dict:  # simple dict response
    if not hs_code[:4].isdigit():  # defensive check
        raise HTTPException(status_code=422, detail="HS code must start with 4 digits")  # client error
    return {"hs_code": hs_code, "chapter": hs_code[:2]}  # JSON


app = FastAPI(title="Tariff API", version="1.0.0")  # app
app.include_router(router)  # mount the router

if __name__ == "__main__":  # self-test
    from fastapi.testclient import TestClient  # test client
    c = TestClient(app)  # create
    print(c.post("/v1/classify", json={"description": "Android phone"}).json())  # success
    print(c.post("/v1/classify", json={"description": "forbidden item"}).status_code)  # 502
    print(c.post("/v1/classify", json={"description": "x"}).status_code)  # 422 (too short)
```

---

## 🟠 FastAPI Integration
This topic is FastAPI itself. A common AI layout: routes stay thin (parse, call service, return), and the LLM logic lives in a service module. Use `async def` when the route awaits network I/O; use plain `def` for blocking libraries (FastAPI runs those in a threadpool).

```python
# Thin route calling a service function
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # model

app = FastAPI()  # app


class Q(BaseModel):  # body
    question: str  # user question


async def answer_service(question: str) -> str:  # business logic lives outside the route
    return f"Answer to: {question}"  # fake


@app.post("/ask")  # route
async def ask(q: Q) -> dict[str, str]:  # thin handler
    return {"answer": await answer_service(q.question)}  # delegate to service
```

---

## 🔗 LangChain / LangGraph Connection
A LangChain chain or LangGraph graph is just an object you call inside a route with `ainvoke`. LangServe-style exposure is possible, but most teams write explicit FastAPI routes for control over auth, validation and errors.

```python
# Route calling a LangChain chain (needs OPENAI_API_KEY)
from fastapi import FastAPI  # framework
from langchain_core.prompts import ChatPromptTemplate  # prompt
from langchain_openai import ChatOpenAI  # model

app = FastAPI()  # app
chain = ChatPromptTemplate.from_template("HS code for: {item}") | ChatOpenAI(model="gpt-4o-mini")  # build once at import


@app.post("/chain")  # route
async def run_chain(item: str) -> dict[str, str]:  # item is a query param here
    msg = await chain.ainvoke({"item": item})  # async call, does not block the server
    return {"answer": str(msg.content)}  # return text
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Blocking call inside `async def`
✅ Correct: use an async client or plain `def`.

```python
# Wrong: the whole server freezes during this call
@app.get("/x")
async def x():
    return requests.get("https://api.example.com").json()
# Right: async HTTP client
@app.get("/x")
async def x():
    async with httpx.AsyncClient() as c:
        return (await c.get("https://api.example.com")).json()
```

❌ Mistake 2: Accepting unbounded input
✅ Correct: limit sizes in the model (protects your token bill).

```python
# Wrong: a user can send a 5 MB description to the LLM
class In(BaseModel):
    description: str
# Right
class In(BaseModel):
    description: str = Field(max_length=2000)
```

❌ Mistake 3: Putting LLM logic and prompts inside route functions. Keep routes thin and testable.

---

## 🧠 Tricky Interview Question

**Q**: "You have `@app.get('/codes/{hs_code}')` and `@app.get('/codes/search')`. Calling `/codes/search` returns validation errors. Why?"

**Answer**: Routes are matched in registration order. `/codes/{hs_code}` is declared first and matches the string "search" as a path parameter, so the second route is never reached. Declare the fixed path `/codes/search` before the dynamic one (or use a different prefix). Also note that path params are strings in the URL and are converted using hints; if `hs_code: int` was used, "search" would produce a 422.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between path, query and body parameters? (Easy)
A1: Path parameters are part of the URL (`/codes/8517`), query parameters come after `?` (`?top_k=3`), and the body is JSON sent with POST/PUT. FastAPI decides by position and type: names in the path template are path params, Pydantic models are the body, simple types are query params.

Q2: How do you see API docs? (Easy)
A2: Open `/docs` for Swagger UI or `/redoc` for ReDoc. The raw schema is at `/openapi.json`.

Q3: `def` vs `async def` routes? (Medium)
A3: `async def` runs on the event loop: use it when you `await` non-blocking I/O. Plain `def` runs in a threadpool, which is safe for blocking libraries. Putting blocking code in `async def` blocks the loop and slows all requests.

Q4: How do you version and organise routes? (Medium)
A4: Use `APIRouter(prefix="/v1", tags=[...])` per feature (classification, admin, health) and `app.include_router(...)`. Versioned prefixes let you change contracts without breaking clients.

Q5: How would you make a classification endpoint idempotent and safe for client retries? (Hard)
A5: Accept an `Idempotency-Key` header, hash it with the user id, store the response in Redis with a TTL (SET NX to claim the key), and return the stored response for repeats. This stops duplicate LLM spend when mobile clients or gateways retry on timeouts. Handle the "in progress" state with a 409 or by awaiting the first result.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You expose an LLM, RAG or agent as an HTTP service
- You want automatic validation and docs
- You need async I/O and high concurrency

❌ Avoid when:
- A simple CLI or batch script is enough
- You need heavy server-rendered HTML (Django may fit better)
- The workload is a long job (use a queue and return a job id)

---

## 📊 Visual Diagram
```
 Client ── POST /v1/classify {"description": "..."} ──►
                                                       │
   ┌──────────────────── FastAPI ──────────────────────▼───────┐
   │ router match → parse+validate (Pydantic) → handler(async)  │
   │                    │422 if invalid            │             │
   │                    ▼                          ▼             │
   │              error JSON                 service → LLM       │
   │                                                │            │
   │ response_model filter ◄────────────────────────┘            │
   └───────────────────────── 200 JSON ─────────────────────────┘
```

---

## 💰 Cost Impact
Routes decide how many tokens users can spend. Enforce `max_length` on inputs (2,000 characters is about 500 tokens), set `max_tokens` on outputs, add rate limits per user, and cache repeated requests. Validation errors (422) cost zero tokens because they stop before the LLM, so strict models save money. Example: blocking 3 percent junk requests (empty or huge) at validation on 100K daily calls saves 3K calls, roughly 2M tokens a day.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Route | URL + method mapped to function | URL + method का function से जोड़ |
| Path parameter | Value inside URL path | URL path में value |
| Query parameter | Value after `?` | `?` के बाद की value |
| Request body | JSON data sent by client | client का भेजा JSON |
| 422 | Validation error status | validation error status |
| APIRouter | Group of routes | routes का समूह |
| response_model | Output schema filter | output schema filter |
| OpenAPI | Standard API description | API का standard description |

---

## ⚡ 3-Line Summary
English: A route maps method + URL to a function, and FastAPI uses type hints to validate input and build docs. Use `async def` for non-blocking I/O, keep routes thin, and bound inputs to control tokens. Group routes with `APIRouter`.
Hindi: Route method + URL को function से जोड़ता है, और FastAPI type hints से input validate और docs बनाता है। Non-blocking I/O के लिए `async def` लो, routes पतले रखो, और tokens नियंत्रित करने के लिए input सीमित करो। Routes को `APIRouter` से group करो।

---

## ➡️ Next Topic
**008. FastAPI Pydantic Models** — next we look closely at the request/response models that validate everything entering and leaving our routes.
