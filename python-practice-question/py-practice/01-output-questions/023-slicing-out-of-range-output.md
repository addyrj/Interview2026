---

# Q023. Slicing out of range output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```python
l = [1, 2, 3]
print(l[5:], l[1:100], l[-100:2])        # (a)
print(l[2:1], l[:0])                     # (b)
print(l[5::-1], l[-10::-1], l[:5:-1])    # (c)
try:
    print(l[5])                          # (d)
except IndexError as e:
    print(e)
l[5:] = [9]                              # (e) slice assignment out of range
print(l)
```

---

## 💡 Quick Concept (2 lines only)
Slices never raise IndexError: out-of-range bounds are clamped. Only single-index access `l[5]` raises.
हिंदी: Slice में range के बाहर index चलता है (clamp हो जाता है), सिर्फ `l[5]` error देता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
l = [1, 2, 3]                                   # Step 1: three elements
print(l[5:], l[1:100], l[-100:2])               # (a) [] [2, 3] [1, 2] (bounds clamped to 0..len)
print(l[2:1], l[:0])                            # (b) [] [] (start >= stop with step +1 is empty)
print(l[5::-1], l[-10::-1], l[:5:-1])           # (c) [3, 2, 1] [] [] (start clamped to last index; -10 clamps before 0)
try:
    print(l[5])                                 # (d) single index -> IndexError
except IndexError as e:
    print(e)                                    # list index out of range
l[5:] = [9]                                     # (e) start clamped to len -> appends
print(l)                                        # [1, 2, 3, 9]

# ============================================
# TEST CASES
# ============================================
# Expected output (real run, Python 3.13):
# [] [2, 3] [1, 2]
# [] []
# [3, 2, 1] [] []
# list index out of range
# [1, 2, 3, 9]
```

---

## 🔍 Why This Works (3 lines max)
`slice.indices(len)` clamps start/stop into the valid range before copying, so there is nothing to fail. Slice assignment with an out-of-range start also clamps, so it appends at the end.
हिंदी: इसी वजह से `s[10:]` safe है, और `l[5:] = [9]` सीधे end में जुड़ जाता है।

---

## ⚡ Alternative Solution
```python
l = [1, 2, 3]                                   # Sample list
print(slice(5, None).indices(len(l)))           # (3, 3, 1) -> the clamped start, stop, step
print("abc"[10:], "abc"[-10:], [][0:5])         # '' abc [] (works on str / empty list too)
print((1, 2)[5:])                               # () (tuples too)

# Safe "get or default" for single items
def get(seq: list, i: int, default=None):
    return seq[i] if -len(seq) <= i < len(seq) else default   # Manual bounds check
print(get(l, 5, "n/a"))                         # n/a
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: assuming a bad slice raises, or that [i] is as forgiving as [i:i+1]
l = [1, 2, 3]                  # Sample list
print(l[10:11])                # [] (no error - bug is silently hidden)

# ✅ Correct: validate length when it matters
if len(l) > 10:                # Explicit check
    print(l[10])
else:
    print("index 10 not available")   # index 10 not available
```

---

## 🎯 Interview Tip (1 line)
Say: "Slices clamp and never raise; only plain indexing raises IndexError — which also means slice bugs fail silently."

---

## 🔗 Related Questions
→ Q022 (string multiplication and slicing) | Q005 (list multiplication aliasing) | Q010 (sorted vs sort)
