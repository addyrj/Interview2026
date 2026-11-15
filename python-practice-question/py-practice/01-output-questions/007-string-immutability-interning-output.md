---

# Q007. String Immutability + Interning Output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```python
import sys

s = "hello"
try:
    s[0] = "J"
except TypeError as e:
    print(e)

t = s
s += " world"
print(s, t)

x = "".join(["hel", "lo"])
y = "hello"
print(x == y, x is y, sys.intern(x) is y)
```

---

## 💡 Quick Concept (2 lines only)
Strings are immutable: "changing" one creates a new string. CPython may intern (share) some strings, but only `==` is guaranteed to compare value.
हिंदी: String बदली नहीं जा सकती, हर बदलाव नया string बनाता है; `is` पर भरोसा मत करो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import sys                              # sys.intern lets us intern manually

# Step 1: item assignment is not allowed on str
s = "hello"                             # create a string
try:
    s[0] = "J"                          # attempt to mutate in place
except TypeError as e:                  # str has no __setitem__
    print(e)                            # Expected: 'str' object does not support item assignment

# Step 2: += rebinds the name to a NEW string; the old one is untouched
t = s                                   # t points to "hello"
s += " world"                           # builds "hello world" and rebinds s
print(s, t)                             # Expected: hello world hello

# Step 3: equal value vs same object
x = "".join(["hel", "lo"])              # built at runtime -> a new string object
y = "hello"                             # literal, interned by the compiler
print(x == y, x is y, sys.intern(x) is y)  # Expected: True False True
```

---

## 🔍 Why This Works (3 lines max)
`str` defines no `__setitem__`, so item assignment raises TypeError, and `+=` creates a fresh string while `t` keeps the old one. Identifier-like literals are interned, but runtime-built strings are not unless you call `sys.intern`.
हिंदी: Runtime पर बना string अलग object होता है; `sys.intern` से वही shared object मिलता है।

---

## ⚡ Alternative Solution
```python
# Modify text by building a new string (slicing + concatenation)
s = "hello"                             # original string
new = "J" + s[1:]                       # new string with first char replaced
print(new, s)                           # Expected: Jello hello

# Or str.replace / list round-trip for many edits
chars = list(s)                         # lists are mutable
chars[0] = "J"                          # edit in place
print("".join(chars))                   # Expected: Jello
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: assuming `is` on strings tells you if they are equal
# a = "".join(["hel", "lo"]); print(a is "hello")   # False (also SyntaxWarning)
# Whether two equal strings share an object depends on how they were created (version/impl dependent)

# ✅ Correct: compare value with ==
# print(a == "hello")   # True
```

---

## 🎯 Interview Tip (1 line)
Say: "Strings are immutable and hashable; interning is a CPython optimisation, so I compare with `==` and build big strings with `''.join`."

---

## 🔗 Related Questions
→ Q003 (is vs ==) | Q004 (small int caching) | Q174 (is, == and interning) | Q282 (string concatenation vs join)
