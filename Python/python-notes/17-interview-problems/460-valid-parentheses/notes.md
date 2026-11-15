---

# 460. Valid Parentheses
# हिंदी में: सही कोष्ठक (Brackets) की जाँच

Full runnable solution with asserts: `main.py` (same folder). Run: `python3 main.py`.

---

## 🔵 Simple Definition (English)
Given a string of brackets `()[]{}`, check whether every opening bracket is closed by the same type of bracket in the correct order. The standard tool is a stack.

## 🔵 सरल परिभाषा (Hindi)
Brackets `()[]{}` की string दी गई है। जाँचना है कि हर खुला bracket उसी type के bracket से सही क्रम में बंद हुआ या नहीं। इसके लिए stack सबसे सही tool है।

---

## 🔴 Problem it Solves
Compilers, JSON parsers, code editors and expression evaluators must reject input like `([)]`. Counting brackets is not enough, because the order and the type both matter. A stack remembers the most recent unmatched opener.

## 🔴 यह क्यों बना? (Hindi)
Compiler, JSON parser, code editor और expression calculator को `([)]` जैसा input reject करना होता है। सिर्फ गिनती काफी नहीं है, क्योंकि क्रम और type दोनों मायने रखते हैं। Stack सबसे आख़िरी खुला bracket याद रखता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Make an empty stack
Step 2 → Opener ( [ { → push it
Step 3 → Closer ) ] } → pop the top; it must be the matching opener
Step 4 → Stack empty or wrong type at a closer → return False
Step 5 → At the end, valid only if the stack is empty
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → खाली stack बनाओ
Step 2 → खुला bracket मिले तो push करो
Step 3 → बंद bracket मिले तो top pop करो, वह matching opener होना चाहिए
Step 4 → stack खाली हो या type गलत हो तो False
Step 5 → अंत में stack खाली हो तभी valid
```

---

## 🟡 Real World Example
A FastAPI service accepts a user-written formula like `(price * (qty + 2))` for a Razorpay discount rule. Before evaluating it, the service checks brackets with this function. A code editor (VS Code) highlights an unmatched `}` the same way.

## 🟡 Real Example Hindi mein
FastAPI service में user Razorpay discount rule के लिए `(price * (qty + 2))` जैसा formula लिखता है। Evaluate करने से पहले यही function brackets जाँचता है। VS Code जैसा editor भी unmatched `}` इसी तरह पकड़ता है।

---

## 💻 Code Example — Basic
```python
# Basic stack check, every line commented
def is_valid(s: str) -> bool:  # returns True when brackets match
    stack: list[str] = []  # holds openers that are not closed yet
    pairs: dict[str, str] = {")": "(", "]": "[", "}": "{"}  # closer -> opener
    for ch in s:  # look at each character
        if ch in pairs:  # it is a closer
            if not stack or stack.pop() != pairs[ch]:  # nothing to match, or wrong type
                return False  # invalid
        else:  # it is an opener (we assume only brackets here)
            stack.append(ch)  # remember it
    return not stack  # valid only if nothing is left open


print(is_valid("()[]{}"))  # all matched
# Output: True
print(is_valid("(]"))  # wrong type
# Output: False
print(is_valid("([)]"))  # wrong order
# Output: False
print(is_valid(""))  # empty string has nothing unmatched
# Output: True
```

## 💻 Code Example — Advanced
```python
# Production style: ignore other characters, report the error position
from typing import Dict, List, Optional, Tuple  # type hints

PAIRS: Dict[str, str] = {")": "(", "]": "[", "}": "{"}  # closer -> opener
OPENERS = set(PAIRS.values())  # fast membership test


def find_error(text: str) -> Optional[int]:
    """Return the index of the first bracket error, or None if valid."""
    stack: List[Tuple[str, int]] = []  # (opener, index) pairs
    for i, ch in enumerate(text):  # keep the position for error messages
        if ch in OPENERS:  # opener
            stack.append((ch, i))  # push with position
        elif ch in PAIRS:  # closer
            if not stack or stack[-1][0] != PAIRS[ch]:  # no match
                return i  # position of the bad closer
            stack.pop()  # matched, remove opener
    return stack[0][1] if stack else None  # leftover opener is the error


print(find_error("(price * (qty + 2))"))  # valid formula
# Output: None
print(find_error("(price * (qty + 2)"))  # first '(' never closed
# Output: 0
print(find_error("a + b)"))  # extra closer at index 5
# Output: 5
print(find_error("{[(])}"))  # ']' at index 3 does not match '('
# Output: 3
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: list is the stack (append / pop at the end)
stack: list[str] = []
stack.append("(")
top = stack.pop()
```

```javascript
// JavaScript: array is the stack (push / pop)
const stack = [];
stack.push("(");
const top = stack.pop();   // undefined if empty, no error
```

Key difference: Python's `list.pop()` on an empty list raises `IndexError`, while JS `pop()` returns `undefined`. In Python, check `if not stack` first.

---

## 🟠 FastAPI Connection
Validate a formula in a request body before processing it, and return `422` with a clear message.

```python
# FastAPI: reject unbalanced formulas (pip install fastapi)
from fastapi import FastAPI, HTTPException  # app and error
from pydantic import BaseModel  # request model


class Formula(BaseModel):  # request body
    text: str  # user formula


app: FastAPI = FastAPI()  # create app
PAIRS = {")": "(", "]": "[", "}": "{"}  # closer -> opener


def balanced(s: str) -> bool:  # same stack idea
    st: list[str] = []  # openers
    for ch in s:  # scan
        if ch in "([{":  # opener
            st.append(ch)  # push
        elif ch in PAIRS and (not st or st.pop() != PAIRS[ch]):  # bad closer
            return False  # invalid
    return not st  # nothing left open


@app.post("/formula")  # POST /formula
def check(body: Formula) -> dict[str, bool]:
    if not balanced(body.text):  # validate
        raise HTTPException(status_code=422, detail="unbalanced brackets")  # error
    return {"ok": True}  # accepted
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Popping from an empty stack
```python
# Wrong - crashes on ")" because the stack is empty:
# stack.pop()  -> IndexError

# Correct - check first:
# if not stack or stack.pop() != pairs[ch]: return False
```

❌ Mistake 2: Only counting brackets
```python
# Wrong - "([)]" has equal counts but is invalid:
print("([)]".count("(") == "([)]".count(")"))  # True (misleading)

# Correct - use a stack so order and type are checked
```

❌ Mistake 3: Forgetting the final check
```python
# Wrong - "(((" returns True if you only check closers:
# return True

# Correct - return not stack
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
def is_valid(s):
    stack = []
    pairs = {")": "(", "]": "[", "}": "{"}
    for ch in s:
        if ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
        else:
            stack.append(ch)
    return not stack

print(is_valid("a(b)c"), is_valid("()"), is_valid("(("))
```

**Answer**:
```
False True False
```
Letters like `a` and `b` go to the `else` branch and are pushed as if they were openers. When `)` arrives it pops `b`, which is not `(`, so the result is `False`. The fix is `elif ch in OPENERS:` so that other characters are ignored (see `main.py`).

---

## ⚫ Interview Questions + Answers

Q1: Why a stack and not a counter?
A1: Brackets nest, so the latest opener must close first (LIFO). A counter cannot tell `(]` from `()`.

Q2: Time and space complexity?
A2: O(n) time (one pass) and O(n) space in the worst case, for example `"((((("`.

Q3: Can we do it in O(1) space?
A3: Only for a single bracket type (one counter). With several types you need the stack.

Q4: What about an empty string?
A4: Valid. Nothing is unmatched.

Q5: How would you extend it to HTML tags?
A5: Push tag names instead of characters and compare the closing tag name with the stack top.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- You parse nested structures (brackets, tags, expressions)
- You need the most recent unmatched item (LIFO)

❌ Avoid when:
- You have only one bracket type and need O(1) space (use a counter)
- You need a full parser (use a real library such as `ast` or a grammar)

---

## 📊 Visual Diagram

```
input: { [ ( ) ] }

char  action            stack (bottom -> top)
{     push              {
[     push              { [
(     push              { [ (
)     pop '(' matches   { [
]     pop '[' matches   {
}     pop '{' matches   (empty)  -> True
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Stack | Last in, first out | आख़िरी आया, पहले गया |
| Opener | `(`, `[`, `{` | खुलने वाला bracket |
| Closer | `)`, `]`, `}` | बंद होने वाला bracket |
| Balanced | Every opener has its closer | संतुलित |
| LIFO | Last In First Out | LIFO क्रम |

---

## ⚡ 3-Line Summary
English: Push openers, pop on closers and compare the type. The string is valid only if no mismatch happens and the stack is empty at the end. O(n) time, O(n) space.
Hindi: Opener को push करो, closer पर pop करके type मिलाओ। कोई mismatch न हो और अंत में stack खाली हो तभी valid। O(n) time, O(n) space।

---

## ➡️ Next Topic
**461. Merge Two Sorted Lists** — combine two sorted sequences with two pointers.
