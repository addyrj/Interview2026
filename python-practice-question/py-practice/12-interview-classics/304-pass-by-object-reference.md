---

# Q304. Pass by Object Reference
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Is Python pass-by-value or pass-by-reference? Predict the output.

```python
def f(lst, n):
    lst.append(1)
    n += 1
    lst = [99]

a, k = [], 0
f(a, k)
print(a, k)
```

---

## 💡 Quick Concept (2 lines only)
Python passes object references by value ("pass by assignment"): the parameter name is bound to the same object. Mutating it is visible; rebinding the name is not.
हिंदी: Function को object का reference मिलता है — mutate करो तो caller को दिखता है, rebind करो तो नहीं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
def f(lst: list[int], n: int) -> None:
    lst.append(1)  # Step 1: mutates the SAME list the caller passed
    n += 1  # Step 2: int is immutable -> rebinds local n only
    lst = [99]  # Step 3: rebinds local name; caller's list untouched


a: list[int] = []  # caller's list
k = 0  # caller's int
f(a, k)  # call

# ============================================
# TEST CASES
# ============================================
print(a, k)  # Expected: [1] 0

def show_ids(x: list[int]) -> bool:
    return id(x) == id(a)  # same object inside the function?

print(show_ids(a))  # Expected: True (no copy made)

def reassign(x: list[int]) -> list[int]:
    x = x + [5]  # '+' builds a NEW list -> local rebinding
    return x  # return it so caller can use it

print(reassign(a), a)  # Expected: [1, 5] [1]

def extend(x: list[int]) -> None:
    x += [5]  # '+=' mutates in place
    
extend(a)  # call
print(a)  # Expected: [1, 5]
```

---

## 🔍 Why This Works (3 lines max)
Arguments are names bound to the caller's objects. `append`/`+=` change the shared object; `=`/`+` rebind the local name to a new object. That's why `x += [5]` and `x = x + [5]` behave differently in a function.
हिंदी: `=` सिर्फ local नाम बदलता है, `.append` / `+=` असली object बदलता है।

---

## ⚡ Alternative Solution
```python
def safe_append(items: list[int], v: int) -> list[int]:
    new = [*items, v]  # copy, then add -> no side effect on caller
    return new  # caller decides what to do

orig = [1, 2]  # data
print(safe_append(orig, 3), orig)  # Expected: [1, 2, 3] [1, 2]

def change_dict(d: dict[str, int]) -> None:
    d["x"] = 1  # dicts mutate like lists

cfg: dict[str, int] = {}  # empty dict
change_dict(cfg)  # call
print(cfg)  # Expected: {'x': 1}
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: expecting a function to "clear" a list by reassigning it
def clear_wrong(lst):
    lst = []  # only rebinds local name

data = [1, 2]
clear_wrong(data)
print(data)  # [1, 2] - unchanged

# ✅ Correct: mutate in place
def clear_ok(lst):
    lst.clear()  # or lst[:] = []

clear_ok(data)
print(data)  # Expected: []
```

---

## 🎯 Interview Tip (1 line)
Say: "Neither pure by-value nor by-reference: it's pass by object reference - mutation is shared, rebinding is local."

---

## 🔗 Related Questions
→ Q001 (mutable default argument) | Q009 (+= vs + on lists) | Q292 (mutable vs immutable) | Q293 (shallow vs deep copy)
