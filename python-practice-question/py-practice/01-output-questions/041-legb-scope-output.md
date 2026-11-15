---

# Q041. LEGB scope output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
What does this print? Pay attention to the class body.

```python
x = "global"
def outer():
    x = "enclosing"
    def inner():
        print(x)
    inner()
    class K:
        x = "class"
        def m(self): return x
        y = x
    print(K().m(), K.y)
outer()
```

---

## 💡 Quick Concept (2 lines only)
Names resolve Local → Enclosing → Global → Built-in. A class body is NOT an enclosing scope for its methods.
हिंदी: Lookup order है Local, Enclosing, Global, Built-in — और class का scope methods के लिए enclosing नहीं होता।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
x = "global"                          # G: module scope
def outer() -> None:
    x = "enclosing"                   # E: enclosing function scope
    def inner() -> None:
        print(x)                      # no local x -> finds E
    inner()                           # prints enclosing
    class K:
        x = "class"                   # class-body local
        def m(self) -> str:
            return x                  # methods skip class scope -> finds E
        y = x                         # class body itself sees class x
        z = [x for _ in range(1)]     # comprehension in class body skips class scope too
    print(K().m(), K.y, K.z)

# ============================================
# TEST CASES
# ============================================
outer()
# Expected:
# enclosing
# enclosing class ['enclosing']

print(len)                            # B: built-in. Expected: <built-in function len>
len = "shadowed"                      # G now hides the builtin
print(len)                            # Expected: shadowed
del len                               # remove the shadow
print(len)                            # Expected: <built-in function len>

def f() -> None:
    try:
        print(a)                      # `a` is assigned below -> local for the whole function
    except UnboundLocalError as e:
        print("UnboundLocalError:", e)
    a = 1
a = "module"
f()
# Expected: UnboundLocalError: cannot access local variable 'a' where it is not associated with a value
```

---

## 🔍 Why This Works (3 lines max)
Method bodies and comprehensions are separate function scopes that look outward through enclosing FUNCTION scopes, skipping class bodies. (PEP 709 inlines comprehensions in 3.12+, but class-body scope is still skipped; the result above was run on 3.13.)
हिंदी: Class body सिर्फ़ अपने code के लिए scope है — methods और comprehension उसे नहीं देखते।

---

## ⚡ Alternative Solution
```python
# Inspect scopes directly
import builtins

def show() -> None:
    v = 1                              # local
    print("v" in locals())             # Expected: True
    print("show" in globals())         # Expected: True
    print(hasattr(builtins, "len"))    # Expected: True
show()                                 # run it
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: expecting method `m` to see the class attribute `x` as a bare name
#    -> it returns "enclosing", not "class"
# ✅ Correct: use self.x or K.x inside methods
```

---

## 🎯 Interview Tip (1 line)
Say: "LEGB, but class bodies are skipped by nested functions — use `self.x`; and any assignment in a function makes that name local for the entire function."

---

## 🔗 Related Questions
→ Q040 (global vs nonlocal) | Q024 (list comprehension scope) | Q179 (comprehension scoping) | Q129 (shadowing built-ins bug)
