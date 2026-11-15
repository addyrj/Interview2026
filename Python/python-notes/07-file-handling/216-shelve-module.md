---

# 216. shelve Module
# हिंदी में: shelve Module (Disk पर persistent dictionary)

---

## 🔵 Simple Definition (English)
`shelve` gives you a persistent dictionary stored on disk. Keys must be strings; values can be almost any picklable Python object. You use it like a normal `dict` (`db['k'] = value`) but the data survives after the program ends.

## 🔵 सरल परिभाषा (Hindi)
`shelve` disk पर रखा हुआ persistent dictionary देता है। Keys सिर्फ़ string होनी चाहिए; values लगभग कोई भी picklable Python object हो सकती है। इसे सामान्य `dict` की तरह इस्तेमाल करते हैं (`db['k'] = value`) पर program खत्म होने के बाद भी data बचा रहता है।

---

## 🔴 Problem it Solves
A small script needs to remember some data between runs (a cache, a counter, user preferences) but a full database is too heavy, and manually calling `pickle.dump` on one big dict rewrites everything for each change. `shelve` stores each key separately in a `dbm` file, so you load and save only the entries you touch.

## 🔴 यह क्यों बना? (Hindi)
एक छोटी script को runs के बीच कुछ data याद रखना है (cache, counter, user preferences) पर पूरा database भारी है, और एक बड़े dict पर हाथ से `pickle.dump` करने पर हर बदलाव में सब कुछ दोबारा लिखना पड़ता है। `shelve` हर key को `dbm` file में अलग रखता है, इसलिए सिर्फ़ छुई हुई entries ही load/save होती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → shelve.open('name') opens (or creates) a dbm file
Step 2 → db['key'] = obj -> obj is pickled and stored under key
Step 3 → db['key'] -> bytes are read and UNPICKLED into a fresh object
Step 4 → Mutating that fresh object does nothing unless writeback=True
Step 5 → writeback=True caches objects and re-saves them on sync()/close()
Step 6 → close() (or the with block) flushes to disk
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → shelve.open('name') dbm file खोलता (या बनाता) है
Step 2 → db['key'] = obj -> obj pickle होकर key के नीचे store होता है
Step 3 → db['key'] -> bytes पढ़कर UNPICKLE होते हैं, यानी हर बार नया object
Step 4 → उस नए object को बदलने का कोई असर नहीं, जब तक writeback=True न हो
Step 5 → writeback=True objects को cache करके sync()/close() पर दोबारा save करता है
Step 6 → close() (या with block) data को disk पर flush करता है
```

---

## 🟡 Real World Example
A CLI tool that downloads exchange rates caches them in a shelf with an expiry time. A Telegram bot remembers each chat's last command between restarts. A scraper stores already-visited URLs so a re-run skips them. For anything with several processes or web traffic, teams use SQLite, Redis or PostgreSQL instead.

## 🟡 Real Example Hindi mein
Exchange rates download करने वाला CLI tool उन्हें expiry time के साथ shelf में cache करता है। Telegram bot restart के बीच हर chat की आखिरी command याद रखता है। Scraper visited URLs store करता है ताकि दोबारा चलाने पर वे skip हों। कई processes या web traffic वाले काम के लिए teams SQLite, Redis या PostgreSQL चुनती हैं।

---

## 💻 Code Example — Basic
```python
import shelve, tempfile, os  # shelve = persistent dict
with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "store")  # base name; backend may add extension
    with shelve.open(path) as db:  # open (creates if missing)
        db["user:1"] = {"name": "Ravi", "age": 30}  # keys MUST be str
        db["nums"] = [1, 2, 3]
    with shelve.open(path) as db:  # reopen: data persisted
        print(sorted(db.keys()))
        print(db["user:1"]["name"], "nums" in db, len(db))
        print(db.get("missing", "default"))
    with shelve.open(path) as db:
        db["nums"].append(4)  # mutation is LOST (no writeback)
        print(db["nums"])
    with shelve.open(path, writeback=True) as db:  # writeback=True caches entries
        db["nums"].append(4)
    with shelve.open(path) as db:
        print(db["nums"])
        del db["nums"]  # delete a key
        print(list(db))
    try:
        with shelve.open(path) as db:
            db[1] = "x"  # int key
    except Exception as e:
        print(type(e).__name__)
    import dbm
    print(dbm.whichdb(path))
```

**Real output** (Python 3.13.3):
```
['nums', 'user:1']
Ravi True 2
default
[1, 2, 3]
[1, 2, 3, 4]
['user:1']
AttributeError
dbm.sqlite3
```

Notes: the file extension and backend depend on the platform (`dbm.sqlite3` is the default on 3.13 when available; earlier versions use `dbm.gnu`, `dbm.ndbm` or `dbm.dumb`), so always pass a base name only. A read-only open of a missing shelf raises `dbm.error` (class name `error`).

## 💻 Code Example — Advanced
```python
from __future__ import annotations
import shelve, tempfile, os, time
from contextlib import contextmanager
from typing import Any, Iterator, Optional


class DiskCache:
    """Tiny TTL cache on top of shelve."""
    def __init__(self, path: str) -> None:
        self.path = path

    @contextmanager
    def _db(self, flag: str = "c") -> Iterator[shelve.Shelf]:
        with shelve.open(self.path, flag=flag) as db:  # 'c' create, 'r' read-only
            yield db

    def set(self, key: str, value: Any, ttl: float = 60) -> None:
        with self._db() as db:
            db[key] = (time.time() + ttl, value)  # store expiry with value

    def get(self, key: str) -> Optional[Any]:
        with self._db() as db:
            item = db.get(key)  # None if absent
            if item is None:
                return None
            expires, value = item
            if expires < time.time():  # expired
                del db[key]
                return None
            return value


with tempfile.TemporaryDirectory() as d:
    cache = DiskCache(os.path.join(d, "cache"))
    cache.set("rate", 83.2, ttl=60)
    cache.set("short", "gone", ttl=0.05)
    time.sleep(0.1)
    print(cache.get("rate"), cache.get("short"), cache.get("none"))
    cache2 = DiskCache(os.path.join(d, "cache"))  # new object, same disk file
    print(cache2.get("rate"))
    try:
        with shelve.open(os.path.join(d, "ro"), flag="r") as db:  # read-only on missing file
            pass
    except Exception as e:
        print(type(e).__name__)
```

**Real output** (Python 3.13.3):
```
83.2 None None
83.2
error
```

This cache is single-process only. Two processes writing the same shelf at once can corrupt it, because `shelve` does no locking.

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
import shelve
with shelve.open("store") as db:
    db["user:1"] = {"name": "Ravi"}   # persists to disk
with shelve.open("store") as db:
    print(db["user:1"]["name"])
```

```javascript
// JavaScript (Node.js) - closest simple options
const Database = require("better-sqlite3");        // npm i better-sqlite3
const db = new Database("store.db");
db.exec("CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v TEXT)");
db.prepare("INSERT OR REPLACE INTO kv VALUES (?, ?)").run("user:1", JSON.stringify({ name: "Ravi" }));
// or: node-persist / lowdb (JSON file based)
```

Node has no built-in persistent dictionary. People use `lowdb`/`node-persist` (JSON files) or SQLite. Python's `shelve` is the quickest option but it is Python-only (pickle) and not safe for concurrent writers.

---

## 🟠 FastAPI Connection
FastAPI services run many workers and threads, so `shelve` is only OK for prototypes or a single-process dev tool. Production code uses Redis or a database. If you do use it, open it per request with a `with` block and remember `shelve` does no locking.

```python
import shelve, tempfile, os
from fastapi import FastAPI
from fastapi.testclient import TestClient
D = tempfile.mkdtemp(); P = os.path.join(D, "hits")
app = FastAPI()
@app.get("/hit/{page}")
def hit(page: str) -> dict[str, int]:
    with shelve.open(P) as db:  # sync def -> runs in threadpool; shelve is NOT multi-process safe
        db[page] = db.get(page, 0) + 1
        return {page: db[page]}
c = TestClient(app)
c.get("/hit/home"); print(c.get("/hit/home").json())
```

**Real output** (Python 3.13.3):
```
{'home': 2}
```


---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Mutating a stored list/dict without writeback
```python
# Wrong - change is silently lost
db["nums"].append(4)

# Right - reassign the value
tmp = db["nums"]; tmp.append(4); db["nums"] = tmp
# or open with shelve.open(path, writeback=True)
```

❌ Mistake 2: Non-string keys
```python
# Wrong
db[1] = "x"            # AttributeError: 'int' object has no attribute 'encode'

# Right
db["1"] = "x"
```

❌ Mistake 3: Not closing the shelf / sharing it across processes
```python
# Wrong - data may not be flushed, no locking between processes
db = shelve.open("store"); db["a"] = 1

# Right
with shelve.open("store") as db:
    db["a"] = 1
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
import shelve, tempfile, os
p = os.path.join(tempfile.mkdtemp(), "db")
with shelve.open(p) as db: db["k"] = [1]
with shelve.open(p) as db:
    db["k"].append(2); print(db["k"])
with shelve.open(p) as db: print(db["k"])
with shelve.open(p, writeback=True) as db: db["k"].append(3)
with shelve.open(p) as db: print(db["k"])
```

**Answer** (real run on Python 3.13.3):
```
[1]
[1]
[1, 3]
```
Each `db['k']` read unpickles a NEW list, so `append(2)` changes a throw-away copy; even the print shows `[1]`. Only `writeback=True` (which keeps the object in a cache and writes it back on close) makes `append(3)` stick, giving `[1, 3]`.

---

## ⚫ Interview Questions + Answers

Q1: What is shelve built on?
A1: `pickle` for serialising values and the `dbm` module for the on-disk key to bytes store. So it inherits pickle's security warning: never open a shelf from an untrusted source.

Q2: What does `writeback=True` do and what is the cost?
A2: It caches every accessed entry in memory and writes them all back on `sync()`/`close()`, so in-place mutation works. Cost: more memory, and a slow close because everything read is re-saved.

Q3: Is shelve thread-safe or process-safe?
A3: No. It has no locking. Protect it with your own `threading.Lock` for threads and use a real database for multiple processes.

Q4: shelve vs sqlite3?
A4: shelve: zero setup, dict API, Python-only, single process. sqlite3: SQL queries, transactions, safe concurrent readers, usable from any language. Prefer SQLite when data matters.

Q5: Why must keys be strings?
A5: The underlying dbm stores bytes keys, so shelve encodes `str` keys itself. Other types fail with an AttributeError.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- A small script or CLI needs a simple persistent cache
- You want dict syntax without designing a schema
- Prototypes where one process owns the file

❌ Avoid when:
- Several processes or web workers write at once
- You need queries, indexes or transactions (use SQLite/Postgres)
- Data comes from untrusted sources (pickle risk)

---

## 📊 Visual Diagram

```
db['a'] = [1,2]            db['a']
     |                          |
  pickle.dumps               dbm lookup 'a'
     v                          v
 +------------+            bytes --pickle.loads--> NEW list
 | dbm file   |                                    (changing it does
 | a -> bytes |                                     not touch the file)
 +------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| shelf | The persistent dict object | disk पर टिका dict |
| dbm | Simple key-bytes database files | key-bytes database |
| writeback | Cache entries, save on close | entries cache करके close पर save |
| sync() | Flush cache to disk | cache को disk पर लिखना |
| Persistent | Survives program restart | program बंद होने के बाद भी बना रहे |
| Locking | Preventing simultaneous writes | एक साथ लिखने से रोकना |

---

## ⚡ 3-Line Summary
English: `shelve` is a pickle-backed dictionary on disk with string keys. Remember that reading returns a copy, so reassign changed values or use `writeback=True`. It is single-process only; use SQLite or Redis for real services.
Hindi: `shelve` disk पर pickle-आधारित dictionary है जिसकी keys string होती हैं। याद रखें कि पढ़ने पर copy मिलती है, इसलिए बदली value दोबारा assign करें या `writeback=True` लें। यह सिर्फ़ single-process के लिए है; असली services के लिए SQLite या Redis लें।

---

## ➡️ Next Topic
**217. Configuration Files** — INI, JSON, TOML and environment variables for app settings.
