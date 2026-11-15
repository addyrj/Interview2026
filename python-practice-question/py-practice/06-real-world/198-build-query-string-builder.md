---

# Q198. Build query string builder
# Category: REAL WORLD PROBLEMS
# Difficulty: ⭐ Easy

---

## ❓ Question
Build `build_query(params)` that turns a dict into a URL query string. Rules: percent-encode keys and values, skip `None`, repeat the key for list values, and render booleans as `true`/`false`.

```python
build_query({"q": "hello world", "tag": ["a", "b"], "x": None})
# 'q=hello%20world&tag=a&tag=b'
```

---

## 💡 Quick Concept (2 lines only)
Encode each key/value with `urllib.parse.quote(..., safe="")`, expand lists into repeated `key=value` pairs, join with `&`.
हिंदी: हर key/value को encode करो, list हो तो key repeat करो, और सब `&` से जोड़ दो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from urllib.parse import quote                       # percent-encoding helper
from typing import Any                               # loose value type

def _enc(v: Any) -> str:
    return quote(str(v), safe="")                    # encode everything unsafe (space -> %20, & -> %26)

def build_query(params: dict[str, Any]) -> str:
    parts: list[str] = []                            # collect "key=value" pieces
    for key, value in params.items():                # walk every param
        if value is None:                            # skip None values entirely
            continue                                 # nothing to send
        if isinstance(value, bool):                  # booleans -> "true"/"false"
            value = "true" if value else "false"     # JS-style, not "True"
        if isinstance(value, (list, tuple)):         # repeated keys: tag=a&tag=b
            parts.extend(f"{_enc(key)}={_enc(v)}" for v in value)  # one pair per item
        else:                                        # normal scalar value
            parts.append(f"{_enc(key)}={_enc(value)}")  # encode key and value
    return "&".join(parts)                           # join with &

# ============================================
# TEST CASES
# ============================================
print(build_query({"q": "hello world", "page": 2}))          # Expected: q=hello%20world&page=2
print(build_query({"tag": ["a", "b"], "x": None}))           # Expected: tag=a&tag=b
print(build_query({"name": "a&b=c", "ok": True}))            # Expected: name=a%26b%3Dc&ok=true
print(repr(build_query({})))                                 # Expected: ''

# --- Real output (Python 3.13) ---
# q=hello%20world&page=2
# tag=a&tag=b
# name=a%26b%3Dc&ok=true
# ''
```

---

## 🔍 Why This Works (3 lines max)
`quote(safe="")` encodes `&`, `=`, `/` and spaces so a value can never break the structure of the query. Checking `bool` before the generic branch matters because `True` would otherwise print as `True`.
हिंदी: `safe=""` से `&` और `=` भी encode होते हैं, इसलिए value query को तोड़ नहीं सकती।

---

## ⚡ Alternative Solution
```python
# ============================================
# ALTERNATIVE: urllib.parse.urlencode
# ============================================
from urllib.parse import urlencode, quote            # stdlib encoder

print(urlencode({"q": "hello world", "page": 2}))                       # space becomes '+' by default
print(urlencode({"q": "hello world"}, quote_via=quote))                 # use %20 instead of '+'
print(urlencode({"tag": ["a", "b"]}, doseq=True))                       # doseq=True repeats the key
print(urlencode({"tag": ["a", "b"]}))                                   # without doseq: list is str()'d!

# --- Real output (Python 3.13) ---
# q=hello+world&page=2
# q=hello%20world
# tag=a&tag=b
# tag=%5B%27a%27%2C+%27b%27%5D
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: plain f-string, no encoding
params = {"name": "a&b=c"}
print("&".join(f"{k}={v}" for k, v in params.items()))  # name=a&b=c  -> server sees TWO params (name, b)

# ✅ Correct: encode first
from urllib.parse import quote
print("&".join(f"{k}={quote(v, safe='')}" for k, v in params.items()))  # name=a%26b%3Dc
```

---

## 🎯 Interview Tip (1 line)
Say: "Always percent-encode — otherwise it's a bug and a parameter-injection hole. `urlencode` uses `+` for spaces; pass `quote_via=quote` for `%20`."

---

## 🔗 Related Questions
→ Q197 (URL parser) | Q182 (pagination helper) | Q183 (retry API call) | Q194 (data fetcher)
