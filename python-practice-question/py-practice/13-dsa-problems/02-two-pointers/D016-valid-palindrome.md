---

# D016. Valid Palindrome
# Category: DSA — Two Pointers
# Difficulty: ⭐ Easy | LeetCode #125

---

## ❓ Problem
A phrase is a palindrome if, after lowercasing and removing all non-alphanumeric characters, it reads the same forwards and backwards. Given a string `s`, return `True` if it is a palindrome.

```
Input:  "A man, a plan, a canal: Panama"
Output: True
```

---

## 💡 Quick Concept (2 lines only)
Put one pointer at each end, skip characters that are not letters/digits, and compare lowercase versions while moving inwards. Mismatch means False.
हिंदी: दोनों सिरों पर pointer रखो, non-alphanumeric characters skip करो, lowercase करके compare करते हुए अंदर आओ।

---

## ✅ Solution

```python
# ============================================
# APPROACH 1: Brute force — clean then compare with reverse
# O(n) time, O(n) space
# ============================================
def is_palindrome_clean(s: str) -> bool:
    cleaned = [c.lower() for c in s if c.isalnum()]  # keep only letters/digits, lowercase
    return cleaned == cleaned[::-1]  # equals its reverse?

# ============================================
# APPROACH 2: Two pointers in place — O(n) time, O(1) space ✅ PREFERRED
# ============================================
def is_palindrome(s: str) -> bool:
    l, r = 0, len(s) - 1  # pointers at both ends
    while l < r:  # until they cross
        while l < r and not s[l].isalnum():  # skip junk on the left
            l += 1  # move left pointer
        while l < r and not s[r].isalnum():  # skip junk on the right
            r -= 1  # move right pointer
        if s[l].lower() != s[r].lower():  # compare case-insensitively
            return False  # mismatch -> not a palindrome
        l += 1  # move inward
        r -= 1  # move inward
    return True  # all pairs matched

# ============================================
# TEST CASES
# ============================================
print(is_palindrome_clean("A man, a plan, a canal: Panama"))  # True
print(is_palindrome("A man, a plan, a canal: Panama"))  # True
print(is_palindrome("race a car"))  # False
print(is_palindrome(" "))  # True
print(is_palindrome(""))  # True
print(is_palindrome("0P"))  # False
print(is_palindrome(".,"))  # True
```

---

## 🔍 Why It Works
```
"A man, a plan..." l='A' r='a' -> equal (lowercased)
l=' ' skipped, r='m' ... keep matching pairs
Each pointer moves at most n steps in total -> O(n)
```
हिंदी: हर pointer कुल n कदम ही चलता है और extra string नहीं बनती, इसलिए O(n) time और O(1) space।

---

## 📊 Complexity
```
Clean + reverse: Time O(n) | Space O(n)
Two pointers:    Time O(n) | Space O(1) ← preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Pythonic one-liner using str.isalnum on a generator
def is_palindrome_short(s: str) -> bool:
    t = "".join(filter(str.isalnum, s.lower()))  # keep letters/digits only
    return t == t[::-1]  # compare with reverse

print(is_palindrome_short("A man, a plan, a canal: Panama"))  # True
print(is_palindrome_short("race a car"))  # False
# VARIANT 2: Valid Palindrome II — may delete at most one character (try skipping s[l] or s[r] on first mismatch)
# VARIANT 3: Longest palindromic substring (expand around centre)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: forgetting lowercase -> "Aa" returns False
return s[l] != s[r]

# ❌ Wrong: using only isalpha() drops digits -> "0P" would wrongly look valid

# ✅ Correct: isalnum() + lower() on both sides
```

---

## 🎯 Interview Tip
Say: "I'll use two pointers so I don't allocate a cleaned copy; empty string and punctuation-only strings count as palindromes." Mention `isalnum` handles digits too.

---

## 🔗 Related Problems
→ D022 (Reverse String) | D017 (Two Sum II) | D019 (Container With Most Water)
