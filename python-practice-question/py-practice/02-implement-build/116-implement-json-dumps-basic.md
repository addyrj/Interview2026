---

# Q116. Implement json.dumps (basic)
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement a basic `dumps(obj)` that serialises `None, bool, int, float, str, list/tuple, dict` to a JSON string (same output as `json.dumps` defaults). Raise `TypeError` for unsupported types.

```python
dumps({"name": "Ann", "ok": True, "x": None})
# '{"name": "Ann", "ok": true, "x": null}'
```

---

## 💡 Quick Concept (2 lines only)
Recursively map each Python type to its JSON text; strings need quoting and escaping. Check `bool` before `int` because `True` is an `int`.
हिंदी: हर type को recursively JSON text में बदलो; bool को int से पहले check करो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import json                                            # only used to compare in tests
from typing import Any                                 # type hints

_ESCAPES = {'"': '\\"', "\\": "\\\\", "\n": "\\n", "\r": "\\r", "\t": "\\t"}  # chars needing escape

def _quote(s: str) -> str:
    out = []                                           # build escaped chars
    for ch in s:                                       # check each char
        if ch in _ESCAPES:                             # known escape
            out.append(_ESCAPES[ch])                   # use escape sequence
        elif ord(ch) < 0x20:                           # other control char
            out.append(f"\\u{ord(ch):04x}")            # \u00XX form
        elif ord(ch) > 126:                            # non-ASCII (ensure_ascii=True default)
            code = ord(ch)                             # code point
            if code > 0xFFFF:                          # needs a surrogate pair
                code -= 0x10000                        # shift
                out.append(f"\\u{0xD800 + (code >> 10):04x}\\u{0xDC00 + (code & 0x3FF):04x}")  # pair
            else:
                out.append(f"\\u{code:04x}")           # BMP char
        else:
            out.append(ch)                             # plain char
    return '"' + "".join(out) + '"'                    # wrap in quotes

def dumps(obj: Any) -> str:
    if obj is None:                                    # Step 1: None -> null
        return "null"
    if obj is True:                                    # Step 2: bool BEFORE int (bool is an int)
        return "true"
    if obj is False:
        return "false"
    if isinstance(obj, (int, float)):                  # Step 3: numbers
        if isinstance(obj, float) and (obj != obj or obj in (float("inf"), float("-inf"))):  # NaN/Inf
            raise ValueError("NaN/Infinity not allowed")  # strict JSON (real json allows by default)
        return repr(obj)                               # repr is round-trip safe
    if isinstance(obj, str):                           # Step 4: strings
        return _quote(obj)
    if isinstance(obj, (list, tuple)):                 # Step 5: arrays
        return "[" + ", ".join(dumps(x) for x in obj) + "]"
    if isinstance(obj, dict):                          # Step 6: objects
        items = []                                     # "key": value pairs
        for k, v in obj.items():                       # insertion order
            if not isinstance(k, str):                 # (real json coerces int keys to str)
                raise TypeError(f"keys must be str, got {type(k).__name__}")
            items.append(f"{_quote(k)}: {dumps(v)}")   # one pair
        return "{" + ", ".join(items) + "}"
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")  # unsupported

# ============================================
# TEST CASES
# ============================================
print(dumps({"name": "Ann", "age": 30, "tags": ["a", "b"], "ok": True, "x": None}))
# Expected: {"name": "Ann", "age": 30, "tags": ["a", "b"], "ok": true, "x": null}
print(dumps([1, 2.5, "hi\n\"q\"", [], {}]))     # Expected: [1, 2.5, "hi\n\"q\"", [], {}]
print(dumps("héllo 😀"))                        # Expected: "héllo 😀"
print(dumps(True), dumps(0), dumps(None), dumps((1, 2)))  # Expected: true 0 null [1, 2]
try:
    dumps({1, 2})                               # sets are not JSON
except TypeError as e:
    print("TypeError:", e)                      # Expected: TypeError: Object of type set is not JSON serializable
assert dumps({"a": [1, 2.5, None, True]}) == json.dumps({"a": [1, 2.5, None, True]})  # matches stdlib
```

---

## 🔍 Why This Works (3 lines max)
Each branch handles one JSON type and containers recurse, so any nesting depth works. Strings are escaped per the JSON spec (quotes, backslash, control chars, non-ASCII as `\uXXXX`) just like the stdlib default.
हिंदी: हर type की अपनी branch है और list/dict अंदर recursion करते हैं।

---

## ⚡ Alternative Solution
```python
# Real-world: use the stdlib and its options
import json                                                         # stdlib
print(json.dumps({"a": [1, 2]}, separators=(",", ":")))             # Output: {"a":[1,2]}  (compact)
print(json.dumps({"a": [1, 2], "b": {"c": 1}}, indent=2))           # pretty-print (multi-line)
print(json.dumps({"d": {1, 2}}, default=sorted))                    # Output: {"d": [1, 2]}  (default= handles unknown types)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: using str() / repr() as "JSON"
print(str({"a": True, "b": None}))     # Output: {'a': True, 'b': None}   <- single quotes, True/None: NOT valid JSON

# ✅ Correct: json.dumps
import json
print(json.dumps({"a": True}))         # Output: {"a": true}
# Also: json.dumps({1: "x"}) -> {"1": "x"} (int keys become strings) and
# json.dumps(float("nan")) -> NaN (not valid JSON; use allow_nan=False to forbid)
```

---

## 🎯 Interview Tip (1 line)
Say: "Recursive type dispatch, bool before int, escape strings, reject unsupported types — and in production I'd use `json.dumps(default=...)`."

---

## 🔗 Related Questions
→ Q117 (json.loads) | Q071 (deep clone a dict) | Q078 (deep equal) | Q196 (CSV to JSON)
