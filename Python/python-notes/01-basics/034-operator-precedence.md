---

# 034. Operator Precedence
# हिंदी में: Operator Precedence — कौन सा operator पहले चलेगा

---

## 🔵 Simple Definition (English)
Operator precedence is the rule that decides which operator is evaluated first in an expression with many operators. Higher precedence runs first. When two operators have equal precedence, associativity (usually left-to-right) decides. Parentheses always win.

## 🔵 सरल परिभाषा (Hindi)
Operator precedence वह नियम है जो तय करता है कि कई operators वाले expression में कौन सा पहले evaluate होगा। ऊँची precedence पहले चलती है। बराबर precedence हो तो associativity (आमतौर पर left-to-right) देखी जाती है। Parentheses सबसे ऊपर।

---

## 🔴 Problem it Solves
Without rules, `2 + 3 * 4` could be 20 or 14. Precedence removes the ambiguity so every Python program gives the same answer. Knowing it prevents subtle bugs like `not a == b` or `x and y or z`.

## 🔴 यह क्यों बना? (Hindi)
नियम न हों तो `2 + 3 * 4` का जवाब 20 भी हो सकता है, 14 भी। Precedence ambiguity हटाती है ताकि हर program में एक ही answer आए।

---

## 🟢 How it Works — Step by Step

```
Highest  1. ( )            parentheses
         2. **             power (right-to-left)
         3. +x -x ~x       unary
         4. * / // %       multiply, divide
         5. + -            add, subtract
         6. << >>          shifts
         7. &              bitwise AND
         8. ^              bitwise XOR
         9. |              bitwise OR
        10. in, not in, is, is not, < <= > >= != ==   (comparisons, chain)
        11. not
        12. and
        13. or
Lowest  14. if-else (ternary), lambda, :=
```

## 🟢 कैसे काम करता है? (Hindi)
```
ऊपर वाली list में ऊपर = पहले चलेगा।
पहले ( ), फिर **, फिर unary, फिर * /, फिर + -,
फिर comparisons, फिर not, and, or — सबसे अंत में ternary/lambda।
शक हो तो ( ) लगाओ।
```

---

## 🟡 Real World Example
Swiggy bill: `total = price * qty + delivery - discount` — multiplication happens before addition, so it is correct without brackets. Access check: `is_admin or is_owner and not banned` — `and` binds tighter than `or`, so it may not mean what the developer intended.

## 🟡 Real Example Hindi mein
Swiggy bill में `price * qty + delivery - discount` सही चलता है क्योंकि गुणा पहले होता है। पर `is_admin or is_owner and not banned` में `and`, `or` से पहले चलता है — अक्सर developer की सोच से अलग।

---

## 💻 Code Example — Basic
```python
# Operator precedence demo
print(2 + 3 * 4)                  # 14  -> * before +
print((2 + 3) * 4)                # 20  -> brackets first
print(2 ** 3 ** 2)                # 512 -> ** is right-associative: 2 ** (3 ** 2)
print(-2 ** 2)                    # -4  -> ** binds tighter than unary minus
print((-2) ** 2)                  # 4   -> brackets change it
print(10 - 4 - 3)                 # 3   -> left to right: (10 - 4) - 3
print(7 // 2 * 2)                 # 6   -> (7 // 2) * 2
print(10 % 4 * 2)                 # 4   -> (10 % 4) * 2

a: bool = True                    # boolean a
b: bool = False                   # boolean b
c: bool = True                    # boolean c
print(a or b and c)               # True -> a or (b and c)
print((a or b) and c)             # True -> brackets
print(not a == b)                 # True -> not (a == b)

x: int = 5                        # integer
print(1 < x < 10)                 # True -> chained comparison
print(x + 1 > 5 and x * 2 < 20)   # True -> arithmetic, then comparison, then and
```
Output:
```
14
20
512
-4
4
3
6
4
True
True
True
True
True
```

## 💻 Code Example — Advanced
```python
# Real traps: and/or vs ternary, bitwise vs comparison, walrus
from typing import Optional                      # type hint

is_admin: bool = False                           # not an admin
is_owner: bool = True                            # but owner
banned: bool = True                              # and banned

buggy: bool = is_admin or is_owner and not banned     # is_admin or (is_owner and (not banned))
fixed: bool = (is_admin or is_owner) and not banned   # intended meaning
print(buggy, fixed)                              # False False  (both False here)

is_admin = True                                  # change: now admin
buggy = is_admin or is_owner and not banned      # True: admin short-circuits
fixed = (is_admin or is_owner) and not banned    # False: banned blocks everyone
print(buggy, fixed)                              # True False  <- different results!

# In Python bitwise & binds TIGHTER than == (unlike C/JS), so this works:
flags: int = 6                                   # binary 110
print(flags & 2 == 2)                            # True  -> (flags & 2) == 2
print(flags | 1 == 7)                            # True  -> (flags | 1) == 7 (6|1 = 7)

# Ternary is almost the lowest:
n: int = 5                                       # a number
label: str = "big" if n > 3 else "small"         # (n > 3) evaluated first
print(label)                                     # big
msg: str = "n=" + "odd" if n % 2 else "even"     # ("n=" + "odd") if n % 2 else "even"
print(msg)                                       # n=odd
msg2: str = "n=" + ("odd" if n % 2 else "even")  # brackets fix intent
print(msg2)                                      # n=odd

# Walrus has the lowest precedence, so wrap it:
data: list[int] = [1, 2, 3]                      # sample list
if (size := len(data)) > 2:                      # brackets needed around :=
    print("size", size)                          # size 3

# Short-circuit returns operands, not bools:
name: Optional[str] = None                       # no name
print(name or "guest")                           # guest
print(0 or [] or "x")                            # x
print(1 and 2 and 3)                             # 3
```
Output:
```
False False
True False
True
True
big
n=odd
n=odd
size 3
guest
x
3
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
print(2 ** 3 ** 2)        # 512  (right-associative)
print(-2 ** 2)            # -4
print(not 1 == 2)         # True
print(1 < 5 < 10)         # True (chained)
print(5 & 3 == 1)         # (5 & 3) == 1 -> True (& is tighter than ==)
```
```javascript
// JavaScript
console.log(2 ** 3 ** 2);     // 512 (same)
// console.log(-2 ** 2);      // SyntaxError! JS forces brackets
console.log(!1 == 2);         // false -> (!1) == 2  (! binds tighter than ==)
console.log(1 < 5 < 10);      // true by luck: (1<5)=true -> true<10
console.log(5 & 3 == 1);      // 5 & (3 == 1) -> 5 & false -> 0 (JS: == is tighter!)
```
Key difference: Python `not` is LOW precedence (`not a == b` is `not (a == b)`), JS `!` is HIGH. Python chains comparisons properly; JS does not. Also, bitwise `&` is tighter than `==` in Python but looser in JS/C.

---

## 🟠 FastAPI Connection
Precedence bites in dependency/permission checks and query filters.

```python
from fastapi import Depends, FastAPI, HTTPException   # imports

app: FastAPI = FastAPI()                              # create app


def check(is_admin: bool, is_owner: bool, banned: bool) -> None:   # permission rule
    if not ((is_admin or is_owner) and not banned):   # explicit brackets = clear intent
        raise HTTPException(status_code=403, detail="Denied")   # reject


@app.get("/secret")                                   # GET /secret
async def secret(is_admin: bool = False, is_owner: bool = False, banned: bool = False) -> dict:
    check(is_admin, is_owner, banned)                 # run the rule
    return {"ok": True}                               # allowed
```
In SQLAlchemy filters, `&` and `|` have HIGHER precedence than `>` and `==`, so write `(User.age > 18) & (User.active == True)` with brackets or you get errors.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Mixing and/or without brackets
```python
# Wrong — unclear:
# allowed = is_admin or is_owner and not banned

# Correct — explicit:
is_admin, is_owner, banned = True, False, False
allowed = (is_admin or is_owner) and not banned
print(allowed)   # True
```

❌ Mistake 2: Using `&` / `|` instead of `and` / `or` on comparisons
```python
# Wrong — & binds tighter than >, so this is x > (0 & x) < 10:
x = 5
# if x > 0 & x < 10: ...    # wrong meaning

# Correct:
if x > 0 and x < 10:
    print("in range")
```

---

## 🧠 Tricky Interview Question

```python
print(not 1 + 1 == 2 and 3 > 2 or 0)
```
Answer: Step by step: `1 + 1` = 2; `2 == 2` is True; `not True` is False; `False and ...` short-circuits to False; then `False or 0` returns the last operand, `0`. Printed: `0` (an int, not False!). `or` returns the last evaluated operand.

---

## ⚫ Interview Questions + Answers

Q1: What is the result of `-3 ** 2`?
A1: `-9`. `**` binds tighter than unary minus, so it is `-(3 ** 2)`.

Q2: Is `**` left or right associative?
A2: Right. `2 ** 3 ** 2` = `2 ** 9` = 512. Most other binary operators are left-associative.

Q3: Order of `not`, `and`, `or`?
A3: `not` first, then `and`, then `or`. Like NOT, AND, OR in logic.

Q4: What does `a < b < c` mean?
A4: `a < b and b < c`, with `b` evaluated only once. Works with any comparison operators, including `in` and `is`.

Q5: Best practice for complex expressions?
A5: Use parentheses or split into named variables. Readability beats memorising the table. Linters (ruff, flake8) warn about ambiguous mixes.

---

## 🔷 When to Use + When Not to Use
✅ Use (rely on precedence) when:
- Simple arithmetic like `a * b + c`
- Chained comparisons like `0 < x < 10`

❌ Avoid relying on it when:
- Mixing `and`/`or`/`not`
- Using `&`/`|` with comparisons (e.g. SQLAlchemy filters)
- Mixing ternary with `+` or `or`

---

## 📊 Visual Diagram
```
2 + 3 * 4 ** 2
          └─┬─┘
     4 ** 2 = 16        (1st)
     3 * 16 = 48        (2nd)
     2 + 48 = 50        (3rd)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Precedence | Which operator goes first | कौन पहले चलेगा |
| Associativity | Order for equal precedence | बराबर precedence पर क्रम |
| Short-circuit | Stop once result known | नतीजा पता चलते ही रुकना |
| Unary | Operator with one operand | एक operand वाला operator |
| Chained comparison | `a < b < c` | जुड़ी तुलना |
| Walrus | `:=` assignment expression | Expression में assignment |

---

## ⚡ 3-Line Summary
English: Order is brackets, `**`, unary, `* / // %`, `+ -`, bitwise, comparisons, `not`, `and`, `or`, ternary. `**` is right-associative; others are left. When in doubt, add parentheses.
Hindi: क्रम: brackets, `**`, unary, गुणा-भाग, जोड़-घटाव, bitwise, comparison, `not`, `and`, `or`, ternary। `**` right-to-left चलता है। शक हो तो brackets लगाओ।

---

## ➡️ Next Topic
**036. Ternary Expression** — one-line `x if condition else y` and its pitfalls.
