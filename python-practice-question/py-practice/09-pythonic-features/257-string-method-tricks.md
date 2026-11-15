---

# Q257. String Method Tricks
# Category: PYTHONIC + MODERN PYTHON FEATURES
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Show 8 string-method tricks that interviewers like: `join` vs `+`, `split` with `maxsplit`, `partition`, `removeprefix/removesuffix` (3.9+), `str.translate`, `casefold`, `startswith` with a tuple, and `zfill`/`center`.

```python
s = "  Hello, World  "
# strip, split, partition, startswith(("a","b")) ... ?
```

---

## 💡 Quick Concept (2 lines only)
Strings are immutable, so every method returns a NEW string. Prefer methods (`join`, `partition`, `removeprefix`) over manual slicing and loops.
हिंदी: String immutable है — हर method नई string लौटाती है, original नहीं बदलता।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
s = "  Hello, World  "                            # sample with spaces

print(repr(s.strip()))                           # 1. strip both ends

print(", ".join(["a", "b", "c"]))                # 2. join: fast way to build strings

print("a=b=c".split("=", 1))                     # 3. maxsplit=1 -> split at first "=" only

print("key=value=x".partition("="))              # 4. always returns a 3-tuple (head, sep, tail)

print("test_file.py".removesuffix(".py"))        # 5. removesuffix (3.9+), not strip(".py")!

table = str.maketrans("aeiou", "12345")          # 6. translate: char -> char mapping
print("education".translate(table))              # fast multi-char replace

print("Straße".casefold() == "STRASSE".casefold())  # 7. casefold: aggressive lowercase for compare

print("image.png".endswith((".png", ".jpg")))    # 8. tuple of options, no "or" chain

print("7".zfill(3), "hi".center(6, "*"))         # 9. zero-pad and centre

# Output:
# 'Hello, World'
# a, b, c
# ['a', 'b=c']
# ('key', '=', 'value=x')
# test_file
# 2d5c1t34n
# True
# True
# 007 **hi**
```

---

## 🔍 Why This Works (3 lines max)
`partition` never raises (missing separator gives `(s, '', '')`), unlike `split` unpacking. `casefold` handles Unicode like German ß -> "ss", which `lower()` does not. `startswith`/`endswith` accept a tuple, so one call checks many options.
हिंदी: `casefold()` Unicode में भी सही compare करता है (ß → ss), जबकि `lower()` नहीं।

---

## ⚡ Alternative Solution
```python
# Counting, finding, and safe checks
text = "banana"                                  # sample text

print(text.count("an"))                          # non-overlapping occurrences
print(text.find("x"), text.find("n"))            # find: -1 if missing (index() would raise)
print(text.replace("a", "A", 2))                 # replace only first 2
print("abc123".isalnum(), "abc".isdigit())       # type checks
print(f"{text!r:>10}")                           # f-string: repr, right-aligned width 10

# Output:
# 2
# -1 2
# bAnAna
# True False
#   'banana'
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: strip() takes a SET of characters, not a substring
print("test.py.py".strip(".py"))                 # strips any of '.', 'p', 'y' from both ends -> 'test'

# ✅ Correct: removesuffix removes the exact suffix once
print("test.py.py".removesuffix(".py"))          # test.py

# Output:
# test
# test.py
```

---

## 🎯 Interview Tip (1 line)
Say: "Strings are immutable; I build with `''.join(parts)` (O(n)) not `+=` in a loop, and use `removeprefix` instead of `strip` for exact prefixes."

---

## 🔗 Related Questions
→ Q007 (string immutability + interning) | Q022 (string multiplication and slicing) | Q282 (string concatenation vs join) | Q243 (advanced f-strings)
