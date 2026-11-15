---

# 218. YAML File Handling
# हिंदी में: YAML File Handling (PyYAML से YAML पढ़ना और लिखना)

---

## 🔵 Simple Definition (English)
YAML is a human-friendly data format that uses indentation instead of braces. Python reads it with the third-party `PyYAML` package (`pip install pyyaml`): `yaml.safe_load()` parses text into dicts/lists, and `yaml.safe_dump()` writes them back. Always use the `safe_` versions.

## 🔵 सरल परिभाषा (Hindi)
YAML इंसानों के पढ़ने लायक data format है जो braces की जगह indentation इस्तेमाल करता है। Python में इसे third-party `PyYAML` package (`pip install pyyaml`) से पढ़ते हैं: `yaml.safe_load()` text को dict/list में बदलता है और `yaml.safe_dump()` वापस लिखता है। हमेशा `safe_` वाले versions ही इस्तेमाल करें।

---

## 🔴 Problem it Solves
Deeply nested config in JSON is noisy (quotes, commas, no comments). Tools like Docker Compose, Kubernetes, GitHub Actions and Ansible chose YAML because it allows comments, multi-line strings and anchors for reuse. Python has no built-in YAML, and the default `yaml.load` can execute code, so people need a safe way to read it.

## 🔴 यह क्यों बना? (Hindi)
गहरी nested config JSON में शोर वाली होती है (quotes, commas, comments नहीं)। Docker Compose, Kubernetes, GitHub Actions और Ansible ने YAML चुना क्योंकि इसमें comments, multi-line strings और दोबारा इस्तेमाल के लिए anchors होते हैं। Python में YAML built-in नहीं है, और पुराना `yaml.load` code चला सकता है, इसलिए पढ़ने का सुरक्षित तरीका ज़रूरी है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → pip install pyyaml (import name is yaml)
Step 2 → text/file -> yaml.safe_load() -> dict / list / scalars
Step 3 → YAML guesses types: true/yes -> bool, 1.5 -> float, ~ -> None, 2024-01-05 -> date
Step 4 → Validate the result (empty file gives None!)
Step 5 → Write back with yaml.safe_dump(data, sort_keys=False)
Step 6 → Multiple documents separated by '---' use safe_load_all
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → pip install pyyaml (import नाम yaml है)
Step 2 → text/file -> yaml.safe_load() -> dict / list / scalars
Step 3 → YAML खुद types अनुमान लगाता है: true/yes -> bool, 1.5 -> float, ~ -> None, 2024-01-05 -> date
Step 4 → नतीजे को validate करो (खाली file पर None मिलता है!)
Step 5 → वापस लिखो yaml.safe_dump(data, sort_keys=False) से
Step 6 → '---' से अलग कई documents के लिए safe_load_all
```

---

## 🟡 Real World Example
A CI tool reads `.github/workflows/*.yml`. A Swiggy-style deployment script loads `docker-compose.yml` to check that every service has a health check. An LLM app stores prompts and model settings in `prompts.yaml` so prompt engineers can edit without touching Python. A FastAPI admin endpoint lets users import a YAML config.

## 🟡 Real Example Hindi mein
CI tool `.github/workflows/*.yml` पढ़ता है। Swiggy जैसी deployment script `docker-compose.yml` load करके जाँचती है कि हर service में health check है। LLM app prompts और model settings `prompts.yaml` में रखता है ताकि prompt engineers Python छुए बिना बदल सकें। FastAPI admin endpoint से users YAML config import कर सकते हैं।

---

## 💻 Code Example — Basic
```python
import yaml  # pip install pyyaml
text = """
name: orders-api
port: 8000
debug: true
ratio: 0.5
nothing: null
tags: [a, b]
db:
  host: localhost
  ports:
    - 5432
    - 5433
"""
cfg = yaml.safe_load(text)  # ALWAYS safe_load
print(cfg["db"]["ports"], type(cfg["debug"]).__name__, cfg["nothing"])
print(yaml.safe_dump(cfg, sort_keys=False, default_flow_style=False).splitlines()[:4])
print(yaml.safe_load("a: yes\nb: no\nc: 08\nd: '08'\ne: 1e3\nf: NO"))
docs = list(yaml.safe_load_all("a: 1\n---\nb: 2\n"))
print(docs)
try:
    yaml.safe_load("a: [1, 2")
except yaml.YAMLError as e:
    print(type(e).__name__)
try:
    yaml.safe_load("x: !!python/object/apply:os.getcwd []")
except yaml.YAMLError as e:
    print("safe_load refused:", type(e).__name__)
print(yaml.safe_load("base: &b {x: 1}\nchild:\n  <<: *b\n  y: 2"))
```

**Real output** (Python 3.13.3):
```
[5432, 5433] bool None
['name: orders-api', 'port: 8000', 'debug: true', 'ratio: 0.5']
{'a': True, 'b': False, 'c': '08', 'd': '08', 'e': '1e3', 'f': False}
[{'a': 1}, {'b': 2}]
ParserError
safe_load refused: ConstructorError
{'base': {'x': 1}, 'child': {'x': 1, 'y': 2}}
```

Notes: YAML 1.1 (PyYAML) turns `yes`/`no`/`on`/`off` into booleans and `010` into octal 8; quote values when you want strings. Anchors (`&b`) and merge keys (`<<: *b`) let you reuse blocks.

## 💻 Code Example — Advanced
```python
from __future__ import annotations
import tempfile
from pathlib import Path
from typing import Any
import yaml
from pydantic import BaseModel, Field, ValidationError


class DB(BaseModel):
    host: str
    port: int = Field(5432, ge=1, le=65535)


class Config(BaseModel):
    name: str
    debug: bool = False
    db: DB


def load_yaml(path: Path) -> Config:
    try:
        raw: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise RuntimeError(f"invalid YAML in {path.name}") from exc
    if not isinstance(raw, dict):  # empty file gives None
        raise RuntimeError("top level must be a mapping")
    return Config.model_validate(raw)  # validate + types


with tempfile.TemporaryDirectory() as d:
    p = Path(d) / "c.yaml"
    p.write_text("name: shop\ndb:\n  host: db1\n")
    cfg = load_yaml(p)
    print(cfg)
    out = Path(d) / "out.yaml"
    out.write_text(yaml.safe_dump(cfg.model_dump(), sort_keys=False))
    print(out.read_text())
    p.write_text("name: shop\ndb:\n  host: db1\n  port: 99999\n")
    try:
        load_yaml(p)
    except ValidationError as e:
        print(e.errors()[0]["loc"], e.errors()[0]["type"])
    p.write_text("")
    try:
        load_yaml(p)
    except RuntimeError as e:
        print(e)
    p.write_text("a: [1,")
    try:
        load_yaml(p)
    except RuntimeError as e:
        print(e)
```

**Real output** (Python 3.13.3):
```
name='shop' debug=False db=DB(host='db1', port=5432)
name: shop
debug: false
db:
  host: db1
  port: 5432

('db', 'port') less_than_equal
top level must be a mapping
invalid YAML in c.yaml
```

Pydantic validates structure and types after parsing, giving clear errors with the location (`('db', 'port')`). An empty YAML file loads as `None`, so the type check on the top level is needed.

---

## 🟠 JavaScript vs Python Comparison

```python
# Python (pip install pyyaml)
import yaml
cfg = yaml.safe_load(open("config.yaml"))
print(cfg["db"]["host"])
text = yaml.safe_dump(cfg, sort_keys=False)
```

```javascript
// JavaScript (npm i yaml)
const YAML = require("yaml");
const cfg = YAML.parse(require("fs").readFileSync("config.yaml", "utf8"));
console.log(cfg.db.host);
const text = YAML.stringify(cfg);
```

Neither language has YAML built in. Python uses `PyYAML` (YAML 1.1) or `ruamel.yaml` (YAML 1.2, keeps comments when saving); Node uses `yaml` or `js-yaml`. The danger of unsafe loaders exists in both ecosystems, so use the safe API.

---

## 🟠 FastAPI Connection
FastAPI itself speaks JSON, but apps read YAML for settings, prompt templates and uploaded configs. Parse with `safe_load`, convert YAML errors into HTTP 400/422, and validate with Pydantic models. FastAPI can also show its OpenAPI schema as YAML if you serialise `app.openapi()` with `yaml.safe_dump`.

```python
import yaml
from fastapi import FastAPI, Request, HTTPException
from fastapi.testclient import TestClient
app = FastAPI()
@app.post("/import-config")
async def import_config(request: Request) -> dict[str, object]:
    body = (await request.body()).decode()
    try:
        data = yaml.safe_load(body)
    except yaml.YAMLError:
        raise HTTPException(400, "invalid yaml")
    return {"keys": sorted(data) if isinstance(data, dict) else []}
c = TestClient(app)
print(c.post("/import-config", content="a: 1\nb: 2").json())
print(c.post("/import-config", content="a: [").status_code)
```

**Real output** (Python 3.13.3):
```
{'keys': ['a', 'b']}
400
```


---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using yaml.load / unsafe_load on untrusted input
```python
# Wrong - the !!python/object tag can run code
yaml.load(text, Loader=yaml.UnsafeLoader)

# Right
yaml.safe_load(text)
```

❌ Mistake 2: Letting YAML guess types you wanted as strings
```python
# Wrong - country code Norway becomes False, version 3.10 becomes 3.1
yaml.safe_load("country: NO\nv: 3.10")     # {'country': False, 'v': 3.1}

# Right - quote them
yaml.safe_load("country: 'NO'\nv: '3.10'")
```

❌ Mistake 3: Not handling an empty file or tabs
```python
# Wrong - crashes later with 'NoneType is not subscriptable'
cfg = yaml.safe_load(open("empty.yaml"))["db"]

# Right
cfg = yaml.safe_load(text) or {}
# and indent with spaces only (tabs are a YAML syntax error)
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
import yaml
print(yaml.safe_load("a: yes\nb: NO\nc: 010\nd: 0o10\ne: ~\nf: 1_000\ng: '1_000'\nh: 1.0\ni: 2024-01-05"))
print(yaml.safe_load("country: NO"), yaml.safe_load("v: 3.10"))
```

**Answer** (real run on Python 3.13.3):
```
{'a': True, 'b': False, 'c': 8, 'd': '0o10', 'e': None, 'f': 1000, 'g': '1_000', 'h': 1.0, 'i': datetime.date(2024, 1, 5)}
{'country': False} {'v': 3.1}
```
PyYAML follows YAML 1.1: `yes` is `True`, `NO` is `False` (the famous 'Norway problem'), `010` is octal 8, `~` is `None`, `1_000` is 1000 but the quoted one stays a string, and `0o10` stays a string. An unquoted date becomes `datetime.date`, and `3.10` becomes the float `3.1`, so always quote codes and versions.

---

## ⚫ Interview Questions + Answers

Q1: `yaml.load` vs `yaml.safe_load`?
A1: `safe_load` builds only plain Python types (dict, list, str, int, float, bool, None, date). `load` with a full loader can construct arbitrary Python objects through tags and run code. Since PyYAML 6, `load` requires an explicit `Loader=` argument.

Q2: What is the Norway problem?
A2: In YAML 1.1 `NO` is parsed as boolean False, so a list of country codes breaks. Quote strings (`'NO'`) or use a YAML 1.2 parser (ruamel.yaml).

Q3: How do you keep comments when editing a YAML file?
A3: PyYAML drops comments on dump. Use `ruamel.yaml` in round-trip mode to preserve comments and ordering.

Q4: YAML vs JSON?
A4: YAML is a superset-style format with comments, anchors and less punctuation, but whitespace-sensitive and error-prone. JSON is stricter, faster to parse and best for APIs.

Q5: How do you read several documents from one file?
A5: `yaml.safe_load_all(stream)` returns a generator of documents separated by `---` (common in Kubernetes manifests).

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Config is nested and humans edit it (CI, Kubernetes, prompts)
- You need comments in the file
- You integrate with tools that already use YAML

❌ Avoid when:
- You exchange data between services (JSON is safer and faster)
- Whitespace mistakes would be costly (use TOML)
- The input is untrusted and you cannot use safe_load

---

## 📊 Visual Diagram

```
config.yaml                     safe_load()              Python
name: shop                   -------------------->     {'name': 'shop',
db:                                                     'db': {'host': 'db1',
  host: db1                                                    'port': 5432}}
  port: 5432                 <--------------------
                               safe_dump()
indentation (spaces) = nesting   | '- ' = list item | '#' = comment
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| YAML | Indentation-based data format | indentation वाला data format |
| safe_load | Parse without running code | code चलाए बिना parse |
| Anchor | &name reusable block | दोबारा इस्तेमाल होने वाला block |
| Merge key | <<: *name copies a block | block copy करने की key |
| Norway problem | NO parsed as False | NO का False बन जाना |
| Round-trip | Edit and save keeping comments | comments बचाकर edit करना |

---

## ⚡ 3-Line Summary
English: Use `yaml.safe_load` and `yaml.safe_dump` from PyYAML; never the unsafe loader. Quote strings that look like booleans, numbers or versions, handle empty files, and validate the result with Pydantic.
Hindi: PyYAML का `yaml.safe_load` और `yaml.safe_dump` इस्तेमाल करें; unsafe loader कभी नहीं। बूलियन, संख्या या version जैसी दिखने वाली strings को quote करें, खाली file संभालें और नतीजे को Pydantic से validate करें।

---

## ➡️ Next Topic
**219. Excel with openpyxl** — create, read and style `.xlsx` spreadsheets from Python.
