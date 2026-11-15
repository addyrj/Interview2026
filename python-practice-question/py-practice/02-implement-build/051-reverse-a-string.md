---

# Q051. Reverse a String
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Implement `reverse_string(s: str) -> str` that returns the string reversed, without using `s[::-1]` or `reversed()` in the main solution.

```python
reverse_string("hello")   # "olleh"
```

---

## 💡 Quick Concept (2 lines only)
Strings are immutable, so convert to a list, swap characters from both ends with two pointers, then join back. The idiomatic one-liner is `s[::-1]`.
हिंदी: String immutable है — list बनाओ, दोनों सिरों से swap करो, फिर `join` करो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

def reverse_string(s: str) -> str:
    chars = list(s)                           # Step 1: strings are immutable -> use a list
    left, right = 0, len(chars) - 1           # Step 2: two pointers at both ends
    while left < right:                       # Step 3: stop when pointers meet
        chars[left], chars[right] = chars[right], chars[left]  # swap without temp variable
        left += 1                             # move left pointer inward
        right -= 1                            # move right pointer inward
    return "".join(chars)                     # Step 4: build the new string

# ============================================
# TEST CASES
# ============================================
print(reverse_string("hello"))        # Expected: olleh
print(repr(reverse_string("")))       # Expected: ''
print(reverse_string("a"))            # Expected: a
print(reverse_string("Python 3.13"))  # Expected: 31.3 nohtyP
```

---

## 🔍 Why This Works (3 lines max)
Swapping the outer pair, then the next pair inward, reverses the sequence in O(n) time with O(n) extra space (the list). Empty and one-character strings skip the loop and return unchanged.
हिंदी: बाहर से अंदर की ओर जोड़ी-जोड़ी swap करने से string उलट जाती है — O(n) time।

---

## ⚡ Alternative Solution
```python
def rev_slice(s: str) -> str:
    return s[::-1]                            # extended slice with step -1 (most Pythonic)

def rev_join(s: str) -> str:
    return "".join(reversed(s))               # reversed() gives an iterator of chars

def rev_rec(s: str) -> str:
    return s if len(s) <= 1 else rev_rec(s[1:]) + s[0]  # recursion: O(n^2), hits recursion limit ~1000

print(rev_slice("hello"), rev_join("hello"), rev_rec("hello"))  # Output: olleh olleh olleh

# Caveat: slicing reverses code points, not grapheme clusters
e = "éa"                                # 'e' + combining acute accent + 'a'
print(e[::-1])                                # Output: áe  (accent now attaches to the wrong letter)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: strings have no .reverse() (that is a list method)
# "hello".reverse()                           # AttributeError (not run)
# reversed("hello") == "olleh"                # False: reversed() returns an iterator, not a str

# ✅ Correct
print("".join(reversed("hello")))             # Output: olleh
print("hello"[::-1])                          # Output: olleh
```

---

## 🎯 Interview Tip (1 line)
Say: "`s[::-1]` is the Pythonic way, but strings are immutable so manual reversal means a list + two pointers — O(n) time and space."

---

## 🔗 Related Questions
→ Q052 (reverse words) | Q053 (palindrome) | Q022 (string multiplication and slicing) | Q023 (slicing out of range)
