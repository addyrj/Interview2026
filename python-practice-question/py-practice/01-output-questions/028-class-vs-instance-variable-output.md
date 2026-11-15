---

# Q028. Class vs instance variable output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```python
class D:
    count = 0                         # class variable
    items = []                        # class variable (mutable)

a, b = D(), D()
a.count = 5
print(a.count, b.count, D.count)      # (a)

D.count = 9
print(a.count, b.count, D.count)      # (b)

a.items.append(1)
print(b.items, D.items, a.items is b.items)   # (c)

a.items = [2]
print(a.items, b.items, D.items)      # (d)
print(a.__dict__, b.__dict__)         # (e)
```

---

## 💡 Quick Concept (2 lines only)
Reading `obj.x` looks in the instance, then the class. Assigning `obj.x = ...` always creates an INSTANCE attribute and shadows the class one; mutating a shared object changes it for all.
हिंदी: Read: पहले instance फिर class; Assign: हमेशा instance में नया attribute बनता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
class D:                                   # Step 1: class with shared attributes
    count = 0                              # Shared immutable int
    items = []                             # Shared mutable list

a, b = D(), D()                            # Two instances
a.count = 5                                # Step 2: creates a.count in a's own __dict__
print(a.count, b.count, D.count)           # (a) 5 0 0

D.count = 9                                # Step 3: change the class attribute
print(a.count, b.count, D.count)           # (b) 5 9 9 (a still shadows with its own 5)

a.items.append(1)                          # Step 4: mutation (no assignment) -> shared list changes
print(b.items, D.items, a.items is b.items)   # (c) [1] [1] True

a.items = [2]                              # Step 5: assignment creates instance attribute
print(a.items, b.items, D.items)           # (d) [2] [1] [1]
print(a.__dict__, b.__dict__)              # (e) {'count': 5, 'items': [2]} {}

# ============================================
# TEST CASES
# ============================================
# Expected output (real run, Python 3.13):
# 5 0 0
# 5 9 9
# [1] [1] True
# [2] [1] [1]
# {'count': 5, 'items': [2]} {}
```

---

## 🔍 Why This Works (3 lines max)
Attribute lookup follows instance `__dict__` then class (then bases). Assignment never writes to the class through an instance. In-place mutation (`append`) does not assign, so it hits the shared object.
हिंदी: `self.n += 1` भी असल में read + assign है — इसलिए instance attribute बन जाता है।

---

## ⚡ Alternative Solution
```python
class E2:                                  # `+=` on an int class attribute
    n = 0                                  # Class variable
    def inc(self):
        self.n += 1                        # Read class n (0), assign instance n = 1
e = E2(); e.inc()                          # Call once
print(e.n, E2.n, e.__dict__)               # 1 0 {'n': 1}

class F2:                                  # Correct way to count instances
    n = 0                                  # Shared counter
    def __init__(self):
        F2.n += 1                          # Assign via the CLASS
F2(); F2()                                 # Two instances
print(F2.n)                                # 2

class G2:                                  # Mutable + `+=` mutates in place, then rebinds
    lst = []                               # Shared list
    def inc(self):
        self.lst += [1]                    # list.__iadd__ mutates shared list, then sets self.lst
x = G2(); x.inc()                          # Call
print(G2.lst, x.__dict__)                  # [1] {'lst': [1]}  (both point to the same list)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: mutable class attribute used as per-instance storage
class Cart:
    items = []                              # Shared by ALL carts
    def add(self, x): self.items.append(x)  # Mutates the shared list

c1, c2 = Cart(), Cart()                     # Two carts
c1.add("apple")                             # Add to c1
print(c2.items)                             # ['apple']  <- leaked into c2!

# ✅ Correct: create the list per instance in __init__
class CartOk:
    def __init__(self):
        self.items = []                     # Own list for each instance
    def add(self, x): self.items.append(x)  # Safe
d1, d2 = CartOk(), CartOk()                 # Two carts
d1.add("apple")                             # Add to d1
print(d2.items)                             # []
```

---

## 🎯 Interview Tip (1 line)
Say: "Instance assignment shadows class attributes, mutation of a shared mutable doesn't — so never use mutable class attributes as per-instance state."

---

## 🔗 Related Questions
→ Q029 (class attribute mutation via instance) | Q001 (mutable default argument) | Q009 (+= vs + on lists)
