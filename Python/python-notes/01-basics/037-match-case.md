---

# 037. match/case (Python 3.10+)
# हिंदी में: match/case — Structural Pattern Matching

---

## 🔵 Simple Definition (English)
`match` / `case` is Python's **structural pattern matching** (Python 3.10+). You give `match` a value, and Python checks it against a series of `case` patterns from top to bottom. A pattern can be a literal, a sequence shape, a dict shape, a class shape, and it can **capture** parts of the value into variables. It is much more than a C-style `switch`.

## 🔵 सरल परिभाषा (Hindi)
`match` / `case` Python का **structural pattern matching** है (Python 3.10+)। आप `match` को एक value देते हैं और Python उसे ऊपर से नीचे `case` patterns से मिलाता है। Pattern literal, sequence की शक्ल, dict की शक्ल, class की शक्ल हो सकता है, और value के हिस्सों को variables में **capture** भी कर सकता है। यह C के `switch` से कहीं ज्यादा शक्तिशाली है।

---

## 🔴 Problem it Solves
Long `if / elif / elif` chains that check `type`, length, keys and values are hard to read and easy to get wrong. For example, handling a command like `["move", x, y]`, `["quit"]` or an API event `{"type": "payment", "amount": 500}` needs many `isinstance`, `len`, and index checks. `match` expresses "what the data looks like" directly and unpacks the pieces in one step.

## 🔴 यह क्यों बना? (Hindi)
लंबे `if / elif` chains जिनमें `type`, length, keys और values जाँचनी पड़ें, पढ़ने में कठिन और गलती-प्रवण होते हैं। जैसे `["move", x, y]`, `["quit"]` या API event `{"type": "payment", "amount": 500}` को handle करने में बहुत सारी `isinstance`, `len` और index checks लगती हैं। `match` सीधे बताता है कि "data कैसा दिखना चाहिए" और टुकड़े एक ही step में निकाल देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → match <subject>:   the subject expression is evaluated ONCE
Step 2 → Python tries each `case <pattern>` from top to bottom
Step 3 → A pattern matches if the SHAPE fits. Pattern kinds:
           case 404:                  literal (==, but None/True/False use `is`)
           case "a" | "b":            OR-pattern
           case [x, y]:               sequence of exactly 2 → captures x, y
           case [first, *rest]:       sequence with star
           case {"type": t}:          mapping with key "type" (extra keys OK)
           case Point(x=0, y=y):      class pattern (isinstance + attributes)
           case Status.OK:            dotted name = constant value (NOT a capture)
           case n if n > 10:          guard (extra condition)
           case _:                    wildcard, matches anything
Step 4 → First matching case runs; its captured names are now variables
Step 5 → No fall-through: after one case body, match ends
Step 6 → No match and no `_` → nothing happens (no error)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → match का subject एक बार evaluate होता है
Step 2 → Python ऊपर से नीचे हर case का pattern आज़माता है
Step 3 → Pattern की शक्ल मिले तो match:
         literal, OR (a | b), sequence [x, y], [first, *rest],
         mapping {"type": t}, class Point(x=0), guard (if ...), wildcard _
Step 4 → पहला matching case चलता है; capture हुए names variables बन जाते हैं
Step 5 → Fall-through नहीं होता: एक case के बाद match खत्म
Step 6 → कुछ match न हो और `_` न हो तो कुछ नहीं होता (error भी नहीं)
```

---

## 🟡 Real World Example
A payment-gateway webhook sends events: `{"event": "payment.captured", "amount": 500}`, `{"event": "refund.created", ...}`, `{"event": "payment.failed", "reason": "..."}`. A single `match` on the dict routes each event to the right handler and extracts fields. A CLI chat bot parses commands (`["add", item]`, `["remove", item]`, `["list"]`). A compiler or JSON-schema walker matches on node shapes. A FastAPI service uses it to dispatch on event type or on `(method, path_parts)`.

## 🟡 Real Example Hindi mein
Payment gateway का webhook events भेजता है: `{"event": "payment.captured", "amount": 500}`, `{"event": "refund.created", ...}`, `{"event": "payment.failed", "reason": "..."}`। एक `match` dict पर हर event को सही handler तक पहुँचाता है और fields निकाल देता है। CLI chat bot commands parse करता है (`["add", item]`, `["remove", item]`, `["list"]`)। FastAPI service में event type या `(method, path_parts)` पर dispatch के लिए इसका use होता है।

---

## 💻 Code Example — Basic
```python
# match/case basics (needs Python 3.10+)

# 1. Literal patterns: like a switch
def http_message(code: int) -> str:
    match code:                          # subject
        case 200:                        # literal pattern
            return "OK"
        case 301 | 302:                  # OR pattern: either value
            return "Redirect"
        case 404:
            return "Not Found"
        case _:                          # wildcard: default
            return "Other"

print(http_message(200))                 # Output: OK
print(http_message(302))                 # Output: Redirect
print(http_message(500))                 # Output: Other


# 2. Sequence patterns: capture parts of a command
def run(command: list[str]) -> str:
    match command:
        case ["quit"]:                               # exactly one item "quit"
            return "bye"
        case ["go", direction]:                      # two items, capture the 2nd
            return f"going {direction}"
        case ["add", *items] if items:               # star capture + guard
            return f"adding {len(items)} items: {items}"
        case []:                                     # empty list
            return "empty command"
        case _:
            return "unknown"

print(run(["quit"]))                     # Output: bye
print(run(["go", "north"]))              # Output: going north
print(run(["add", "milk", "egg"]))       # Output: adding 2 items: ['milk', 'egg']
print(run([]))                           # Output: empty command
print(run(["fly"]))                      # Output: unknown


# 3. Capture with a guard
def grade(score: int) -> str:
    match score:
        case n if n >= 90:               # capture n, then test with `if`
            return "A"
        case n if n >= 75:
            return "B"
        case _:
            return "C"

print(grade(95), grade(80), grade(10))   # Output: A B C


# 4. Tuples and matching on type
def describe(value: object) -> str:
    match value:
        case int() | float():            # class patterns with no args = isinstance
            return "number"
        case str():
            return "text"
        case (x, y):                     # any 2-item sequence
            return f"pair {x},{y}"
        case None:                       # None is matched with `is`
            return "nothing"
        case _:
            return "something else"

print(describe(3), describe("hi"), describe((1, 2)), describe(None))
# Output: number text pair 1,2 nothing
```

## 💻 Code Example — Advanced
```python
# Advanced: dict patterns (webhooks), class patterns, enums, nested patterns, guards
from dataclasses import dataclass          # for class patterns
from enum import Enum                      # for named constants
from typing import Any                     # loose JSON type


class Status(Enum):
    ACTIVE = "active"                      # constant 1
    BLOCKED = "blocked"                    # constant 2


@dataclass
class Point:
    x: int                                 # horizontal
    y: int                                 # vertical


@dataclass
class Circle:
    center: Point                          # nested dataclass
    radius: float                          # size


def where(p: Point) -> str:
    match p:
        case Point(x=0, y=0):              # class pattern with keyword attributes
            return "origin"
        case Point(x=0, y=y):              # capture y
            return f"on y-axis at {y}"
        case Point(x, 0):                  # positional works for dataclasses
            return f"on x-axis at {x}"
        case Point(x, y) if x == y:        # guard
            return "on diagonal"
        case _:
            return "somewhere"


def area(shape: object) -> float:
    match shape:
        case Circle(center=Point(x=0, y=0), radius=r):   # nested pattern
            return round(3.14159 * r * r, 2)
        case Circle(radius=r):
            return round(3.14159 * r * r, 2)
        case _:
            raise TypeError(f"unsupported shape: {shape!r}")


def handle_event(event: dict[str, Any]) -> str:
    """Route a payment-gateway style webhook."""
    match event:
        case {"event": "payment.captured", "amount": int(amount)} if amount > 0:
            return f"captured Rs {amount}"                       # extra keys are ignored
        case {"event": "payment.failed", "reason": str(reason)}:
            return f"failed: {reason}"
        case {"event": "refund.created", "refund": {"id": rid, "amount": amt}}:
            return f"refund {rid} of Rs {amt}"                   # nested dict pattern
        case {"event": str(name)}:
            return f"ignored event {name}"                       # known key, unknown type
        case _:
            return "invalid payload"                             # no 'event' key at all


def user_label(status: Status) -> str:
    match status:
        case Status.ACTIVE:                # dotted name = compare to the constant
            return "can log in"
        case Status.BLOCKED:
            return "denied"


def first_and_rest(items: list[int]) -> str:
    match items:
        case []:
            return "empty"
        case [only]:
            return f"one: {only}"
        case [first, second, *rest]:
            return f"first={first}, second={second}, rest={rest}"
    return "unreachable for lists, but keeps type checkers calm"


def main() -> None:
    print(where(Point(0, 0)))                       # Output: origin
    print(where(Point(0, 7)))                       # Output: on y-axis at 7
    print(where(Point(4, 0)))                       # Output: on x-axis at 4
    print(where(Point(3, 3)))                       # Output: on diagonal
    print(where(Point(1, 2)))                       # Output: somewhere
    print(area(Circle(Point(0, 0), 2)))             # Output: 12.57
    print(handle_event({"event": "payment.captured", "amount": 500, "id": "p1"}))
    # Output: captured Rs 500
    print(handle_event({"event": "payment.failed", "reason": "low balance"}))
    # Output: failed: low balance
    print(handle_event({"event": "refund.created", "refund": {"id": "r9", "amount": 50}}))
    # Output: refund r9 of Rs 50
    print(handle_event({"event": "payment.captured", "amount": -5}))
    # Output: ignored event payment.captured   (guard failed, falls to next matching case)
    print(handle_event({"hello": 1}))               # Output: invalid payload
    print(user_label(Status.BLOCKED))               # Output: denied
    print(first_and_rest([1, 2, 3, 4]))             # Output: first=1, second=2, rest=[3, 4]
    try:
        area("not a shape")                         # no case matches except _ -> raises
    except TypeError as exc:
        print("TypeError:", exc)                    # Output: TypeError: unsupported shape: 'not a shape'


if __name__ == "__main__":
    main()                                          # run only when executed directly
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: pattern matching with unpacking
def handle(msg: dict) -> str:
    match msg:
        case {"type": "click", "x": x, "y": y}:      # shape + capture
            return f"click at {x},{y}"
        case {"type": "key", "key": "q" | "Q"}:      # OR pattern
            return "quit"
        case [a, b, *rest]:                          # sequences
            return f"{a} {b} {rest}"
        case _:
            return "unknown"
```
```javascript
// JavaScript: switch only compares values; no shape matching or capture
function handle(msg) {
  switch (msg.type) {
    case "click":
      return `click at ${msg.x},${msg.y}`;    // manual access
    case "key":
      if (msg.key === "q" || msg.key === "Q") return "quit";
      break;                                  // forgetting break = fall-through bug
    default:
      return "unknown";
  }
  // destructuring is separate from switch:
  const { type, x, y } = msg;
  // Arrays: if (Array.isArray(msg) && msg.length >= 2) { const [a, b, ...rest] = msg; }
}
// A TC39 proposal for pattern matching exists but is not shipped yet.
```

Key differences: JS `switch` only compares a value with `===` and **falls through** unless you `break`. Python `match` has no fall-through, checks the **structure**, binds variables, supports guards, `|`, and class patterns. Python's `case x:` with a bare name is a **capture** (always matches), not a comparison with variable `x`.

---

## 🟠 FastAPI Connection
`match` is useful in FastAPI services for routing webhook payloads by event type, handling a discriminated union of request bodies, or mapping `(method, status)` pairs to messages. Pydantic models are normal classes, so you can use class patterns on them: `case PaymentEvent(amount=a)`. Keep endpoint code clear: use `match` inside helper functions and keep path operations thin.

```python
# FastAPI example (needs: pip install fastapi pydantic) and Python 3.10+
from typing import Annotated, Literal               # type tools
from fastapi import FastAPI                         # framework
from pydantic import BaseModel, Field               # models


class Captured(BaseModel):
    kind: Literal["captured"]                       # discriminator value
    amount: int                                     # rupees


class Failed(BaseModel):
    kind: Literal["failed"]                         # discriminator value
    reason: str                                     # error text


Event = Annotated[Captured | Failed, Field(discriminator="kind")]   # tagged union

app: FastAPI = FastAPI()                            # create app


@app.post("/webhook")                               # POST /webhook
async def webhook(event: Event) -> dict[str, str]:
    match event:                                    # class patterns on Pydantic models
        case Captured(amount=amount):
            return {"msg": f"captured Rs {amount}"}
        case Failed(reason=reason):
            return {"msg": f"failed: {reason}"}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using a bare variable name as if it were a constant
```python
RED = "red"

def color(c: str) -> str:
    match c:
        # Wrong: `RED` is a CAPTURE pattern: it matches anything and rebinds RED!
        # case RED:
        #     return "stop"
        # Right: use a dotted name (Enum / class attribute) or a literal
        case "red":
            return "stop"
        case _:
            return "go"

print(color("red"), color("green"))        # Output: stop go
```

❌ Mistake 2: Putting `case _` (or a capture) before specific cases
```python
def f(x: int) -> str:
    match x:
        # Wrong: this irrefutable pattern first would be a SyntaxError
        # case _: return "any"
        # case 1: return "one"
        case 1:
            return "one"
        case _:                            # Right: wildcard LAST
            return "any"

print(f(1), f(2))                          # Output: one any
```

❌ Mistake 3: Expecting `case [x, y]` to match strings or exact length rules
```python
def f(v: object) -> str:
    match v:
        # Wrong assumption: "ab" would match [x, y]. Strings are NOT matched as sequences.
        case [x, y]:
            return f"pair {x} {y}"
        case _:
            return "not a pair"

print(f([1, 2]), f("ab"))                  # Output: pair 1 2 not a pair
```

❌ Mistake 4: Forgetting that dict patterns ignore extra keys but sequence patterns do not
```python
def g(d: dict) -> str:
    match d:
        case {"a": 1}:                     # extra keys are allowed here
            return "has a=1"
        case _:
            return "no"

print(g({"a": 1, "b": 2}))                 # Output: has a=1
# For sequences the length must match: [1, 2] does not match case [1]
```

---

## 🧠 Tricky Interview Question

```python
def f(x):
    match x:
        case [a, b]:
            return f"seq {a} {b}"
        case {"k": v}:
            return f"map {v}"
        case str() as s:
            return f"str {s}"
        case 1 | 2 | 3:
            return "small"
        case True:
            return "true"
        case other:
            return f"other {other}"

print(f([1, 2]))
print(f("ab"))
print(f({"k": 9, "z": 0}))
print(f(True))
print(f(1.0))
print(f(0))
```

**Answer:**
```
seq 1 2
str ab
map 9
small
small
other 0
```
`[1, 2]` matches the sequence pattern. `"ab"` is a string and strings are **not** treated as sequences by `match`, so it reaches `str()`. The dict has an extra key `z`, but mapping patterns allow extras. `True == 1` and literal number patterns use `==`, so `True` hits `1 | 2 | 3` first (the later `case True` is never reached); likewise `1.0 == 1` gives `small`. `0` matches nothing earlier, and `case other` is a capture that accepts anything. A bare name capture is *irrefutable*, so it must be last.

---

## ⚫ Interview Questions + Answers

Q1: How is `match/case` different from `switch` in other languages?
A1: It matches **structure**, not just values: sequences, mappings, classes, nested shapes, with variable capture, OR-patterns (`|`), `as` binding, and `if` guards. There is no fall-through and no `break`. Only the first matching case runs. It is also a statement, not an expression, and it has no exhaustiveness check at runtime (type checkers like mypy/pyright can check it for enums and unions).

Q2: What is the difference between a capture pattern and a value pattern?
A2: A bare name (`case x:`) always matches and binds the subject to `x` (a capture). To compare with a constant you must use a literal (`case 404`) or a **dotted name** (`case Status.OK`, `case http.HTTPStatus.OK`). So `case RED:` for a module-level constant does not compare, it captures. Wildcard `_` matches anything without binding.

Q3: What does `case Point(x=0, y=y)` do?
A3: It is a class pattern: it checks `isinstance(subject, Point)` and then checks/captures the attributes. Keyword form reads attributes by name. Positional form `Point(0, y)` needs `__match_args__`, which `@dataclass` and `NamedTuple` generate automatically; for normal classes you define `__match_args__ = ("x", "y")`.

Q4: Are strings and bytes matched by sequence patterns?
A4: No. `str`, `bytes` and `bytearray` are explicitly excluded from sequence patterns, so `case [a, b]` does not match `"ab"`. Match them with literal patterns or `str()`. Other sequences like list, tuple, `range` and `deque` match. Mappings match any `collections.abc.Mapping` and ignore extra keys unless you use `**rest` (to capture them) or check them in a guard.

Q5: When should you prefer `if/elif` or a dict dispatch over `match`?
A5: For simple value-to-value mappings use a dict (`HANDLERS[event_type](payload)`), which is data-driven and easy to extend. For two or three boolean conditions, `if/elif` is clearer. Use `match` when branching on the *shape* of data (parsed JSON, ASTs, commands, tagged unions) and when you want to unpack pieces. Also remember `match` needs Python 3.10+; if you must support 3.8/3.9 you cannot use it.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Parsing commands, tokens, ASTs, JSON events
- Branching by type + fields together (class patterns)
- You need to unpack nested structures in one step
- Replacing deep `if/elif` with `isinstance`/`len` checks

❌ Avoid when:
- A simple `if/else` or dict lookup is enough
- You must support Python older than 3.10
- You want to compare with a variable (use `if x == y`, or a dotted name)
- Performance-critical hot loops with a few int comparisons (plain `if` can be faster)

---

## 📊 Visual Diagram
```
 match event:                       subject evaluated once
   │
   ├─ case {"event": "payment.captured", "amount": a}  ── shape fits? ──► yes → run body, STOP
   │                                                      │ no
   ├─ case {"event": "payment.failed", "reason": r}   ── shape fits? ──► yes → run body, STOP
   │                                                      │ no
   ├─ case {"event": name}                            ── shape fits? ──► yes → run body, STOP
   │                                                      │ no
   └─ case _                                          ── always matches ─► default body

 No fall-through.  First match wins.  Captured names (a, r, name) become variables.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Pattern matching | Checking data against shapes | Data की शक्ल मिलाना |
| Subject | The value after `match` | `match` के बाद की value |
| Capture pattern | Bare name that binds a value | Value को नाम में पकड़ना |
| Wildcard `_` | Matches anything, binds nothing | कुछ भी match, कोई binding नहीं |
| Guard | `if` condition after a pattern | Pattern के बाद की `if` शर्त |
| OR pattern | `a \| b` alternatives | विकल्प वाला pattern |
| Class pattern | `Point(x=0)` check type + attrs | Type और attributes जाँचना |
| `__match_args__` | Order for positional class patterns | Positional matching का क्रम |

---

## ⚡ 3-Line Summary
English: `match/case` (3.10+) matches the shape of data (literals, sequences, mappings, classes), captures pieces into variables, supports `|` and `if` guards, and never falls through. A bare name is a capture, so use literals or dotted names for constants, and put `_` last. Use it for commands, events and nested data, not for simple value switches.
Hindi: `match/case` (3.10+) data की शक्ल (literal, sequence, mapping, class) मिलाता है, हिस्सों को variables में पकड़ता है, `|` और `if` guard चलते हैं, और fall-through नहीं होता। Bare name capture होता है, इसलिए constants के लिए literal या dotted name लो और `_` आखिर में रखो। Commands, events और nested data के लिए use करो, सामान्य value switch के लिए नहीं।

---

## ➡️ Next Topic
**038. Loops: for / while** — iteration, `range`, `break`/`continue`, and the `for ... else` clause.
