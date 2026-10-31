---

# 031. Assignment Operators
# हिंदी में: Assignment Operators — value देने वाले operators

---

## 🔵 Simple Definition (English)
Assignment operators bind a name to a value. `=` is basic assignment. Augmented operators (`+=`, `-=`, `*=`, `/=`, `//=`, `%=`, `**=`, `&=`, `|=`, `^=`, `<<=`, `>>=`) update a variable using its own value. `:=` (walrus, Python 3.8+) assigns **inside** an expression. Python also supports chained (`a = b = 0`) and unpacking (`x, y = 1, 2`) assignment.

## 🔵 सरल परिभाषा (Hindi)
Assignment operators किसी नाम को value से जोड़ते हैं। `=` basic assignment है। Augmented operators (`+=`, `-=`, `*=` आदि) variable को उसकी अपनी value से update करते हैं। `:=` (walrus, Python 3.8+) expression के **अंदर** assign करता है। Chained (`a = b = 0`) और unpacking (`x, y = 1, 2`) भी चलती है।

---

## 🔴 Problem it Solves
Updating a value from its old value (`count = count + 1`) is extremely common, and repeating the name is noisy and error-prone. Augmented assignment shortens it and, for mutable objects like lists, can update **in place** without creating a new object. Unpacking removes temporary variables (swap in one line), and walrus avoids computing a value twice.

## 🔴 यह क्यों बना? (Hindi)
पुरानी value से नई value बनाना (`count = count + 1`) बहुत आम है, और नाम दोहराना शोर और गलती का कारण है। Augmented assignment इसे छोटा करता है, और lists जैसे mutable objects को **in place** update कर सकता है। Unpacking से temporary variables हटते हैं (एक line में swap), और walrus से value दो बार compute नहीं करनी पड़ती।

---

## 🟢 How it Works — Step by Step

```
Step 1 → x = 5
           Python creates the int object 5, then BINDS the name x to it.
           (Names are labels on objects, not boxes holding values.)
Step 2 → x += 3
           Calls x.__iadd__(3) if it exists (in-place), else x = x.__add__(3)
           ints/str/tuple are immutable → a NEW object is created, x re-bound
           list is mutable → list.__iadd__ extends the SAME object in place
Step 3 → a, b = b, a
           Right side is evaluated fully first → tuple (b, a), then unpacked
Step 4 → a = b = []
           Both names point to the SAME list object
Step 5 → if (n := len(items)) > 3:
           Assigns n and returns its value in one expression
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → x = 5 : object 5 बनता है और नाम x उससे bind होता है (नाम label है, डिब्बा नहीं)
Step 2 → x += 3 : __iadd__ हो तो in-place, वरना x = x + 3
         int/str/tuple immutable → नया object; list mutable → वही object बदलता है
Step 3 → a, b = b, a : पहले right side का tuple बनता है, फिर unpack होता है
Step 4 → a = b = [] : दोनों नाम एक ही list की ओर इशारा करते हैं
Step 5 → (n := len(items)) : assign भी और value भी वापस
```

---

## 🟡 Real World Example
Swiggy order counters: `orders_today += 1`, wallet: `balance -= amount`, price: `price *= 1.18`. Config merge: `settings |= overrides` (dict union, 3.9+). Reading a file in chunks: `while chunk := f.read(8192):`. Fibonacci / swap: `a, b = b, a + b`. In a FastAPI service you often write `total += item.price * item.qty` while accumulating a bill.

## 🟡 Real Example Hindi mein
Swiggy के counters: `orders_today += 1`, wallet: `balance -= amount`, price: `price *= 1.18`। Config merge: `settings |= overrides` (dict union, 3.9+)। File को chunks में पढ़ना: `while chunk := f.read(8192):`। Fibonacci / swap: `a, b = b, a + b`। FastAPI में bill जोड़ते समय `total += item.price * item.qty` आम है।

---

## 💻 Code Example — Basic
```python
# Assignment operators basics

x: int = 10                          # plain assignment

x += 5                               # x = x + 5
print(x)                             # Output: 15
x -= 3                               # x = x - 3
print(x)                             # Output: 12
x *= 2                               # x = x * 2
print(x)                             # Output: 24
x /= 4                               # x = x / 4  (becomes float)
print(x)                             # Output: 6.0
x //= 4                              # floor division
print(x)                             # Output: 1.0
x **= 3                              # power
print(x)                             # Output: 1.0
y: int = 17
y %= 5                               # remainder
print(y)                             # Output: 2

# Bitwise augmented assignment
flags: int = 0b0101
flags |= 0b0010                      # set a bit
print(bin(flags))                    # Output: 0b111
flags &= 0b0110                      # keep only some bits
print(bin(flags))                    # Output: 0b110
flags ^= 0b0100                      # toggle a bit
print(bin(flags))                    # Output: 0b10
flags <<= 2                          # shift left in place
print(flags)                         # Output: 8

# Strings and lists also support += and *=
text: str = "Hi"
text += " Priya"                     # builds a new string
print(text)                          # Output: Hi Priya
items: list[int] = [1, 2]
items += [3, 4]                      # extends the same list
items *= 2                           # repeats contents
print(items)                         # Output: [1, 2, 3, 4, 1, 2, 3, 4]

# Multiple assignment
a, b, c = 1, 2, 3                    # unpack three values
print(a, b, c)                       # Output: 1 2 3
a, b = b, a                          # swap without temp variable
print(a, b)                          # Output: 2 1

# Chained assignment (same value, immutable types are fine)
p = q = 0
print(p, q)                          # Output: 0 0

# Extended unpacking with *
first, *middle, last = [1, 2, 3, 4, 5]
print(first, middle, last)           # Output: 1 [2, 3, 4] 5

# Walrus operator: assign inside an expression
names: list[str] = ["a", "b", "c", "d"]
if (count := len(names)) > 3:        # compute once, use twice
    print(f"too many: {count}")      # Output: too many: 4
```

## 💻 Code Example — Advanced
```python
# Advanced: in-place vs new object, aliasing, nested unpacking, walrus patterns
import re                                  # for the regex walrus example
from collections.abc import Iterator       # type for generator


def chunks(data: bytes, size: int) -> Iterator[bytes]:
    """Yield fixed-size pieces using the walrus operator in a loop."""
    view = memoryview(data)                # cheap slicing
    pos: int = 0                           # current position
    while chunk := view[pos : pos + size]: # empty slice is falsy -> loop ends
        yield bytes(chunk)                 # give the piece
        pos += size                        # move forward


def fib(n: int) -> list[int]:
    """Fibonacci using tuple assignment (simultaneous update)."""
    a, b = 0, 1                            # first two numbers
    out: list[int] = []                    # results
    for _ in range(n):
        out.append(a)                      # store current
        a, b = b, a + b                    # right side evaluated first
    return out


def parse_order(line: str) -> tuple[str, int] | None:
    """Walrus with regex: match once, reuse the match object."""
    if m := re.fullmatch(r"(\w+)x(\d+)", line):    # assign and test together
        return m.group(1), int(m.group(2))          # use m directly
    return None


def main() -> None:
    # 1. In-place vs rebinding: same id means same object
    nums: list[int] = [1, 2]
    before: int = id(nums)
    nums += [3]                                # in-place (list.__iadd__)
    print(id(nums) == before)                  # Output: True
    nums = nums + [4]                          # creates a NEW list
    print(id(nums) == before)                  # Output: False

    s: str = "ab"
    sid: int = id(s)
    s += "c"                                   # strings are immutable -> new object
    print(id(s) == sid)                        # Output: False

    # 2. Aliasing: a = b = [] shares one list
    a = b = []                                 # same list object
    a.append(1)
    print(b)                                   # Output: [1]
    c, d = [], []                              # two separate lists
    c.append(1)
    print(d)                                   # Output: []

    # 3. Tuple += list works on tuple? no: list += tuple works, tuple stays immutable
    t: tuple[int, ...] = (1, 2)
    t += (3,)                                  # creates a new tuple, rebinds t
    print(t)                                   # Output: (1, 2, 3)

    # 4. Nested unpacking
    (name, (lat, lon)), score = ("Delhi", (28.6, 77.2)), 9
    print(name, lat, lon, score)               # Output: Delhi 28.6 77.2 9

    # 5. Unpacking dict items and ignoring values
    for key, _ in {"x": 1, "y": 2}.items():    # _ means "ignored"
        print(key, end=" ")                    # Output: x y
    print()

    # 6. Dict update operator (3.9+)
    settings: dict[str, int] = {"timeout": 10, "retries": 3}
    settings |= {"retries": 5, "debug": 1}     # in-place merge
    print(settings)                            # Output: {'timeout': 10, 'retries': 5, 'debug': 1}

    # 7. Walrus helpers
    print(list(chunks(b"abcdefg", 3)))         # Output: [b'abc', b'def', b'g']
    print(fib(8))                              # Output: [0, 1, 1, 2, 3, 5, 8, 13]
    print(parse_order("pizzax2"), parse_order("bad input"))
    # Output: ('pizza', 2) None

    # 8. Annotated assignment without value (just declares the type)
    limit: int                                 # no value yet
    limit = 100                                # assign later
    print(limit)                               # Output: 100

    # 9. Augmented assignment evaluates the target only once
    data: list[int] = [10, 20, 30]
    i: int = 0
    data[i] += 5                               # index expression evaluated once
    print(data)                                # Output: [15, 20, 30]


if __name__ == "__main__":
    main()                                     # run only when executed directly
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
x = 5
x += 2                       # 7
x **= 2                      # 49   power-assign
x //= 5                      # 9    floor-divide-assign
a, b = 1, 2
a, b = b, a                  # swap (no temp, no destructuring needed)
first, *rest = [1, 2, 3]     # rest = [2, 3]
p = q = []                   # both names, SAME list
if (n := 10) > 5:            # walrus
    print(n)
# no x++ / x-- in Python
```
```javascript
// JavaScript
let x = 5;
x += 2;                      // 7
x **= 2;                     // 49
x = Math.floor(x / 5);       // no //= operator
let a = 1, b = 2;
[a, b] = [b, a];             // swap with destructuring
const [first, ...rest] = [1, 2, 3];
let p, q;
p = q = [];                  // chained: same array
x++; x--;                    // increment / decrement exist
let m; m ||= 5; m &&= 6; m ??= 7;   // logical assignment operators
```

Key differences: Python has no `++`/`--`, but has `//=`, `@=`, and `:=`. In Python, assignment is a **statement** (cannot be used inside an expression, except walrus); in JS, `=` is an expression (`if (x = 5)` is legal and dangerous). Python's `a += b` on a list mutates in place; JS `+=` on arrays converts them to strings. Python swaps with plain tuple assignment.

---

## 🟠 FastAPI Connection
In FastAPI code, augmented assignment accumulates totals and counters; unpacking returns multiple values from helpers (`items, total = await load_page(...)`); and the dict `|=` merges default settings with overrides. Be careful with **module-level mutable state** in an app with several workers: `counter += 1` on a global is not shared between processes and is not thread-safe across threads; use Redis or a database for real counters.

```python
# FastAPI example (needs: pip install fastapi pydantic)
from fastapi import FastAPI                        # framework
from pydantic import BaseModel                     # request model

app: FastAPI = FastAPI()                           # create app


class Item(BaseModel):
    price: float                                   # price per item
    qty: int = 1                                   # quantity


@app.post("/bill")                                 # POST /bill
async def bill(items: list[Item]) -> dict[str, float]:
    total: float = 0.0                             # running total
    for item in items:
        total += item.price * item.qty             # augmented assignment
    gst: float = round(total * 0.18, 2)            # tax
    total += gst                                   # add tax
    return {"gst": gst, "total": round(total, 2)}  # JSON response
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Chained assignment with mutable objects
```python
# Wrong: both names share ONE list
a = b = []
a.append(1)
print(b)                    # Output: [1]  (surprise!)

# Right: separate objects
a, b = [], []
a.append(1)
print(b)                    # Output: []
```

❌ Mistake 2: Using `+=` on a name that is not defined locally
```python
count = 0

def increment() -> None:
    # Wrong: UnboundLocalError, Python sees an assignment so `count` is local
    # count += 1
    global count            # Right (or better: pass and return values)
    count += 1

increment()
print(count)                # Output: 1
```

❌ Mistake 3: Expecting `x++`
```python
x = 5
# Wrong: x++   (SyntaxError)  and ++x is just +(+x) which does nothing
print(++x)                  # Output: 5

# Right
x += 1
print(x)                    # Output: 6
```

❌ Mistake 4: Surprise with `+=` on a list inside a tuple
```python
t = ([1, 2], 3)
# Wrong assumption: error means nothing changed
try:
    t[0] += [99]            # list is extended, THEN the tuple assignment fails
except TypeError as exc:
    print("TypeError:", exc)
print(t)                    # Output: ([1, 2, 99], 3)  (list changed anyway!)

# Right: mutate the list directly
t[0].append(100)
print(t)                    # Output: ([1, 2, 99, 100], 3)
```

---

## 🧠 Tricky Interview Question

```python
a = [1, 2]
b = a
b += [3]
print(a)

x = (1, 2)
y = x
y += (3,)
print(x)

i = 0
lst = [10, 20, 30]
i, lst[i] = 2, 99
print(i, lst)
```

**Answer:**
```
[1, 2, 3]
(1, 2)
2 [10, 20, 99]
```
`b += [3]` calls `list.__iadd__`, which extends the **same** list, so `a` sees the change. Tuples are immutable: `y += (3,)` builds a new tuple and rebinds `y`; `x` keeps `(1, 2)`. In the last case, targets are assigned **left to right** *after* the right side is evaluated: first `i = 2`, then `lst[i]` uses the **new** `i` (2), so `lst[2] = 99`, not `lst[0]`. Remember the rule: "evaluate the right side, then assign targets left to right".

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `a = a + b` and `a += b`?
A1: For immutable types (int, str, tuple) they are equivalent: a new object is created. For mutable types, `+=` calls `__iadd__` and modifies the object **in place**, so other references to it see the change, while `a = a + b` creates a new object and rebinds only `a`. With lists this is why `a += [x]` can differ from `a = a + [x]`.

Q2: What is the walrus operator and when should you use it?
A2: `:=` assigns a value to a name and returns that value in the same expression (PEP 572, Python 3.8). Good uses: `while chunk := f.read(n)`, `if (m := regex.match(s))`, and comprehension filters that need a computed value twice. Avoid it when it makes code harder to read, and it cannot be used for simple top-level statements without brackets (`x := 5` alone is a SyntaxError).

Q3: How does tuple unpacking `a, b = b, a` work without a temp variable?
A3: The right side `(b, a)` is evaluated first into a tuple holding the old values (CPython optimizes this to a stack rotation), then the names are assigned from it left to right. So no value is lost. It also works for lists, strings, and any iterable, with `*` capturing the rest.

Q4: What happens with `a = b = []`?
A4: Python evaluates `[]` once and binds both names to that **single** object. Mutating through one name is visible through the other. It is fine for immutable values (`a = b = 0`), but dangerous for lists, dicts and sets. Same trap: `[[0]*3]*3` repeats one inner list three times.

Q5: Why does `count += 1` inside a function raise `UnboundLocalError` for a global variable?
A5: Any assignment (including augmented) inside a function makes that name **local** for the whole function, so reading it before assigning fails. Fix: declare `global count` (or `nonlocal` in nested functions), or better, avoid global state: pass values in, return values out, or use a class.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Counters, totals, accumulators: `total += x`
- Swaps and multiple returns: `a, b = b, a`
- Walrus in `while` loops and regex matching
- `|=` to merge dicts and sets in place

❌ Avoid when:
- Chaining assignment with mutable objects (`a = b = []`)
- Building long strings with `+=` in a big loop (use `"".join(...)`)
- Using walrus where a normal line is clearer
- Updating global counters in multi-process servers

---

## 📊 Visual Diagram
```
 Names are labels pointing to objects

 a = [1, 2]        a ──► [1, 2]
 b = a             a ──► [1, 2] ◄── b          (one object, two names)
 b += [3]          a ──► [1, 2, 3] ◄── b       (SAME object changed in place)
 b = b + [4]       a ──► [1, 2, 3]
                   b ──► [1, 2, 3, 4]          (NEW object, b re-bound)

 x = 5 ; x += 1    5 (unchanged)   x ──► 6     (int is immutable)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Binding | Attaching a name to an object | नाम को object से जोड़ना |
| Augmented assignment | Operator like `+=` that updates in one step | `+=` जैसा update operator |
| In-place | Changing the same object | उसी object में बदलाव |
| Unpacking | Splitting an iterable into names | Iterable को नामों में बाँटना |
| Walrus `:=` | Assignment expression | Expression के अंदर assignment |
| Aliasing | Two names for one object | एक object के दो नाम |
| Mutable / Immutable | Can / cannot change after creation | बदला जा सकता है / नहीं |

---

## ⚡ 3-Line Summary
English: `=` binds a name to an object; augmented operators like `+=` update in place for mutable types and rebind for immutable ones. Use tuple unpacking for swaps, `*` for the rest, and `:=` to assign inside an expression. Watch out for `a = b = []` aliasing and `UnboundLocalError` with globals.
Hindi: `=` नाम को object से bind करता है; `+=` जैसे operators mutable types में in-place बदलते हैं और immutable में नया object बनाकर rebind करते हैं। Swap के लिए tuple unpacking, बाकी के लिए `*`, और expression के अंदर assign के लिए `:=`। `a = b = []` aliasing और globals के `UnboundLocalError` से सावधान रहो।

---

## ➡️ Next Topic
**037. match/case (Python 3.10+)** — structural pattern matching, Python's powerful alternative to long `if/elif` chains.
