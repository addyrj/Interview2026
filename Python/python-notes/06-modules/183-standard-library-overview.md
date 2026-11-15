---

# 183. Standard Library Overview
# हिंदी में: Standard Library का परिचय ("batteries included")

---

## 🔵 Simple Definition (English)
The standard library is the large set of modules that ships with Python itself, so you can import them without `pip install`. It covers files, dates, JSON, HTTP, regular expressions, testing, concurrency, math, databases (SQLite) and more. Python calls this "batteries included".

## 🔵 सरल परिभाषा (Hindi)
Standard library उन modules का बड़ा समूह है जो Python के साथ ही आता है, इसलिए `pip install` के बिना import होता है। इसमें files, dates, JSON, HTTP, regular expressions, testing, concurrency, math, database (SQLite) वगैरह हैं। Python इसे "batteries included" कहता है।

---

## 🔴 Problem it Solves
Without a rich standard library every project would depend on dozens of third-party packages for basics, creating version conflicts and security risk. Knowing the stdlib means you write less code, add fewer dependencies, and avoid reinventing (badly) things like date parsing or argument handling.

## 🔴 यह क्यों बना? (Hindi)
Rich standard library न हो तो हर project को basics के लिए दर्जनों third-party packages चाहिए, जिनसे version conflicts और security risk बढ़ते हैं। Stdlib जानने से कम code लिखना पड़ता है, dependencies कम रहती हैं और date parsing या argument handling जैसी चीज़ें गलत तरीके से दोबारा नहीं बनानी पड़तीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → `import json` : found in the stdlib folder (listed on sys.path)
Step 2 → Some modules are pure Python (.py), some are C extensions (math, _json)
Step 3 → Same import rules as any module: cached in sys.modules
Step 4 → sys.stdlib_module_names (3.10+) lists every stdlib top-level name
Step 5 → Not installed by pip, versioned with Python itself (3.12 vs 3.13 differ)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → `import json` : stdlib folder (sys.path में) में मिलता है
Step 2 → कुछ modules pure Python (.py), कुछ C extensions (math, _json) हैं
Step 3 → import के नियम वही हैं: sys.modules में cache
Step 4 → sys.stdlib_module_names (3.10+) सारे stdlib नामों की list देता है
Step 5 → pip से नहीं आता, Python के version के साथ बदलता है (3.12 बनाम 3.13)
```

---

## 🟡 Real World Example
A Swiggy ops script: `pathlib` to find CSVs, `csv` to read, `datetime` for delivery times, `collections.Counter` to count orders per area, `logging` for audit, `argparse` for CLI flags, `sqlite3` for a local cache, `subprocess` to call `git`. Zero pip packages.

## 🟡 Real Example Hindi mein
Swiggy की ops script: CSV खोजने को `pathlib`, पढ़ने को `csv`, delivery time के लिए `datetime`, area-wise orders गिनने को `collections.Counter`, audit के लिए `logging`, CLI flags के लिए `argparse`, local cache के लिए `sqlite3`, `git` चलाने को `subprocess`। एक भी pip package नहीं।

---

## 💻 Code Example — Basic
```python
# A tour of useful stdlib modules - every line commented
import json  # JSON encode/decode
import re  # regular expressions
import hashlib  # hashes
import base64  # base64 encoding
import statistics  # mean/median
import subprocess  # run other programs
import urllib.parse  # URL parsing
import uuid  # unique ids
from collections import Counter  # counting
from decimal import Decimal  # exact decimal maths
from itertools import count, islice  # lazy iteration tools

print(json.dumps({"a": [1, 2]}))  # dict -> JSON text
# Output: {"a": [1, 2]}
print(re.findall(r"\d+", "a1b22"))  # all digit groups
# Output: ['1', '22']
print(hashlib.sha256(b"hi").hexdigest()[:12])  # first 12 hex chars of the hash
# Output: 8f434346648f
print(base64.b64encode(b"hi"))  # bytes -> base64 bytes
# Output: b'aGk='
print(statistics.mean([1, 2, 3, 4]))  # average
# Output: 2.5
print(urllib.parse.urlparse("https://x.com/a?b=1").query)  # URL part
# Output: b=1
print(uuid.UUID(int=1))  # deterministic UUID for the demo
# Output: 00000000-0000-0000-0000-000000000001
print(Counter("aab").most_common(1))  # most frequent element
# Output: [('a', 2)]
print(Decimal("0.1") + Decimal("0.2"))  # exact money maths (float gives 0.30000000000000004)
# Output: 0.3
print(list(islice(count(5), 3)))  # first 3 of an infinite counter
# Output: [5, 6, 7]
print(subprocess.run(["echo", "hi"], capture_output=True, text=True).stdout.strip())  # run a command
# Output: hi
```

## 💻 Code Example — Advanced
```python
# Stdlib-only mini app: parse log lines, aggregate, store in SQLite, report - no pip.
import csv  # CSV reading
import io  # in-memory text file
import logging  # structured logs
import sqlite3  # embedded database
import statistics  # median
from collections import defaultdict  # grouping
from dataclasses import dataclass  # lightweight records
from datetime import datetime  # timestamps
from typing import Dict, List  # type hints

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")  # log setup
log = logging.getLogger("etl")  # named logger

RAW: str = "order_id,area,minutes\n1,Indiranagar,31\n2,Koramangala,24\n3,Indiranagar,45\n4,Koramangala,x\n"


@dataclass(frozen=True)
class Delivery:
    order_id: int  # primary key
    area: str  # delivery area
    minutes: int  # time taken


def parse(text: str) -> List[Delivery]:
    """Parse rows, skipping and logging bad ones."""
    rows: List[Delivery] = []  # good rows
    for row in csv.DictReader(io.StringIO(text)):  # iterate dict rows
        try:
            rows.append(Delivery(int(row["order_id"]), row["area"], int(row["minutes"])))
        except ValueError:  # e.g. minutes = "x"
            log.warning("skipping bad row %s", row["order_id"])  # audit trail
    return rows  # clean data


def main() -> Dict[str, float]:
    items = parse(RAW)  # extract
    with sqlite3.connect(":memory:") as db:  # in-memory database
        db.execute("CREATE TABLE d (id INTEGER PRIMARY KEY, area TEXT, minutes INT)")
        db.executemany("INSERT INTO d VALUES (?, ?, ?)", [(i.order_id, i.area, i.minutes) for i in items])
        by_area: Dict[str, List[int]] = defaultdict(list)  # group minutes by area
        for area, minutes in db.execute("SELECT area, minutes FROM d"):
            by_area[area].append(minutes)  # collect
    report = {a: statistics.median(m) for a, m in by_area.items()}  # median per area
    log.info("done at %s", datetime(2024, 1, 1).isoformat())  # fixed date for stable output
    return report


print(main())  # run it
# Output (log lines go to stderr):
#   WARNING skipping bad row 4
#   INFO done at 2024-01-01T00:00:00
# Output: {'Indiranagar': 38.0, 'Koramangala': 24}
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python stdlib
import json, pathlib, hashlib, datetime, argparse
data = json.loads(pathlib.Path("a.json").read_text())      # file + JSON, no installs
```

```javascript
// Node core modules + common npm packages
import fs from "node:fs/promises";            // core
import crypto from "node:crypto";             // core (hash)
const data = JSON.parse(await fs.readFile("a.json", "utf8"));
// Dates: no rich stdlib -> dayjs / date-fns (npm); CLI args: commander / yargs (npm)
```

Key difference: Python's stdlib covers dates, CSV, SQLite, argument parsing, unit tests and more; in Node you often add npm packages for those.

---

## 🟠 FastAPI Connection
FastAPI itself is a thin layer: you still use `uuid` for ids, `datetime` for timestamps, `logging`, `pathlib`, `hashlib`/`secrets` for tokens, `asyncio` for concurrency, `contextlib` for lifespan, `enum` for choices and `typing` for models.

```python
# Stdlib-heavy FastAPI endpoint (needs: pip install fastapi)
import secrets  # secure random tokens
import uuid  # ids
from datetime import datetime, timezone  # timezone-aware time
from enum import Enum  # fixed choices
from fastapi import FastAPI  # framework


class Plan(str, Enum):  # enum used as a validated query parameter
    free = "free"
    pro = "pro"


app: FastAPI = FastAPI()  # app


@app.post("/keys")  # POST /keys?plan=pro
def create_key(plan: Plan) -> dict[str, str]:
    return {  # all values from the standard library
        "id": str(uuid.uuid4()),  # unique id
        "token": secrets.token_urlsafe(16),  # unguessable token
        "plan": plan.value,  # chosen plan
        "created": datetime.now(timezone.utc).isoformat(),  # UTC timestamp
    }
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Installing a package for something the stdlib does
```python
# Wrong: pip install simplejson / python-dateutil for basic JSON / dates
# Correct: json, datetime (3.9+ zoneinfo for time zones)
```

❌ Mistake 2: Using insecure/outdated stdlib parts
```python
# Wrong: random.choice for tokens, pickle on untrusted data, md5 for passwords
# Correct: secrets.token_urlsafe(), json, hashlib.scrypt / a password library
```

❌ Mistake 3: Using `float` for money and naive datetimes
```python
# Wrong: 0.1 + 0.2 -> 0.30000000000000004 ; datetime.utcnow() (deprecated since 3.12)
# Correct: Decimal("0.1") + Decimal("0.2") ; datetime.now(timezone.utc)
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
import sys
print("json" in sys.stdlib_module_names)
print("requests" in sys.stdlib_module_names)
print(sys.stdlib_module_names.__class__.__name__)
```

**Answer**:
```
True
False
frozenset
```
`sys.stdlib_module_names` (Python 3.10+) is a frozenset of top-level stdlib names. `requests` is third-party and needs `pip`. Removed modules differ by version: for example `distutils`, `imp` and `asynchat` were removed in Python 3.12, `cgi`, `telnetlib` and `pipes` in 3.13.

---

## ⚫ Interview Questions + Answers

Q1: How do you know whether a module is stdlib or third-party?
A1: Check `sys.stdlib_module_names`, or look where `module.__file__` lives: stdlib is under `lib/python3.x/`, third-party under `site-packages`.

Q2: Name five stdlib modules you use daily.
A2: `pathlib`, `json`, `datetime`, `collections`, `logging` (also `typing`, `itertools`, `functools`, `asyncio`, `re`).

Q3: `os.path` vs `pathlib`?
A3: `pathlib.Path` is the modern object-oriented API (`/` operator, `read_text`); `os.path` is older string-based functions. Prefer `pathlib`.

Q4: Is the stdlib always better than a third-party package?
A4: No. `requests`/`httpx` beat `urllib`; `pytest` beats `unittest` for ergonomics; `pydantic` beats `dataclasses` for validation. Use stdlib first, then upgrade when you hit a real limit.

Q5: Which stdlib parts changed recently?
A5: 3.11 added `tomllib`; 3.12 removed `distutils` and `asyncore`; 3.13 removed 19 "dead batteries" (`cgi`, `crypt`, `telnetlib`...) and added experimental free-threading and JIT builds.

---

## 🔷 When to Use + When Not to Use

✅ Use stdlib when:
- Scripts, CLIs, small services, and zero-dependency libraries
- Security matters (fewer dependencies to audit)
- Behaviour must stay stable for years

❌ Avoid stdlib-only when:
- A mature third-party tool is far better (HTTP clients, data frames, validation)
- You need features stdlib lacks (async DB drivers, ML)
- Performance requires NumPy-style C-speed arrays

---

## 📊 Visual Diagram

```
 Python install
 ├── stdlib  (no pip)
 │    text: re, string, textwrap      data: json, csv, sqlite3, pickle
 │    files: pathlib, os, shutil, tempfile, glob
 │    time: datetime, zoneinfo, time  math: math, statistics, decimal, random
 │    types: typing, dataclasses, enum, collections, itertools, functools
 │    runtime: sys, os, logging, argparse, subprocess, threading, asyncio
 │    net: http, urllib, socket, ssl, email   test: unittest, doctest
 └── site-packages (pip: fastapi, pydantic, requests ...)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Standard library | Modules shipped with Python | Python के साथ आने वाले modules |
| Batteries included | Rich built-in tools | सब कुछ साथ में |
| Third-party | Installed via pip | pip से आने वाला |
| C extension | Module written in C | C में लिखा module |
| Deprecated | Planned for removal | हटाए जाने वाला |
| Dependency | Package your code needs | आपके code की निर्भरता |

---

## ⚡ 3-Line Summary
English: The standard library ships with Python and covers files, dates, JSON, regex, SQLite, logging, CLI and concurrency. Prefer it first to keep dependencies low, then add third-party tools for real gaps. Check version notes, since modules get removed.
Hindi: Standard library Python के साथ आती है और files, dates, JSON, regex, SQLite, logging, CLI, concurrency सँभालती है। पहले इसे चुनें ताकि dependencies कम रहें, फिर असली कमी पर third-party जोड़ें। Version notes देखें क्योंकि modules हटते रहते हैं।

---

## ➡️ Next Topic
**184. os Module — Complete Guide** — the first deep dive into a stdlib module: files, environment variables and processes.
