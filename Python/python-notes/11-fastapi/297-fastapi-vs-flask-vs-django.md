---

# 297. FastAPI vs Flask vs Django
# हिंदी में: FastAPI बनाम Flask बनाम Django

---

## 🔵 Simple Definition (English)
Django is a "batteries included" full framework (ORM, admin, auth, templates). Flask is a small, flexible micro-framework where you add pieces yourself. FastAPI is a modern framework focused on APIs: it uses type hints for validation, generates docs automatically and supports `async` natively.

## 🔵 सरल परिभाषा (Hindi)
Django एक "सब कुछ साथ में" वाला पूरा framework है (ORM, admin, auth, templates)। Flask एक छोटा, लचीला micro-framework है जिसमें बाकी चीज़ें आप खुद जोड़ते हैं। FastAPI एक आधुनिक framework है जो APIs पर केंद्रित है: type hints से validation करता है, docs अपने-आप बनाता है और `async` को natively support करता है।

---

## 🔴 Problem it Solves
Choosing the wrong framework costs months. Django is heavy for a small JSON API. Flask has no validation, so each team writes its own, and its async support is limited. FastAPI was created to give Flask's simplicity with automatic validation, OpenAPI docs and high concurrency, which suits microservices and AI backends.

## 🔴 यह क्यों बना? (Hindi)
गलत framework चुनने से महीनों बर्बाद होते हैं। छोटे JSON API के लिए Django भारी है। Flask में validation नहीं है, इसलिए हर team अपना लिखती है, और async support सीमित है। FastAPI इसलिए बना कि Flask जैसी सादगी के साथ automatic validation, OpenAPI docs और ज़्यादा concurrency मिले, जो microservices और AI backends के लिए ठीक है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Django: URLconf -> view -> ORM -> template/serializer (sync, WSGI; ASGI optional)
Step 2 → Flask : route decorator -> view function -> you add DB, validation, auth (WSGI)
Step 3 → FastAPI: route decorator -> type hints parsed -> Pydantic validates -> your function
Step 4 → FastAPI builds OpenAPI JSON from the hints, so /docs needs no extra work
Step 5 → FastAPI runs on ASGI (uvicorn): async def handlers share one event loop
Step 6 → Pick by need: full site + admin = Django; tiny/simple = Flask; API/AI/async = FastAPI
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Django: URLconf -> view -> ORM -> template/serializer (sync, WSGI; ASGI वैकल्पिक)
Step 2 → Flask : route decorator -> view function -> DB, validation, auth आप खुद जोड़ते हैं (WSGI)
Step 3 → FastAPI: route decorator -> type hints पढ़े जाते हैं -> Pydantic validate करता है -> आपका function
Step 4 → FastAPI hints से OpenAPI JSON बनाता है, इसलिए /docs के लिए अलग काम नहीं
Step 5 → FastAPI ASGI (uvicorn) पर चलता है: async def handlers एक event loop साझा करते हैं
Step 6 → ज़रूरत से चुनें: पूरी site + admin = Django; छोटा/सरल = Flask; API/AI/async = FastAPI
```

---

## 🟡 Real World Example
An Indian fintech: the internal admin panel and customer database screens use Django (its admin saves months). The payment webhook receiver is a small Flask service written years ago. The new AI chatbot backend that streams LLM tokens and calls many external APIs concurrently is FastAPI, because async and Pydantic models fit it perfectly.

## 🟡 Real Example Hindi mein
एक भारतीय fintech में: internal admin panel और customer database screens Django में हैं (उसका admin महीनों बचाता है)। Payment webhook receiver कई साल पुरानी छोटी Flask service है। नया AI chatbot backend, जो LLM tokens stream करता है और कई external APIs एक साथ बुलाता है, FastAPI में है क्योंकि async और Pydantic models उसमें बिल्कुल फिट बैठते हैं।

---

## 💻 Code Example — Basic
```python
# Basic: the SAME endpoint in Flask and FastAPI (verified: Flask 3.x, FastAPI 0.162, Python 3.13)
# pip install flask fastapi httpx pydantic
from flask import Flask, jsonify  # Flask pieces
from fastapi import FastAPI  # FastAPI
from pydantic import BaseModel  # response model
from fastapi.testclient import TestClient  # to call the app without a server

# ----- Flask version -----
flask_app: Flask = Flask(__name__)  # create Flask app


@flask_app.get("/users/<int:uid>")  # converter <int:uid> only matches digits
def f_user(uid: int):  # Flask has no real type validation of the function
    return jsonify(id=uid)  # build JSON manually


# ----- FastAPI version -----
class User(BaseModel):  # response schema, also used for docs
    id: int


app: FastAPI = FastAPI()  # create FastAPI app


@app.get("/users/{uid}")  # path parameter
def user(uid: int) -> User:  # the type hint IS the validation
    return User(id=uid)  # model is serialized to JSON


# ----- compare behaviour -----
print(flask_app.test_client().get("/users/abc").status_code)  # Flask: no route matches
# Output: 404
c: TestClient = TestClient(app)  # FastAPI test client
r = c.get("/users/abc")  # same bad input
print(r.status_code, r.json()["detail"][0]["type"])  # FastAPI explains the error
# Output: 422 int_parsing
print(c.get("/users/7").json())  # valid input
# Output: {'id': 7}
print(list(c.get("/openapi.json").json()["paths"]))  # free OpenAPI schema
# Output: ['/users/{uid}']
```

## 💻 Code Example — Advanced
```python
# Advanced: how the three differ in features - a small decision helper + FastAPI async fan-out
import asyncio  # for concurrency
from dataclasses import dataclass  # simple data holder
from typing import Literal  # restricted strings
import httpx  # async HTTP client
from fastapi import FastAPI  # framework

Need = Literal["admin_site", "simple_api", "async_ai_api"]  # types of project


@dataclass(frozen=True)  # immutable, hashable
class Verdict:  # result of the helper
    framework: str  # chosen framework
    reason: str  # one line reason


def choose(need: Need) -> Verdict:  # tiny decision function (interview talking point)
    table: dict[str, Verdict] = {  # lookup table
        "admin_site": Verdict("Django", "ORM + admin + auth + migrations built in"),
        "simple_api": Verdict("Flask", "minimal, you pick every library"),
        "async_ai_api": Verdict("FastAPI", "async, Pydantic validation, auto docs"),
    }
    return table[need]  # return matching verdict


print(choose("async_ai_api"))  # show one choice
# Output: Verdict(framework='FastAPI', reason='async, Pydantic validation, auto docs')

app: FastAPI = FastAPI()  # FastAPI strength: concurrent I/O inside a handler


@app.get("/aggregate")  # calls two services at the same time
async def aggregate() -> dict[str, int]:
    async def fake_service(name: str, delay: float) -> int:  # pretend external API
        await asyncio.sleep(delay)  # non-blocking wait
        return len(name)  # fake result

    a, b = await asyncio.gather(  # both run together: ~0.2 s total, not 0.4 s
        fake_service("pricing", 0.2), fake_service("stock", 0.2)
    )
    return {"pricing": a, "stock": b}  # {"pricing": 7, "stock": 5}

# In Django (sync views) or Flask (sync by default) the same code would call the services
# one after another, or need extra setup (async views, threads) to run them together.
```

---

## 🟠 JavaScript vs Python Comparison
Think of Express = Flask (minimal, bring your own pieces), NestJS = Django-like structure, and Fastify with schema validation (Ajv) + Swagger plugin = FastAPI.

| Feature | FastAPI | Flask | Django |
|---|---|---|---|
| Type | API framework | Micro-framework | Full-stack framework |
| Server interface | ASGI | WSGI (async limited) | WSGI + ASGI |
| Validation | Built in (Pydantic) | Add yourself | Forms / DRF serializers |
| Auto API docs | Yes (`/docs`) | No (add plugin) | No (DRF + drf-spectacular) |
| ORM | None (use SQLAlchemy) | None | Built in |
| Admin panel | No | No | Yes |
| Learning curve | Low-medium | Lowest | Highest |

```python
# Python (FastAPI)
@app.get("/hello/{name}")
async def hello(name: str) -> dict[str, str]:
    return {"hello": name}
```
```javascript
// JavaScript (Express)
app.get('/hello/:name', (req, res) => {
  res.json({ hello: req.params.name });   // no validation, no auto docs
});
```

Key differences: Express and Flask hand you raw request data. FastAPI parses and validates it from the function signature before your code runs.

---

## 🟠 FastAPI Connection
This topic IS about choosing FastAPI. Choose it when: you build JSON APIs, microservices, ML/LLM backends, or need WebSockets/streaming. FastAPI is not ideal when: you need a ready admin panel, server-rendered HTML pages with forms and sessions, or an ORM with migrations out of the box (Django gives these).

```python
# FastAPI shows its strengths in 10 lines (needs: pip install fastapi)
from fastapi import FastAPI  # framework
from pydantic import BaseModel, Field  # validation

app: FastAPI = FastAPI(title="Orders")  # title appears in /docs


class OrderIn(BaseModel):  # request body schema
    item: str = Field(min_length=1)  # validated automatically
    qty: int = Field(ge=1, le=10)  # 1..10


@app.post("/orders", status_code=201)  # validation + docs + status code in one place
def create(order: OrderIn) -> dict[str, str | int]:
    return {"item": order.item, "qty": order.qty}  # invalid body never reaches here
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Choosing by hype ("FastAPI is faster, so rewrite everything")
✅ Correct: Choose by need. Most apps are limited by the database, not the framework. Django's admin and ORM can save more time than FastAPI's speed.

```python
# Wrong: rewriting a working Django CRUD site in FastAPI and then rebuilding auth + admin
# Right: keep Django for the site, add FastAPI only for the new async/AI service
```

❌ Mistake 2: Thinking FastAPI is always async
✅ Correct: Use `def` for blocking libraries (FastAPI runs them in a threadpool) and `async def` only with async libraries.

```python
# Wrong
@app.get("/x")
async def x(): requests.get("https://example.com")   # blocks the event loop
# Right
@app.get("/x")
def x(): requests.get("https://example.com")         # runs in a thread
```

❌ Mistake 3: Expecting Flask-like "return anything"
✅ Correct: FastAPI validates and serializes the return value with the type hint or `response_model`; return dicts, models or `Response` objects.

---

## 🧠 Tricky Interview Question

**Q**: Same request `GET /users/abc` to both apps above. What status does each return and why?

```python
# Flask route: "/users/<int:uid>"
# FastAPI route: "/users/{uid}" with uid: int
# Request: GET /users/abc
```

**Answer**:
```
Flask   -> 404 (the int converter does not match "abc", so no route exists)
FastAPI -> 422 (route matches, then validation fails: type 'int_parsing')
```
In Flask, validation is part of URL matching, so a bad value looks like "page not found". In FastAPI the route matches first and then Pydantic validates the value, giving a detailed, machine readable 422 error. (Verified by running both.)

---

## ⚫ Interview Questions + Answers

Q1: Why is FastAPI considered fast?
A1: It runs on ASGI (uvicorn/uvloop) and Starlette, uses Pydantic v2 with a Rust core for validation, and handles I/O concurrently with `async`. For CPU-heavy work it is no faster than others.

Q2: What are WSGI and ASGI?
A2: WSGI is the old synchronous Python web interface (Flask, classic Django). ASGI is the async successor supporting WebSockets and long-lived connections (FastAPI, Starlette, Django 3.0+ optional).

Q3: Does FastAPI replace Django?
A3: No. Django is a full-stack framework with ORM, admin, auth and migrations. FastAPI covers the HTTP/API layer only, so you add SQLAlchemy, Alembic and auth yourself.

Q4: Can Flask do async?
A4: Flask 2+ supports `async def` views, but each request still runs in a worker thread/greenlet with WSGI, so you do not get the full concurrency of an ASGI server.

Q5: Which would you pick for an ML model serving API and why?
A5: FastAPI: Pydantic models document inputs, async handles many waiting clients, `/docs` helps frontend teams, and it streams responses easily.

---

## 🔷 When to Use + When Not to Use

✅ Use FastAPI when:
- Building JSON/REST APIs, microservices, LLM/ML backends, WebSocket or streaming features
- You want automatic validation and OpenAPI docs

✅ Use Django when:
- You need admin, auth, ORM, migrations and templates together, content sites, internal tools

✅ Use Flask when:
- A very small service or prototype, or you need full control and already know it

❌ Avoid FastAPI when:
- You want a ready admin/CMS or heavy server-side HTML rendering

---

## 📊 Visual Diagram

```
  Scope of features
  Django   ████████████████████  ORM + admin + auth + forms + templates
  FastAPI  ██████████            routing + validation + docs + async (add DB yourself)
  Flask    █████                 routing + templates (add everything else)

  Server:  Flask/Django → WSGI (gunicorn)      FastAPI → ASGI (uvicorn)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Micro-framework | Small core, you add parts | छोटा core, बाकी खुद जोड़ें |
| Batteries included | Many features built in | कई सुविधाएँ साथ में |
| WSGI | Old sync Python web standard | पुराना sync web standard |
| ASGI | Async Python web standard | async web standard |
| OpenAPI | Machine readable API description | API का मशीन-पठनीय विवरण |
| ORM | Maps DB tables to Python classes | tables को classes से जोड़ना |

---

## ⚡ 3-Line Summary
English: Django is the full-stack choice, Flask is the minimal choice, FastAPI is the modern API choice with validation, docs and async. Pick based on needs (admin and ORM vs small service vs async API), not on hype.
Hindi: Django पूरा full-stack विकल्प है, Flask न्यूनतम विकल्प है, और FastAPI validation, docs और async वाला आधुनिक API विकल्प है। चुनाव ज़रूरत (admin और ORM, छोटी service, या async API) के हिसाब से करें, hype से नहीं।

---

## ➡️ Next Topic
**298. FastAPI Performance** — what makes it fast, sync vs async handlers and how to avoid blocking the event loop.
