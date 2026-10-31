---

# 018. None — NoneType
# हिंदी में: None — "कोई value नहीं"

---

## 🔵 Simple Definition (English)
`None` is Python's special object that means "no value here". It is the only instance of the type `NoneType`. Functions without a `return` give back `None`. It is falsy, and you should always test it with `is None`, not `== None`.

## 🔵 सरल परिभाषा (Hindi)
`None` Python का special object है जिसका मतलब है "यहाँ कोई value नहीं"। यह `NoneType` type का अकेला instance है। जिस function में `return` नहीं होता वो `None` लौटाता है। यह falsy है, और इसे हमेशा `is None` से check करें, `== None` से नहीं।

---

## 🔴 Problem it Solves
Programs need a way to say "nothing / not set / not found". Using `0`, `""` or `-1` for that is ambiguous — `0` can be a real balance. `None` is a unique marker that cannot be confused with real data, used for optional values, missing results, and default arguments.

## 🔴 यह क्यों बना? (Hindi)
"कुछ नहीं / set नहीं / मिला नहीं" बताने का तरीका चाहिए। इसके लिए `0`, `""`, `-1` confusing हैं — `0` असली balance भी हो सकता है। `None` एक unique marker है जो असली data से confuse नहीं होता — optional values, missing results और default arguments के लिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python creates ONE None object at startup (singleton)
Step 2 → Every `x = None` points to that same object
Step 3 → Function with no return statement returns None implicitly
Step 4 → `x is None` compares memory identity (fast, safe)
Step 5 → In a condition, None is falsy -> branch skipped
Step 6 → Calling a method on None raises AttributeError
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Python startup पर सिर्फ एक None object बनाता है (singleton)
Step 2 → हर `x = None` उसी एक object को point करता है
Step 3 → बिना return वाला function implicitly None लौटाता है
Step 4 → `x is None` memory identity compare करता है (fast, safe)
Step 5 → Condition में None falsy है -> branch skip
Step 6 → None पर method call करने पर AttributeError आता है
```

---

## 🟡 Real World Example
Zomato search returns `None` when a restaurant ID does not exist. A user profile has `middle_name: str | None = None`. A database query like `session.get(User, 99)` gives `None` for a missing row. FastAPI turns that `None` into a 404 response.

## 🟡 Real Example Hindi mein
Zomato में restaurant ID न मिले तो search `None` देता है। User profile में `middle_name: str | None = None` होता है। `session.get(User, 99)` missing row पर `None` देता है। FastAPI उसी `None` को 404 response में बदल देता है।

---

## 💻 Code Example — Basic
```python
# None basics

# Assign None to mean "no value yet":
result: str | None = None         # optional string, currently empty
print(result)                     # None
print(type(result))               # <class 'NoneType'>

# Test with `is`, not `==`:
print(result is None)             # True
print(result is not None)         # False

# None is falsy:
print(bool(None))                 # False
if not result:                    # runs because None is falsy
    print("no result yet")        # no result yet

# Function without return gives None:
def say_hi() -> None:             # return type None
    print("hi")                   # just prints

value = say_hi()                  # prints hi, returns None
print(value)                      # None

# Dict .get returns None for missing key:
user: dict[str, str] = {"name": "Asha"}   # small dict
print(user.get("email"))          # None
print(user.get("email", "n/a"))   # n/a  (custom default)

# None is not 0, "" or False:
print(None == 0)                  # False
print(None == "")                 # False
print(None == False)              # False
```

## 💻 Code Example — Advanced
```python
# Advanced None — Optional handling, sentinel, safe chaining
from dataclasses import dataclass


@dataclass
class Address:
    city: str | None = None                  # city may be missing


@dataclass
class User:
    name: str                                # required
    address: Address | None = None           # optional nested object


_MISSING = object()                          # sentinel: distinguishes "not passed" from None


def find_user(users: dict[int, User], user_id: int) -> User | None:
    """Return user or None when not found."""
    return users.get(user_id)                # dict.get gives None if missing


def get_city(user: User | None) -> str:
    """Safely walk user -> address -> city (like JS optional chaining)."""
    if user is None or user.address is None:     # guard clauses
        return "unknown"                         # fallback
    return user.address.city or "unknown"        # city may also be None


def update(value: object = _MISSING) -> str:
    """Tell apart 'no argument' from 'explicit None'."""
    if value is _MISSING:                    # nothing passed
        return "not provided"
    if value is None:                        # None passed on purpose
        return "clear the field"
    return f"set to {value}"                 # normal value


def add_item(item: str, bucket: list[str] | None = None) -> list[str]:
    """Correct pattern for mutable default arguments."""
    if bucket is None:                       # create fresh list each call
        bucket = []
    bucket.append(item)                      # add item
    return bucket


def main() -> None:
    users: dict[int, User] = {1: User("Asha", Address("Pune")), 2: User("Ravi")}
    print(get_city(find_user(users, 1)))     # Pune
    print(get_city(find_user(users, 2)))     # unknown
    print(get_city(find_user(users, 99)))    # unknown

    print(update())                          # not provided
    print(update(None))                      # clear the field
    print(update(5))                         # set to 5

    print(add_item("a"))                     # ['a']
    print(add_item("b"))                     # ['b']  (no shared state)

    # Error: calling a method on None
    try:
        find_user(users, 99).name.upper()    # type: ignore[union-attr]
    except AttributeError as exc:            # None has no attribute 'name'
        print(exc)                           # 'NoneType' object has no attribute 'name'

    # None is a singleton:
    a, b = None, None
    print(a is b)                            # True
    print(id(a) == id(b))                    # True


if __name__ == "__main__":
    main()
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python — ONE "nothing" value
x = None
print(x is None)          # True
print(None == 0)          # False
# Missing dict key:
d = {"a": 1}
print(d.get("b"))         # None
# d["b"] -> KeyError (does not silently give None)
```
```javascript
// JavaScript — TWO "nothing" values: null and undefined
let x = null;
console.log(x === null);   // true
console.log(null == 0);    // false
console.log(null == undefined); // true (loose equality)
// Missing object key:
const d = { a: 1 };
console.log(d.b);          // undefined (no error)
```

Key differences: Python has only `None` (like JS `null`), no `undefined`. A missing dict key raises `KeyError` unless you use `.get()`. A function with no return gives `None` (JS gives `undefined`). Python has no `?.` optional chaining — use `if x is not None`.

---

## 🟠 FastAPI Connection
In FastAPI, `None` marks optional fields and optional query parameters. A missing DB row (`None`) is converted into `HTTPException(404)`.

```python
# FastAPI example (needs: pip install fastapi)
from fastapi import FastAPI, HTTPException

app = FastAPI()                                      # create app

FAKE_DB: dict[int, str] = {1: "Asha", 2: "Ravi"}     # tiny in-memory "database"


@app.get("/users/{user_id}")
def get_user(user_id: int, q: str | None = None) -> dict[str, str]:
    # q is optional: /users/1 -> q is None, /users/1?q=x -> q == "x"
    name = FAKE_DB.get(user_id)                      # None when not found
    if name is None:                                 # check with `is None`
        raise HTTPException(status_code=404, detail="User not found")
    return {"name": name, "q": q or ""}              # q may be None -> ""
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `== None`
```python
# Wrong — a class can override __eq__ and fake equality:
if value == None:
    pass

# Correct — identity check:
if value is None:
    pass
```

❌ Mistake 2: Forgetting a function returns None
```python
# Wrong — list.sort() returns None, not the sorted list:
nums = [3, 1, 2]
result = nums.sort()
print(result)             # None

# Correct:
result = sorted(nums)     # returns new sorted list
print(result)             # [1, 2, 3]
```

❌ Mistake 3: Mutable default instead of None
```python
# Wrong — the list is shared across all calls:
def add(item, bucket=[]):
    bucket.append(item)
    return bucket

# Correct:
def add(item, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
def f(items=None):
    items = items or [1]
    return items

print(f([]))
print(f(None))
print(None is None, None == None)
print(bool(None), type(None).__name__)
```
Answer: `[1]`, `[1]`, `True True`, `False NoneType`. The first call surprises people: `[]` is falsy, so `[] or [1]` picks `[1]` even though the caller passed an empty list on purpose. Use `if items is None:` to tell "not passed" from "empty".

---

## ⚫ Interview Questions + Answers

Q1: What is the type of `None`?
A1: `NoneType`. There is exactly one instance, `None` (a singleton). You cannot create more: `type(None)()` returns the same `None`. Because it is a singleton, `is` is the correct and fastest comparison.

Q2: Why use `is None` instead of `== None`?
A2: `==` calls `__eq__`, which a class can override (even to return True for None). `is` checks identity and cannot be fooled. Also faster, and PEP 8 requires it. Linters (ruff, flake8) flag `== None` as E711.

Q3: What does a function return if there is no `return` statement?
A3: `None`. Same for a bare `return`. That is why `print(print("x"))` prints `x` then `None`. Methods that mutate in place (`list.append`, `sort`, `reverse`) return `None` too, so `x = x.append(1)` destroys your list.

Q4: How do you type an optional value?
A4: `str | None` (Python 3.10+) or `Optional[str]` from `typing`. Both mean "str or None". Note: `Optional` does not mean "has a default" — it only means None is allowed. In FastAPI, `q: str | None = None` makes the query param optional.

Q5: What is the difference between `None` and a sentinel `object()`?
A5: `None` is a valid value users may pass on purpose (e.g. "clear this field"). A private sentinel (`_MISSING = object()`) lets you detect "argument not given at all". Use sentinel when `None` is itself meaningful, as in PATCH-style update functions.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- A value is optional or not yet known
- A lookup can fail (`dict.get`, DB query)
- Default for mutable arguments (`bucket=None`)
- Functions that only do side effects (return `None`)

❌ Avoid when:
- You can return an empty list/dict instead (callers avoid None checks)
- You need to explain WHY there is no value — raise an exception
- Using `None` as a magic flag with many meanings — use an Enum

---

## 📊 Visual Diagram
```
 x = None                 name = "Asha"
   |                          |
   v                          v
 +-----------+          +-----------+
 | NoneType  |          |    str    |
 |   None    | <- one   |  "Asha"   |
 +-----------+   copy   +-----------+
   ^    ^
   |    |
   a    b       (a is b) -> True  (same singleton)

 if x is None:   -> identity check  (correct)
 if x == None:   -> calls __eq__    (avoid)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| None | "No value" object | "कोई value नहीं" object |
| NoneType | Type of None | None का type |
| Singleton | Only one instance exists | सिर्फ एक instance |
| Sentinel | Unique marker object | Unique marker object |
| Optional | Value or None | Value या None |
| Implicit return | Function ends -> None | Function खत्म -> None |

---

## ⚡ 3-Line Summary
English: `None` means "no value" and is the single instance of `NoneType`. Check it with `is None`, never `== None`. Functions without return, failed `.get()` lookups and optional fields all give `None`.
Hindi: `None` का मतलब "कोई value नहीं", और यह `NoneType` का अकेला instance है। इसे `is None` से check करें, `== None` से नहीं। बिना return के function, fail हुआ `.get()` और optional fields `None` देते हैं।

---

## ➡️ Next Topic
**019. type() + isinstance()** — how to inspect an object's type at runtime and why `isinstance` beats `type ==`.
