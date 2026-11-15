---

# 329. OpenAPI + Swagger Docs
# हिंदी में: OpenAPI + Swagger Docs (अपने आप बनने वाली API documentation)

---

## 🔵 Simple Definition (English)
OpenAPI is a standard JSON description of your API (paths, parameters, bodies, responses). FastAPI builds it automatically from your type hints and Pydantic models and serves it at `/openapi.json`, with interactive Swagger UI at `/docs` and ReDoc at `/redoc`.

## 🔵 सरल परिभाषा (Hindi)
OpenAPI आपकी API का standard JSON विवरण है (paths, parameters, bodies, responses)। FastAPI इसे आपके type hints और Pydantic models से अपने आप बनाता है और `/openapi.json` पर देता है; interactive Swagger UI `/docs` पर और ReDoc `/redoc` पर मिलता है।

---

## 🔴 Problem it Solves
Hand-written API docs go stale and testing needs Postman collections. With OpenAPI, the docs are always in sync with the code, you can try endpoints in the browser, and tools can generate client code, tests and mocks from the one schema.

## 🔴 यह क्यों बना? (Hindi)
हाथ से लिखे API docs पुराने हो जाते हैं और testing के लिए Postman collections चाहिए। OpenAPI से docs हमेशा code से मेल खाते हैं, endpoints browser में आज़माए जा सकते हैं, और एक ही schema से client code, tests और mocks बन सकते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You write routes with type hints and Pydantic models
Step 2 → FastAPI inspects them at startup and builds the OpenAPI dict (cached after first call)
Step 3 → `GET /openapi.json` returns it
Step 4 → `/docs` loads Swagger UI, which reads that JSON and renders a try-it-out UI
Step 5 → `/redoc` renders the same schema as read-only docs
Step 6 → Tools (openapi-generator, Postman, Schemathesis) import the JSON
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप type hints और Pydantic models के साथ routes लिखते हैं
Step 2 → FastAPI startup पर उन्हें जाँचकर OpenAPI dict बनाता है (पहली बार के बाद cache होता है)
Step 3 → `GET /openapi.json` वही लौटाता है
Step 4 → `/docs` Swagger UI खोलता है जो वह JSON पढ़कर try-it-out UI दिखाता है
Step 5 → `/redoc` उसी schema को read-only docs की तरह दिखाता है
Step 6 → Tools (openapi-generator, Postman, Schemathesis) JSON import करते हैं
```

---

## 🟡 Real World Example
A backend team shares `/docs` with the frontend team, who test calls with an auth token directly in Swagger UI. QA runs Schemathesis against `/openapi.json` to fuzz every endpoint. In production the docs are disabled for public internet or put behind login.

## 🟡 Real Example Hindi mein
Backend team `/docs` frontend team से साझा करती है, जो Swagger UI में ही auth token लगाकर calls आज़माती है। QA `/openapi.json` पर Schemathesis चलाकर हर endpoint को fuzz करती है। Production में public internet के लिए docs बंद या login के पीछे रखे जाते हैं।

---

## 💻 Code Example — Basic
The three built-in URLs and what the schema contains.

```python
# Basic OpenAPI / Swagger - every line commented
from fastapi import FastAPI  # app
from fastapi.testclient import TestClient  # client
from pydantic import BaseModel  # request model


class Item(BaseModel):  # request body model
    name: str  # required string
    price: float = 0.0  # optional float


app: FastAPI = FastAPI(title="Demo")  # app


@app.post("/items")  # route
def create(item: Item) -> Item:  # request + response model
    return item  # echo


client: TestClient = TestClient(app)  # client
print(client.get("/docs").status_code, client.get("/redoc").status_code, client.get("/openapi.json").status_code)  # 3 built-in URLs
# Output: 200 200 200
schema: dict = client.get("/openapi.json").json()  # fetch schema
print(schema["openapi"][:1], list(schema["paths"]))  # OpenAPI 3.x
# Output: 3 ['/items']
print(schema["components"]["schemas"]["Item"]["required"])  # derived from the type hints
# Output: ['name']
```

## 💻 Code Example — Advanced
Custom docs URLs, docs disabled in prod, documented extra responses and field examples.

```python
# Production style: hide docs in prod, custom docs urls, extra responses, examples, custom schema tweak
import os  # env
from fastapi import FastAPI  # app
from fastapi.testclient import TestClient  # client
from pydantic import BaseModel, Field  # model


ENV: str = os.getenv("APP_ENV", "dev")  # dev or prod
IS_PROD: bool = ENV == "prod"  # flag


class Payment(BaseModel):  # request model with examples
    amount: int = Field(gt=0, description="Amount in paise", examples=[49900])  # field docs
    upi_id: str = Field(examples=["asha@upi"])  # field docs


app: FastAPI = FastAPI(
    title="Pay API",  # title
    docs_url=None if IS_PROD else "/swagger",  # custom Swagger URL, off in prod
    redoc_url=None,  # disable ReDoc
    openapi_url=None if IS_PROD else "/api/openapi.json",  # off in prod
)


@app.post("/pay", responses={402: {"description": "Payment failed"}, 409: {"description": "Duplicate"}})  # document extra codes
def pay(p: Payment) -> dict[str, str]:  # handler
    return {"status": "paid"}  # data


client: TestClient = TestClient(app)  # client
print(client.get("/swagger").status_code, client.get("/docs").status_code)  # custom URL works, default gone
# Output: 200 404
schema: dict = client.get("/api/openapi.json").json()  # schema at custom path
print(sorted(schema["paths"]["/pay"]["post"]["responses"]))  # codes documented
# Output: ['200', '402', '409', '422']
print(schema["components"]["schemas"]["Payment"]["properties"]["amount"])  # field docs in schema
# Output: {'type': 'integer', 'exclusiveMinimum': 0.0, 'title': 'Amount', 'description': 'Amount in paise', 'examples': [49900]}
```

---

## 🟠 JavaScript vs Python Comparison

```python
app = FastAPI()          # /docs and /openapi.json exist automatically
# Disable in prod:
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
```

```javascript
// Express: wire it manually
const swaggerUi = require('swagger-ui-express');
const spec = require('./openapi.json');   // written/maintained by hand
app.use('/docs', swaggerUi.serve, swaggerUi.setup(spec));
```

In Express you maintain the OpenAPI spec yourself and mount Swagger UI. FastAPI generates the spec from code with zero setup, so the biggest difference is that the docs are always correct and free.

---

## 🟠 FastAPI Connection
Document errors with `responses=`, give examples with `Field(examples=[...])` or `model_config['json_schema_extra']`, and set `response_model` so the response schema is accurate. To add an auth button in Swagger, use security schemes (`OAuth2PasswordBearer`, `HTTPBearer`, `APIKeyHeader`). Never expose internal admin APIs in the public schema.

```python
from fastapi import FastAPI, Depends
from fastapi.security import HTTPBearer

bearer: HTTPBearer = HTTPBearer()  # adds the 'Authorize' button in /docs
app: FastAPI = FastAPI(title="Pay API", swagger_ui_parameters={"persistAuthorization": True})


@app.get("/me")
def me(creds=Depends(bearer)) -> dict[str, str]:
    return {"token_prefix": creds.credentials[:4]}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Leaving docs open in production
```python
app = FastAPI()  # /docs public on the internet
```
✅ Correct:
```python
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)  # or protect behind auth
```

❌ Mistake 2: No `response_model` / return type
```python
@app.get('/u')
def u(): return db_user  # schema says 'any'
```
✅ Correct:
```python
@app.get('/u')
def u() -> UserOut: return db_user  # exact schema
```

❌ Mistake 3: Expecting docs to show undocumented errors
```python
raise HTTPException(409)  # not in docs
```
✅ Correct:
```python
@app.post('/x', responses={409: {'description': 'Duplicate'}})
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI(docs_url=None, redoc_url=None)
c = TestClient(app)
print(c.get("/docs").status_code, c.get("/openapi.json").status_code)
app2 = FastAPI(openapi_url=None)
c2 = TestClient(app2)
print(c2.get("/docs").status_code, c2.get("/openapi.json").status_code)
```

**Answer**:
```
404 200
404 404
```
`docs_url=None` and `redoc_url=None` remove only the UI pages; `/openapi.json` remains. `openapi_url=None` removes the schema, and since the UI pages need the schema they are not added either, so `/docs` also gives 404.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between OpenAPI and Swagger?
A1: OpenAPI is the specification (formerly called Swagger spec). Swagger UI is one tool that renders it; ReDoc is another.

Q2: How does FastAPI know my types?
A2: It reads function signatures/annotations and Pydantic models, and converts them to JSON Schema inside the OpenAPI document.

Q3: How do I hide docs in production?
A3: Set `docs_url=None, redoc_url=None, openapi_url=None` based on an environment variable, or protect them with authentication.

Q4: How can I customize the schema?
A4: Use `responses`, `Field(examples=...)`, `json_schema_extra`, or override `app.openapi` to edit the dict (cache it).

Q5: How do I generate a client?
A5: Download `/openapi.json` and run a generator such as openapi-generator or openapi-typescript; set unique operation ids first.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Every API: it is free and always accurate
- Frontend/partner collaboration
- Contract tests and client generation

❌ Avoid when:
- Exposing docs publicly for private/internal APIs
- Documenting by hand beside generated docs
- Huge example payloads with real data

---

## 📊 Visual Diagram

```
type hints + Pydantic models
        |
        v   (startup / first call)
   app.openapi()  ---> /openapi.json (JSON Schema inside)
        |                  |
        v                  v
   /docs (Swagger UI)   /redoc        generators, Postman, Schemathesis
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| OpenAPI | API description standard | API विवरण का मानक |
| Swagger UI | Interactive docs page | आज़माने लायक docs page |
| ReDoc | Read-only docs page | सिर्फ़ पढ़ने वाला docs page |
| JSON Schema | Describes data shape | data का आकार बताता है |
| Security scheme | Auth definition in docs | docs में auth की परिभाषा |
| Schemathesis | Property-based API tester | OpenAPI से API test करने वाला tool |

---

## ⚡ 3-Line Summary
English: FastAPI turns type hints and models into an OpenAPI schema at `/openapi.json`, with Swagger UI at `/docs` and ReDoc at `/redoc`. Document extra responses and examples, and disable or protect docs in production.
Hindi: FastAPI type hints और models को `/openapi.json` पर OpenAPI schema बनाता है, `/docs` पर Swagger UI और `/redoc` पर ReDoc के साथ। अतिरिक्त responses और examples document करें, और production में docs बंद या सुरक्षित रखें।

---

## ➡️ Next Topic
**330. Async in FastAPI** — when to use `async def` vs `def` and how to avoid blocking the event loop.

---

**Verification note:** Every code block was run with FastAPI 0.162.4, Starlette 1.10.0, Python 3.13.3 using TestClient / httpx (no real browser). The Output comments are the real printed output. `fa_code` Authorize-button snippet was not run; generators/Postman/Schemathesis were not run.
