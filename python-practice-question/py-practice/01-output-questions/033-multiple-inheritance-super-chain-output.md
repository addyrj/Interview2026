---

# Q033. Multiple inheritance super() chain output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
What does this print? Is `C` ever skipped?

```python
class A:
    def __init__(self):
        print("A start"); super().__init__(); print("A end")
class B(A):
    def __init__(self):
        print("B start"); super().__init__(); print("B end")
class C(A):
    def __init__(self):
        print("C start"); super().__init__(); print("C end")
class D(B, C):
    def __init__(self):
        print("D start"); super().__init__(); print("D end")

D()
```

---

## 💡 Quick Concept (2 lines only)
`super()` in `B` does not mean "A" — it means the next class after `B` in the MRO of the instance, which is `C`. Every class runs once.
हिंदी: `B` का `super()` A नहीं, instance के MRO की अगली class (यानी C) को call करता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
class A:
    def __init__(self) -> None:
        print("A start")          # reached last (before object)
        super().__init__()        # next is object
        print("A end")
class B(A):
    def __init__(self) -> None:
        print("B start")
        super().__init__()        # next in D's MRO after B is C, not A
        print("B end")
class C(A):
    def __init__(self) -> None:
        print("C start")
        super().__init__()        # next after C is A
        print("C end")
class D(B, C):
    def __init__(self) -> None:
        print("D start")
        super().__init__()        # next after D is B
        print("D end")

# ============================================
# TEST CASES
# ============================================
D()
# Expected:
# D start
# B start
# C start
# A start
# A end
# C end
# B end
# D end
print([k.__name__ for k in D.__mro__])  # Expected: ['D', 'B', 'C', 'A', 'object']
```

---

## 🔍 Why This Works (3 lines max)
The MRO is D, B, C, A, object; each `super()` moves one step right, so the "start" lines go down the MRO and the "end" lines unwind in reverse. A runs exactly once, not twice.
हिंदी: Start lines MRO के order में, end lines उल्टे order में — A सिर्फ़ एक बार चलता है।

---

## ⚡ Alternative Solution
```python
# Same chain, but print the MRO position automatically
class Base:
    def __init__(self) -> None:
        print("Base")                 # tail of the chain
class Left(Base):
    def __init__(self) -> None:
        print("Left"); super().__init__()   # continues via MRO
class Right(Base):
    def __init__(self) -> None:
        print("Right"); super().__init__()  # continues via MRO
class Both(Left, Right):
    pass                              # inherits Left.__init__

Both()  # Expected: Left, Right, Base (one per line)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: hardcode the parent in B -> C is skipped in the chain
class B2(A):
    def __init__(self):
        print("B2 start"); A.__init__(self); print("B2 end")
class D2(B2, C):
    def __init__(self):
        print("D2 start"); super().__init__(); print("D2 end")
D2()
# Real output: D2 start, B2 start, A start, A end, B2 end, D2 end  (C never runs!)
# ✅ Correct: use super().__init__() everywhere
```

---

## 🎯 Interview Tip (1 line)
Say: "`super()` is cooperative: every class calls `super()` once, and the MRO guarantees each runs exactly once."

---

## 🔗 Related Questions
→ Q031 (inheritance and super) | Q032 (diamond MRO) | Q163 (explain MRO) | Q271 (mixin pattern)
