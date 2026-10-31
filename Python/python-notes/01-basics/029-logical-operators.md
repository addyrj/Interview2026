---

# 029. Logical Operators (and, or, not)
# हिंदी में: Logical Operators (and, or, not)

---

## 🔵 Simple Definition (English)
Logical operators combine conditions. `and` is true when both sides are true, `or` is true when at least one side is true, `not` flips a value. In Python they use **words** (not `&&`, `||`, `!`), they **short-circuit**, and `and`/`or` return one of the operands, not always `True`/`False`.

## 🔵 सरल परिभाषा (Hindi)
Logical operators conditions को जोड़ते हैं। `and` तब true जब दोनों true, `or` तब true जब कम से कम एक true, `not` value को पलट देता है। Python में ये **शब्द** हैं (`&&`, `||`, `!` नहीं), ये **short-circuit** करते हैं, और `and`/`or` हमेशा `True`/`False` नहीं बल्कि किसी एक operand को return करते हैं।

---

## 🔴 Problem it Solves
Real decisions have many conditions: "user is logged in AND has permission", "coupon valid OR user is premium". Without logical operators you would nest many `if`s. Short-circuiting also gives safety (check `user is not None and user.age > 18` without crashing) and speed (skip expensive checks). Returning operands enables defaults: `name = given or "guest"`.

## 🔴 यह क्यों बना? (Hindi)
असली फैसलों में कई conditions होती हैं: "user logged in AND permission है", "coupon valid OR user premium"। Logical operators न हों तो बहुत सारे nested `if` लगते। Short-circuit से safety (`user is not None and user.age > 18` crash नहीं करता) और speed (महँगी checks skip) मिलती है। Operand return होने से defaults बनते हैं: `name = given or "guest"`।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Truthiness: each operand is judged as truthy or falsy
           Falsy: False, None, 0, 0.0, "", [], (), {}, set(), range(0)
           Everything else is truthy
Step 2 → a and b :
           if a is falsy  → return a   (b is NOT evaluated)
           else           → return b
Step 3 → a or b :
           if a is truthy → return a   (b is NOT evaluated)
           else           → return b
Step 4 → not a :  always returns a real bool (True / False)
Step 5 → Precedence: not  >  and  >  or      (use brackets for clarity)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → हर operand truthy या falsy माना जाता है
         Falsy: False, None, 0, 0.0, "", [], (), {}, set()
Step 2 → a and b : a falsy हो तो a लौटाओ (b चलता ही नहीं), नहीं तो b
Step 3 → a or b  : a truthy हो तो a लौटाओ (b चलता ही नहीं), नहीं तो b
Step 4 → not a   : हमेशा असली bool देता है
Step 5 → Precedence: not > and > or (बेहतर है brackets लगाओ)
```

---

## 🟡 Real World Example
Free-delivery rule on a food app: `if total >= 199 and not is_blocked:`. Discount rule: `if is_premium or coupon_valid:`. Config default: `timeout = user_timeout or 30`. Safe access: `if user and user.profile and user.profile.email:`. In FastAPI auth: `if token and token.startswith("Bearer ")` stops `startswith` from running on `None`.

## 🟡 Real Example Hindi mein
Food app का free-delivery नियम: `if total >= 199 and not is_blocked:`। Discount: `if is_premium or coupon_valid:`। Config default: `timeout = user_timeout or 30`। Safe access: `if user and user.profile and user.profile.email:`। FastAPI auth में `if token and token.startswith("Bearer ")` से `None` पर `startswith` नहीं चलता।

---

## 💻 Code Example — Basic
```python
# Logical operators basics

age: int = 25                              # a number
has_id: bool = True                        # a flag

# and: both must be true
print(age >= 18 and has_id)                # Output: True
print(age >= 30 and has_id)                # Output: False

# or: at least one must be true
print(age < 18 or has_id)                  # Output: True

# not: flips the value
print(not has_id)                          # Output: False

# Truthy and falsy values
for value in [0, 1, "", "hi", [], [0], None]:      # try several values
    print(repr(value), bool(value))                # show how Python sees each
# Output:
# 0 False
# 1 True
# '' False
# 'hi' True
# [] False
# [0] True
# None False

# and / or RETURN an operand, not just a bool
print(0 and 5)                             # Output: 0     first falsy value
print(3 and 5)                             # Output: 5     all truthy -> last value
print(0 or 5)                              # Output: 5     first truthy value
print("" or "guest")                       # Output: guest default value pattern

# Short-circuit: the right side is skipped when not needed
def noisy() -> bool:                       # shows when it runs
    print("noisy called")
    return True

print(False and noisy())                   # Output: False  (noisy NOT called)
print(True or noisy())                     # Output: True   (noisy NOT called)
print(True and noisy())                    # Output: noisy called  then  True

# Combining with brackets for clarity
is_member: bool = False
total: int = 250
if (total >= 199 and has_id) or is_member:
    print("free delivery")                 # Output: free delivery
```

## 💻 Code Example — Advanced
```python
# Advanced: defaults, guards, short-circuit safety, any/all, and a permission engine
from dataclasses import dataclass, field        # small models


@dataclass
class User:
    name: str                                    # display name
    email: str | None = None                     # may be missing
    roles: set[str] = field(default_factory=set) # permissions
    banned: bool = False                         # flag


def display_name(user: User | None) -> str:
    """Safe chain: stops at the first falsy value, no AttributeError."""
    return (user and user.name) or "Anonymous"   # None -> "Anonymous"


def can_publish(user: User | None, draft: str) -> bool:
    """All conditions must pass; cheap checks first."""
    return bool(
        user                                     # logged in?
        and not user.banned                      # not banned?
        and "editor" in user.roles               # has role?
        and draft.strip()                        # not empty text?
    )


def pick_email(primary: str | None, backup: str | None) -> str:
    """Use `or` to chain fallbacks (but beware of valid falsy values!)."""
    return primary or backup or "no-reply@example.com"


def get_port(value: int | None) -> int:
    """Correct default for numbers: use `is None`, because 0 is falsy."""
    return 8000 if value is None else value      # keeps a valid 0


calls: list[str] = []                            # record which checks ran


def check(name: str, result: bool) -> bool:
    calls.append(name)                           # remember it was evaluated
    return result


def main() -> None:
    editor: User = User("Priya", "p@x.com", {"editor"})
    guest: User = User("Rahul")
    print(display_name(editor), display_name(None))   # Output: Priya Anonymous
    print(can_publish(editor, "Hello"))               # Output: True
    print(can_publish(guest, "Hello"))                # Output: False
    print(can_publish(None, "Hello"))                 # Output: False
    print(can_publish(editor, "   "))                 # Output: False
    print(pick_email(None, ""))                       # Output: no-reply@example.com

    print(get_port(0), 0 or 8000)                     # Output: 0 8000  (the `or` bug)

    # Short-circuit order is visible in side effects
    check("a", False) and check("b", True)            # b is skipped
    check("c", True) or check("d", True)              # d is skipped
    print(calls)                                      # Output: ['a', 'c']

    # any / all: logical operators over many items (also short-circuit)
    scores: list[int] = [72, 85, 91]
    print(all(s >= 70 for s in scores))               # Output: True
    print(any(s >= 90 for s in scores))               # Output: True
    print(all([]), any([]))                           # Output: True False  (empty cases)

    # De Morgan's laws: not (A and B) == (not A) or (not B)
    for a in (True, False):
        for b in (True, False):
            assert (not (a and b)) == ((not a) or (not b))
            assert (not (a or b)) == ((not a) and (not b))
    print("De Morgan holds")                          # Output: De Morgan holds

    # XOR for booleans: use != (or ^ on bools)
    print(True != False, True ^ True)                 # Output: True False

    # Walrus + and: compute once, use twice
    data: list[int] = [1, 2, 3]
    if data and (n := len(data)) > 2:
        print("big list of", n)                       # Output: big list of 3


if __name__ == "__main__":
    main()                                            # run only when executed directly
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
print(not True)                 # False
print(1 and 2)                  # 2
print(0 or "x")                 # 'x'
print([] or "empty")            # 'empty'   empty list is FALSY in Python
print(None or 0 or "")          # ''        last operand when all falsy
name = user_name or "guest"     # default pattern
x = a if a is not None else b   # exact None check
```
```javascript
// JavaScript
console.log(!true);             // false
console.log(1 && 2);            // 2
console.log(0 || "x");          // 'x'
console.log([] || "empty");     // []        empty array is TRUTHY in JS!
console.log(null || 0 || "");   // ''
const name = userName || "guest";   // same pattern
const y = a ?? b;               // nullish coalescing: only null/undefined fall back
// a && b, a || b, !a  and also  &&=  ||=  ??=
```

Key differences: Python uses `and`, `or`, `not`. Empty list `[]` and empty dict `{}` are **falsy** in Python but **truthy** in JS (only `0, "", null, undefined, NaN, false` are falsy there). JS has `??` to treat only `null`/`undefined` as missing; in Python write `a if a is not None else b`.

---

## 🟠 FastAPI Connection
Logical operators are everywhere in endpoint guards: permission checks (`user.is_active and user.is_admin`), optional parameters (`if q and len(q) > 2`), and building filters. In SQLAlchemy and Pydantic you cannot use `and`/`or` on column expressions because Python cannot overload them; use `&`, `|`, `~` with brackets or `sqlalchemy.and_()`, `or_()`, `not_()`.

```python
# FastAPI example (needs: pip install fastapi)
from fastapi import FastAPI, HTTPException, Header   # framework + header reader

app: FastAPI = FastAPI()                             # create app
ADMIN_TOKENS: set[str] = {"secret-admin"}            # fake token store


@app.delete("/orders/{order_id}")                    # DELETE /orders/5
async def delete_order(
    order_id: int,
    x_token: str | None = Header(default=None),      # optional header X-Token
) -> dict[str, int]:
    # `and` guards against None: x_token is checked before it is used
    if not (x_token and x_token in ADMIN_TOKENS):
        raise HTTPException(status_code=403, detail="Admin only")
    return {"deleted": order_id}                     # JSON response
```

```python
# SQLAlchemy style conditions (conceptual, not runnable here):
# Wrong: select(User).where(User.age > 18 and User.active)     # python `and` breaks it
# Right: select(User).where((User.age > 18) & (User.active == True))
#        or: select(User).where(and_(User.age > 18, User.active.is_(True)))
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: `or` default hides valid falsy values
```python
# Wrong: user explicitly sets quantity 0, but it is replaced by 1
quantity = 0
print(quantity or 1)                       # Output: 1  (bug!)

# Right: check for None explicitly
print(quantity if quantity is not None else 1)   # Output: 0
```

❌ Mistake 2: Writing `x == 1 or 2`
```python
x = 5
# Wrong: always truthy, because it means (x == 1) or (2)
print(bool(x == 1 or 2))                   # Output: True  (even though x is 5!)

# Right
print(x == 1 or x == 2)                    # Output: False
print(x in (1, 2))                         # Output: False  (cleaner)
```

❌ Mistake 3: Using `&` and `|` for logic on non-bools
```python
# Wrong: & is bitwise; with ints it gives numbers, and it has higher precedence
print(1 & 2)                               # Output: 0   (not True!)

# Right
print(1 and 2)                             # Output: 2
print(bool(1 and 2))                       # Output: True
```

❌ Mistake 4: Forgetting precedence of `and` over `or`
```python
a, b, c = True, False, False
# Wrong assumption: left to right => (a or b) and c => False
print(a or b and c)                        # Output: True  (means a or (b and c))

# Right: bracket what you mean
print((a or b) and c)                      # Output: False
```

---

## 🧠 Tricky Interview Question

```python
print(1 and 2 or 3)
print(0 and 2 or 3)
print(1 and 0 or 3)
print(not 0 == 0)
print(None or [] or {} or "end")
print([] and 5)
print("a" and "b" and "c")
x = []
y = x or [1]
print(y is x)
```

**Answer:**
```
2
3
3
False
end
[]
c
False
```
`1 and 2` gives `2` (both truthy, last one), then `2 or 3` gives `2`. `0 and 2` gives `0` (first falsy), then `0 or 3` gives `3`. `1 and 0` gives `0`, `0 or 3` gives `3` (this is the old "and-or ternary" trap: if the middle value is falsy, you get the else value). `not 0 == 0` is `not (0 == 0)`, which is `False`. `None or [] or {} or "end"` skips all falsy values and returns `"end"`. `[] and 5` stops at the empty list and returns `[]`. `"a" and "b" and "c"` returns the last: `"c"`. `x or [1]` returns a **new** list because `x` is empty (falsy), so `y is x` is `False`.

---

## ⚫ Interview Questions + Answers

Q1: What does `and` / `or` return in Python?
A1: One of the operands, not necessarily a bool. `a and b` returns `a` if `a` is falsy, otherwise `b`. `a or b` returns `a` if truthy, otherwise `b`. `not` is the only logical operator that always returns a real `bool`. Wrap with `bool(...)` when you need a strict bool (for example in an API response).

Q2: What is short-circuit evaluation and why does it matter?
A2: Python stops evaluating as soon as the result is known: `False and X` never evaluates `X`, and `True or X` never evaluates `X`. It prevents errors (`user and user.name`), saves time (put cheap checks first), and can hide side effects (functions on the right may never run). `any()` and `all()` also short-circuit.

Q3: What values are falsy in Python?
A3: `False`, `None`, numeric zero (`0`, `0.0`, `0j`, `Decimal(0)`), empty containers (`""`, `[]`, `()`, `{}`, `set()`, `range(0)`), and objects whose `__bool__` returns `False` or `__len__` returns `0`. Everything else is truthy. Remember `"0"` and `"False"` (non-empty strings) are truthy.

Q4: Why can't you overload `and` / `or` like `+`?
A4: Because they must short-circuit, which requires special evaluation order. Python cannot call a method with an unevaluated right side. That's why NumPy, pandas and SQLAlchemy use `&`, `|`, `~` instead, and why you need brackets: `(df.age > 18) & (df.city == "Delhi")`.

Q5: How would you write `a if cond else b` using `and`/`or`, and why shouldn't you?
A5: Old style: `cond and a or b`. It fails when `a` is falsy (returns `b` even if `cond` is true). Use the conditional expression `a if cond else b` instead; it is correct for all values.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Combining 2-3 simple conditions
- Guards: `if obj and obj.attr`
- Defaults for non-numeric, non-boolean values: `name or "guest"`
- `any()` / `all()` for many conditions

❌ Avoid when:
- The valid value might be falsy (`0`, `""`, `[]`, `False`): use `is None`
- You need bitwise or elementwise logic on arrays (use `&`, `|`)
- Chains longer than 3 or 4 parts: extract named booleans
- Relying on side effects in the right-hand operand

---

## 📊 Visual Diagram
```
 a and b                        a or b                      not a
 ───────                        ──────                      ─────
 a falsy? ──yes──► return a     a truthy? ──yes──► return a  always bool
    │ no                           │ no
    ▼                              ▼
 return b                       return b

 Truth table (bool inputs)
  A      B     │ A and B │ A or B │ not A
 True   True   │  True   │  True  │ False
 True   False  │  False  │  True  │ False
 False  True   │  False  │  True  │ True
 False  False  │  False  │  False │ True
 Precedence: not > and > or
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Truthy | Value treated as True | जो True माना जाए |
| Falsy | Value treated as False | जो False माना जाए |
| Short-circuit | Stop once result is known | नतीजा पता चलते ही रुकना |
| Operand | The value an operator returns/uses | Operator की value |
| De Morgan's law | not(A and B) = not A or not B | De Morgan का नियम |
| Guard | Condition protecting later code | आगे के code की सुरक्षा शर्त |
| `__bool__` | Magic method defining truthiness | Truthiness तय करने वाला method |

---

## ⚡ 3-Line Summary
English: `and`, `or`, `not` combine conditions, short-circuit, and `and`/`or` return an operand, not necessarily a bool. Falsy values are `False`, `None`, zeros and empty containers. Use `is None` when `0` or `""` is valid, and brackets when mixing `and` with `or`.
Hindi: `and`, `or`, `not` conditions जोड़ते हैं, short-circuit करते हैं, और `and`/`or` operand लौटाते हैं, हमेशा bool नहीं। Falsy: `False`, `None`, zero और खाली containers। जब `0` या `""` valid हो तो `is None` use करो, और `and`/`or` मिलाने पर brackets लगाओ।

---

## ➡️ Next Topic
**030. Bitwise Operators** — `& | ^ ~ << >>`, binary numbers, flags and permissions, and fast tricks.
