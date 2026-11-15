---

# 208. JSON File Handling
# हिंदी में: JSON File Handling (json.load, json.dump)

---

## 🔵 Simple Definition (English)
JSON is a text format for structured data (objects, lists, strings, numbers, true/false/null). Python's `json` module converts between JSON text and Python objects: `json.dump(obj, f)` writes to a file, `json.load(f)` reads from a file; `dumps`/`loads` work with strings.

## 🔵 सरल परिभाषा (Hindi)
JSON structured data (objects, lists, strings, numbers, true/false/null) का text format है। Python का `json` module JSON text और Python objects के बीच बदलता है: `json.dump(obj, f)` file में लिखता है, `json.load(f)` file से पढ़ता है; `dumps`/`loads` strings के साथ चलते हैं।

---

## 🔴 Problem it Solves
Python dicts and lists live only in memory. To save settings, send data to a browser or another service, or store AI chat history, you need a universal text format that every language understands. JSON is that format, and the `json` module avoids hand-written (and buggy) string building.

## 🔴 यह क्यों बना? (Hindi)
Python के dict और list सिर्फ memory में रहते हैं। Settings save करने, browser या दूसरी service को data भेजने, या AI chat history रखने के लिए ऐसा universal text format चाहिए जिसे हर भाषा समझे। JSON वही format है, और `json` module हाथ से string बनाने की गलतियों से बचाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python object (dict/list/str/int/float/bool/None)
Step 2 → json.dump(obj, f) / json.dumps(obj) -> JSON text   (serialize)
Step 3 → Mapping: dict->object, list/tuple->array, str->string, True->true, None->null
Step 4 → json.load(f) / json.loads(text) -> Python object  (deserialize)
Step 5 → Unsupported types (datetime, Decimal, set) -> TypeError unless you give default=
Step 6 → Bad text -> json.JSONDecodeError with line/column
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Python object (dict/list/str/int/float/bool/None)
Step 2 → json.dump(obj, f) / json.dumps(obj) से JSON text बनता है (serialize)
Step 3 → mapping: dict->object, list/tuple->array, True->true, None->null
Step 4 → json.load(f) / json.loads(text) से वापस Python object (deserialize)
Step 5 → datetime, Decimal, set जैसे types पर TypeError, जब तक default= न दें
Step 6 → खराब text पर json.JSONDecodeError (line/column के साथ)
```

---

## 🟡 Real World Example
A Swiggy mobile app reads `config.json` for feature flags. A Razorpay webhook stores raw payloads as JSON for audits. An AI chatbot saves each conversation as `chat-123.json` (list of `{role, content}` messages) and logs events as JSON Lines (`events.jsonl`). `package.json`-style settings files in tools follow the same format.

## 🟡 Real Example Hindi mein
Swiggy की mobile app feature flags के लिए `config.json` पढ़ती है। Razorpay webhook का raw payload audit के लिए JSON में रखा जाता है। AI chatbot हर बातचीत को `chat-123.json` (`{role, content}` messages की list) में सहेजता है और events को JSON Lines (`events.jsonl`) में लिखता है।

---

## 💻 Code Example — Basic
```python
# JSON file handling - every line commented
import json  # standard library
import tempfile  # temp folder
from pathlib import Path  # paths

d: Path = Path(tempfile.mkdtemp())  # temporary directory
p: Path = d / "c.json"  # JSON file path
data = {  # a Python dict
    "name": "आदित्य",  # Hindi text
    "age": 25,  # int
    "skills": ["py", "sql"],  # list
    "active": True,  # bool
    "manager": None,  # None becomes null
    "score": 9.5,  # float
}

with open(p, "w", encoding="utf-8") as f:  # open for writing
    json.dump(data, f, ensure_ascii=False, indent=2)  # write; keep Hindi readable
print(p.read_text(encoding="utf-8"))  # show the file
# Output:
# {
#   "name": "आदित्य",
#   "age": 25,
#   "skills": [
#     "py",
#     "sql"
#   ],
#   "active": true,
#   "manager": null,
#   "score": 9.5
# }

with open(p, encoding="utf-8") as f:  # open for reading
    back = json.load(f)  # file -> Python object
print(back == data, type(back).__name__)  # same data, a dict
# Output: True dict

print(json.dumps({"b": 1, "a": 2}, sort_keys=True, separators=(",", ":")))  # compact + sorted
# Output: {"a":2,"b":1}

print(json.loads('{"a": [1, 2, {"b": null}], "t": true}'))  # string -> Python
# Output: {'a': [1, 2, {'b': None}], 't': True}

print(json.dumps("नमस्ते"), json.dumps("नमस्ते", ensure_ascii=False))  # escape or not
# Output: "नमस्ते" "नमस्ते"

print(json.dumps((1, 2)), json.loads("[1,2]"))  # tuple becomes array, comes back as list
# Output: [1, 2] [1, 2]
```

## 💻 Code Example — Advanced
```python
# Production style: custom types, error messages, JSON Lines, atomic save
import json  # json module
import os  # fsync / replace
import tempfile  # temp folder
from datetime import date, datetime  # types JSON lacks
from decimal import Decimal  # exact money type
from pathlib import Path  # paths
from typing import Any, Dict  # type hints


def default(o: Any) -> Any:
    """Called only for objects json cannot handle."""
    if isinstance(o, (datetime, date)):  # dates
        return o.isoformat()  # '2026-01-31T10:30:00'
    if isinstance(o, Decimal):  # money
        return str(o)  # keep exact digits as text
    if isinstance(o, set):  # sets
        return sorted(o)  # stable list
    raise TypeError(f"Cannot serialize {type(o).__name__}")  # everything else


payload = {"t": datetime(2026, 1, 31, 10, 30), "amt": Decimal("10.25"), "s": {3, 1}}  # mixed types
print(json.dumps(payload, default=default))  # works with default=
# Output: {"t": "2026-01-31T10:30:00", "amt": "10.25", "s": [1, 3]}

try:  # without default=
    json.dumps({"d": datetime(2026, 1, 1)})  # datetime
except TypeError as exc:  # TypeError
    print("TypeError:", exc)  # message
# Output: TypeError: Object of type datetime is not JSON serializable


def hook(o: Dict[str, Any]) -> Any:
    """Called for every decoded JSON object (dict)."""
    if "ts" in o:  # our timestamp field
        o["ts"] = datetime.fromisoformat(o["ts"])  # string -> datetime
    return o  # must return the object


print(json.loads('{"ts":"2026-01-31T10:30:00"}', object_hook=hook))  # decoded with hook
# Output: {'ts': datetime.datetime(2026, 1, 31, 10, 30)}
print(json.loads('{"p": 10.10}', parse_float=Decimal))  # exact decimals
# Output: {'p': Decimal('10.10')}


def load_config(path: Path, fallback: Dict[str, Any]) -> Dict[str, Any]:
    """Read config JSON, with friendly errors."""
    try:  # risky part
        with open(path, encoding="utf-8") as fh:  # open
            return json.load(fh)  # parse
    except FileNotFoundError:  # no file yet
        return fallback  # use defaults
    except json.JSONDecodeError as exc:  # bad JSON
        raise ValueError(f"{path.name}: bad JSON at line {exc.lineno}") from exc  # helpful


d: Path = Path(tempfile.mkdtemp())  # temp folder
print(load_config(d / "none.json", {"x": 1}))  # missing -> fallback
# Output: {'x': 1}
(d / "bad.json").write_text('{"a": }')  # invalid JSON
try:  # parse it
    load_config(d / "bad.json", {})  # raises
except ValueError as exc:  # our error
    print(exc)  # message
# Output: bad.json: bad JSON at line 1

# JSON Lines: one JSON object per line, easy to append and stream
jl: Path = d / "e.jsonl"  # file
with open(jl, "w", encoding="utf-8") as f:  # write
    for i in range(3):  # three events
        f.write(json.dumps({"i": i}) + "\n")  # one per line
with open(jl, encoding="utf-8") as f:  # read lazily
    print([json.loads(line)["i"] for line in f if line.strip()])  # parse each line
# Output: [0, 1, 2]


def save_json(path: Path, obj: Any) -> None:
    """Atomic save: readers never see a half-written file."""
    tmp: Path = path.with_suffix(".tmp")  # temp file
    with open(tmp, "w", encoding="utf-8") as fh:  # write there first
        json.dump(obj, fh, indent=2)  # serialize
        fh.flush()  # to OS
        os.fsync(fh.fileno())  # to disk
    os.replace(tmp, path)  # atomic swap


save_json(d / "c.json", {"v": 1})  # save
print(json.loads((d / "c.json").read_text()))  # read back
# Output: {'v': 1}
```
Verified on Python 3.13.3. Error message wording (for example "Illegal trailing comma before end of object") was improved in Python 3.13 and differs in older versions.

---

## 🟠 JavaScript vs Python Comparison

```python
# Python way
import json
text = json.dumps({"a": 1, "ok": True, "x": None})   # '{"a": 1, "ok": true, "x": null}'
obj = json.loads(text)                               # {'a': 1, 'ok': True, 'x': None}
with open("c.json", "w", encoding="utf-8") as f:
    json.dump(obj, f, indent=2)
```
```javascript
// JavaScript way
const text = JSON.stringify({ a: 1, ok: true, x: null });   // '{"a":1,"ok":true,"x":null}'
const obj = JSON.parse(text);                               // { a: 1, ok: true, x: null }
import { writeFileSync, readFileSync } from "node:fs";
writeFileSync("c.json", JSON.stringify(obj, null, 2));      // pretty with 2 spaces
const back = JSON.parse(readFileSync("c.json", "utf-8"));
```

Key differences: `JSON.stringify` = `json.dumps`, `JSON.parse` = `json.loads`; Python adds `dump`/`load` for files. Python separators are `", "` and `": "` by default (spaces), JS is compact. Python can write `NaN` (not valid JSON) unless `allow_nan=False`; JS turns NaN into `null`. Python dict keys are always converted to strings.

---

## 🟠 FastAPI Connection
FastAPI converts return values to JSON automatically using `jsonable_encoder` (handles datetime, Decimal, UUID, Pydantic models). You need the `json` module for reading files, config, stored payloads and request bodies read manually. With Pydantic, `model.model_dump_json()` and `Model.model_validate_json(text)` replace `dumps/loads` and validate at the same time.

```python
# FastAPI: load config JSON at startup, validate with Pydantic (pip install fastapi)
import json  # json module
import tempfile  # temp folder
from pathlib import Path  # paths
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # validation


class Settings(BaseModel):  # shape of the config file
    app_name: str  # required text
    debug: bool = False  # optional flag


CFG: Path = Path(tempfile.mkdtemp()) / "settings.json"  # demo config path
CFG.write_text(json.dumps({"app_name": "pay-api"}), encoding="utf-8")  # create sample

settings: Settings = Settings.model_validate_json(CFG.read_text(encoding="utf-8"))  # read + validate
app: FastAPI = FastAPI(title=settings.app_name)  # use it


@app.get("/config")  # GET /config
def show() -> Settings:
    return settings  # FastAPI serializes the model to JSON
# Tested with TestClient: GET /config -> {"app_name": "pay-api", "debug": false}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Mixing `dump`/`dumps` and `load`/`loads`
✅ Correct:

```python
# Wrong - json.load(text) expects a FILE object, json.dumps(obj, f) is wrong too
# json.load('{"a": 1}')
# Right
json.loads('{"a": 1}')        # string in
json.load(open("c.json"))     # file in
```

❌ Mistake 2: Expecting non-string keys and tuples to survive
✅ Correct:

```python
import json
# Wrong - keys become strings, and True collides with 1
print(json.dumps({1: "x", True: "w"}))        # {"1": "w"}
print(json.loads(json.dumps({1: "x"})))       # {'1': 'x'}  (key is now a str)
# Right - use string keys yourself and convert back when needed
```

❌ Mistake 3: Using single quotes / trailing commas / forgetting `default=`
✅ Correct:

```python
# Wrong - not valid JSON (Python repr is not JSON)
json.loads("{'a': 1}")          # JSONDecodeError
json.loads('{"a": 1,}')         # JSONDecodeError
json.dumps({"d": datetime.now()})  # TypeError
# Right
json.loads('{"a": 1}')
json.dumps({"d": datetime.now()}, default=str)
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
import json
print(json.dumps({1: "x", 2.5: "y", None: "z", True: "w"}))
print(json.loads('{"a":1,"a":2}'))
print(json.dumps((1, 2)), type(json.loads("[1,2]")).__name__)
print(json.dumps(float("nan")))
```

**Answer**:
```
{"1": "w", "2.5": "y", "null": "z"}
{'a': 2}
[1, 2] list
NaN
```
Keys are converted to strings. `True == 1`, so they are the same dict key and the later value `"w"` wins before JSON even sees it. Duplicate keys in JSON text: the last one wins. Tuples become arrays and come back as lists. Python outputs `NaN`, which is not valid standard JSON (use `allow_nan=False` to get a `ValueError`).

---

## ⚫ Interview Questions + Answers

Q1: `json.dump` vs `json.dumps`?
A1: `dump(obj, file)` writes to a file object; `dumps(obj)` returns a string. The `s` means string. Same for `load`/`loads`.

Q2: How to store a `datetime` or `Decimal`?
A2: Pass `default=` that converts them (isoformat string, str). Or use Pydantic, which does it for you. On load, convert back with `object_hook` or a model.

Q3: Why `ensure_ascii=False`?
A3: By default non-ASCII characters are written as `\uXXXX` escapes. With `False` you get readable Hindi/emoji, so the file must be opened as UTF-8.

Q4: How do you handle a 2 GB JSON?
A4: `json.load` loads everything. Prefer JSON Lines (parse line by line) or a streaming parser such as `ijson`.

Q5: Is `pickle` the same as `json`?
A5: No. `json` is text, language-neutral and safe. `pickle` is Python-only binary and can execute code when loading, so never unpickle untrusted data.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Config files, API payloads, saved chat histories
- Data exchange with JS, mobile apps and other services
- Human-readable data you may diff in Git

❌ Avoid when:
- Huge datasets (use JSON Lines, Parquet or a database)
- You need exact money without conversion (store strings or integers of paise)
- You need comments or binary data (YAML, TOML, bytes/base64)

---

## 📊 Visual Diagram

```
Python object            JSON text
-------------            ---------
dict          --dump-->  { "k": ... }
list / tuple  --dump-->  [ ... ]
str           --dump-->  "text"
int / float   --dump-->  123 / 1.5
True/False    --dump-->  true / false
None          --dump-->  null
              <--load--  (objects come back as dict, arrays as list)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Serialize | Python object -> text | object से text बनाना |
| Deserialize | Text -> Python object | text से object बनाना |
| JSONDecodeError | Raised for invalid JSON | गलत JSON पर आने वाला error |
| ensure_ascii | Escape non-ASCII characters | non-ASCII को escape करना |
| JSON Lines | One JSON per line file | हर line में एक JSON वाली file |
| object_hook | Function run on each decoded object | हर decode हुए object पर चलने वाला function |

---

## ⚡ 3-Line Summary
English: `json.dump/load` work with files and `dumps/loads` with strings. Use `encoding="utf-8"`, `ensure_ascii=False` for Hindi, `default=` for datetime/Decimal, and catch `JSONDecodeError`. Use JSON Lines for big or append-only data.
Hindi: `json.dump/load` files के साथ और `dumps/loads` strings के साथ चलते हैं। `encoding="utf-8"`, Hindi के लिए `ensure_ascii=False`, datetime/Decimal के लिए `default=` और `JSONDecodeError` पकड़ना याद रखें। बड़े या append-only data के लिए JSON Lines इस्तेमाल करें।

---

## ➡️ Next Topic
**209. Binary File Handling** — reading and writing bytes: images, `struct`, and chunked copy.
