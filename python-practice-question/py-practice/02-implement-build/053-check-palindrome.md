---

# Q053. Check Palindrome
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Implement `is_palindrome(s: str) -> bool` that ignores case and non-alphanumeric characters.

```python
is_palindrome("A man, a plan, a canal: Panama")   # True
is_palindrome("hello")                            # False
```

---

## 💡 Quick Concept (2 lines only)
Clean the string (keep letters/digits, lowercase), then compare characters from both ends moving inward. Any mismatch means not a palindrome.
हिंदी: पहले string साफ करो (सिर्फ letters/digits, lowercase), फिर दोनों सिरों से compare करो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

def is_palindrome(s: str) -> bool:
    cleaned = [c.lower() for c in s if c.isalnum()]  # Step 1: keep alnum chars, lowercase them
    left, right = 0, len(cleaned) - 1                # Step 2: two pointers
    while left < right:                              # Step 3: compare inward
        if cleaned[left] != cleaned[right]:          # mismatch -> not a palindrome
            return False                             # early exit
        left += 1                                    # move left pointer
        right -= 1                                   # move right pointer
    return True                                      # Step 4: all pairs matched

# ============================================
# TEST CASES
# ============================================
print(is_palindrome("racecar"))                          # Expected: True
print(is_palindrome("A man, a plan, a canal: Panama"))   # Expected: True
print(is_palindrome("hello"))                            # Expected: False
print(is_palindrome(""))                                 # Expected: True
print(is_palindrome("No 'x' in Nixon"))                  # Expected: True
```

---

## 🔍 Why This Works (3 lines max)
A palindrome reads the same forwards and backwards, so each mirrored pair must match. Cleaning first makes spaces/punctuation/case irrelevant; empty strings count as palindromes. O(n) time, O(n) space for the cleaned list.
हिंदी: Palindrome में हर mirrored जोड़ी बराबर होनी चाहिए; empty string भी palindrome मानी जाती है।

---

## ⚡ Alternative Solution
```python
def is_pal2(s: str) -> bool:
    t = "".join(c.casefold() for c in s if c.isalnum())  # clean (casefold handles Unicode better)
    return t == t[::-1]                                  # compare with its reverse

print(is_pal2("A man, a plan, a canal: Panama"), is_pal2("hello"))  # Output: True False
print(is_pal2("race a car"))                                        # Output: False

def num_pal(n: int) -> bool:
    return n >= 0 and str(n) == str(n)[::-1]             # integers: negatives are not palindromes

print(num_pal(121), num_pal(-121))                       # Output: True False
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: comparing raw string, ignoring case and punctuation
def bad(s: str) -> bool:
    return s == s[::-1]

print(bad("A man, a plan, a canal: Panama"))   # Output: False  (should be True)

# ✅ Correct: normalize first (see solution) - or two pointers skipping non-alnum to get O(1) space
```

---

## 🎯 Interview Tip (1 line)
Say: "Normalize, then two pointers; clarify case/punctuation rules, and mention the O(1)-space variant that skips non-alphanumerics in place."

---

## 🔗 Related Questions
→ Q051 (reverse a string) | Q052 (reverse words) | Q054 (count vowels) | Q102 (linked list)
