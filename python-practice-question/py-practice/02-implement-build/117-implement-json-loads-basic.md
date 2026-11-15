---

# Q117. Implement json.loads (basic)
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Implement a basic `loads(text)` JSON parser (objects, arrays, strings with escapes, numbers, `true/false/null`) using recursive descent. Raise an error on invalid input.

```python
loads('{"a": [1, 2.5], "b": null}')   # {'a': [1, 2.5], 'b': None}
```

---

## 💡 Quick Concept (2 lines only)
Keep a position index; look at the next character to decide which value type to parse, and recurse for arrays and objects.
हिंदी: Index रखो, अगला character देखकर type तय करो, और array/object के लिए recursion चलाओ।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import json                                             # only used to compare in tests
from typing import Any                                  # type hints

class JSONError(ValueError):                            # our parse error
    pass

class Parser:
    def __init__(self, text: str) -> None:
        self.s = text                                   # input text
        self.i = 0                                      # current position

    def ws(self) -> None:
        while self.i < len(self.s) and self.s[self.i] in " \t\n\r":  # skip whitespace
            self.i += 1

    def expect(self, lit: str) -> None:
        if not self.s.startswith(lit, self.i):          # literal must match here
            raise JSONError(f"Expected {lit!r} at {self.i}")
        self.i += len(lit)                              # consume it

    def value(self) -> Any:
        self.ws()                                       # ignore leading spaces
        if self.i >= len(self.s):                       # nothing left
            raise JSONError("Unexpected end")
        c = self.s[self.i]                              # look at next char
        if c == "{": return self.obj()                  # object
        if c == "[": return self.arr()                  # array
        if c == '"': return self.string()               # string
        if c == "t": self.expect("true"); return True   # literals
        if c == "f": self.expect("false"); return False
        if c == "n": self.expect("null"); return None
        return self.number()                            # otherwise a number

    def obj(self) -> dict:
        self.i += 1; result: dict = {}; self.ws()       # skip '{'
        if self.s[self.i:self.i + 1] == "}":            # empty object
            self.i += 1; return result
        while True:
            self.ws(); key = self.string(); self.ws()   # key must be a string
            self.expect(":")                            # colon separator
            result[key] = self.value()                  # parse value recursively
            self.ws()
            if self.s[self.i:self.i + 1] == ",":        # more pairs follow
                self.i += 1; continue
            self.expect("}"); return result             # end of object

    def arr(self) -> list:
        self.i += 1; result: list = []; self.ws()       # skip '['
        if self.s[self.i:self.i + 1] == "]":            # empty array
            self.i += 1; return result
        while True:
            result.append(self.value()); self.ws()      # parse element
            if self.s[self.i:self.i + 1] == ",":        # more elements follow
                self.i += 1; continue
            self.expect("]"); return result             # end of array

    def string(self) -> str:
        self.expect('"'); out: list[str] = []           # opening quote
        esc = {'"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f", "n": "\n", "r": "\r", "t": "\t"}
        while self.i < len(self.s):
            c = self.s[self.i]; self.i += 1             # take char
            if c == '"':                                # closing quote
                return "".join(out)
            if c == "\\":                               # escape sequence
                n = self.s[self.i]; self.i += 1
                if n == "u":                            # \uXXXX
                    out.append(chr(int(self.s[self.i:self.i + 4], 16))); self.i += 4
                else:
                    out.append(esc[n])                  # simple escape
            else:
                out.append(c)                           # normal char
        raise JSONError("Unterminated string")

    def number(self) -> int | float:
        start = self.i
        while self.i < len(self.s) and self.s[self.i] in "+-0123456789.eE":  # number chars
            self.i += 1
        text = self.s[start:self.i]                     # slice the number
        if not text:
            raise JSONError(f"Unexpected char {self.s[start]!r} at {start}")
        return float(text) if any(ch in text for ch in ".eE") else int(text)  # int or float

def loads(text: str) -> Any:
    p = Parser(text)                                    # new parser
    result = p.value(); p.ws()                          # parse top-level value
    if p.i != len(text):                                # trailing garbage?
        raise JSONError(f"Extra data at {p.i}")
    return result

# ============================================
# TEST CASES
# ============================================
print(loads('{"a": [1, 2.5, -3e2], "b": {"c": null}, "d": "x\\ny \\u00e9"}'))
# Expected: {'a': [1, 2.5, -300.0], 'b': {'c': None}, 'd': 'x\ny é'}
print(loads("[]"), loads("{}"), loads(" true "), loads('"hi"'), loads("42"))  # Expected: [] {} True hi 42
for bad in ['{"a": }', "[1, 2", "tru", '{"a" 1}', "[1] x"]:
    try:
        loads(bad)                                      # invalid JSON
    except (JSONError, IndexError) as e:
        print(type(e).__name__, e)
# Expected (in order):
# JSONError Unexpected char '}' at 6
# JSONError Expected ']' at 5
# JSONError Expected 'true' at 0
# JSONError Expected ':' at 5
# JSONError Extra data at 4
assert loads('{"k": [1, {"z": false}]}') == json.loads('{"k": [1, {"z": false}]}')  # matches stdlib
```

---

## 🔍 Why This Works (3 lines max)
Each grammar rule (value, object, array, string, number) is one method, and objects/arrays call `value()` recursively. The index only moves forward, so parsing is O(n). Simplified: no leading-zero or number-format validation.
हिंदी: हर JSON rule का अलग method है और nested structure recursion से parse होता है।

---

## ⚡ Alternative Solution
```python
# Real-world: stdlib with hooks, or ast.literal_eval for Python-literal syntax (not JSON!)
import json, ast                                                       # stdlib modules
print(json.loads('{"a": [1, 2]}', object_hook=lambda d: {k.upper(): v for k, v in d.items()}))
# Output: {'A': [1, 2]}
print(ast.literal_eval('{"a": [1, 2], "b": None}'))                    # Output: {'a': [1, 2], 'b': None}  (Python syntax, uses None)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: JSON with single quotes, or eval() on JSON text
import json
try: json.loads("{'a': 1}")
except json.JSONDecodeError as e: print("JSONDecodeError:", e)
# Output: JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)
try: eval('{"a": true}')                  # eval is also a security hole!
except NameError as e: print("NameError:", e)   # Output: NameError: name 'true' is not defined

# ✅ Correct: json.loads for JSON (double quotes only), never eval
```

---

## 🎯 Interview Tip (1 line)
Say: "Recursive descent with a cursor — one function per grammar rule, O(n); and never use eval() to parse JSON."

---

## 🔗 Related Questions
→ Q116 (json.dumps) | Q078 (deep equal) | Q196 (CSV to JSON) | Q197 (URL parser)
