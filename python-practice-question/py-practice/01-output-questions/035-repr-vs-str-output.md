---

# Q035. __repr__ vs __str__ output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐ Easy

---

## ❓ Question
What does each line print?

```python
class Point:
    def __init__(self, x, y): self.x, self.y = x, y
    def __repr__(self): return f"Point(x={self.x}, y={self.y})"
    def __str__(self):  return f"({self.x}, {self.y})"

p = Point(1, 2)
print(p)
print([p])
print(f"{p} {p!r}")
```

---

## 💡 Quick Concept (2 lines only)
`__str__` is the friendly text for users (`print`, `str`, f-string); `__repr__` is the unambiguous developer form used inside containers and the REPL.
हिंदी: `print` और f-string `__str__` लेते हैं, लेकिन list/dict के अंदर हमेशा `__repr__` दिखता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
class Point:
    def __init__(self, x: int, y: int) -> None:
        self.x, self.y = x, y                   # store coordinates
    def __repr__(self) -> str:
        return f"Point(x={self.x}, y={self.y})" # developer-oriented
    def __str__(self) -> str:
        return f"({self.x}, {self.y})"          # user-oriented

p = Point(1, 2)                                 # build an object

# ============================================
# TEST CASES
# ============================================
print(p)                 # Expected: (1, 2)
print(str(p))            # Expected: (1, 2)
print(repr(p))           # Expected: Point(x=1, y=2)
print([p])               # Expected: [Point(x=1, y=2)]   (containers use repr)
print(f"{p} {p!r}")      # Expected: (1, 2) Point(x=1, y=2)
print("%s %r" % (p, p))  # Expected: (1, 2) Point(x=1, y=2)
print({"k": p})          # Expected: {'k': Point(x=1, y=2)}

class OnlyRepr:
    def __repr__(self) -> str:
        return "OnlyRepr()"                     # str() falls back to this
print(OnlyRepr(), [OnlyRepr()])  # Expected: OnlyRepr() [OnlyRepr()]

class OnlyStr:
    def __str__(self) -> str:
        return "pretty"                         # repr() does NOT fall back to this
o = OnlyStr()
print(o)                 # Expected: pretty
print([o])               # Expected: [<__main__.OnlyStr object at 0x...>]  (address varies)
```

---

## 🔍 Why This Works (3 lines max)
`str()` calls `__str__`, which defaults to `__repr__` if missing; the reverse is not true. `list.__repr__` calls `repr()` on each element.
हिंदी: `__str__` न हो तो `__repr__` चलता है, लेकिन `__repr__` न हो तो default `<object at 0x..>` मिलता है।

---

## ⚡ Alternative Solution
```python
# dataclass generates a good __repr__ automatically
from dataclasses import dataclass

@dataclass
class P2:
    x: int                    # field
    y: int                    # field

print(P2(1, 2))               # Expected: P2(x=1, y=2)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: defining only __str__ and being surprised that logs/lists show <object at 0x...>
# ✅ Correct: always define __repr__ first (ideally eval-like); add __str__ only if needed
```

---

## 🎯 Interview Tip (1 line)
Say: "`__repr__` is for developers and should be unambiguous; `__str__` is for end users — if you write only one, write `__repr__`."

---

## 🔗 Related Questions
→ Q036 (property setter) | Q306 (dunder methods you must know) | Q246 (dataclasses)
