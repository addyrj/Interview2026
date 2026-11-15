---

# Q309. Python 2 vs 3 key differences
# Category: INTERVIEW CLASSICS
# Difficulty: ⭐ Easy

---

## ❓ Question
Name the key differences between Python 2 and Python 3 and show each one in code. (Python 2 is end-of-life since Jan 2020, but interviewers still ask this.)

Predict the output of each line:
```python
# NOT RUN (question view)
print(7 / 2)
print(7 // 2)
print(type("x"), type(b"x"))
print(range(3))
print({"a": 1}.keys())
```

---

## 💡 Quick Concept (2 lines only)
Python 3 fixed design mistakes: `print` is a function, `/` is true division, `str` is Unicode (bytes are separate), and `range`/`map`/`dict.keys()` return lazy views, not lists.
हिंदी: Python 3 में print function है, `/` हमेशा float देता है, str Unicode है, और range/map/keys lazy होते हैं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
# Step 1: print is a function (Py2: `print "hi"` statement)
print("hi")                              # needs parentheses in Python 3

# Step 2: true division vs floor division
print(7 / 2)                             # Py3: 3.5 (Py2 gave 3 for ints)
print(7 // 2)                            # floor division, same in both: 3

# Step 3: no int/long split, ints have unlimited size
print(type(10 ** 20))                    # <class 'int'> (Py2 had separate `long`)

# Step 4: str is Unicode, bytes is separate type
print(type("x"), type(b"x"))             # <class 'str'> <class 'bytes'>
print("héllo".encode("utf-8"))           # str -> bytes explicitly

# Step 5: range/map/dict.keys() are lazy in Py3
print(range(3), list(range(3)))          # range object, convert with list()
print({"a": 1}.keys())                   # dict_keys view, not a list
print(list(map(str, [1, 2])))            # map is an iterator, wrap in list()

# Step 6: no implicit ordering between different types
try:                                     # Py2 allowed 1 < "a"
    print(1 < "a")                       # Py3 raises TypeError
except TypeError as e:                   # catch to show message
    print("TypeError:", e)               # print the error text

# Step 7: new syntax: f-strings, unpacking, `raise ... from`
a, *rest = [1, 2, 3]                     # extended unpacking (Py3 only)
print(a, rest)                           # 1 [2, 3]
try:                                     # exception chaining example
    try:                                 # inner try
        1 / 0                            # raises ZeroDivisionError
    except ZeroDivisionError as e:       # catch with `as` (Py2 used a comma)
        raise ValueError("bad") from e   # chain explicitly
except ValueError as e:                  # outer catch
    print(repr(e.__cause__))             # ZeroDivisionError('division by zero')

# ============================================
# TEST CASES
# ============================================
# Real output from Python 3.13:
# hi
# 3.5
# 3
# <class 'int'>
# <class 'str'> <class 'bytes'>
# b'h\xc3\xa9llo'
# range(0, 3) [0, 1, 2]
# dict_keys(['a'])
# ['1', '2']
# TypeError: '<' not supported between instances of 'int' and 'str'
# 1 [2, 3]
# ZeroDivisionError('division by zero')
```

---

## 🔍 Why This Works (3 lines max)
Py3 broke backward compatibility on purpose: text vs binary is explicit, `/` never silently truncates, and lazy iterators save memory. Other changes: `input()` replaces `raw_input()`, `xrange` became `range`, `unicode` became `str`.
हिंदी: Py3 ने जानबूझकर पुरानी गलतियाँ ठीक कीं — text और bytes अलग, और lazy iterators से memory बचती है।

---

## ⚡ Alternative Solution
```python
# Quick programmatic checks of Py3 behaviour (each line prints True)
import sys                                    # access version info
print(sys.version_info >= (3, 0))             # True: running Python 3
print(isinstance("x", str) and not isinstance(b"x", str))  # True: str vs bytes split
print(7 / 2 == 3.5 and 7 // 2 == 3)           # True: true vs floor division
print(not isinstance(range(3), list))         # True: range is lazy, not a list
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: assuming `/` truncates and map() returns a list (Py2 habits)
# half = len(items) / 2        # float in Py3 -> items[half] raises TypeError
# squares = map(f, items); squares[0]   # TypeError: 'map' object is not subscriptable

# ✅ Correct: use // for indexes, wrap lazy iterators in list()
items = [1, 2, 3, 4, 5]                       # sample data
half = len(items) // 2                        # integer index
print(items[half])                            # 3
squares = list(map(lambda v: v * v, items))   # materialize the map
print(squares[0])                             # 1
```

---

## 🎯 Interview Tip (1 line)
Mention the big four (print/division, str vs bytes, lazy iterators, int unification) and that Py2 is EOL — then say you only write Python 3.

---

## 🔗 Related Questions
→ 310, 297, 291
