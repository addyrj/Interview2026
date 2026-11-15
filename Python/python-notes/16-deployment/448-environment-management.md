---

# 448. Environment Management
# हिंदी में: Environment Management (dev / staging / prod की settings)

---

## 🔵 Simple Definition (English)
Environment management means keeping configuration (database URL, secret keys, debug flag) outside the code, in environment variables or `.env` files, so the same code runs in dev, staging and production with different values. In Python this is usually done with `os.environ` or `pydantic-settings`.

## 🔵 सरल परिभाषा (Hindi)
Environment management का मतलब है configuration (database URL, secret key, debug flag) को code से बाहर, environment variables या `.env` file में रखना, ताकि वही code dev, staging और production में अलग values के साथ चले। Python में यह `os.environ` या `pydantic-settings` से होता है।

---

## 🔴 Problem it Solves
Hard-coded passwords end up in Git history, and changing a URL needs a code change and a redeploy. Developers also break production by using the dev database. Separating config from code (the 12-factor app rule) fixes leaks, makes deploys repeatable, and lets one Docker image run everywhere.

## 🔴 यह क्यों बना? (Hindi)
Code में लिखे password Git history में leak हो जाते हैं, और URL बदलने के लिए code बदलकर दोबारा deploy करना पड़ता है। कभी-कभी developer गलती से production में dev database इस्तेमाल कर लेता है। Config को code से अलग रखने (12-factor app नियम) से leak रुकता है, deploy दोहराने योग्य बनता है और एक ही Docker image हर जगह चल जाती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Code declares what it needs (a Settings class with types)
Step 2 → The platform supplies values: real env vars (prod) or a .env file (dev)
Step 3 → Real environment variables override .env file values
Step 4 → pydantic-settings reads, converts types ("4" -> 4, "true" -> True), validates
Step 5 → Missing or invalid value -> app fails at startup (fail fast)
Step 6 → One cached Settings object is shared, and injected with Depends
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Code बताता है कि उसे क्या चाहिए (types वाली Settings class)
Step 2 → Platform values देता है: असली env vars (prod) या .env file (dev)
Step 3 → असली environment variable, .env file की value को override करता है
Step 4 → pydantic-settings पढ़ता है, type बदलता है ("4" -> 4) और validate करता है
Step 5 → Value missing या गलत हो तो app start पर ही fail (fail fast)
Step 6 → एक cached Settings object सब जगह Depends से मिलता है
```

---

## 🟡 Real World Example
A Swiggy-style order service runs in three places: laptop (SQLite, debug on), staging (small Postgres, test payment keys) and production (managed Postgres, live Razorpay keys). The Docker image is built once; Kubernetes/VPS injects `APP_DATABASE_URL`, `APP_SECRET_KEY` and `APP_ENV=prod` at start. Secrets live in a secrets manager (AWS Secrets Manager, GitHub Secrets), never in Git.

## 🟡 Real Example Hindi mein
Swiggy जैसी order service तीन जगह चलती है: laptop (SQLite, debug on), staging (छोटा Postgres, test payment keys) और production (managed Postgres, live Razorpay keys)। Docker image एक बार बनती है; start पर Kubernetes/VPS `APP_DATABASE_URL`, `APP_SECRET_KEY` और `APP_ENV=prod` देता है। Secrets, secrets manager (AWS Secrets Manager, GitHub Secrets) में रहते हैं, Git में कभी नहीं।

---

## 💻 Code Example — Basic
```python
# Basic: read configuration with os.environ (standard library only)
import os  # access environment variables

os.environ["APP_ENV"] = "dev"  # simulate the platform setting a variable
env: str = os.environ.get("APP_ENV", "dev")  # read with a default value
print(env)  # Output: dev

port: int = int(os.environ.get("APP_PORT", "8000"))  # env values are ALWAYS strings -> convert
print(port, type(port).__name__)  # Output: 8000 int

debug: bool = os.environ.get("APP_DEBUG", "false").lower() == "true"  # "false" string is truthy, so compare
print(debug)  # Output: False

try:  # a required variable must fail loudly
    secret: str = os.environ["APP_SECRET_KEY"]  # [] raises KeyError when missing
except KeyError as exc:  # catch the missing key
    print("missing:", exc)  # Output: missing: 'APP_SECRET_KEY'
```

## 💻 Code Example — Advanced
```python
# Production: typed, validated settings with pydantic-settings
# pip install pydantic-settings   (tested with pydantic 2.14, pydantic-settings 2.16)
import os  # to simulate environment values
import tempfile  # temp folder for a demo .env
from functools import lru_cache  # build Settings only once
from typing import Literal  # restrict allowed values

from pydantic import Field, SecretStr, ValidationError  # validation tools
from pydantic_settings import BaseSettings, SettingsConfigDict  # settings base


class Settings(BaseSettings):
    """All configuration in one validated place."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_", extra="ignore")  # read APP_* vars
    env: Literal["dev", "staging", "prod"] = "dev"  # only these three names allowed
    debug: bool = False  # "true"/"1" become True
    database_url: str = "sqlite:///./dev.db"  # safe local default
    secret_key: SecretStr = Field(min_length=8)  # REQUIRED, hidden when printed
    workers: int = Field(default=1, ge=1, le=16)  # between 1 and 16


@lru_cache  # same object every call (cheap dependency)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]  # values come from the environment


os.chdir(tempfile.mkdtemp())  # work in an empty temp folder

try:  # 1) nothing configured -> startup failure
    Settings()  # type: ignore[call-arg]
except ValidationError as e:  # pydantic lists every problem
    print("missing:", e.errors()[0]["loc"], e.errors()[0]["type"])
# Output: missing: ('secret_key',) missing

with open(".env", "w") as f:  # 2) write a demo .env file
    f.write("APP_SECRET_KEY=supersecret123\nAPP_DEBUG=true\nAPP_WORKERS=4\n")
s: Settings = get_settings()  # load from .env
print(s.env, s.debug, s.workers, s.secret_key, s.secret_key.get_secret_value()[:4])
# Output: dev True 4 ********** supe

os.environ["APP_WORKERS"] = "8"  # 3) real env var beats .env
print(Settings().workers)  # type: ignore[call-arg]
# Output: 8

os.environ["APP_WORKERS"] = "99"  # 4) invalid value
try:
    Settings()  # type: ignore[call-arg]
except ValidationError as e:
    print(e.errors()[0]["type"], e.errors()[0]["msg"])
# Output: less_than_equal Input should be less than or equal to 16

print(get_settings() is get_settings())  # cached singleton
# Output: True
```

Verified by running on Python 3.13.3: all outputs above are real.

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
import os
db = os.environ.get("DATABASE_URL", "sqlite:///dev.db")   # always a string
# .env loading: python-dotenv or pydantic-settings
```
```javascript
// JavaScript (Node)
// node --env-file=.env app.js      (Node 20.6+), or the dotenv package
const db = process.env.DATABASE_URL ?? "sqlite:dev.db";    // always a string
```

Key differences: both read strings from the process environment. Node's `process.env` and Python's `os.environ` behave the same way, but Python usually adds `pydantic-settings` for typing and validation (similar to `zod` plus `dotenv` in Node). Frontend frameworks bake env values into the bundle at build time (`NEXT_PUBLIC_*`); a Python backend reads them at runtime.

---

## 🟠 FastAPI Connection
Expose `get_settings` as a dependency so tests can override it with `app.dependency_overrides`.

```python
# FastAPI: settings as a dependency (pip install fastapi pydantic-settings)
from functools import lru_cache  # cache
from typing import Annotated  # modern dependency typing

from fastapi import Depends, FastAPI  # framework
from pydantic_settings import BaseSettings, SettingsConfigDict  # settings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_")  # APP_ENV, APP_DEBUG
    env: str = "dev"  # environment name
    debug: bool = False  # debug flag


@lru_cache
def get_settings() -> Settings:
    return Settings()  # read once


app: FastAPI = FastAPI()  # create app


@app.get("/info")  # GET /info
def info(settings: Annotated[Settings, Depends(get_settings)]) -> dict[str, object]:
    return {"env": settings.env, "debug": settings.debug}  # never return secrets
```

In a test: `app.dependency_overrides[get_settings] = lambda: Settings(env="test")`.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Treating env values as bool or int
✅ Correct: convert (or let pydantic convert).

```python
# Wrong - the string "false" is truthy!
import os
os.environ["APP_DEBUG"] = "false"
if os.environ["APP_DEBUG"]:
    print("debug ON")  # runs, surprise!
# Right
debug: bool = os.environ["APP_DEBUG"].lower() in {"1", "true", "yes"}
```

❌ Mistake 2: Committing `.env` to Git
✅ Correct: add `.env` to `.gitignore`, commit a `.env.example` with fake values only. If a secret was committed, rotate it; deleting the file does not erase Git history.

❌ Mistake 3: Using `if ENV == "prod"` branches all over the code
✅ Correct: keep the difference in values (URLs, flags) inside Settings, not in logic branches that are never tested.

---

## 🧠 Tricky Interview Question

**Q**: What does this print?

```python
import os
os.environ["APP_RETRIES"] = 3
```

**Answer**: `TypeError: str expected, not int`. Environment variables are strings only, so assign `"3"` and convert with `int()` on read. Related trap: `os.environ.get("X", 5)` returns the int `5` when X is missing but the string `"5"` when X is set to 5, so the type depends on whether the variable exists. Always give a string default and convert once.

---

## ⚫ Interview Questions + Answers

Q1: Why not keep secrets in code or config files in Git?
A1: Git history is permanent and widely copied. Anyone with repo access, including old forks, can read them. Use env vars injected at runtime plus a secrets manager.

Q2: What is the order of precedence in pydantic-settings?
A2: Init arguments, then environment variables, then `.env` file, then secrets directory, then field defaults. Real env vars therefore override `.env`.

Q3: What is a 12-factor app's config rule?
A3: "Store config in the environment." Config that changes between deploys must not be in code, so the same build artifact can run anywhere.

Q4: How do you manage dev/staging/prod differences safely?
A4: A single `APP_ENV` plus per-environment values from the platform; separate databases and API keys per environment; validate at startup; keep prod secrets accessible only to the prod deploy job (GitHub Environments).

Q5: How do you handle a leaked secret?
A5: Revoke and rotate it immediately, redeploy with the new value, check logs for misuse, and add secret scanning (GitHub push protection) to prevent repeats.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any value differs between machines (URLs, keys, ports, feature flags)
- You build one Docker image and deploy it to many stages
- You need startup validation with clear error messages

❌ Avoid when:
- The value is a true constant (e.g. `PI`, an HTTP status), keep it in code
- Data is large or changes often at runtime (use a database or feature-flag service)
- You put secrets in `ARG`/`ENV` lines of a Dockerfile (they stay in image layers)

---

## 📊 Visual Diagram

```
                  ┌────────────── same code / same image ─────────────┐
 laptop  ── .env ─►│                                                   │
 staging ── env ──►│  Settings (pydantic)  ──► validate ──► app runs   │
 prod    ── env ──►│        │                      │                   │
                  └────────┼──────────────────────┼───────────────────┘
        priority:  env var > .env > default       └─► invalid? crash at startup
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Environment variable | Key=value given to a process | process को दिया गया key=value |
| .env file | Local file of variables | local variables की file |
| 12-factor app | Rules for cloud-ready apps | cloud-ready app के नियम |
| Secret | Sensitive value (password, key) | संवेदनशील value |
| Fail fast | Crash early on bad config | गलत config पर शुरू में ही रुकना |
| SecretStr | Type that hides its value | value छिपाने वाला type |

---

## ⚡ 3-Line Summary
English: Keep configuration out of code and inject it through environment variables. Use pydantic-settings for types, validation and defaults, and cache one Settings object. Never commit secrets; rotate any that leak.
Hindi: Configuration को code से बाहर रखें और environment variables से दें। Types, validation और defaults के लिए pydantic-settings इस्तेमाल करें और एक ही Settings object cache करें। Secrets कभी commit न करें; leak हो तो तुरंत बदल दें।

---

## ➡️ Next Topic
**449. Python Production Checklist** — everything to verify (config, logging, security, health, limits) before going live.
