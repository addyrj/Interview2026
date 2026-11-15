---

# Q029. Class attribute mutation via instance output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will this print?

```python
class Counter:
    count: int = 0      # class attribute (immutable int)
    items: list = []    # class attribute (mutable list)

a = Counter()
b = Counter()
a.count += 1
a.items.append("x")
print(a.count, b.count, Counter.count)
print(a.items, b.items, Counter.items)
```

---

## 💡 Quick Concept (2 lines only)
Reading `a.attr` falls back to the class; assigning `a.attr = ...` always creates an instance attribute. In-place mutation (`append`) never assigns, so it changes the shared class object.
हिंदी: Assign करने पर instance का अपना attribute बनता है, लेकिन list को in-place बदलने पर सब instances में बदलाव दिखता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
class Counter:
    count: int = 0            # class attribute (int, immutable)
    items: list = []          # class attribute (list, mutable)

a = Counter()                 # first instance
b = Counter()                 # second instance
# Step 1: a.count += 1  ==  a.count = a.count + 1
#   read finds Counter.count (0), write creates a.count = 1 on the INSTANCE
a.count += 1
# Step 2: append mutates the one shared list, no assignment happens
a.items.append("x")

# ============================================
# TEST CASES
# ============================================
print(a.count, b.count, Counter.count)  # Expected: 1 0 0
print(a.items, b.items, Counter.items)  # Expected: ['x'] ['x'] ['x']
print("count" in a.__dict__, "items" in a.__dict__)  # Expected: True False
Counter.count = 10            # change the class attribute
print(a.count, b.count)       # Expected: 1 10  (a shadows it, b follows class)
a.items = ["own"]             # plain assignment -> new instance attribute
print(a.items, b.items)       # Expected: ['own'] ['x']
```

---

## 🔍 Why This Works (3 lines max)
Attribute lookup order is instance `__dict__` first, then the class. `+=` on an int is read + rebind, so it lands on the instance; `list.append` is a method call on the shared object, so no rebind occurs.
हिंदी: `+=` int पर नया instance attribute बनाता है, `append` class की shared list को ही बदलता है।

---

## ⚡ Alternative Solution
```python
# Give every instance its own list inside __init__
class Fixed:
    def __init__(self) -> None:
        self.items: list[str] = []   # per-instance list, not shared

x, y = Fixed(), Fixed()              # two independent objects
x.items.append("x")                  # only x changes
print(x.items, y.items)              # Expected: ['x'] []
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: expecting a.count += 1 to change Counter.count (so b.count == 1)
#    and expecting a.items.append to stay private to a
# ✅ Correct: use Counter.count += 1 to change the class value,
#    and create mutable state in __init__ (self.items = [])
```

---

## 🎯 Interview Tip (1 line)
Say: "Lookup is instance then class; assignment always targets the instance, but mutating a shared mutable class attribute leaks across instances."

---

## 🔗 Related Questions
→ Q028 (class vs instance variable) | Q001 (mutable default argument) | Q138 (shared class variable bug)
