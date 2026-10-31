---

# 040. break + continue + pass
# हिंदी में: break + continue + pass (loop control)

---

## 🔵 Simple Definition (English)
These three keywords control flow inside loops and blocks. `break` leaves the loop completely. `continue` skips the rest of this round and starts the next one. `pass` does nothing: it is a placeholder because Python needs at least one statement in every block.

## 🔵 सरल परिभाषा (Hindi)
ये तीन keywords loop के flow को control करते हैं। `break` पूरा loop छोड़ देता है। `continue` इस round का बाकी हिस्सा छोड़कर अगला round शुरू करता है। `pass` कुछ नहीं करता, यह सिर्फ placeholder है क्योंकि हर block में कम से कम एक statement चाहिए।

---

## 🔴 Problem it Solves
Without them you need extra flag variables and deep `if` nesting: "found = False ... if not found ...". `break` stops work once the answer is found, `continue` filters bad items early (a guard clause), and `pass` lets you write empty classes, functions and except blocks without a syntax error because Python has no `{}`.

## 🔴 यह क्यों बना? (Hindi)
इनके बिना flag variables और गहरे nested `if` लिखने पड़ते। `break` जवाब मिलते ही काम रोक देता है, `continue` खराब items को जल्दी skip करता है, और `pass` से खाली class/function/except बिना syntax error के लिख सकते हैं, क्योंकि Python में `{}` नहीं होता।

---

## 🟢 How it Works — Step by Step

```
break    → Step 1: exit the nearest enclosing loop NOW
           Step 2: skip the loop's else block
           Step 3: continue with code after the loop

continue → Step 1: stop current iteration
           Step 2: for → take next item; while → re-check condition

pass     → Step 1: do nothing, move to next line
```

## 🟢 कैसे काम करता है? (Hindi)
```
break    → सबसे अंदर वाला loop तुरंत खत्म, else भी skip
continue → मौजूदा round छोड़ो, अगले round पर जाओ
pass     → कुछ नहीं करता, बस block को valid बनाता है
```

---

## 🟡 Real World Example
Swiggy bulk order import: loop over rows, `continue` on rows with a missing phone number, `break` when a "TOTAL" footer row appears, and `pass` in an `except` for a known harmless error. In an AI pipeline: skip empty chunks (`continue`), stop reading once the token budget is full (`break`).

## 🟡 Real Example Hindi mein
Swiggy के bulk order import में: phone number न हो तो row पर `continue`, "TOTAL" footer आते ही `break`, और किसी बेहानिकारक error के except में `pass`। AI pipeline में: खाली chunks `continue` से skip, token budget भरते ही `break`।

---

## 💻 Code Example — Basic
```python
# Basic break / continue / pass - every line commented
from typing import List  # type hint helper

nums: List[int] = [1, 2, 3, 4, 5, 6]  # sample data

for n in nums:  # walk every number
    if n == 4:  # stop condition
        break  # leave the loop entirely
    print("break demo:", n)  # runs for 1, 2, 3 only
# Output:
# break demo: 1
# break demo: 2
# break demo: 3

for n in nums:  # walk again
    if n % 2 == 0:  # even numbers are unwanted
        continue  # skip to the next number
    print("continue demo:", n)  # only odd numbers reach here
# Output:
# continue demo: 1
# continue demo: 3
# continue demo: 5


class EmptyModel:  # a class with no body yet
    pass  # placeholder keeps the syntax valid


def todo() -> None:  # function to implement later
    pass  # does nothing for now


print(EmptyModel(), todo())  # todo() returns None
# Output: <__main__.EmptyModel object at 0x...> None  (address differs per run)

for n in range(3):  # loop three times
    if n == 1:  # special case
        pass  # "I have nothing to do here" - loop continues normally
    print("after pass:", n)  # still runs for every n
# Output:
# after pass: 0
# after pass: 1
# after pass: 2

# break only exits the INNER loop
for i in range(2):  # outer loop
    for j in range(5):  # inner loop
        if j == 2:  # inner stop
            break  # exits only the inner loop
        print(i, j)  # prints j = 0, 1 for each i
# Output:
# 0 0
# 0 1
# 1 0
# 1 1
```

## 💻 Code Example — Advanced
```python
# Production style: guard clauses, exit from nested loops, for-else, suppress
from contextlib import suppress  # clean replacement for try/except/pass
from typing import Dict, List, Optional, Tuple  # type hints

rows: List[Dict[str, Optional[str]]] = [  # imported CSV-like rows
    {"id": "1", "phone": "999"},  # good row
    {"id": "2", "phone": None},  # bad row: no phone
    {"id": "TOTAL", "phone": None},  # footer row, stop here
    {"id": "4", "phone": "888"},  # never reached
]

valid_ids: List[str] = []  # collects good ids
for row in rows:  # loop over the rows
    if row["id"] == "TOTAL":  # footer marks end of data
        break  # stop reading
    if row["phone"] is None:  # guard clause for bad data
        continue  # skip, no deep nesting needed
    valid_ids.append(row["id"] or "")  # keep the good id
print(valid_ids)  # Output: ['1']


def find_pair(grid: List[List[int]], target: int) -> Optional[Tuple[int, int]]:
    for r, row in enumerate(grid):  # outer loop with row index
        for c, value in enumerate(row):  # inner loop with column index
            if value == target:  # found it
                return (r, c)  # return exits BOTH loops at once
    return None  # not found anywhere


print(find_pair([[1, 2], [3, 4]], 3))  # Output: (1, 0)
print(find_pair([[1, 2], [3, 4]], 9))  # Output: None


def is_prime(n: int) -> bool:  # classic for-else use
    if n < 2:  # 0 and 1 are not prime
        return False  # quick exit
    for d in range(2, int(n ** 0.5) + 1):  # test divisors up to sqrt(n)
        if n % d == 0:  # divisible: not prime
            break  # stop searching
    else:  # no break happened: nothing divided n
        return True  # so it is prime
    return False  # we broke out, so not prime


print([x for x in range(2, 20) if is_prime(x)])  # Output: [2, 3, 5, 7, 11, 13, 17, 19]

# pass inside except is dangerous; suppress() makes the intent explicit
data: Dict[str, int] = {"a": 1}  # small dict
with suppress(KeyError):  # ignore ONLY KeyError
    print(data["missing"])  # raises KeyError, silently ignored
print("still running")  # Output: still running
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
for n in [1, 2, 3, 4]:
    if n == 2:
        continue          # skip 2
    if n == 4:
        break             # stop at 4
    print(n)              # 1, 3

class Todo:
    pass                  # empty block needs pass
```

```javascript
// JavaScript
for (const n of [1, 2, 3, 4]) {
  if (n === 2) continue;  // skip 2
  if (n === 4) break;     // stop at 4
  console.log(n);         // 1, 3
}

class Todo {}             // empty braces are fine, no pass needed
outer: for (;;) { break outer; }  // JS has labeled break; Python does NOT
```

Key differences: Python has no `pass` equivalent in JS because empty `{}` is legal. JS has labeled `break outer`; Python does not, so use `return`, a flag, or `for...else`. Python's `...` (Ellipsis) is also a common placeholder.

---

## 🟠 FastAPI Connection
In FastAPI code, `continue` is used to skip invalid items in bulk endpoints, `break` to stop streaming when a client disconnects, and `pass` for placeholder route stubs or abstract hooks while designing.

```python
# FastAPI: bulk endpoint skipping bad rows (needs: pip install fastapi)
from typing import Dict, List  # type hints
from fastapi import FastAPI  # the framework

app: FastAPI = FastAPI()  # create app


@app.post("/bulk")  # POST /bulk
def bulk(items: List[Dict[str, str]]) -> Dict[str, int]:  # body is a list of dicts
    saved: int = 0  # how many were accepted
    for item in items:  # loop over the payload
        if not item.get("email"):  # guard: email missing
            continue  # skip this item only
        saved += 1  # pretend we saved it
    return {"saved": saved}  # report the count


@app.get("/coming-soon")  # route not ready yet
def coming_soon() -> None:  # stub
    pass  # placeholder, returns null
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Thinking `break` exits all nested loops
```python
# Wrong assumption: break stops everything
for i in range(3):
    for j in range(3):
        if j == 1:
            break           # exits ONLY the inner loop; outer continues

# Correct: wrap in a function and return, or use a flag
def search() -> None:
    for i in range(3):
        for j in range(3):
            if j == 1:
                return      # leaves both loops
```

❌ Mistake 2: `continue` in a `while` before updating the counter
```python
# Wrong - infinite loop, i never increases when i == 2:
i = 0
# while i < 5:
#     if i == 2:
#         continue
#     i += 1

# Correct - update first:
i = 0
while i < 5:
    i += 1
    if i == 2:
        continue
```

❌ Mistake 3: Silent `except: pass`
```python
# Wrong - hides every bug, even typos and Ctrl+C:
# try:
#     risky()
# except:
#     pass

# Correct - catch a specific error and log it:
# except ValueError as exc:
#     logger.warning("bad value: %s", exc)
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
for i in range(5):
    if i == 3:
        break
    pass
else:
    print("A")
print("B", i)

def f():
    try:
        return "try"
    finally:
        for _ in range(1):
            break
        print("finally")
print(f())
```

**Answer**: `B 3`, then `finally`, then `try`. The `break` skips `else`, so "A" never prints. In `f`, the `break` only affects the tiny inner loop; `finally` still runs its print, and the function returns "try".

---

## ⚫ Interview Questions + Answers

Q1: Difference between `break`, `continue` and `pass`?
A1: `break` ends the loop. `continue` skips to the next iteration. `pass` is a no-op placeholder that does not change flow at all.

Q2: How do you break out of nested loops in Python?
A2: There is no labeled break. Options: put the loops in a function and `return`; use a flag variable; use `for...else` with `continue`/`break`; or raise and catch a custom exception (last resort).

Q3: Does `continue` skip the `else` of a loop?
A3: No. `else` only depends on whether `break` happened. `continue` just moves on to the next iteration, and `else` runs at the end if no `break` occurred.

Q4: Why does Python need `pass`?
A4: Blocks are defined by indentation, and an empty block is a `SyntaxError`. `pass` (or `...`) fills it. Typical uses: empty classes, custom exceptions, stubs, abstract methods.

Q5: What is the difference between `pass` and `continue`?
A5: `pass` does nothing and the code below it still runs. `continue` jumps to the next iteration, so the code below it in the body is skipped.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- `break` once the answer is found (search, token budget, sentinel)
- `continue` as a guard clause to avoid deep nesting
- `pass` for stubs, empty exception classes, placeholders

❌ Avoid when:
- `except: pass` hides real errors (log or use `suppress`)
- Many `break`/`continue` make the loop hard to read (extract a function)
- A comprehension with a condition does the same filter more cleanly

---

## 📊 Visual Diagram

```
 for item in items:
   ├─ continue ──► jump to next item (skip rest of body)
   ├─ break    ──► jump OUT of loop (skip else)
   ├─ pass     ──► nothing, go to next line
   └─ (end)    ──► next item ... finally else runs if no break
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| break | Exit the loop | loop से बाहर निकलना |
| continue | Skip to next iteration | अगले round पर जाना |
| pass | Do-nothing placeholder | कुछ न करने वाला placeholder |
| Guard clause | Early skip of bad input | खराब input को जल्दी हटाना |
| Ellipsis `...` | Another placeholder | pass जैसा दूसरा placeholder |
| suppress | Ignore a named exception | चुने हुए error को ignore करना |

---

## ⚡ 3-Line Summary
English: `break` exits the loop, `continue` skips to the next iteration, `pass` is an empty placeholder. `break` only leaves the innermost loop and skips `else`. Avoid `except: pass`; use specific exceptions or `suppress`.
Hindi: `break` loop से निकलता है, `continue` अगले round पर जाता है, `pass` खाली placeholder है। `break` सिर्फ सबसे अंदर वाला loop छोड़ता है और `else` skip करता है। `except: pass` से बचें।

---

## ➡️ Next Topic
**041. range() Function** — generate number sequences for loops with start, stop and step.
