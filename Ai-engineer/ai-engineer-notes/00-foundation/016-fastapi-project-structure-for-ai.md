---

# 016. FastAPI Project Structure for AI
# हिंदी में: AI के लिए FastAPI Project Structure

---

## 🔵 Simple Definition (English)
Project structure is how you split an AI service into folders and layers: routes (HTTP), services (business logic), LLM/prompt layer, repositories (database), schemas (Pydantic), and core (config, dependencies). Each layer has one job, so the app stays testable and changeable as it grows.

## 🔵 सरल परिभाषा (Hindi)
Project structure यह है कि AI service को folders और layers में कैसे बाँटें: routes (HTTP), services (business logic), LLM/prompt layer, repositories (database), schemas (Pydantic) और core (config, dependencies)। हर layer का एक ही काम होता है, इसलिए app बढ़ने पर भी testable और बदलने लायक रहता है।

---

## 🔴 Problem it Solves
Many AI projects start as one `main.py` with prompts, SQL, API keys and routes mixed together. Soon nobody can change a prompt without touching routes, tests need a real LLM, and two developers conflict on one file. A clear structure separates concerns, so you can swap the model, test with fakes and version prompts safely.

## 🔴 यह क्यों बना? (Hindi)
कई AI projects एक `main.py` से शुरू होते हैं जिसमें prompts, SQL, API keys और routes सब मिले होते हैं। जल्दी ही prompt बदलने के लिए routes छूने पड़ते हैं, tests को असली LLM चाहिए, और दो developers एक file पर टकराते हैं। साफ़ structure concerns अलग करता है ताकि model बदलना, fakes से test करना और prompts को सुरक्षित version करना आसान हो।

---

## 🟢 How it Works — Step by Step

```
Step 1 → app/main.py: create FastAPI app, lifespan (pools, clients), include routers, handlers
Step 2 → app/api/: thin routers: parse request, call a service, return a schema
Step 3 → app/services/: business logic (classify_product) that coordinates LLM + DB + cache
Step 4 → app/llm/: LLM client wrapper, prompt templates (versioned), output parsing, token accounting
Step 5 → app/repositories/: all SQL (or ORM) lives here; services never write SQL
Step 6 → app/schemas/: Pydantic models for requests, responses, LLM outputs
Step 7 → app/core/: settings (pydantic-settings), dependencies, logging, errors. tests/ mirrors app/
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → app/main.py: FastAPI app, lifespan (pools, clients), routers include, handlers
Step 2 → app/api/: पतले routers: request parse, service call, schema return
Step 3 → app/services/: business logic (classify_product) जो LLM + DB + cache coordinate करता है
Step 4 → app/llm/: LLM client wrapper, versioned prompt templates, output parsing, token accounting
Step 5 → app/repositories/: सारा SQL (या ORM) यहाँ; services कभी SQL नहीं लिखते
Step 6 → app/schemas/: requests, responses, LLM outputs के Pydantic models
Step 7 → app/core/: settings (pydantic-settings), dependencies, logging, errors। tests/ app/ जैसा बना होता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: `api/classify.py` receives the request; `services/classification.py` checks the cache, retrieves candidate codes, calls `llm/classifier.py` (which uses prompt `classify_v3`), saves via `repositories/classifications.py`, and returns a `ClassifyResponse`. A new model or prompt change touches only `llm/`. Tests inject a fake LLM into the service.

**Zomato AI**: `services/recommend.py` combines `repositories/menu.py` with `llm/ranker.py`, so product teams can change ranking prompts without touching the API layer.

## 🟡 Real Example Hindi mein
**Tariff System**: `api/classify.py` request लेता है; `services/classification.py` cache देखता है, candidate codes लाता है, `llm/classifier.py` (prompt `classify_v3`) call करता है, `repositories/classifications.py` से save करता है और `ClassifyResponse` लौटाता है। नया model या prompt बदलने पर सिर्फ़ `llm/` बदलता है। Tests service में fake LLM inject करते हैं।

**Zomato AI**: `services/recommend.py` `repositories/menu.py` और `llm/ranker.py` को जोड़ता है, इसलिए product team API layer छुए बिना ranking prompts बदल सकती है।

---

## 💻 Code Example — Basic
```python
# Basic: the recommended layout (print it) and a tiny layered app in ONE file to show the idea.
# Real layout:
LAYOUT = """
tariff-ai/
├── app/
│   ├── main.py                # app factory + lifespan + routers
│   ├── api/
│   │   ├── deps.py            # Depends() providers
│   │   └── classify.py        # thin routes
│   ├── core/
│   │   ├── config.py          # pydantic-settings
│   │   └── errors.py          # custom exceptions + handlers
│   ├── schemas/classify.py    # Pydantic models
│   ├── services/classification.py
│   ├── llm/
│   │   ├── client.py          # provider wrapper + token usage
│   │   ├── prompts.py         # versioned prompt templates
│   │   └── classifier.py      # build prompt, call, parse
│   └── repositories/classifications.py   # SQL only
├── tests/                     # mirrors app/, uses fake LLM
├── pyproject.toml
├── Dockerfile
└── .env.example               # never commit .env
"""
print(LAYOUT)  # show the layout

from fastapi import FastAPI  # framework
from fastapi.testclient import TestClient  # tests
from pydantic import BaseModel  # schema


class ClassifyResponse(BaseModel):  # schemas layer
    hs_code: str  # code


class Classifier:  # llm layer (fake)
    async def classify(self, text: str) -> str:  # returns a code
        return "8517.13"  # canned


class ClassificationService:  # services layer
    def __init__(self, classifier: Classifier) -> None:  # injected dependency
        self.classifier = classifier  # store

    async def run(self, text: str) -> ClassifyResponse:  # business logic
        return ClassifyResponse(hs_code=await self.classifier.classify(text))  # call llm layer


app = FastAPI()  # main layer
service = ClassificationService(Classifier())  # wiring


@app.get("/classify")  # api layer: thin
async def classify(q: str) -> ClassifyResponse:  # handler
    return await service.run(q)  # delegate


print(TestClient(app).get("/classify?q=phone").json())  # {'hs_code': '8517.13'}
```

## 💻 Code Example — Advanced
```python
# Production wiring in one runnable file: settings, lifespan, app factory, versioned prompts,
# repository interface, service with cache+LLM+repo, router, error handler, and a test using fakes.
# (In a real project each section below is its own module from the layout above.)
import asyncio  # async
from contextlib import asynccontextmanager  # lifespan
from functools import lru_cache  # cached settings
from typing import Annotated, AsyncIterator, Protocol  # typing

from fastapi import APIRouter, Depends, FastAPI, Request  # FastAPI
from fastapi.responses import JSONResponse  # responses
from fastapi.testclient import TestClient  # tests
from pydantic import BaseModel, Field  # models


# ---- core/config.py ----
class Settings(BaseModel):  # in real code: pydantic_settings.BaseSettings reading .env
    app_name: str = "tariff-ai"  # name
    model: str = "gpt-4o-mini"  # default model
    prompt_version: str = "classify_v3"  # active prompt
    max_input_chars: int = 2000  # cost guard


@lru_cache  # build once
def get_settings() -> Settings:  # settings provider
    return Settings()  # would read environment variables


# ---- core/errors.py ----
class LLMUnavailable(Exception):  # domain error
    """Raised when the model provider fails."""


# ---- schemas ----
class ClassifyIn(BaseModel):  # request
    description: str = Field(min_length=3, max_length=2000)  # bounded


class ClassifyOut(BaseModel):  # response
    hs_code: str  # code
    source: str  # "cache" or "llm"
    prompt_version: str  # for traceability


# ---- llm/prompts.py ----
PROMPTS = {"classify_v3": "Return the HS code for: {description}"}  # versioned templates live in one place


# ---- ports (interfaces) ----
class LLM(Protocol):  # what the service needs from an LLM
    async def complete(self, prompt: str) -> str: ...  # returns text


class Repo(Protocol):  # what the service needs from storage
    async def save(self, description: str, hs_code: str) -> None: ...  # persist


class Cache(Protocol):  # what the service needs from cache
    async def get(self, key: str) -> str | None: ...  # read
    async def set(self, key: str, value: str) -> None: ...  # write


# ---- services/classification.py ----
class ClassificationService:  # business logic, no HTTP, no SQL
    def __init__(self, llm: LLM, repo: Repo, cache: Cache, settings: Settings) -> None:  # injected
        self.llm, self.repo, self.cache, self.s = llm, repo, cache, settings  # store

    async def classify(self, description: str) -> ClassifyOut:  # main use case
        key = f"{self.s.prompt_version}:{' '.join(description.lower().split())}"  # versioned key
        if (hit := await self.cache.get(key)) is not None:  # cache first (0 tokens)
            return ClassifyOut(hs_code=hit, source="cache", prompt_version=self.s.prompt_version)  # done
        prompt = PROMPTS[self.s.prompt_version].format(description=description)  # render prompt
        try:  # external call
            code = (await asyncio.wait_for(self.llm.complete(prompt), timeout=10)).strip()  # call with timeout
        except (asyncio.TimeoutError, ConnectionError) as exc:  # provider trouble
            raise LLMUnavailable(str(exc) or "timeout") from exc  # domain error
        await self.cache.set(key, code)  # fill cache
        await self.repo.save(description, code)  # audit trail
        return ClassifyOut(hs_code=code, source="llm", prompt_version=self.s.prompt_version)  # result


# ---- infrastructure (fakes here; real: OpenAI client, asyncpg repo, redis cache) ----
class FakeLLM:  # fake model
    calls = 0  # counter

    async def complete(self, prompt: str) -> str:  # canned
        FakeLLM.calls += 1  # count
        return "8517.13"  # answer


class MemRepo:  # in-memory repo
    rows: list[tuple[str, str]] = []  # storage

    async def save(self, description: str, hs_code: str) -> None:  # save
        self.rows.append((description, hs_code))  # append


class MemCache:  # in-memory cache
    def __init__(self) -> None:  # init
        self.d: dict[str, str] = {}  # data

    async def get(self, key: str) -> str | None:  # read
        return self.d.get(key)  # value or None

    async def set(self, key: str, value: str) -> None:  # write
        self.d[key] = value  # store


# ---- api/deps.py ----
def get_service(request: Request, settings: Annotated[Settings, Depends(get_settings)]) -> ClassificationService:  # provider
    return request.app.state.service_factory(settings)  # built from app.state


# ---- api/classify.py ----
router = APIRouter(prefix="/v1", tags=["classify"])  # router


@router.post("/classify", response_model=ClassifyOut)  # thin route
async def classify(body: ClassifyIn, svc: Annotated[ClassificationService, Depends(get_service)]) -> ClassifyOut:  # handler
    return await svc.classify(body.description)  # delegate to service


# ---- main.py ----
def create_app(llm: LLM | None = None) -> FastAPI:  # app factory: tests pass fakes
    cache, repo = MemCache(), MemRepo()  # real app: created in lifespan from settings

    @asynccontextmanager  # lifespan
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:  # startup/shutdown
        app.state.service_factory = lambda s: ClassificationService(llm or FakeLLM(), repo, cache, s)  # wiring
        yield  # run

    app = FastAPI(title=get_settings().app_name, lifespan=lifespan)  # app
    app.include_router(router)  # mount routers

    @app.exception_handler(LLMUnavailable)  # error mapping lives in one place
    async def llm_down(request: Request, exc: LLMUnavailable) -> JSONResponse:  # handler
        return JSONResponse(status_code=502, content={"error": "llm_unavailable"})  # reply

    return app  # done


if __name__ == "__main__":  # test with fakes
    class DownLLM:  # failing fake
        async def complete(self, prompt: str) -> str:  # raises
            raise ConnectionError("down")  # provider error

    with TestClient(create_app()) as c:  # normal app
        print(c.post("/v1/classify", json={"description": "Android phone"}).json())  # source llm
        print(c.post("/v1/classify", json={"description": "android   PHONE"}).json())  # source cache
        print("llm calls:", FakeLLM.calls)  # 1
    with TestClient(create_app(DownLLM())) as c:  # failing app
        print(c.post("/v1/classify", json={"description": "Laptop"}).status_code)  # 502
```

---

## 🟠 FastAPI Integration
Use an app factory (`create_app`) so tests can build the app with fakes; use `APIRouter` per feature; use `pydantic-settings` for config; mount versioned prefixes (`/v1`). Run with `uvicorn app.main:app` or a factory: `uvicorn app.main:create_app --factory`.

```python
# core/config.py with pydantic-settings (pip install pydantic-settings)
from pydantic_settings import BaseSettings, SettingsConfigDict  # settings base


class Settings(BaseSettings):  # reads environment and .env
    model_config = SettingsConfigDict(env_file=".env", env_prefix="TARIFF_")  # TARIFF_OPENAI_API_KEY etc.
    openai_api_key: str = ""  # secret, never hard-code
    database_url: str = "postgresql://localhost/tariff"  # DB
    redis_url: str = "redis://localhost:6379"  # cache
    model: str = "gpt-4o-mini"  # default model
```

---

## 🔗 LangChain / LangGraph Connection
Keep chains and graphs in their own package (`app/llm/` or `app/agents/`), built once in `lifespan` and injected into services. Prompts are versioned templates (`ChatPromptTemplate`) stored as files or constants; LangGraph state schemas live in `schemas/`; tools live in `app/tools/` and call services, not the HTTP layer.

```python
# app/llm/classifier.py - chain built once, injected into the service
from langchain_core.prompts import ChatPromptTemplate  # prompt
from langchain_openai import ChatOpenAI  # model


def build_classifier_chain(model: str):  # factory used in lifespan
    prompt = ChatPromptTemplate.from_messages([  # versioned prompt lives here
        ("system", "You are a customs classification expert. Return only the HS code."),  # system
        ("human", "{description}"),  # user
    ])  # template
    return prompt | ChatOpenAI(model=model, temperature=0, max_tokens=30)  # LCEL chain, tiny output
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Business logic and SQL inside route functions
✅ Correct: routes call a service; services call repositories.

```python
# Wrong: route does everything, cannot unit test without DB and LLM
@app.post("/classify")
async def classify(body):
    row = await pool.fetchrow("SELECT ...")
    resp = await openai_client.chat.completions.create(...)
# Right
@router.post("/classify")
async def classify(body: In, svc: Service = Depends(get_service)):
    return await svc.classify(body.description)
```

❌ Mistake 2: Hard-coded secrets and prompts scattered across files
✅ Correct: settings from environment; prompts in one versioned module.

```python
# Wrong
client = OpenAI(api_key="sk-live-123...")
# Right
settings = Settings()   # reads env
client = AsyncOpenAI(api_key=settings.openai_api_key)
```

❌ Mistake 3: Circular imports between layers. Dependency direction must be api → services → (llm, repositories) → core/schemas, never backwards.

---

## 🧠 Tricky Interview Question

**Q**: "Your team wants to A/B test two prompt versions on 10 percent of traffic without redeploying. Where does that live in your structure?"

**Answer**: In the LLM/prompt layer plus the service. Keep prompts in a versioned registry (`PROMPTS["classify_v3"]`, `"classify_v4"`), and have the service pick a version through a small router (hash of user id modulo 100 against a flag stored in config or a feature-flag service). Record `prompt_version` in every response and DB row, so you can compare accuracy, token usage and latency per version. Routes do not change. Because the choice is in the service via injected settings, tests can force a version.

---

## ⚫ Interview Questions + Answers

Q1: Why keep routes thin? (Easy)
A1: Routes handle HTTP concerns only (parse, status codes). Logic in services is reusable (workers, CLI, tests) and testable without HTTP.

Q2: Where do you put prompts? (Easy)
A2: In a dedicated module or files, versioned, separate from route code. Prompts change often and need tracking, review and evaluation.

Q3: What is an app factory and why use it? (Medium)
A3: A function `create_app(settings, llm=...)` returning a configured FastAPI app. Tests build apps with fakes and different settings, avoiding global state and import-time side effects.

Q4: How do you manage configuration and secrets? (Medium)
A4: `pydantic-settings` reads environment variables (and `.env` locally). Secrets come from the platform secret manager in production. Never commit `.env`; commit `.env.example`. Validate settings at startup so the app fails fast when a key is missing.

Q5: How would you structure a multi-agent LangGraph feature inside this layout? (Hard)
A5: Create `app/agents/<name>/` with `state.py` (TypedDict/Pydantic), `nodes.py` (async functions that call services and tools), `graph.py` (builds and compiles the graph with a Postgres or Redis checkpointer), and `tools.py`. Build the compiled graph in `lifespan`, expose it through a dependency, and call it from a thin route or a worker with a `thread_id`. Nodes depend on services via injection rather than importing FastAPI. Evaluate graphs with a test suite using fake LLMs for determinism, and trace with LangSmith or OpenTelemetry. Keep token budgets per run in state.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The service will live longer than a prototype or has more than one developer
- You want fake-LLM tests and swappable providers
- Prompts and models change frequently

❌ Avoid when:
- A throwaway demo (one file is fine)
- Over-abstracting with interfaces for things that will never change
- Splitting into microservices before you need them

---

## 📊 Visual Diagram
```
 HTTP ──► api/ (routes, thin)
              │ Depends()
              ▼
         services/  ◄── core/ (config, errors, logging)
          │      │
          ▼      ▼
       llm/   repositories/ ──► Postgres
   (prompts,      cache ───────► Redis
    client,
    parsing) ──► OpenAI / Anthropic

 schemas/ used by all layers ;  tests/ replace llm/repo/cache with fakes
 Dependency direction:  api → services → llm/repo → core
```

---

## 💰 Cost Impact
Structure influences spend. A single `llm/` layer is the one place to enforce `max_tokens`, log token usage, switch to a cheaper model, add caching and apply timeouts, rather than hoping each route remembers. Versioned prompts let you measure token usage and quality per version and keep only cheaper, equally good prompts. Fake LLMs in tests make CI cost zero tokens (a suite of 300 tests calling a real model at 1K tokens each would burn 300K tokens per run, on every commit). Example: moving from 1,200-token to 700-token prompt on 100K daily calls saves 50M tokens per day.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Layered architecture | Separate layers with one job each | हर एक काम वाली अलग layers |
| Service | Business logic layer | business logic layer |
| Repository | Data access layer | data access layer |
| App factory | Function that builds the app | app बनाने वाला function |
| Settings | Typed configuration | typed configuration |
| Prompt registry | Versioned prompt store | versioned prompts का store |
| Port/Protocol | Interface a layer needs | layer को चाहिए interface |
| Lifespan | Startup/shutdown wiring | startup/shutdown wiring |

---

## ⚡ 3-Line Summary
English: Split an AI service into api, services, llm, repositories, schemas and core, with dependencies pointing inward. Use an app factory, settings from env and versioned prompts. This makes tests cheap and model or prompt changes safe.
Hindi: AI service को api, services, llm, repositories, schemas और core में बाँटो, dependencies अंदर की ओर रखो। App factory, env से settings और versioned prompts use करो। इससे tests सस्ते होते हैं और model या prompt बदलना सुरक्षित।

---

## ➡️ Next Topic
**017. FastAPI Middleware** — cross-cutting concerns such as request ids, timing, CORS and logging are added with middleware around every route.
