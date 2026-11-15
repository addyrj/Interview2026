---

# 215. Pickle Module
# हिंदी में: Pickle Module (Python objects को bytes में बदलना)

---

## 🔵 Simple Definition (English)
`pickle` converts almost any Python object (dicts, sets, class instances, nested structures) into bytes (`dumps`/`dump`) and rebuilds it later (`loads`/`load`). It is Python-only and NOT safe for untrusted input, because loading a pickle can run arbitrary code.

## 🔵 सरल परिभाषा (Hindi)
`pickle` लगभग किसी भी Python object (dict, set, class instance, nested structure) को bytes में बदलता है (`dumps`/`dump`) और बाद में वापस बना देता है (`loads`/`load`)। यह सिर्फ़ Python के लिए है और untrusted input के लिए सुरक्षित नहीं, क्योंकि pickle load करते समय कोई भी code चल सकता है।

---

## 🔴 Problem it Solves
JSON only handles basic types: no sets, tuples (they become lists), custom classes, or shared references. To save a trained model, a cache entry or a worker's task between processes, you needed a format that keeps full Python objects. Pickle does that with almost no code, which is why `multiprocessing`, `joblib` and scikit-learn use it internally.

## 🔴 यह क्यों बना? (Hindi)
JSON सिर्फ़ basic types संभालता है: set नहीं, tuple list बन जाता है, custom class और shared references नहीं। Trained model, cache entry या processes के बीच task सहेजने के लिए ऐसा format चाहिए था जो पूरे Python objects रखे। Pickle यह लगभग बिना code के करता है, इसीलिए `multiprocessing`, `joblib` और scikit-learn इसे अंदर इस्तेमाल करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → pickle.dumps(obj) walks the object graph
Step 2 → Writes opcodes: 'import module.Class, build it, set its state'
Step 3 → Result is bytes (protocol 4 default in 3.13, 5 highest)
Step 4 → pickle.loads(bytes) executes those opcodes
Step 5 → Class is found by NAME (module.qualname) and __init__ is NOT called
Step 6 → Danger: __reduce__ can name ANY callable, so loads() can run os.system
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → pickle.dumps(obj) object graph पर चलता है
Step 2 → opcodes लिखता है: 'module.Class import करो, बनाओ, state set करो'
Step 3 → नतीजा bytes है (3.13 में default protocol 4, highest 5)
Step 4 → pickle.loads(bytes) उन opcodes को execute करता है
Step 5 → class NAME (module.qualname) से मिलती है और __init__ call नहीं होता
Step 6 → खतरा: __reduce__ कोई भी callable बता सकता है, इसलिए loads() os.system चला सकता है
```

---

## 🟡 Real World Example
An ML service saves a fitted scikit-learn pipeline with `joblib.dump` (pickle based) and loads it at startup. A job queue (RQ) pickles function arguments for workers. A server caches an expensive computed object in Redis as bytes it wrote itself. A security review rejects code that unpickles files uploaded by users.

## 🟡 Real Example Hindi mein
ML service fitted scikit-learn pipeline को `joblib.dump` (pickle based) से save करती है और startup पर load करती है। Job queue (RQ) workers के लिए function arguments pickle करती है। Server महँगी गणना वाला object खुद लिखे bytes के रूप में Redis में cache करता है। Security review में वह code reject होता है जो users की upload की हुई files unpickle करे।

---

## 💻 Code Example — Basic
```python
import pickle, io  # pickle module
from dataclasses import dataclass

data = {"name": "Asha", "scores": [1, 2, 3], "tags": {"a", "b"}, "pt": (1, 2)}  # many types
blob: bytes = pickle.dumps(data)  # object -> bytes
print(type(blob).__name__, blob[:2])
back = pickle.loads(blob)  # bytes -> object
print(back == data, back is data)

with open("/dev/null", "wb") as fh:  # file API shown with a real temp file below
    pass
import tempfile, os
with tempfile.NamedTemporaryFile(delete=False) as f:
    pickle.dump([1, 2, 3], f)  # write to file
    name = f.name
with open(name, "rb") as f:  # must be binary mode
    print(pickle.load(f))
os.remove(name)

shared = [1]
obj = [shared, shared]  # same list twice
copy = pickle.loads(pickle.dumps(obj))
print(copy[0] is copy[1])  # sharing preserved

try:
    pickle.dumps(lambda x: x)  # lambdas can't be pickled
except Exception as e:
    print(type(e).__name__, e)

@dataclass
class P:
    x: int
print(pickle.loads(pickle.dumps(P(5))))  # classes need to be importable by name
print(pickle.HIGHEST_PROTOCOL, pickle.DEFAULT_PROTOCOL)
```

**Real output** (Python 3.13.3):
```
bytes b'\x80\x04'
True False
[1, 2, 3]
True
PicklingError Can't pickle <function <lambda> at 0x101337880>: attribute lookup <lambda> on __main__ failed
P(x=5)
5 4
```

Notes: the `PicklingError` message contains a memory address that varies. Unpickling does not call `__init__`; it restores the stored state directly.

## 💻 Code Example — Advanced
```python
from __future__ import annotations
import hashlib, hmac, io, json, pickle
from typing import Any


class RestrictedUnpickler(pickle.Unpickler):
    """Only allow a tiny whitelist of classes - blocks arbitrary code execution."""
    ALLOWED = {("builtins", "set"), ("builtins", "frozenset")}

    def find_class(self, module: str, name: str) -> Any:
        if (module, name) in self.ALLOWED:
            return super().find_class(module, name)
        raise pickle.UnpicklingError(f"forbidden: {module}.{name}")


def safe_loads(blob: bytes) -> Any:
    return RestrictedUnpickler(io.BytesIO(blob)).load()


class Evil:
    def __reduce__(self):  # tells pickle how to rebuild -> runs a callable on load!
        import os
        return (os.getcwd, ())  # harmless demo; attacker would use os.system


blob = pickle.dumps(Evil())
print(type(pickle.loads(blob)).__name__)  # str: os.getcwd() RAN during loads
try:
    safe_loads(blob)
except pickle.UnpicklingError as e:
    print("blocked:", e)
print(safe_loads(pickle.dumps({1, 2})))

SECRET = b"server-secret"
def sign(b: bytes) -> bytes:
    return hmac.new(SECRET, b, hashlib.sha256).digest() + b
def verify(s: bytes) -> bytes:
    mac, b = s[:32], s[32:]
    if not hmac.compare_digest(mac, hmac.new(SECRET, b, hashlib.sha256).digest()):
        raise ValueError("tampered")
    return b
s = sign(pickle.dumps([1, 2]))
print(pickle.loads(verify(s)))
try:
    verify(s[:-1] + b"X")
except ValueError as e:
    print(e)

class Conn:
    def __init__(self) -> None:
        self.url = "db://x"; self.sock = object()  # unpicklable-ish runtime resource
    def __getstate__(self) -> dict[str, Any]:
        return {"url": self.url}  # drop the socket
    def __setstate__(self, st: dict[str, Any]) -> None:
        self.url = st["url"]; self.sock = object()  # recreate
c2 = pickle.loads(pickle.dumps(Conn()))
print(c2.url)
```

**Real output** (Python 3.13.3):
```
str
blocked: forbidden: posix.getcwd
{1, 2}
[1, 2]
tampered
db://x
```

`os.getcwd` ran DURING `pickle.loads` and its return value (a str) became the 'object'. An attacker would use `os.system` instead. The restricted unpickler and the HMAC signature are mitigations; the real rule is: never unpickle data you did not create. The HMAC signs bytes only your server can produce.

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
import pickle
blob = pickle.dumps({"tags": {"a", "b"}, "pt": (1, 2)})   # keeps set and tuple
obj = pickle.loads(blob)
```

```javascript
// JavaScript
const obj = { tags: new Set(["a", "b"]), pt: [1, 2] };
JSON.stringify(obj);          // '{"tags":{},"pt":[1,2]}'  Set is LOST
// structuredClone(obj) copies Set/Map/Date in memory (not to disk)
// v8.serialize(obj) -> Buffer keeps Set/Map, Node only
```

JavaScript has no standard pickle. `JSON.stringify` drops Sets and Maps, `structuredClone` is in-memory only, and Node's `v8.serialize` is the nearest binary equivalent. Neither runs code on load, which is why pickle's design is riskier than JSON.

---

## 🟠 FastAPI Connection
FastAPI uses JSON (Pydantic) on the wire, not pickle. Pickle appears behind the scenes: caching computed results, loading ML models once at startup (lifespan), and background workers. Never accept pickle bytes from a request body.

```python
import pickle
from fastapi import FastAPI, Request, HTTPException
from fastapi.testclient import TestClient
app = FastAPI()
CACHE: dict[str, bytes] = {}
@app.put("/cache/{key}")
def put(key: str, value: dict[str, int]) -> dict[str, int]:
    CACHE[key] = pickle.dumps(value)  # server-owned data only
    return {"stored_bytes": len(CACHE[key])}
@app.get("/cache/{key}")
def get(key: str) -> dict[str, int]:
    if key not in CACHE:
        raise HTTPException(404)
    return pickle.loads(CACHE[key])  # safe: WE wrote it, never client bytes
c = TestClient(app)
print(c.put("/cache/k", json={"a": 1}).status_code, c.get("/cache/k").json())
```

**Real output** (Python 3.13.3):
```
200 {'a': 1}
```


---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Unpickling data from users or the network
```python
# Wrong - remote code execution
obj = pickle.loads(await request.body())

# Right - accept JSON and validate with Pydantic
payload = Model.model_validate_json(await request.body())
```

❌ Mistake 2: Opening the file in text mode
```python
# Wrong - TypeError: pickle needs bytes
with open("m.pkl", "w") as f:
    pickle.dump(obj, f)

# Right
with open("m.pkl", "wb") as f:
    pickle.dump(obj, f)
```

❌ Mistake 3: Storing pickles as long-term data
```python
# Wrong - breaks when you rename/move the class or upgrade the library
pickle.dump(user_obj, f)

# Right - persist plain data (JSON/DB) and rebuild objects from it
json.dump(user_obj.to_dict(), f)
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
import pickle
a = [1, 2]; d = {"x": a, "y": a}
e = pickle.loads(pickle.dumps(d))
print(e["x"] is e["y"], e["x"] is a)
class C:
    def __init__(self): print("init")
c = C(); c2 = pickle.loads(pickle.dumps(c))
print(type(c2).__name__)
```

**Answer** (real run on Python 3.13.3):
```
True False
init
C
```
Shared references are preserved inside one pickle (`x` and `y` point to the same new list) but the result is a copy, not the original (`is a` is False). `__init__` is not run when unpickling, so 'init' prints only once, for the first `C()`.

---

## ⚫ Interview Questions + Answers

Q1: Why is pickle insecure?
A1: Pickle is a tiny virtual machine. An object's `__reduce__` can return any callable and arguments, e.g. `(os.system, ('rm -rf ~',))`, and `loads` calls it. Treat a pickle like an executable.

Q2: Pickle vs JSON?
A2: JSON: text, safe, language independent, basic types only. Pickle: binary, Python only, almost any object, unsafe on untrusted data, version fragile. Use JSON for APIs and storage you share; pickle only for private caches and internal transfers.

Q3: What cannot be pickled?
A3: Lambdas, nested functions, open files, sockets, locks, DB connections, generators. Define a `__getstate__`/`__setstate__` pair to drop and rebuild such fields.

Q4: How do you make unpickling safer?
A4: Override `Unpickler.find_class` with a whitelist, sign the bytes with HMAC, or avoid pickle (use JSON, MessagePack, Protobuf, or `safetensors` for ML weights).

Q5: What is `pickle.HIGHEST_PROTOCOL`?
A5: The newest binary protocol (5 in Python 3.8+), supports out-of-band buffers and is faster for big arrays. The default in 3.13 is protocol 4. Older Pythons cannot read newer protocols.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Caching computed Python objects that YOUR code wrote and will read
- Passing objects between your own processes (multiprocessing does it)
- Saving ML models with trusted tools (joblib) in a closed environment

❌ Avoid when:
- Data comes from users, other services or the internet
- You need a long-lived or cross-language format
- You need human-readable data (use JSON/YAML)

---

## 📊 Visual Diagram

```
obj --dumps--> bytes: [opcodes: IMPORT my.Class, NEW, SETSTATE {...}]
                         |
                    (disk / Redis / socket)
                         v
bytes --loads--> VM runs opcodes --> obj'   (a COPY)

DANGER:  opcodes may say  CALL os.system("...")  <- runs on loads()
Rule: only loads() bytes that YOU wrote
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Serialisation | Object to bytes | object से bytes बनाना |
| Protocol | Pickle format version | pickle का format version |
| __reduce__ | Tells pickle how to rebuild | pickle को बताता है कैसे बनाना है |
| HMAC | Signature proving authenticity | असली होने का signature |
| RCE | Remote code execution | दूर से code चलाना |
| joblib | Pickle wrapper for big arrays | बड़े arrays के लिए pickle wrapper |

---

## ⚡ 3-Line Summary
English: `pickle` saves and restores almost any Python object, keeping shared references, but it is Python-only and executes code on load. Use it only for data your own code created, and prefer JSON for anything external.
Hindi: `pickle` लगभग हर Python object को save/restore करता है (shared references समेत), पर यह सिर्फ़ Python में चलता है और load पर code चलाता है। इसे सिर्फ़ अपने code के बनाए data के लिए इस्तेमाल करें; बाहरी data के लिए JSON चुनें।

---

## ➡️ Next Topic
**216. shelve Module** — a persistent dictionary on disk built on pickle.
