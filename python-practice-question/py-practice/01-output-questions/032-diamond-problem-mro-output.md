---

# Q032. Diamond problem MRO output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Which `hello()` runs, and what is `D`'s MRO?

```python
class A:
    def hello(self): return "A"
class B(A):
    def hello(self): return "B"
class C(A):
    def hello(self): return "C"
class D(B, C):
    pass

print(D().hello())
```

---

## 💡 Quick Concept (2 lines only)
Python uses C3 linearization: children before parents, and the order of bases is preserved. `D(B, C)` gives `D, B, C, A, object`.
हिंदी: MRO में child पहले, parent बाद में, और base classes का लिखा हुआ order बना रहता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
class A:
    def hello(self) -> str:
        return "A"                  # root of the diamond
class B(A):
    def hello(self) -> str:
        return "B"                  # left branch
class C(A):
    def hello(self) -> str:
        return "C"                  # right branch
class D(B, C):                      # B listed first -> B wins
    pass

# ============================================
# TEST CASES
# ============================================
print(D().hello())                          # Expected: B
print([k.__name__ for k in D.__mro__])      # Expected: ['D', 'B', 'C', 'A', 'object']
print([k.__name__ for k in D.mro()])        # Expected: ['D', 'B', 'C', 'A', 'object']

class E(C, B):                              # swap the bases
    pass
print(E().hello(), [k.__name__ for k in E.__mro__])
# Expected: C ['E', 'C', 'B', 'A', 'object']

try:
    class Bad(A, B):                        # A before its own subclass B
        pass
except TypeError as e:
    print("TypeError:", e)
# Expected: TypeError: Cannot create a consistent method resolution order (MRO) for bases A, B
```

---

## 🔍 Why This Works (3 lines max)
C3 merges the parents' MROs so A (shared base) comes only after both B and C. Lookup walks that list and stops at the first class defining `hello`. An impossible ordering (`A, B`) raises `TypeError`.
हिंदी: Shared base A सबसे आख़िर में आता है, इसलिए B (पहला base) जीतता है।

---

## ⚡ Alternative Solution
```python
# Inspect where a method really comes from
for klass in D.__mro__:                      # walk the MRO in order
    if "hello" in klass.__dict__:            # first class that defines it
        print(klass.__name__)                # Expected: B
        break                                # stop at the first hit
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: thinking depth-first left-to-right gives D, B, A, C
#    (that was the old Python 2 classic-class rule -> would pick A.hello)
# ✅ Correct: C3 puts A after BOTH B and C -> D, B, C, A, object
```

---

## 🎯 Interview Tip (1 line)
Say: "Python 3 uses C3 linearization, so there's no ambiguity — check `Class.__mro__` instead of guessing."

---

## 🔗 Related Questions
→ Q031 (inheritance and super) | Q033 (super chain) | Q163 (explain MRO) | Q302 (MRO)
