---

# Q310. Python vs JavaScript (for a JS developer)
# Category: INTERVIEW CLASSICS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
You know JavaScript well. List the Python behaviours that differ most from JS (equality, truthiness, scoping, `this`/`self`, async model, type coercion) and demonstrate each with code.

---

## 💡 Quick Concept (2 lines only)
Python is strongly typed (no silent `1 + "1"`), uses indentation for blocks, has no `undefined`/`null` split (just `None`), and its `async` needs an explicit event loop (`asyncio.run`). Empty containers are falsy, `==` compares values, `is` compares identity.
हिंदी: Python में type coercion नहीं होता, `None` ही null है, खाली list/dict falsy हैं, और async के लिए `asyncio.run` चाहिए।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import asyncio                                   # Python's event-loop library

# Step 1: no implicit type coercion (JS: 1 + "1" === "11")
try:                                             # JS would silently give "11"
    print(1 + "1")                               # Python raises
except TypeError as e:                           # catch the error
    print("TypeError:", e)                       # show message

# Step 2: == compares values, is compares identity (JS: === ~ ==, no `is`)
print([1, 2] == [1, 2])                          # True: same values (JS gives false for arrays)
print([1, 2] is [1, 2])                          # False: different objects

# Step 3: truthiness differs ([] and {} are falsy in Python, truthy in JS)
print(bool([]), bool({}), bool(0), bool(""), bool(None))   # False x5
print(bool("0"), bool([0]))                      # True True (non-empty)

# Step 4: single None instead of null/undefined
d = {"a": 1}                                     # sample dict
print(d.get("missing"))                          # None (no undefined); d["missing"] raises KeyError

# Step 5: integer division and exponent operators
print(7 // 2, 2 ** 10, -7 // 2)                  # 3 1024 -4 (floors, not truncates)

# Step 6: `self` is explicit, no implicit `this`
class Counter:                                   # simple class
    def __init__(self) -> None:                  # constructor (JS: constructor())
        self.n = 0                               # instance attribute (JS: this.n)
    def inc(self) -> int:                        # self passed explicitly
        self.n += 1                              # mutate state
        return self.n                            # return new value
c = Counter()                                    # no `new` keyword
print(c.inc(), c.inc())                          # 1 2
m = c.inc                                        # bound method keeps self (JS loses `this`)
print(m())                                       # 3

# Step 7: block scope does NOT exist (only function scope)
for i in range(3):                               # loop variable
    pass                                         # nothing
print(i)                                         # 2 -> `i` leaks out (JS `let` would not)

# Step 8: async needs an explicit loop; coroutines are lazy until awaited
async def fetch(x: int) -> int:                  # like `async function`
    await asyncio.sleep(0.01)                    # simulated I/O
    return x * 2                                 # result
async def main() -> list[int]:                   # top-level coroutine
    return await asyncio.gather(fetch(1), fetch(2))  # like Promise.all
print(asyncio.run(main()))                       # [2, 4]; start loop explicitly

# ============================================
# TEST CASES
# ============================================
# Real output from Python 3.13:
# TypeError: unsupported operand type(s) for +: 'int' and 'str'
# True
# False
# False False False False False
# True True
# None
# 3 1024 -4
# 1 2
# 3
# 2
# [2, 4]
```

---

## 🔍 Why This Works (3 lines max)
Python favours explicit over implicit: no coercion, explicit `self`, explicit event loop. Function-level scope plus `nonlocal`/`global` replaces `let`/`const` block scope; there is no `const` at all (use UPPER_CASE by convention).
हिंदी: Python explicit को पसंद करता है — `self` खुद लिखो, loop खुद चलाओ, और block scope नहीं होता।

---

## ⚡ Alternative Solution
```python
# Quick JS -> Python cheat-sheet in runnable form
nums = [1, 2, 3, 4]                              # JS: const nums = [1,2,3,4]
print([n * 2 for n in nums if n % 2 == 0])       # [4, 8]  JS: nums.filter(..).map(..)
user = {"name": "Ada", "age": 30}                # JS object -> dict
name, age = user["name"], user["age"]            # JS: const {name, age} = user
print(f"{name} is {age}")                        # JS template literal -> f-string
merged = {**user, "age": 31}                     # JS: {...user, age: 31}
print(merged)                                    # {'name': 'Ada', 'age': 31}
first, *rest = nums                              # JS: const [first, ...rest] = nums
print(first, rest)                               # 1 [2, 3, 4]
print(user.get("email", "n/a"))                  # JS: user.email ?? "n/a"
print(len(nums), "x" * 3, "a-b".split("-"))      # JS: .length, repeat, split
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: JS habits that fail in Python
# if (x == null)  -> use `x is None`, never `x == None`
# arr.length      -> len(arr)
# obj.key on dict -> obj["key"] (dict is not an object)
# true / false    -> True / False (capitalised)
# NOT RUN (shown as comments above)

# ✅ Correct: the Python spellings (runnable)
x = None                                         # null equivalent
print(x is None)                                 # True: identity check for None
arr = [1, 2, 3]                                  # list
print(len(arr), True and not False)              # 3 True
```

---

## 🎯 Interview Tip (1 line)
Point out Python is strongly but dynamically typed, single-threaded for CPU work (GIL) so you use asyncio for I/O and multiprocessing for CPU — a concrete contrast with Node's event loop.

---

## 🔗 Related Questions
→ 309, 298, 299, 294
