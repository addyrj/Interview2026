---

# 299. Installing + First App
# हिंदी में: FastAPI Install करना + पहला App

---

## 🔵 Simple Definition (English)
Installing FastAPI means creating a virtual environment, running `pip install "fastapi[standard]"`, then writing a Python file with `app = FastAPI()` and route functions decorated with `@app.get(...)`. You run it with `fastapi dev` or `uvicorn` and open `/docs` for free interactive documentation.

## 🔵 सरल परिभाषा (Hindi)
FastAPI install करने का मतलब है virtual environment बनाना, `pip install "fastapi[standard]"` चलाना, फिर एक Python file में `app = FastAPI()` और `@app.get(...)` से सजाए route functions लिखना। इसे `fastapi dev` या `uvicorn` से चलाएँ और मुफ़्त interactive documentation के लिए `/docs` खोलें।

---

## 🔴 Problem it Solves
Beginners often install packages globally, mix versions between projects, or forget the ASGI server. A clean venv + pinned install avoids "works on my machine". The first app also shows the core idea: a Python function plus a decorator becomes an HTTP endpoint with validation and docs, with almost no boilerplate.

## 🔴 यह क्यों बना? (Hindi)
Beginners अक्सर packages global install कर देते हैं, projects के बीच versions मिला देते हैं, या ASGI server भूल जाते हैं। साफ venv + pinned install से "मेरे machine पर चलता है" वाली समस्या नहीं होती। पहला app मूल विचार भी दिखाता है: Python function + decorator = validation और docs वाला HTTP endpoint, लगभग बिना boilerplate के।

---

## 🟢 How it Works — Step by Step

```
Step 1 → python3 -m venv .venv && source .venv/bin/activate
Step 2 → pip install "fastapi[standard]"   (adds uvicorn, httpx, CLI, jinja2 ...)
Step 3 → Create main.py: app = FastAPI(); @app.get("/") def root(): ...
Step 4 → Run: fastapi dev main.py   (auto reload)  or  uvicorn main:app --reload
Step 5 → Open http://127.0.0.1:8000/       -> JSON response
Step 6 → Open http://127.0.0.1:8000/docs   -> Swagger UI, /redoc -> ReDoc
Step 7 → /openapi.json is the machine readable schema generated from your code
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → python3 -m venv .venv && source .venv/bin/activate
Step 2 → pip install "fastapi[standard]"   (uvicorn, httpx, CLI, jinja2 ... भी आते हैं)
Step 3 → main.py बनाएँ: app = FastAPI(); @app.get("/") def root(): ...
Step 4 → चलाएँ: fastapi dev main.py   (auto reload)  या  uvicorn main:app --reload
Step 5 → http://127.0.0.1:8000/ खोलें       -> JSON response
Step 6 → http://127.0.0.1:8000/docs खोलें   -> Swagger UI, /redoc -> ReDoc
Step 7 → /openapi.json आपके code से बना machine-readable schema है
```

---

## 🟡 Real World Example
A startup builds a "Zomato Lite" backend. Day 1: one file `main.py` with `/health` and `/restaurants`. The frontend developer opens `/docs` and tests endpoints without Postman. The DevOps engineer uses `/health` in the Kubernetes liveness probe. Later the file is split into routers, but the first app pattern stays the same.

## 🟡 Real Example Hindi mein
एक startup "Zomato Lite" backend बनाता है। पहले दिन एक file `main.py` में `/health` और `/restaurants` होते हैं। Frontend developer `/docs` खोलकर बिना Postman के endpoints test करता है। DevOps engineer `/health` को Kubernetes liveness probe में इस्तेमाल करता है। बाद में file routers में बँट जाती है, पर पहले app का pattern वही रहता है।

---

## 💻 Code Example — Basic
```python
# Basic first app (verified: fastapi 0.162, Python 3.13). Save as main.py
# Install first:  pip install "fastapi[standard]"
from fastapi import FastAPI  # import the framework class
from fastapi.testclient import TestClient  # lets us call the app without starting a server

app: FastAPI = FastAPI(title="Zomato Lite", version="1.0.0")  # create the application object


@app.get("/")  # register GET / -> this function
def root() -> dict[str, str]:  # return type hint documents the response
    return {"message": "Hello FastAPI"}  # dict is converted to JSON automatically


@app.get("/health")  # health check used by load balancers / Kubernetes
async def health() -> dict[str, str]:  # async def is allowed too
    return {"status": "ok"}  # simple JSON body


# ---- calling the app in-process (same as a browser would, but no server) ----
c: TestClient = TestClient(app)  # create a test client for the app
r = c.get("/")  # send GET /
print(r.status_code, r.json(), r.headers["content-type"])  # status, body, content type
# Output: 200 {'message': 'Hello FastAPI'} application/json
print(c.get("/health").json())  # call the async endpoint
# Output: {'status': 'ok'}
print(c.get("/nope").status_code, c.get("/nope").json())  # unknown path
# Output: 404 {'detail': 'Not Found'}
print(c.post("/").status_code, c.post("/").json())  # wrong HTTP method
# Output: 405 {'detail': 'Method Not Allowed'}
print(c.get("/docs").status_code, c.get("/openapi.json").json()["info"])  # free docs
# Output: 200 {'title': 'Zomato Lite', 'version': '1.0.0'}
print(sorted(app.openapi()["paths"]))  # all documented paths
# Output: ['/', '/health']

# To run for real:   fastapi dev main.py      -> http://127.0.0.1:8000/docs
#                    uvicorn main:app --reload
```

## 💻 Code Example — Advanced
```python
# Production-style skeleton: lifespan, router, health, run from Python
# pip install "fastapi[standard]"
from contextlib import asynccontextmanager  # for startup/shutdown handling
from typing import AsyncIterator  # lifespan return type
import logging  # standard logging

from fastapi import APIRouter, FastAPI  # app + router
from fastapi.testclient import TestClient  # to verify here

log: logging.Logger = logging.getLogger("app")  # module logger


@asynccontextmanager  # code before yield = startup, after = shutdown
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.started = True  # e.g. open DB pool, load ML model here
    log.info("startup complete")  # log startup
    yield  # the app serves requests now
    log.info("shutdown complete")  # close resources here


app: FastAPI = FastAPI(  # main application object
    title="Zomato Lite",  # shown in /docs
    version="1.0.0",  # API version
    lifespan=lifespan,  # attach startup/shutdown
    docs_url="/docs",  # Swagger UI path (set None to hide in prod if needed)
)

router: APIRouter = APIRouter(prefix="/api/v1", tags=["restaurants"])  # groups routes


@router.get("/restaurants")  # becomes GET /api/v1/restaurants
def list_restaurants() -> list[dict[str, str | int]]:
    return [{"id": 1, "name": "Biryani House"}, {"id": 2, "name": "Dosa Corner"}]  # fake data


app.include_router(router)  # mount the router on the app


@app.get("/health", tags=["ops"])  # operational endpoint
def health() -> dict[str, bool]:
    return {"started": bool(app.state.started)}  # proves lifespan ran


if __name__ == "__main__":  # allow: python main.py
    import uvicorn  # ASGI server

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)  # start server

# Verified with TestClient (use "with" so the lifespan runs):
# with TestClient(app) as c:
#     c.get("/health").json()                -> {'started': True}
#     c.get("/api/v1/restaurants").json()[0] -> {'id': 1, 'name': 'Biryani House'}
```

---

## 🟠 JavaScript vs Python Comparison
The first FastAPI app is very close to an Express app. Decorators play the role of `app.get(path, handler)`.

```python
# Python (FastAPI)
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello"}      # auto JSON
# run: fastapi dev main.py  (port 8000)
```
```javascript
// JavaScript (Express)
const express = require('express');
const app = express();

app.get('/', (req, res) => {
  res.json({ message: 'Hello' });    // explicit res.json
});
app.listen(8000);                    // you start the server in code
// run: node server.js  (nodemon for reload)
```

Key differences: FastAPI returns values instead of calling `res.json`. The server (uvicorn) is a separate process, like running Node behind a process manager. `/docs` is generated for free; Express needs swagger packages.

---

## 🟠 FastAPI Connection
This topic is the foundation of every FastAPI project. Everything later (path params, query params, bodies, dependencies, auth) is added to this same `app` object and decorated functions.

```python
# FastAPI: virtual environment commands (shell, not Python)
# python3 -m venv .venv
# source .venv/bin/activate            (Windows: .venv\Scripts\activate)
# pip install "fastapi[standard]"      (quotes needed in zsh)
# pip freeze > requirements.txt        (pin versions)
# fastapi dev main.py                  (development, auto reload)
# fastapi run main.py                  (production style, no reload)
from fastapi import FastAPI  # the only import needed for a first app

app: FastAPI = FastAPI()  # object name must match "main:app" in uvicorn


@app.get("/ping")  # route
def ping() -> dict[str, str]:  # handler
    return {"ping": "pong"}  # response
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Installing only `fastapi` and then wondering how to run it
✅ Correct: FastAPI is a framework, not a server. Install `"fastapi[standard]"` (includes uvicorn and the CLI) or `pip install fastapi uvicorn`.

```python
# Wrong
# pip install fastapi         ->  "uvicorn: command not found"
# Right
# pip install "fastapi[standard]"
```

❌ Mistake 2: Wrong module path in the run command
✅ Correct: `uvicorn <file>:<variable>`. File `main.py` with `app = FastAPI()` is `main:app`.

```python
# Wrong: uvicorn main:application   (no such variable) / uvicorn main.py:app
# Right: uvicorn main:app --reload
```

❌ Mistake 3: Naming your file `fastapi.py` or running without a venv
✅ Correct: A file named `fastapi.py` shadows the real package and imports fail. Always use a venv and a different file name like `main.py`.

---

## 🧠 Tricky Interview Question

**Q**: What does each of these requests return?

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient
app = FastAPI()

@app.get("/")
def root(): return {"message": "Hello FastAPI"}

c = TestClient(app)
print(c.get("/nope").status_code)
print(c.post("/").status_code)
print(c.get("/").headers["content-type"])
print(c.get("/openapi.json").status_code)
```

**Answer**:
```
404
405
application/json
200
```
Unknown path gives 404. A known path with the wrong method gives 405 (not 404), because the route exists. The dict becomes `application/json`. The OpenAPI schema is served automatically at `/openapi.json`.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between FastAPI and uvicorn?
A1: FastAPI is the application framework (routes, validation). Uvicorn is the ASGI server that listens on a port and calls the app. You need both.

Q2: What does `fastapi dev` do?
A2: It is the FastAPI CLI (from `fastapi[standard]`). It runs your app with auto reload for development. `fastapi run` is the production mode without reload.

Q3: Where are the automatic docs?
A3: Swagger UI at `/docs`, ReDoc at `/redoc`, raw schema at `/openapi.json`. You can change or disable them with `docs_url`, `redoc_url`, `openapi_url`.

Q4: Why use `TestClient` as a context manager (`with TestClient(app) as c`)?
A4: The `with` block runs the lifespan startup and shutdown events. Without it, startup code does not run.

Q5: Should handlers be `def` or `async def`?
A5: `async def` if you use `await` with async libraries; otherwise `def` (FastAPI runs it in a threadpool). See topic 298.

---

## 🔷 When to Use + When Not to Use

✅ Use `fastapi dev` / `--reload` when:
- Developing locally and you want automatic restarts

❌ Avoid `--reload` when:
- Running in production or load testing (it adds a file watcher and runs one process)
- Inside Docker for prod images (use `fastapi run` or `uvicorn --workers`)

---

## 📊 Visual Diagram

```
 Browser / curl / frontend
        │  HTTP request  GET /health
        ▼
   uvicorn (ASGI server, port 8000)
        │
        ▼
   app = FastAPI()  ── route table ──►  health()  ──► {"status": "ok"}
        │
        ├── /docs          Swagger UI
        ├── /redoc         ReDoc
        └── /openapi.json  schema generated from type hints
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| venv | Isolated Python environment | अलग Python वातावरण |
| uvicorn | ASGI server that runs the app | app चलाने वाला server |
| Route / endpoint | URL + method + function | URL + method + function |
| Decorator | `@app.get` registers a function | function को register करने वाला |
| Swagger UI | Interactive API docs page | interactive API docs |
| Lifespan | Startup and shutdown code | शुरू और बंद होने का code |

---

## ⚡ 3-Line Summary
English: Create a venv, install `"fastapi[standard]"`, write `app = FastAPI()` and decorate functions with `@app.get`. Run with `fastapi dev main.py` and explore `/docs`. FastAPI is the framework, uvicorn is the server.
Hindi: venv बनाएँ, `"fastapi[standard]"` install करें, `app = FastAPI()` लिखें और functions को `@app.get` से सजाएँ। `fastapi dev main.py` से चलाएँ और `/docs` देखें। FastAPI framework है, uvicorn server है।

---

## ➡️ Next Topic
**300. Path Parameters** — dynamic URLs like `/orders/{order_id}` with automatic validation.
