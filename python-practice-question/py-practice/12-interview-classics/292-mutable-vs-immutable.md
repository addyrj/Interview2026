---

# Q292. Mutable vs Immutable
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What is the difference between mutable and immutable types in Python? Show how it affects `id()` and function arguments.

---

## 💡 Quick Concept (2 lines only)
Immutable objects (int, str, tuple, frozenset, bytes) never change - "modifying" creates a new object. Mutable ones (list, dict, set) change in place.
हिंदी: Immutable बदलने पर नया object बनता है, mutable उसी object में बदलाव होता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
s = "hi"  # Step 1: immutable str
old_id = id(s)  # remember identity
s += "!"  # Step 2: creates a NEW string
same_str = id(s) == old_id  # compare identities

nums = [1, 2]  # Step 3: mutable list
old_list_id = id(nums)  # remember identity
nums += [3]  # Step 4: in-place extend
same_list = id(nums) == old_list_id  # compare identities


def add_item(items: list[int], n: int) -> None:  # Step 5: function that mutates its argument
    items.append(n)  # changes the caller's list


def add_one(x: int) -> int:  # Step 6: function on immutable
    x += 1  # rebinds local name only
    return x  # return new value


# ============================================
# TEST CASES
# ============================================
print(s, same_str)  # Expected: hi! False
print(nums, same_list)  # Expected: [1, 2, 3] True
data = [1]  # list to pass
add_item(data, 2)  # mutate in function
print(data)  # Expected: [1, 2]
n = 5  # int to pass
add_one(n)  # result discarded
print(n)  # Expected: 5 (unchanged)
d = {"a": 1}  # dict is mutable
d["b"] = 2  # in-place change
print(d)  # Expected: {'a': 1, 'b': 2}
```

---

## 🔍 Why This Works (3 lines max)
`str +=` builds a new object and rebinds the name, while `list +=` calls `__iadd__` and mutates in place. So a function can change a passed list but never a passed int or str.
हिंदी: Mutable object function में बदलता है तो caller को भी दिखता है, immutable का नहीं।

---

## ⚡ Alternative Solution
```python
fs = frozenset({1, 2})  # immutable set
print(hash(fs) == hash(frozenset({2, 1})))  # Expected: True

a = (1, [2, 3])  # tuple holds a mutable list
a[1].append(4)  # allowed
print(a)  # Expected: (1, [2, 3, 4])
try:
    a[1] += [5]  # augmented assign on a tuple item
except TypeError as e:  # the list grows, then the item assignment fails
    print(e, a)  # Expected: 'tuple' object does not support item assignment (1, [2, 3, 4, 5])
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: assuming b is an independent copy
a = [1, 2]  # list
b = a  # same object, not a copy
b.append(3)  # mutates both names
print(a)  # [1, 2, 3]

# ✅ Correct: copy explicitly
c = a.copy()  # new list
c.append(4)  # only c changes
print(a, c)  # Expected: [1, 2, 3] [1, 2, 3, 4]
```

---

## 🎯 Interview Tip (1 line)
Say: "Mutability decides hashability and aliasing behaviour: only immutable (hashable) objects are safe dict keys and safe default arguments."

---

## 🔗 Related Questions
→ Q001 (mutable default argument) | Q291 (list vs tuple) | Q304 (pass by object reference) | Q175 (mutability and hashability)
