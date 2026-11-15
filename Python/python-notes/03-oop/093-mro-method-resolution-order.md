---

# 093. MRO — Method Resolution Order
# हिंदी में: MRO — Method Resolution Order (method खोजने का क्रम)

---

## 🔵 Simple Definition (English)
MRO is the ordered list of classes Python searches when you access an attribute or method on an object. You can see it with `Class.__mro__` or `Class.mro()`. Python builds it with the C3 linearization algorithm.

## 🔵 सरल परिभाषा (Hindi)
MRO उन classes की क्रमबद्ध सूची है जिनमें Python किसी object का attribute या method ढूँढता है। इसे `Class.__mro__` या `Class.mro()` से देख सकते हैं। Python इसे C3 linearization algorithm से बनाता है।

---

## 🔴 Problem it Solves
With one parent the search path is obvious. With several parents (and diamonds) Python needs a fixed, predictable rule for which method is used and in what order `super()` calls run. Older Python versions used depth-first search, which could call a grandparent before its own child and give wrong results. C3 guarantees two rules: a child always comes before its parents, and the left-to-right order of the bases is kept.

## 🔴 यह क्यों बना? (Hindi)
एक parent हो तो search का रास्ता साफ़ है। कई parents (और diamond) में Python को ऐसा तय और अनुमानित नियम चाहिए कि कौन सा method चलेगा और `super()` calls किस क्रम में चलेंगे। पुराने Python में depth-first search था जो grandparent को उसके child से पहले बुला सकता था और गलत नतीजे देता था। C3 दो नियम पक्के करता है: child हमेशा parents से पहले आता है और bases का बाएँ से दाएँ क्रम बना रहता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Take the class and its bases: D(B, C)
Step 2 → MRO(D) = D + merge(MRO(B), MRO(C), [B, C])
Step 3 → Merge: pick the first head that does not appear in the tail of any other list
Step 4 → B is fine, then C (A is blocked because C still lists it in a tail), then A, then object
Step 5 → Result D, B, C, A, object is stored in `D.__mro__`
Step 6 → Lookup and `super()` both walk this list; if no valid merge exists, TypeError
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Class और उसके bases लें: D(B, C)
Step 2 → MRO(D) = D + merge(MRO(B), MRO(C), [B, C])
Step 3 → Merge: वह पहला head चुनें जो किसी दूसरी सूची की tail में न हो
Step 4 → B ठीक है, फिर C (A रुका क्योंकि C की tail में है), फिर A, फिर object
Step 5 → नतीजा D, B, C, A, object `D.__mro__` में रखा जाता है
Step 6 → Lookup और `super()` दोनों इसी सूची पर चलते हैं; सही merge न बने तो TypeError
```

---

## 🟡 Real World Example
Debugging a Django or SQLAlchemy mixin: print `Model.__mro__` to see why a `save()` override runs in a certain order. Logging and audit mixins rely on `super().save()` forming a chain through the MRO. In interviews, MRO questions test whether you know that `super()` follows the MRO of the object's type, not the written parent.

## 🟡 Real Example Hindi mein
Django या SQLAlchemy mixin debug करते समय `Model.__mro__` print करके देखते हैं कि `save()` override किस क्रम में चल रहा है। Logging और audit mixins `super().save()` की ऐसी chain पर निर्भर हैं जो MRO से बनती है। Interviews में MRO सवाल जाँचते हैं कि आप जानते हैं `super()` लिखे हुए parent को नहीं, object के type की MRO को follow करता है।

---

## 💻 Code Example — Basic
```python
# Basic: MRO = the order Python searches classes for a method
class A:
    def hello(self) -> str:
        return "A"


class B(A):
    def hello(self) -> str:
        return "B"


class C(A):
    def hello(self) -> str:
        return "C"


class D(B, C):                                    # diamond: D -> B, C -> A
    pass


print(D().hello())                                # B (first in MRO that has hello)
print(D.__mro__)                                  # tuple of classes in search order
print([k.__name__ for k in D.mro()])              # same, as a list
print(D.__mro__[-1] is object)                    # object is always last


class E(C, B):                                    # swap parents
    pass


print(E().hello(), [k.__name__ for k in E.mro()]) # now C comes before B

# Output:
# B
# (<class '__main__.D'>, <class '__main__.B'>, <class '__main__.C'>, <class '__main__.A'>, <class 'object'>)
# ['D', 'B', 'C', 'A', 'object']
# True
# C ['E', 'C', 'B', 'A', 'object']
```

## 💻 Code Example — Advanced
```python
# Advanced: C3 linearization, super() follows the MRO (not "the parent"), and conflicts
from __future__ import annotations


class Base:
    def run(self) -> list[str]:
        return ["Base"]


class Left(Base):
    def run(self) -> list[str]:
        return ["Left"] + super().run()           # super() = NEXT class in MRO of type(self)


class Right(Base):
    def run(self) -> list[str]:
        return ["Right"] + super().run()


class Child(Left, Right):
    def run(self) -> list[str]:
        return ["Child"] + super().run()


print(Child().run())                              # Child Left Right Base: every class once
print([c.__name__ for c in Child.mro()])
print(Left().run())                               # alone, Left's super is Base (MRO differs!)

# C3 rules: children before parents, left-to-right order of bases kept
try:
    class Bad(Base, Left): ...                    # parent listed before its own child
except TypeError as e:
    print("Error:", e)


def explain(cls: type) -> str:                    # helper to debug MRO issues
    return " -> ".join(k.__name__ for k in cls.__mro__)


print(explain(Child))


class A:
    def who(self) -> str:
        return "A"


class B(A):
    pass


class C(A):
    def who(self) -> str:
        return "C"


class D(B, C):
    pass


print(D().who(), explain(D))                      # C: B has no who, C is before A
print(D.who is C.who, D.__mro__.index(C) < D.__mro__.index(A))
print(super(Left, Child()).run())                 # start the search AFTER Left in Child's MRO

# Output:
# ['Child', 'Left', 'Right', 'Base']
# ['Child', 'Left', 'Right', 'Base', 'object']
# ['Left', 'Base']
# Error: Cannot create a consistent method resolution order (MRO) for bases Base, Left
# Child -> Left -> Right -> Base -> object
# C D -> B -> C -> A -> object
# True True
# ['Right', 'Base']
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Lookup order | `Class.__mro__` (C3) | prototype chain (one line) |
| Inspect | `Class.mro()` | `Object.getPrototypeOf` loop |
| Several parents | yes, ordered by C3 | no |
| `super` | next class in MRO | parent prototype only |
| Inconsistent order | TypeError at class creation | not possible |

```python
# Python way
class A: ...
class B(A): ...
class C(A): ...
class D(B, C): ...

print([k.__name__ for k in D.mro()])   # ['D', 'B', 'C', 'A', 'object']
```
```javascript
// JavaScript way
class A {}
class B extends A {}
const chain = [];
let p = B.prototype;
while (p) { chain.push(p.constructor.name); p = Object.getPrototypeOf(p); }
console.log(chain);   // [ 'B', 'A', 'Object' ]  (a single line only)
```

Key difference: JavaScript has one linear prototype chain, so no ordering rules are needed. Python's multiple inheritance needs C3 to flatten a graph of parents into one line; `__mro__` is the Python equivalent of walking the prototype chain.

---

## 🟠 FastAPI Connection
Pydantic v2 combines fields from several base models by walking the MRO in reverse, so the example shows `name` (from the right-most base) before `created`. SQLAlchemy mixins and FastAPI dependency classes also rely on the same ordering rules.

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel


class Timestamped(BaseModel):
    created: str = "2026-01-01"


class Named(BaseModel):
    name: str


class Article(Timestamped, Named):                # pydantic merges fields along the MRO
    pass


app = FastAPI()


@app.post("/a")
def a(x: Article) -> dict:
    return {"fields": list(Article.model_fields), "mro": [c.__name__ for c in Article.__mro__[:3]]}


print(TestClient(app).post("/a", json={"name": "n"}).json())

# Output:
# {'fields': ['name', 'created'], 'mro': ['Article', 'Timestamped', 'Named']}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Thinking `super()` always calls the written parent
✅ Correct: remember it follows the MRO of the real object

```python
class Base:
    def run(self) -> list[str]:
        return ["Base"]
class Left(Base):
    def run(self) -> list[str]:
        return ["Left"] + super().run()
class Right(Base):
    def run(self) -> list[str]:
        return ["Right"] + super().run()
class Child(Left, Right): ...
print(Left().run())          # ['Left', 'Base']
print(Child().run())         # ['Left', 'Right', 'Base']  Right is called, not Base
```

❌ Mistake 2: Ordering bases so that a parent comes before its own child
✅ Correct: list the more specific class first

```python
class A: ...
class B(A): ...
try:
    class Bad(A, B): ...
except TypeError as e:
    print("Error:", e)
class Good(B, A): ...
print(Good.__mro__[1].__name__)
```

❌ Mistake 3: Guessing the order instead of printing it
✅ Correct: inspect `__mro__` when in doubt

```python
class A:
    def who(self) -> str: return "A"
class B(A): ...
class C(A):
    def who(self) -> str: return "C"
class D(B, C): ...
print(D().who())             # C, not A!
print(" -> ".join(k.__name__ for k in D.__mro__))
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class A:
    def go(self): print("A", end=" ")
class B(A):
    def go(self):
        print("B", end=" "); super().go()
class C(A):
    def go(self):
        print("C", end=" "); super().go()
class D(B, C):
    def go(self):
        print("D", end=" "); super().go()
D().go(); print()
B().go(); print()
print([k.__name__ for k in D.mro()])
```

Output:
```
D B C A 
B A 
['D', 'B', 'C', 'A', 'object']
```

Answer: `D.mro()` is D, B, C, A, object. `super()` in each class calls the next class in THAT list, so `D().go()` prints `D B C A`: B's `super().go()` goes to C, not A. For a plain `B()` object the MRO is only B, A, object, so the same method prints `B A`. This shows that `super()` depends on the type of the object, not on where the code is written.

---

## ⚫ Interview Questions + Answers

Q1: What is MRO?
A1: The order in which Python searches a class and its ancestors for attributes and methods. View it with `Class.__mro__` or `Class.mro()`; `object` is always last.

Q2: Which algorithm does Python use and what are its rules?
A2: C3 linearization (since Python 2.3). Rules: a class comes before its parents (monotonic), and the order of the bases in the class statement is preserved. If both cannot be satisfied, TypeError is raised.

Q3: How does `super()` use the MRO?
A3: `super()` finds the current class in `type(self).__mro__` and starts the search at the next class. With cooperative methods it creates a chain that visits every class once.

Q4: Why does `class Bad(A, B)` fail when B inherits A?
A4: A would have to be before B (listed first) and after B (parent after child). No consistent order exists, so Python raises `TypeError: Cannot create a consistent method resolution order`.

Q5: How do you start `super()` search from a specific class?
A5: Use the two-argument form `super(Left, obj)` which starts after `Left` in `type(obj).__mro__`. It is rarely needed; mostly useful for debugging or teaching.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Debugging which method runs in multi-parent classes
- Designing mixins and cooperative `super()` chains
- Answering interview questions about the diamond problem
- Checking why a mixin override is ignored

❌ Avoid when:
- Relying on subtle MRO tricks in team code; prefer simple hierarchies
- Hard-coding parent calls (`Parent.method(self)`) in multi-parent classes
- Fixing ordering errors by guessing; print `__mro__` first

---

## 📊 Visual Diagram
```
class D(B, C)       B(A)   C(A)

MRO(D) = D + merge( [B, A, o], [C, A, o], [B, C] )
  take B   (not in any tail)          -> D B
  take C   (A is in tail of [C, A])   -> D B C
  take A                              -> D B C A
  take object                         -> D B C A object

        A
       / \
      B   C        super() inside B  -> C
       \ /         super() inside C  -> A
        D
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| MRO | Search order of classes | Classes के search का क्रम |
| C3 linearization | Algorithm that builds the MRO | MRO बनाने वाला algorithm |
| `__mro__` | Tuple holding the order | क्रम वाला tuple |
| Monotonic | Child before parents always | Child हमेशा parents से पहले |
| Diamond | Two parents, one grandparent | दो parents, एक grandparent |
| `super()` | Next class in MRO | MRO की अगली class |

---

## ⚡ 3-Line Summary
English: MRO is the C3-built list of classes Python searches for attributes and `super()` calls. A child always comes before its parents and the base order is preserved. Print `Class.__mro__` to debug, and remember `super()` follows the object's type.
Hindi: MRO उन classes की C3 से बनी सूची है जिसमें Python attributes और `super()` calls ढूँढता है। Child हमेशा parents से पहले आता है और bases का क्रम बना रहता है। Debug के लिए `Class.__mro__` print करें और याद रखें `super()` object के type को follow करता है।

---

## ➡️ Next Topic
**094. `super()` Function** — how `super()` walks the MRO to reuse parent code, with cooperative `__init__` chains.
