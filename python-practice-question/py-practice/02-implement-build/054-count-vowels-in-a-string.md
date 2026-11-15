---

# Q054. Count Vowels in a String
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Implement `count_vowels(s: str) -> int` that counts vowels (a, e, i, o, u) case-insensitively.

```python
count_vowels("Hello World")   # 3
```

---

## 💡 Quick Concept (2 lines only)
Lowercase the string once and test each character for membership in the vowel set. Set/frozenset lookup is O(1).
हिंदी: string को lowercase करो और हर character को vowels के set में check करो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

def count_vowels(s: str) -> int:
    count = 0                                 # Step 1: running total
    for ch in s.lower():                      # Step 2: lowercase once so 'A' counts too
        if ch in "aeiou":                     # Step 3: membership test against the vowels
            count += 1                        # Step 4: increment on a match
    return count                              # Step 5: final answer

# ============================================
# TEST CASES
# ============================================
print(count_vowels("Hello World"))    # Expected: 3
print(count_vowels("rhythm"))         # Expected: 0
print(count_vowels("AEIOU"))          # Expected: 5
print(count_vowels(""))               # Expected: 0
```

---

## 🔍 Why This Works (3 lines max)
Every character is checked exactly once, so it is O(n) time and O(1) space. Lowercasing first avoids listing uppercase vowels separately.
हिंदी: हर character एक बार check होता है — O(n) time, extra memory नहीं।

---

## ⚡ Alternative Solution
```python
from collections import Counter                # for per-vowel frequencies

VOWELS = frozenset("aeiou")                    # constant set of vowels

def cv2(s: str) -> int:
    return sum(ch in VOWELS for ch in s.lower())  # True counts as 1, so sum() counts matches

print(cv2("Hello World"))                      # Output: 3

def vowel_freq(s: str) -> dict[str, int]:
    return dict(Counter(ch for ch in s.lower() if ch in VOWELS))  # count each vowel

print(vowel_freq("Education"))                 # Output: {'e': 1, 'u': 1, 'a': 1, 'i': 1, 'o': 1}
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: forgetting uppercase vowels
def bad(s: str) -> int:
    return sum(1 for ch in s if ch in "aeiou")

print(bad("HELLO"))                            # Output: 0  (should be 2)

# ✅ Correct: normalize case
print(cv2("HELLO"))                            # Output: 2

# Also beware: "" in "aeiou" is True and "ae" in "aeiou" is True (substring test!),
# so only test single characters: iterate char by char.
```

---

## 🎯 Interview Tip (1 line)
Say: "Normalize case, use a set for O(1) membership, and ask whether 'y' or non-English vowels count."

---

## 🔗 Related Questions
→ Q051 (reverse a string) | Q066 (count occurrences) | Q053 (palindrome) | Q257 (string method tricks)
