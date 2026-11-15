---

# 190. json Module
# हिंदी में: json Module (Python data ↔ JSON text)

---

## 🔵 Simple Definition (English)
`json` converts Python objects (dict, list, str, int, float, bool, None) to JSON text with `dumps` / `dump`, and JSON text back to Python objects with `loads` / `load`. JSON is the common data format of web APIs and config files.

## 🔵 सरल परिभाषा (Hindi)
`json` Python objects (dict, list, str, int, float, bool, None) को `dumps` / `dump` से JSON text में बदलता है, और JSON text को `loads` / `load` से वापस Python objects में। JSON web APIs और config files का सबसे आम data format है।

---

## 🔴 Problem it Solves
Programs written in different languages need a shared text format to exchange data. Python's `str(dict)` or `pickle` are not understood by JavaScript, mobile apps or other services (and `pickle` is unsafe on untrusted data). `json` gives a standard, language independent, human readable format.

## 🔴 यह क्यों बना? (Hindi)
अलग-अलग भाषाओं के programs को data बाँटने के लिए एक साझा text format चाहिए। Python का `str(dict)` या `pickle` JavaScript, mobile apps या दूसरी services नहीं समझतीं (और untrusted data पर `pickle` असुरक्षित है)। `json` एक standard, भाषा-निरपेक्ष, इंसान को पढ़ने लायक format देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → dumps(obj): walks the object and writes JSON text
Step 2 → Mapping: dict→object, list/tuple→array, str→string, int/float→number,
         True/False→true/false, None→null
Step 3 → Unknown types (datetime, Decimal, set...) → TypeError unless default= is given
Step 4 → loads(text): parses text, objects become dict, arrays become list
Step 5 → Hooks: object_hook, parse_float, parse_int customise decoding
Step 6 → dump/load (no "s") work with file objects, dumps/loads with strings
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → dumps(obj): object को घूमकर JSON text लिखता है
Step 2 → Mapping: dict→object, list/tuple→array, str→string, int/float→number,
         True/False→true/false, None→null
Step 3 → अनजान types (datetime, Decimal, set...) → TypeError, जब तक default= न दिया हो
Step 4 → loads(text): text parse करके objects को dict और arrays को list बनाता है
Step 5 → Hooks: object_hook, parse_float, parse_int decoding बदलने देते हैं
Step 6 → dump/load (बिना "s") file objects के साथ, dumps/loads strings के साथ
```

---

## 🟡 Real World Example
A Razorpay webhook sends a JSON body; your service parses it, verifies the signature on the raw bytes, and stores the payload. A Swiggy backend caches restaurant menus as JSON strings in Redis. An AI app asks an LLM for structured output, then calls `json.loads` on the reply (inside try/except, because models sometimes return broken JSON).

## 🟡 Real Example Hindi mein
Razorpay webhook JSON body भेजता है; आपकी service उसे parse करती है, raw bytes पर signature verify करती है और payload store करती है। Swiggy backend restaurant menus को JSON string के रूप में Redis में cache करता है। AI app LLM से structured output माँगकर reply पर `json.loads` चलाती है (try/except में, क्योंकि model कभी-कभी टूटा JSON देता है)।

---

## 💻 Code Example — Basic
```python
# Basic json examples - every line commented
import json  # standard JSON library
import tempfile  # for the file demo
from pathlib import Path  # file path

user: dict = {"name": "Asha", "age": 28, "active": True, "tags": ["ai", "api"], "boss": None}  # Python dict
text: str = json.dumps(user)  # Python -> JSON string
print(text)  # True->true, None->null
back: dict = json.loads(text)  # JSON string -> Python
print(back == user, type(back["active"]).__name__)  # round trip works

print(json.dumps(user, indent=2, sort_keys=True))  # pretty + sorted keys
print(json.dumps(user, separators=(",", ":")))  # compact (smallest size)
print(json.dumps({"city": "दिल्ली"}))  # non-ASCII escaped by default
print(json.dumps({"city": "दिल्ली"}, ensure_ascii=False))  # keep real characters

with tempfile.TemporaryDirectory() as tmp:  # sandbox
    f: Path = Path(tmp) / "user.json"  # file path
    with f.open("w", encoding="utf-8") as fh:  # open for writing
        json.dump(user, fh, ensure_ascii=False)  # dump (no s) writes to a file
    with f.open(encoding="utf-8") as fh:  # open for reading
        loaded: dict = json.load(fh)  # load (no s) reads from a file
    print(loaded["tags"])  # ['ai', 'api']

try:  # invalid JSON
    json.loads("{'a': 1}")  # single quotes are not valid JSON
except json.JSONDecodeError as exc:  # specific error
    print("JSONDecodeError:", exc.msg, "at line", exc.lineno, "col", exc.colno)

print(json.dumps({1: "a", 2.5: "b", True: "c"}))  # keys become strings; True == 1, so those two keys merge!
print(json.loads('{"n": 1, "f": 1.5, "big": 12345678901234567890}'))  # ints stay ints
```

Output (verified by running; ids/timestamps/paths may vary):
```
{"name": "Asha", "age": 28, "active": true, "tags": ["ai", "api"], "boss": null}
True bool
{
  "active": true,
  "age": 28,
  "boss": null,
  "name": "Asha",
  "tags": [
    "ai",
    "api"
  ]
}
{"name":"Asha","age":28,"active":true,"tags":["ai","api"],"boss":null}
{"city": "\u0926\u093f\u0932\u094d\u0932\u0940"}
{"city": "दिल्ली"}
['ai', 'api']
JSONDecodeError: Expecting property name enclosed in double quotes at line 1 col 2
{"1": "c", "2.5": "b"}
{'n': 1, 'f': 1.5, 'big': 12345678901234567890}
```

## 💻 Code Example — Advanced
```python
# Production style: custom types, hooks, safe parsing, JSON Lines, NaN handling
import json  # JSON library
from dataclasses import asdict, dataclass  # dataclass -> dict
from datetime import date, datetime, timezone  # date types
from decimal import Decimal  # money type
from enum import Enum  # enum type
from typing import Any, Dict, Iterator, List  # type hints
from uuid import UUID, uuid5, NAMESPACE_DNS  # uuid type


class Status(str, Enum):
    PAID = "paid"  # enum value
    FAILED = "failed"  # enum value


@dataclass
class Payment:
    id: UUID  # unique id
    amount: Decimal  # money must not be float
    status: Status  # enum
    created: datetime  # timestamp
    due: date  # date only


def encode_default(obj: Any) -> Any:
    """Called by json only for objects it does not know."""
    if isinstance(obj, (datetime, date)):  # dates
        return obj.isoformat()  # ISO 8601 string
    if isinstance(obj, Decimal):  # money
        return str(obj)  # string keeps exact value
    if isinstance(obj, UUID):  # ids
        return str(obj)  # canonical string
    if isinstance(obj, Enum):  # enums
        return obj.value  # underlying value
    if isinstance(obj, set):  # sets
        return sorted(obj)  # JSON has no set -> list
    raise TypeError(f"{type(obj).__name__} is not JSON serializable")  # keep the contract


pay: Payment = Payment(
    id=uuid5(NAMESPACE_DNS, "example.com"),  # fixed uuid for a stable demo
    amount=Decimal("199.90"),  # exact decimal
    status=Status.PAID,  # enum
    created=datetime(2025, 11, 10, 9, 30, tzinfo=timezone.utc),  # aware datetime
    due=date(2025, 11, 30),  # date
)
payload: str = json.dumps(asdict(pay), default=encode_default, indent=2)  # custom encode
print(payload)

try:  # without default= the call fails
    json.dumps({"amount": Decimal("1.5")})  # Decimal unknown
except TypeError as exc:  # expected
    print("TypeError:", exc)  # message

# Decode back: parse_float=Decimal keeps money exact
data: Dict[str, Any] = json.loads('{"amount": 199.90, "qty": 2}', parse_float=Decimal)
print(data, type(data["amount"]).__name__)  # Decimal('199.90')
print(json.loads('{"amount": 199.90}')["amount"] + 0.0)  # default float

# object_hook turns every decoded dict into something richer
def revive(d: Dict[str, Any]) -> Dict[str, Any]:
    if "due" in d:  # our own marker
        d["due"] = date.fromisoformat(d["due"])  # string -> date
    return d  # always return the dict

print(json.loads('{"due": "2025-11-30"}', object_hook=revive))  # revived date

# NaN is NOT valid JSON, ask for strict output
try:  # allow_nan=False raises on NaN/Infinity
    json.dumps({"x": float("nan")}, allow_nan=False)  # would produce invalid JSON otherwise
except ValueError as exc:  # expected
    print("ValueError:", exc)  # message
print(json.dumps({"x": float("nan")}))  # default writes NaN (invalid for JS/most parsers)

# JSON Lines: one JSON per line, great for big logs and streaming
def read_jsonl(lines: List[str]) -> Iterator[Dict[str, Any]]:
    for line in lines:  # one record per line
        if line.strip():  # skip blank lines
            yield json.loads(line)  # parse lazily

print(list(read_jsonl(['{"a": 1}', "", '{"a": 2}'])))  # two records
```

Output (verified by running; ids/timestamps/paths may vary):
```
{
  "id": "cfbff0d1-9375-5685-968c-48ce8b15ae17",
  "amount": "199.90",
  "status": "paid",
  "created": "2025-11-10T09:30:00+00:00",
  "due": "2025-11-30"
}
TypeError: Object of type Decimal is not JSON serializable
{'amount': Decimal('199.90'), 'qty': 2} Decimal
199.9
{'due': datetime.date(2025, 11, 30)}
ValueError: Out of range float values are not JSON compliant: nan
{"x": NaN}
[{'a': 1}, {'a': 2}]
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
import json
s = json.dumps({"a": 1, "ok": True, "x": None})   # '{"a": 1, "ok": true, "x": null}'
obj = json.loads(s)                               # dict
pretty = json.dumps(obj, indent=2)
```

```javascript
// JavaScript
const s = JSON.stringify({ a: 1, ok: true, x: null });   // '{"a":1,"ok":true,"x":null}'
const obj = JSON.parse(s);                               // object
const pretty = JSON.stringify(obj, null, 2);
```

Key differences: `JSON.stringify` is compact by default; Python's `dumps` adds spaces after `,` and `:` (use `separators=(",", ":")` to match). Python escapes non-ASCII by default (`ensure_ascii=True`). Python can write `NaN` / `Infinity` (invalid JSON) unless `allow_nan=False`; `JSON.stringify` turns them into `null`. Python's `json.loads` keeps big integers exact; JavaScript loses precision above 2^53.

---

## 🟠 FastAPI Connection
FastAPI uses Pydantic to turn request JSON into typed models and response models back into JSON, so you rarely call `json` directly. `jsonable_encoder` converts datetimes, Decimals and models into JSON-safe Python values (for Redis, databases). Invalid JSON gives HTTP 422 automatically. Use `json` yourself for webhooks (raw body signature), caches and files.

```python
# FastAPI: how JSON conversion works (pip install fastapi httpx)
from datetime import datetime, timezone  # timestamps
from decimal import Decimal  # money
from typing import Any, Dict  # type hints
from fastapi import Body, FastAPI  # app + body
from fastapi.encoders import jsonable_encoder  # python -> JSON-safe python
from pydantic import BaseModel  # data model

app: FastAPI = FastAPI()  # create app


class Order(BaseModel):
    id: int  # order id
    total: Decimal  # money
    placed: datetime  # time


@app.post("/orders")  # POST /orders
def create(order: Order) -> Order:  # FastAPI parses JSON -> Order, and Order -> JSON
    return order  # no json.dumps needed


@app.post("/raw")  # POST /raw
def raw(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    return {"keys": sorted(payload)}  # any JSON object accepted
```

Output (verified by running; ids/timestamps/paths may vary):
```
200 {'id': 1, 'total': '199.90', 'placed': '2025-11-10T09:30:00Z'}
{'keys': ['a', 'b']}
422
{'t': '2025-01-01T00:00:00+00:00', 'd': 1.5}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Serialising datetime / Decimal / set directly
```python
# Wrong - TypeError: Object of type datetime is not JSON serializable
# json.dumps({"t": datetime.now()})

# Correct
# json.dumps({"t": datetime.now()}, default=str)    # quick
# json.dumps(data, default=encode_default)          # explicit, better
```

❌ Mistake 2: Mixing up `dump`/`dumps` and `load`/`loads`
```python
# Wrong - AttributeError: 'str' object has no attribute 'read'
# json.load('{"a": 1}')

# Correct
# json.loads('{"a": 1}')            # string
# json.load(open("a.json"))         # file object
```

❌ Mistake 3: Using floats for money, and trusting `loads` output shape
```python
# Wrong - float rounding, and KeyError if the client omitted a field
# price = json.loads(body)["price"] * 100

# Correct - exact decimals + validate with Pydantic
# data = json.loads(body, parse_float=Decimal)
# order = Order.model_validate(data)
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
import json
print(json.dumps({1: "a", True: "b", None: "c"}))
print(json.loads("[1, 2.0, true, null]"))
print(json.dumps((1, 2)), json.loads(json.dumps((1, 2))) == (1, 2))
print(json.loads('{"a": 1, "a": 2}'))
print(json.dumps("é"), json.dumps(float("inf")))
```

**Answer**:
```
{"1": "b", "null": "c"}
[1, 2.0, True, None]
[1, 2] False
{'a': 2}
"\u00e9" Infinity
```
`1` and `True` are the same dictionary key (`True == 1`), so the later value `"b"` wins and the keys are turned into strings. A tuple becomes an array and returns as a list, so the round trip is not equal to a tuple. Duplicate keys do not raise; the last one wins. Non-ASCII is escaped, and `Infinity` is written even though it is invalid JSON. (Verified by running.)

---

## ⚫ Interview Questions + Answers

Q1: `json.dumps` vs `json.dump`?
A1: `dumps` returns a string; `dump` writes to a file-like object. Same for `loads` (from string) and `load` (from file). The "s" means "string".

Q2: How do you serialise a custom class or a datetime?
A2: Pass `default=func` to `dumps`; it receives unknown objects and returns something JSON can handle (string, dict, list). Or convert first with `dataclasses.asdict` / Pydantic `model_dump(mode="json")`.

Q3: Why is `json` safer than `pickle`?
A3: JSON only builds basic data (dict, list, str, numbers). `pickle` can execute arbitrary code while loading, so never unpickle untrusted data.

Q4: How do you read a very large JSON file?
A4: `json.load` loads everything into RAM. For huge data use JSON Lines (one object per line, read line by line) or a streaming parser like `ijson`.

Q5: Does `json` keep key order?
A5: Yes. Since Python 3.7 dict keeps insertion order and `dumps` writes it in that order. `sort_keys=True` makes the output stable for hashing or diffs.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Talking to web APIs, webhooks, browsers and other languages
- Config files and simple caches
- Logging structured events (JSON Lines)

❌ Avoid when:
- You need comments or complex types in config (use TOML/YAML)
- Data is huge and binary (use Parquet, MessagePack, protobuf)
- You need to restore arbitrary Python objects (JSON loses types: tuple, set, datetime)

---

## 📊 Visual Diagram

```
  Python                dumps ──►          JSON text
  dict    {"a": 1}                         {"a": 1}
  list/tuple [1, 2]                        [1, 2]
  str     "hi"                             "hi"
  int/float 1 / 1.5                        1 / 1.5
  True/False/None                          true/false/null
          ◄── loads
  (datetime, Decimal, set ✖ need default= / object_hook)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Serialize | Python object → text | object को text बनाना |
| Deserialize | Text → Python object | text को object बनाना |
| `default=` | Function for unknown types when dumping | अनजान types के लिए function |
| `object_hook` | Function called for each decoded dict | हर decoded dict पर चलने वाला function |
| JSON Lines | One JSON object per line | हर line में एक JSON |
| ensure_ascii | Escape non-ASCII characters | non-ASCII को escape करना |

---

## ⚡ 3-Line Summary
English: `json.dumps/loads` work with strings and `dump/load` with files. JSON only knows dict, list, str, number, bool and null, so use `default=` / `object_hook` (or Pydantic) for dates, money and custom types.
Hindi: `json.dumps/loads` strings के साथ और `dump/load` files के साथ चलते हैं। JSON सिर्फ dict, list, str, number, bool और null जानता है, इसलिए dates, money और custom types के लिए `default=` / `object_hook` (या Pydantic) इस्तेमाल करें।

---

## ➡️ Next Topic
**191. csv Module** — read and write table data (rows and columns) that spreadsheets understand.
