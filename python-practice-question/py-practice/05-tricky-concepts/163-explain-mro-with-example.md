---

# Q163. Explain MRO with Example
# Category: Tricky Concepts
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What is the Method Resolution Order (MRO)? Show how it resolves the diamond problem and how `super()` follows it.

---

## 💡 Quick Concept (2 lines only)
MRO is the order in which Python searches base classes for an attribute, computed by the C3 linearization (children before parents, left-to-right, each class once).
हिंदी: MRO वह क्रम है जिसमें Python base classes में method ढूँढता है — child पहले, parent बाद में, हर class एक बार।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
class A:                                      # Step 1: top of the diamond
    def hello(self) -> list[str]:             # base implementation
        return ["A"]                          # end of the chain

class B(A):                                   # Step 2: left branch
    def hello(self) -> list[str]:             # overrides A
        return ["B"] + super().hello()        # super() = NEXT class in MRO, not necessarily A

class C(A):                                   # Step 3: right branch
    def hello(self) -> list[str]:             # overrides A
        return ["C"] + super().hello()        # cooperative call

class D(B, C):                                # Step 4: bottom of the diamond
    def hello(self) -> list[str]:             # overrides both
        return ["D"] + super().hello()        # starts the chain

# ============================================
# TEST CASES
# ============================================
print([k.__name__ for k in D.__mro__])        # Expected: ['D', 'B', 'C', 'A', 'object']
print(D().hello())                            # Expected: ['D', 'B', 'C', 'A']  (A runs once, after C)
print([k.__name__ for k in B.__mro__])        # Expected: ['B', 'A', 'object']  (B alone has no C)

# Inconsistent order -> TypeError at class creation
class X: ...                                  # simple class
class Y(X): ...                               # Y before X is needed
try:                                          # try to create a class that contradicts the order
    class Z(X, Y): ...                        # X listed before its own subclass Y
except TypeError as e:                        # C3 cannot linearize
    print("TypeError:", str(e).splitlines()[0])   # Expected: TypeError: Cannot create a consistent method resolution order (MRO) for bases X, Y
```

---

## 🔍 Why This Works (3 lines max)
C3 merges the parents' MROs so every class appears before its bases and the order of bases in `class D(B, C)` is kept. That puts `C` between `B` and `A`, so `B`'s `super()` calls `C`, not `A`. `super()` means "next in the MRO of `type(self)`".
हिंदी: `super()` का मतलब parent नहीं, बल्कि MRO में अगली class है — इसीलिए B के बाद C चलता है।

---

## ⚡ Alternative Solution
```python
# Inspect MRO with inspect, and see which class provides a method
import inspect                                # standard introspection module

class Base:                                   # base
    def who(self) -> str:                     # defines who()
        return "Base"                         # answer
class Left(Base):                             # no who() override
    pass                                      # inherits
class Right(Base):                            # overrides who()
    def who(self) -> str:                     # override
        return "Right"                        # answer
class Child(Left, Right):                     # Left first, then Right
    pass                                      # inherits only

print(Child().who())                          # Expected: Right  (MRO: Child, Left, Right, Base -> Right defines it before Base)
print([c.__name__ for c in inspect.getmro(Child)])   # Expected: ['Child', 'Left', 'Right', 'Base', 'object']
print(Child.mro() == list(Child.__mro__))     # Expected: True  (.mro() returns a list)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: calling parents directly -> A.hello runs twice in a diamond
class A:
    def hello(self): print("A")
class B(A):
    def hello(self): A.hello(self); print("B")   # hard-codes A
class C(A):
    def hello(self): A.hello(self); print("C")   # hard-codes A
class D(B, C):
    def hello(self): B.hello(self); C.hello(self)   # prints A, B, A, C

# ✅ Correct: use super() everywhere so each class runs exactly once, in MRO order
```

---

## 🎯 Interview Tip (1 line)
Say: "MRO uses C3 linearization; `super()` follows `type(self).__mro__`, so all classes in a hierarchy should call `super()` cooperatively."

---

## 🔗 Related Questions
→ Q031 (inheritance and super) | Q032 (diamond MRO) | Q033 (super chain) | Q271 (mixin pattern) | Q302 (MRO classic)
