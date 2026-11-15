---

# Q038. Decorator stacking order output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What does this print, and in what order?

```python
def bold(fn):
    print("decorating with bold")
    def w():
        print("bold wrapper running")
        return "<b>" + fn() + "</b>"
    return w

def italic(fn):
    print("decorating with italic")
    def w():
        print("italic wrapper running")
        return "<i>" + fn() + "</i>"
    return w

@bold
@italic
def hi(): return "hi"

print(hi())
```

---

## 💡 Quick Concept (2 lines only)
Stacked decorators apply bottom-up at definition time (`hi = bold(italic(hi))`), but the wrappers run top-down at call time.
हिंदी: Decorate करना नीचे से ऊपर होता है, लेकिन call करने पर सबसे ऊपर वाला wrapper पहले चलता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from typing import Callable

def bold(fn: Callable[[], str]) -> Callable[[], str]:
    print("decorating with bold")            # runs at definition time
    def w() -> str:
        print("bold wrapper running")        # runs at call time
        return "<b>" + fn() + "</b>"         # wraps the inner result
    return w

def italic(fn: Callable[[], str]) -> Callable[[], str]:
    print("decorating with italic")          # runs at definition time
    def w() -> str:
        print("italic wrapper running")      # runs at call time
        return "<i>" + fn() + "</i>"
    return w

@bold                  # applied second  -> outermost
@italic                # applied first   -> innermost
def hi() -> str:
    return "hi"        # original function

# ============================================
# TEST CASES
# ============================================
# Expected at definition time (before any call):
# decorating with italic
# decorating with bold
print("--- call")
# Expected: --- call
print(hi())
# Expected:
# bold wrapper running
# italic wrapper running
# <b><i>hi</i></b>
```

---

## 🔍 Why This Works (3 lines max)
`@bold @italic def hi` equals `hi = bold(italic(hi))`: italic runs first and returns a wrapper, which bold then wraps. Calling `hi()` enters the outermost wrapper first, then goes inward.
हिंदी: `hi = bold(italic(hi))` — अंदर वाला पहले decorate होता है, बाहर वाला पहले execute होता है।

---

## ⚡ Alternative Solution
```python
# Same result with manual composition (no @ syntax)
def hi2() -> str:
    return "hi"                          # plain function

hi2 = bold(italic(hi2))                  # prints italic then bold decorating lines
print(hi2())                             # Expected: bold wrapper running, italic wrapper running, <b><i>hi</i></b>
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: assuming the top decorator is applied first (so italic would be outer)
#    Wrong output: <i><b>hi</b></i>
# ✅ Correct: decorators apply bottom-up -> <b><i>hi</i></b>
```

---

## 🎯 Interview Tip (1 line)
Say: "`@a @b def f` is `f = a(b(f))` — applied bottom-up, executed top-down; order matters for things like auth then caching."

---

## 🔗 Related Questions
→ Q039 (decorator without wraps) | Q166 (decorators with arguments) | Q255 (decorator tricks) | Q296 (decorators real use case)
