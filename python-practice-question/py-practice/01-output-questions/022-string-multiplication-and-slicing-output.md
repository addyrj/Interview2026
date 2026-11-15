---

# Q022. String multiplication and slicing output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐ Easy

---

## ❓ Question
What will the following code print?

```python
s = "abc"
print(s * 3, s * 0 == "", s * -1 == "")             # (a)
print("ab" * 2 + "c", ("a" + "b") * 2)              # (b)
print("hello"[1:4], "hello"[::-1], "hello"[::2])    # (c)
print("hello"[-3:], "hello"[:-1], "hello"[::-2])    # (d)
print("hello"[3:1:-1])                              # (e)
```

---

## 💡 Quick Concept (2 lines only)
`str * n` repeats (n <= 0 gives an empty string); slicing is `[start:stop:step]` with stop excluded and a negative step walking backwards.
हिंदी: `s[start:stop:step]` — stop शामिल नहीं होता; step `-1` मतलब उल्टा चलना।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
s = "abc"                                              # Step 1: base string
print(s * 3, s * 0 == "", s * -1 == "")                # (a) abcabcabc True True
print("ab" * 2 + "c", ("a" + "b") * 2)                 # (b) ababc abab (* binds before +)
print("hello"[1:4], "hello"[::-1], "hello"[::2])       # (c) ell olleh hlo
print("hello"[-3:], "hello"[:-1], "hello"[::-2])       # (d) llo hell olh
print("hello"[3:1:-1])                                 # (e) ll (indexes 3, 2; stop 1 excluded)

# ============================================
# TEST CASES
# ============================================
# Expected output (real run, Python 3.13):
# abcabcabc True True
# ababc abab
# ell olleh hlo
# llo hell olh
# ll
```

---

## 🔍 Why This Works (3 lines max)
`*` has higher precedence than `+`, so `"ab" * 2 + "c"` is `"abab" + "c"`. Slices pick indexes `start, start+step, ...` until `stop` (exclusive); with a negative step defaults flip to start at the end.
हिंदी: Slicing नई string बनाती है, original नहीं बदलती (strings immutable हैं)।

---

## ⚡ Alternative Solution
```python
s = "abc"                          # Base string
print(s[1], s[-1], s[1:2])         # b c b  (index gives a char, slice gives a str)
print(s[:] == s[::])               # True (full copies)
print([0] * 3, [1, 2] * 2, (1,) * 3)   # [0, 0, 0] [1, 2, 1, 2] (1, 1, 1) (works on sequences)

# Slice objects can be named for readability
last_two = slice(-2, None)         # Same as [-2:]
print("hello"[last_two])           # lo
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: trying to modify a string by index
s = "abc"                          # Immutable str
try:
    s[0] = "x"                     # Not allowed
except TypeError as e:
    print(e)                       # 'str' object does not support item assignment

# ✅ Correct: build a new string
s = "x" + s[1:]                    # xbc
print(s)                           # xbc
```

---

## 🎯 Interview Tip (1 line)
Say: "Slicing is [start:stop:step] with stop exclusive, `[::-1]` reverses, and strings are immutable so every slice returns a new object."

---

## 🔗 Related Questions
→ Q023 (slicing out of range) | Q007 (string immutability) | Q051 (reverse a string)
