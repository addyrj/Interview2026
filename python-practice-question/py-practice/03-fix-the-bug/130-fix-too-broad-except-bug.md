---

# Q130. Fix Too-Broad except Bug
# Category: Fix the Bug
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
`parse_age` returns `0` for everything that goes wrong — a typo in the key, bad JSON, even passing `None`. The bugs are invisible. Find and fix the problem.

```python
# BUGGY CODE:
import json

def parse_age_buggy(raw: str) -> int:
    try:
        data = json.loads(raw)      # may raise JSONDecodeError / TypeError
        return data["age"]          # may raise KeyError
    except Exception:               # ❌ catches EVERYTHING, hides real bugs
        return 0                    # silent fallback
```

---

## 💡 Quick Concept (2 lines only)
Catch only the exceptions you EXPECT and know how to handle. `except Exception` also swallows programming errors (`TypeError`, `NameError`, typos), so bugs turn into silent wrong answers.
हिंदी: सिर्फ expected exceptions पकड़ो — `except Exception` असली bugs छुपा देता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import json                                    # std-lib JSON parser

def parse_age_buggy(raw: str) -> int:
    try:
        data = json.loads(raw)                 # parse text
        return data["age"]                     # read key
    except Exception:                          # ❌ too broad
        return 0                               # hides everything

print(parse_age_buggy('{"age": 30}'))          # Expected: 30
print(parse_age_buggy('{"nme": 30}'))          # Expected: 0  (typo hidden... or real missing key?)
print(parse_age_buggy(None))                   # Expected: 0  (a caller bug, silently ignored)

def parse_age(raw: str) -> int:
    try:
        data = json.loads(raw)                 # Step 1: parse
    except json.JSONDecodeError:               # Step 2: only the EXPECTED parse failure
        return 0                               # bad user input -> default
    try:
        return int(data["age"])                # Step 3: read + convert
    except KeyError:                           # only the expected missing-key case
        return 0                               # default when key is absent

# ============================================
# TEST CASES
# ============================================
print(parse_age('{"age": 30}'), parse_age('bad'), parse_age('{"x":1}'))  # Expected: 30 0 0
try:
    parse_age(None)                            # programmer error: wrong type
except TypeError as e:                         # now it is NOT hidden
    print("TypeError:", e)                     # Expected: TypeError: the JSON object must be str, bytes or bytearray, not NoneType
```

---

## 🔍 Why This Works (3 lines max)
Narrow `except` clauses let unexpected errors propagate with a full traceback, so bugs get noticed and fixed. Keep each `try` body small so you know which line raised. If you really must catch broadly, log with `logger.exception(...)` and re-raise.
हिंदी: narrow except + छोटा try block — unexpected error ऊपर तक जाता है और दिख जाता है।

---

## ⚡ Alternative Solution
```python
import json                                          # std-lib JSON

# Alternative 1: tuple of expected exceptions
def parse_age2(raw: str) -> int:
    try:
        return int(json.loads(raw)["age"])           # parse + read + convert
    except (json.JSONDecodeError, KeyError):         # only these two are "expected"
        return 0                                     # default

print(parse_age2('{"age": 7}'), parse_age2('{}'), parse_age2('{{'))  # Output: 7 0 0
try:
    parse_age2(None)                                 # wrong type
except TypeError as e:
    print("TypeError:", e)                           # Output: TypeError: the JSON object must be str, bytes or bytearray, not NoneType

# Alternative 2: avoid exceptions for missing keys with .get()
print(json.loads('{"age": 5}').get("age", 0))        # Output: 5
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: broad except + pass — error vanishes, nobody knows it happened
try:
    result = 10 / int("abc")       # ValueError
except Exception:
    pass                           # silent failure

# ✅ Correct: handle what you expect, log/re-raise the rest
import logging                     # std-lib logging
try:
    result = 10 / int("abc")       # ValueError
except ValueError:                 # expected bad input
    logging.warning("not a number")  # visible, specific
```

---

## 🎯 Interview Tip (1 line)
Say: "Catch the narrowest exception you can handle, keep the `try` body tiny, and never use `except: pass` — at least log and re-raise."

---

## 🔗 Related Questions
→ Q042 (try/except/else/finally order) | Q044 (exception chaining) | Q131 (bare except) | Q260 (exception groups and add_note)
