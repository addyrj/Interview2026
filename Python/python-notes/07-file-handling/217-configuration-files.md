---

# 217. Configuration Files
# हिंदी में: Configuration Files (App की settings: INI, JSON, TOML, env)

---

## 🔵 Simple Definition (English)
A configuration file stores settings (ports, hostnames, feature flags) outside the code so you can change behaviour without editing the program. Python reads INI with `configparser`, JSON with `json`, TOML with `tomllib` (3.11+), and environment variables with `os.environ`.

## 🔵 सरल परिभाषा (Hindi)
Configuration file settings (port, hostname, feature flags) को code से बाहर रखती है ताकि program बदले बिना behaviour बदला जा सके। Python में INI के लिए `configparser`, JSON के लिए `json`, TOML के लिए `tomllib` (3.11+) और environment variables के लिए `os.environ` इस्तेमाल होता है।

---

## 🔴 Problem it Solves
Hard-coded values (`DB_HOST = 'localhost'`) force a code change and redeploy for every environment (dev, staging, production), and secrets end up in Git. Config files and env vars separate WHAT the app does from WHERE and HOW it runs, which is the 12-factor app rule.

## 🔴 यह क्यों बना? (Hindi)
Hard-coded values (`DB_HOST = 'localhost'`) हर environment (dev, staging, production) के लिए code बदलने और redeploy करने पर मजबूर करती हैं, और secrets Git में पहुँच जाते हैं। Config files और env vars "app क्या करता है" को "कहाँ और कैसे चलता है" से अलग करते हैं, यही 12-factor app का नियम है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Pick a format: INI (simple), JSON (universal), TOML (typed, readable), YAML (see 218)
Step 2 → Load the file with the matching parser
Step 3 → Environment variables override file values (APP_PORT=9000)
Step 4 → Convert types (strings from INI/env -> int/bool)
Step 5 → Validate (port range, required keys) at startup and fail fast
Step 6 → Build ONE immutable Settings object and pass or inject it
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → format चुनो: INI (सरल), JSON (सार्वभौमिक), TOML (typed, पढ़ने में आसान), YAML (218 देखें)
Step 2 → सही parser से file load करो
Step 3 → environment variables file की values override करें (APP_PORT=9000)
Step 4 → types बदलो (INI/env की strings -> int/bool)
Step 5 → startup पर validate करो (port range, ज़रूरी keys) और जल्दी fail करो
Step 6 → एक ही immutable Settings object बनाओ और उसे pass/inject करो
```

---

## 🟡 Real World Example
A Razorpay-style service has `pyproject.toml` for tooling, `config.toml` for defaults and env vars for secrets (`DATABASE_URL`). Docker/Kubernetes pass env vars at deploy time. Pytest reads `pytest.ini`; Alembic reads `alembic.ini`; tools like Black and Ruff read `pyproject.toml`.

## 🟡 Real Example Hindi mein
Razorpay जैसी service में tooling के लिए `pyproject.toml`, defaults के लिए `config.toml` और secrets के लिए env vars (`DATABASE_URL`) होते हैं। Docker/Kubernetes deploy के समय env vars देते हैं। Pytest `pytest.ini` पढ़ता है; Alembic `alembic.ini`; Black और Ruff जैसे tools `pyproject.toml`।

---

## 💻 Code Example — Basic
```python
import configparser, json, tomllib, os, tempfile  # json/toml/ini loaders
ini = """
[database]
host = localhost
port = 5432
debug = true
[app]
name = My API
"""
cp = configparser.ConfigParser()  # INI parser
cp.read_string(ini)  # parse text
print(cp["database"]["host"], cp.getint("database", "port"), cp.getboolean("database", "debug"))
print(cp.get("app", "timeout", fallback="30"))  # default if missing
print(cp.sections())

print(json.loads('{"debug": true, "port": 8000}')["port"])

toml_text = """
title = "svc"
[server]
port = 8000
hosts = ["a", "b"]
"""
cfg = tomllib.loads(toml_text)  # 3.11+ in stdlib, read-only
print(cfg["server"]["hosts"], type(cfg["server"]["port"]).__name__)
with tempfile.NamedTemporaryFile("wb", suffix=".toml", delete=False) as f:
    f.write(toml_text.encode())
with open(f.name, "rb") as fh:  # tomllib requires BINARY mode
    print(tomllib.load(fh)["title"])
os.remove(f.name)
os.environ["APP_PORT"] = "9000"
print(int(os.environ.get("APP_PORT", "8000")), os.environ.get("NOPE", "fallback"))
```

**Real output** (Python 3.13.3):
```
localhost 5432 True
30
['database', 'app']
8000
['a', 'b'] int
svc
9000 fallback
```

Notes: `tomllib` is read-only (no writing; use `tomli_w` to write) and needs a file opened in BINARY mode. INI values are always strings until you call `getint`/`getboolean`. `ConfigParser` lower-cases option names.

## 💻 Code Example — Advanced
```python
from __future__ import annotations
import os, tomllib, tempfile, textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Settings:
    app_name: str
    port: int
    debug: bool
    hosts: list[str] = field(default_factory=list)


def load_settings(path: Path, env_prefix: str = "APP_") -> Settings:
    """File gives defaults; environment variables override (12-factor)."""
    try:
        with path.open("rb") as fh:
            raw: dict[str, Any] = tomllib.load(fh)
    except FileNotFoundError:
        raw = {}  # no file: use defaults
    except tomllib.TOMLDecodeError as exc:
        raise RuntimeError(f"bad config {path}: {exc}") from exc
    server = raw.get("server", {})
    port = int(os.environ.get(f"{env_prefix}PORT", server.get("port", 8000)))
    debug_raw = os.environ.get(f"{env_prefix}DEBUG", str(server.get("debug", False)))
    debug = debug_raw.lower() in {"1", "true", "yes"}
    if not 1 <= port <= 65535:
        raise ValueError(f"invalid port {port}")
    return Settings(raw.get("name", "app"), port, debug, list(server.get("hosts", [])))


with tempfile.TemporaryDirectory() as d:
    p = Path(d) / "cfg.toml"
    p.write_text(textwrap.dedent('''
        name = "orders"
        [server]
        port = 8000
        debug = false
        hosts = ["a.example", "b.example"]
    '''))
    print(load_settings(p))
    os.environ["APP_PORT"] = "9100"; os.environ["APP_DEBUG"] = "yes"
    print(load_settings(p))
    print(load_settings(Path(d) / "missing.toml"))
    p.write_text("name = = 1")
    try:
        load_settings(p)
    except RuntimeError as e:
        print("RuntimeError:", str(e).split(": ", 1)[1][:40])
```

**Real output** (Python 3.13.3):
```
Settings(app_name='orders', port=8000, debug=False, hosts=['a.example', 'b.example'])
Settings(app_name='orders', port=9100, debug=True, hosts=['a.example', 'b.example'])
Settings(app_name='app', port=9100, debug=True, hosts=[])
RuntimeError: Invalid value (at line 1, column 8)
```

Order of priority here: environment variable > file > default. `from exc` keeps the original parse error in the traceback. For bigger apps use `pydantic-settings`, which does the same with validation built in.

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
import os, tomllib, json
port = int(os.environ.get("PORT", "8000"))        # env var with default
with open("config.toml", "rb") as f:
    cfg = tomllib.load(f)                          # TOML
cfg2 = json.load(open("config.json"))              # JSON
```

```javascript
// JavaScript (Node.js)
const port = parseInt(process.env.PORT ?? "8000", 10);   // env var with default
const cfg = JSON.parse(require("fs").readFileSync("config.json", "utf8"));
require("dotenv").config();        // npm i dotenv  (loads .env into process.env)
// TOML: npm i smol-toml
```

Both read env vars the same way (`os.environ` vs `process.env`). Node developers usually use `.env` with `dotenv`; Python also supports `.env` via `python-dotenv` or `pydantic-settings`. TOML is standard-library in Python 3.11+, a package in Node.

---

## 🟠 FastAPI Connection
FastAPI apps load settings once and inject them with `Depends`. Cache the loader with `functools.lru_cache`, and override it in tests with `app.dependency_overrides`. The official recommendation is `pydantic-settings` (`BaseSettings`) which reads env vars and `.env` files with type validation.

```python
from functools import lru_cache
import os
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel
class Settings(BaseModel):
    app_name: str = "orders"
    port: int = int(os.environ.get("APP_PORT", "8000"))
@lru_cache
def get_settings() -> Settings:
    return Settings()
app = FastAPI()
@app.get("/info")
def info(s: Settings = Depends(get_settings)) -> dict[str, object]:
    return {"app": s.app_name, "port": s.port}
c = TestClient(app); print(c.get("/info").json())
app.dependency_overrides[get_settings] = lambda: Settings(app_name="test", port=1)
print(c.get("/info").json())
```

**Real output** (Python 3.13.3):
```
{'app': 'orders', 'port': 8000}
{'app': 'test', 'port': 1}
```


---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Treating INI/env values as typed
```python
# Wrong - "false" is a non-empty string, so this is True!
debug = bool(os.environ.get("DEBUG", "false"))

# Right
debug = os.environ.get("DEBUG", "false").lower() in {"1", "true", "yes"}
```

❌ Mistake 2: Committing secrets to Git
```python
# Wrong
SECRET_KEY = "sk_live_abc123"

# Right - read from environment, keep .env in .gitignore
SECRET_KEY = os.environ["SECRET_KEY"]   # KeyError at startup if missing = good (fail fast)
```

❌ Mistake 3: Opening TOML in text mode
```python
# Wrong - TypeError: File must be opened in binary mode
with open("c.toml") as f:
    tomllib.load(f)

# Right
with open("c.toml", "rb") as f:
    tomllib.load(f)
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
import configparser
cp = configparser.ConfigParser(); cp.read_string("[S]\nDebug = false\nurl = http://x/%20")
print(bool(cp["S"]["Debug"]), cp.getboolean("S", "debug"), list(cp["S"]))
try: cp["S"]["url"]
except configparser.InterpolationSyntaxError: print("InterpolationSyntaxError")
print(cp.get("S", "url", raw=True))
```

**Answer** (real run on Python 3.13.3):
```
True False ['debug', 'url']
InterpolationSyntaxError
http://x/%20
```
`bool('false')` is `True` because any non-empty string is truthy, while `getboolean` understands `false`. `ConfigParser` lower-cases keys (`debug`, not `Debug`). A literal `%` in a value triggers `BasicInterpolation` and raises `InterpolationSyntaxError`; use `raw=True` or `%%`.

---

## ⚫ Interview Questions + Answers

Q1: Which config format should I choose?
A1: TOML for tool/app config in Python (typed, comments, standard library). JSON for machine-to-machine. YAML for Kubernetes/CI style nesting. INI for very simple settings. Env vars for secrets and per-environment values.

Q2: What is the 12-factor rule about config?
A2: Store config in the environment, strictly separated from code, so the same build can run in dev, staging and production.

Q3: Why `os.environ['X']` vs `os.environ.get('X')`?
A3: `[]` raises `KeyError` when missing, good for required settings (fail fast). `.get` returns None/default, good for optional ones.

Q4: How do you keep secrets safe?
A4: Never commit them. Use env vars, `.env` files in `.gitignore`, or a secrets manager (AWS Secrets Manager, Vault). Do not log them.

Q5: How do you avoid re-parsing the config on every request?
A5: Load once at startup (module level or `lru_cache` function) and reuse the immutable object; in FastAPI inject it with `Depends(get_settings)`.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Values differ per environment (DB URL, API keys, ports)
- You want to change behaviour without redeploying code
- You need feature flags or tunables for non-developers

❌ Avoid when:
- The value is a true constant of the algorithm
- It is large or changes constantly (use a database)
- You would store secrets in a plain file inside the repo

---

## 📊 Visual Diagram

```
defaults in code  <  config.toml  <  environment variables  <  CLI flags
      (lowest priority)                         (highest priority)

 config.toml ----+
 APP_PORT=9100 --+--> load_settings() --> Settings(port=9100, ...)
                                              |
                              injected via Depends(get_settings)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Config | Settings kept outside code | code के बाहर की settings |
| Environment variable | OS-level key=value setting | OS स्तर की setting |
| TOML | Typed readable config format | typed और पढ़ने में आसान format |
| 12-factor | Rules for cloud-ready apps | cloud-ready apps के नियम |
| Fail fast | Stop at startup on bad config | गलत config पर शुरू में ही रुकना |
| Override | Higher priority replaces lower | ऊँची priority नीचे वाली को बदले |

---

## ⚡ 3-Line Summary
English: Keep settings out of code: TOML/JSON/INI files for defaults and environment variables for secrets and per-environment values. Convert types explicitly, validate at startup, and inject one cached Settings object.
Hindi: Settings को code से बाहर रखें: defaults के लिए TOML/JSON/INI files और secrets व per-environment values के लिए environment variables। Types साफ़ तौर पर बदलें, startup पर validate करें और एक cached Settings object inject करें।

---

## ➡️ Next Topic
**218. YAML File Handling** — read and write YAML safely with PyYAML.
