---

# 328. Tags + Metadata
# हिंदी में: Tags + Metadata (docs को व्यवस्थित और समझने लायक बनाना)

---

## 🔵 Simple Definition (English)
Tags group endpoints in the Swagger docs; metadata (title, description, version, summary, deprecated, operation id) describes the API and each route. FastAPI puts all of this into the OpenAPI schema automatically.

## 🔵 सरल परिभाषा (Hindi)
Tags Swagger docs में endpoints को group करते हैं; metadata (title, description, version, summary, deprecated, operation id) API और हर route को समझाता है। FastAPI यह सब अपने आप OpenAPI schema में डालता है।

---

## 🔴 Problem it Solves
With 100 endpoints, an unsorted Swagger page is useless for frontend developers and partners. They need grouping, short titles, descriptions, warnings for deprecated routes, and stable operation ids so generated SDKs have clean method names.

## 🔴 यह क्यों बना? (Hindi)
100 endpoints हों तो बिना क्रम का Swagger page frontend developers और partners के लिए बेकार है। उन्हें grouping, छोटे titles, descriptions, deprecated routes की चेतावनी और स्थिर operation ids चाहिए ताकि generated SDKs के method names साफ़ रहें।

---

## 🟢 How it Works — Step by Step

```
Step 1 → App metadata: `FastAPI(title=, description=, version=, contact=, license_info=)`
Step 2 → Route metadata: `tags=`, `summary=`, `description=` (or the docstring), `deprecated=True`
Step 3 → Tag descriptions/order: `openapi_tags=[{name, description}]`
Step 4 → Router tags: `APIRouter(tags=[...])` merge with route and include tags
Step 5 → `generate_unique_id_function` / `operation_id` control SDK method names
Step 6 → `include_in_schema=False` hides a route from docs (still callable)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → App metadata: `FastAPI(title=, description=, version=, contact=, license_info=)`
Step 2 → Route metadata: `tags=`, `summary=`, `description=` (या docstring), `deprecated=True`
Step 3 → Tag description/क्रम: `openapi_tags=[{name, description}]`
Step 4 → Router tags, route और include के tags से merge होते हैं
Step 5 → `generate_unique_id_function` / `operation_id` SDK के method names तय करते हैं
Step 6 → `include_in_schema=False` route को docs से छुपाता है (फिर भी call हो सकता है)
```

---

## 🟡 Real World Example
A Stripe-like public API groups docs as Payments, Refunds, Customers, with Markdown descriptions and links to guides. The mobile team generates a Kotlin client from `/openapi.json`; stable operation ids like `payments_create_payment` give clean method names. Old `/v1` routes are marked deprecated.

## 🟡 Real Example Hindi mein
Stripe जैसी public API docs को Payments, Refunds, Customers में group करती है, Markdown descriptions और guides के links के साथ। Mobile team `/openapi.json` से Kotlin client generate करती है; `payments_create_payment` जैसी स्थिर operation ids साफ़ method names देती हैं। पुराने `/v1` routes deprecated दिखते हैं।

---

## 💻 Code Example — Basic
App info and route info appear in the generated OpenAPI schema.

```python
# Basic tags + metadata - every line commented
from fastapi import FastAPI  # app
from fastapi.testclient import TestClient  # client

app: FastAPI = FastAPI(  # app-level metadata
    title="Shop API",  # shown at top of /docs
    description="Orders and users for the shop.",  # supports Markdown
    version="1.2.0",  # API version (not the Python version)
)


@app.get(  # route with docs metadata
    "/items",  # path
    tags=["items"],  # groups the route in /docs
    summary="List items",  # short title
    description="Returns all items.",  # long text
)
def items() -> list[str]:  # handler
    """Docstring is used as description if you skip description=."""
    return ["pen"]  # data


schema: dict = TestClient(app).get("/openapi.json").json()  # the generated schema
print(schema["info"]["title"], schema["info"]["version"])  # app metadata
# Output: Shop API 1.2.0
op: dict = schema["paths"]["/items"]["get"]  # operation object
print(op["tags"], op["summary"])  # route metadata
# Output: ['items'] List items
```

## 💻 Code Example — Advanced
Tag descriptions and order, enum tags, custom operation ids, deprecated and hidden routes.

```python
# Production style: tag descriptions, Enum tags, deprecated, hidden routes, operation ids
from enum import Enum  # tags as constants
from fastapi import FastAPI  # app
from fastapi.routing import APIRoute  # for custom operation ids
from fastapi.testclient import TestClient  # client


class Tags(str, Enum):  # constants stop typos in tag names
    users = "users"  # tag value
    orders = "orders"  # tag value


TAGS_METADATA: list[dict] = [  # ordering + descriptions in /docs
    {"name": "users", "description": "Account operations."},  # users group
    {"name": "orders", "description": "Order lifecycle.", "externalDocs": {"description": "Guide", "url": "https://example.com/guide"}},  # orders group
]


def make_id(route: APIRoute) -> str:  # stable operationId for client generators
    tag: str = str(route.tags[0].value if route.tags else "default")  # enum -> str
    return f"{tag}_{route.name}"  # e.g. users_list_users


app: FastAPI = FastAPI(
    title="Shop API", openapi_tags=TAGS_METADATA, generate_unique_id_function=make_id,  # use metadata and id function
)


@app.get("/users", tags=[Tags.users])  # enum tag
def list_users() -> list[str]:  # handler
    return ["asha"]  # data


@app.get("/old", tags=[Tags.orders], deprecated=True)  # marked deprecated in docs
def old_orders() -> list[int]:  # handler
    return [1]  # data


@app.get("/internal", include_in_schema=False)  # hidden from docs but still works
def internal() -> dict[str, bool]:  # handler
    return {"ok": True}  # data


client: TestClient = TestClient(app)  # client
schema: dict = client.get("/openapi.json").json()  # schema
print([t["name"] for t in schema["tags"]])  # tag order
# Output: ['users', 'orders']
print(schema["paths"]["/users"]["get"]["operationId"])  # custom id
# Output: users_list_users
print(schema["paths"]["/old"]["get"]["deprecated"], "/internal" in schema["paths"])  # flags
# Output: True False
print(client.get("/internal").json())  # hidden route still callable
# Output: {'ok': True}
```

---

## 🟠 JavaScript vs Python Comparison

```python
app = FastAPI(title="Shop API", version="1.2.0")

@app.get("/items", tags=["items"], summary="List items")
def items(): ...
```

```javascript
// Express + swagger-jsdoc comments (manual)
/**
 * @openapi
 * /items:
 *   get:
 *     tags: [items]
 *     summary: List items
 */
app.get('/items', listItems);
```

In Express you hand-write OpenAPI in comments or YAML and keep it in sync yourself. FastAPI generates it from your code, so metadata is just keyword arguments and the docs cannot drift from the real routes.

---

## 🟠 FastAPI Connection
Use an `Enum` for tags to avoid typos, set `openapi_tags` for descriptions and order, and customize `generate_unique_id_function` before generating client SDKs (openapi-generator, openapi-typescript). Docstrings become Markdown descriptions; text after `\f` is cut from docs.

```python
from fastapi import FastAPI

app: FastAPI = FastAPI(
    title="Shop API",
    summary="Orders and users",
    description="## Shop\nPublic API for the **Shop** apps.",
    version="2.0.0",
    contact={"name": "API Team", "email": "api@shop.example"},
    license_info={"name": "MIT"},
    openapi_tags=[{"name": "orders", "description": "Order lifecycle"}],
)


@app.get("/orders", tags=["orders"], summary="List orders")
def orders() -> list[int]:
    """Return order ids.\n\nSupports **Markdown** in the docstring."""
    return [1, 2]
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Typos in tag names
```python
@app.get('/a', tags=['user'])
@app.get('/b', tags=['users'])  # two groups
```
✅ Correct:
```python
class Tags(str, Enum): users = 'users'
@app.get('/a', tags=[Tags.users])
```

❌ Mistake 2: Deleting a route instead of deprecating
```python
# remove /old -> clients break overnight
```
✅ Correct:
```python
@app.get('/old', deprecated=True)  # warn first, remove later
```

❌ Mistake 3: Using `include_in_schema=False` as security
```python
@app.get('/admin-secret', include_in_schema=False)  # still public!
```
✅ Correct:
```python
# add authentication; hiding from docs only hides it from docs
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
from fastapi import APIRouter, FastAPI

router = APIRouter(tags=["router-tag"])

@router.get("/x", tags=["route-tag"])
def x():
    return 1

app = FastAPI()
app.include_router(router, tags=["include-tag"])
print(app.openapi()["paths"]["/x"]["get"]["tags"])
```

**Answer**:
```
['include-tag', 'router-tag', 'route-tag']
```
Tags are merged, not replaced. The order is: tags passed to `include_router` first, then the router's own tags, then the route's tags. Swagger will show the endpoint under all three groups.

---

## ⚫ Interview Questions + Answers

Q1: What do tags do?
A1: They group endpoints in Swagger/ReDoc and are used by SDK generators to organize clients.

Q2: How do I control tag order/descriptions?
A2: Pass `openapi_tags=[{...}]` to `FastAPI`; the list order sets the display order.

Q3: What is operationId and why care?
A3: A unique id per operation. Generators use it for method names. Default is like `read_item_items__id__get`; override with `operation_id=` or `generate_unique_id_function`.

Q4: How to mark a route deprecated?
A4: `@app.get('/x', deprecated=True)`. It stays callable but is struck through in docs.

Q5: How do I hide an endpoint from docs?
A5: `include_in_schema=False`. It is still reachable, so it is not a security feature.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Public or partner APIs
- Teams generating SDKs/clients
- Large APIs needing grouped docs

❌ Avoid when:
- Relying on hiding as security
- Changing operation ids after clients are generated
- Putting secrets in descriptions

---

## 📊 Visual Diagram

```
FastAPI(title, version, openapi_tags)  --->  info + tags[]
@app.get(tags, summary, deprecated)    --->  paths./x.get{tags, summary, operationId, deprecated}
                  |
                  v
          /openapi.json  --->  Swagger UI (/docs) , ReDoc (/redoc) , SDK generators
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Tag | Group label in docs | docs में group का नाम |
| Summary | Short route title | route का छोटा शीर्षक |
| operationId | Unique operation name | operation का unique नाम |
| Deprecated | Still works, avoid using | चलता है पर इस्तेमाल न करें |
| Metadata | Data about the API | API के बारे में जानकारी |
| include_in_schema | Show/hide in docs | docs में दिखाना/छुपाना |

---

## ⚡ 3-Line Summary
English: Tags group endpoints; title, version, summary and descriptions document them; `deprecated` and `operation_id` help clients. All of it flows into `/openapi.json` automatically. Hiding from docs is not security.
Hindi: Tags endpoints को group करते हैं; title, version, summary और descriptions उन्हें समझाते हैं; `deprecated` और `operation_id` clients की मदद करते हैं। यह सब अपने आप `/openapi.json` में जाता है। Docs से छुपाना security नहीं है।

---

## ➡️ Next Topic
**329. OpenAPI + Swagger Docs** — how the schema and the interactive docs are produced and customized.

---

**Verification note:** Every code block was run with FastAPI 0.162.4, Starlette 1.10.0, Python 3.13.3 using TestClient / httpx (no real browser). The Output comments are the real printed output. Explanation about SDK generators is general knowledge (no generator was run).
