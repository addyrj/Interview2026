---

# D022. Reverse String
# Category: DSA — Two Pointers
# Difficulty: ⭐ Easy | LeetCode #344

---

## ❓ Problem
Reverse a list of characters `s` **in place** using O(1) extra memory.

```
Input:  s = ["h","e","l","l","o"]
Output: ["o","l","l","e","h"]
```

---

## 💡 Quick Concept (2 lines only)
Two pointers, one at each end: swap and move inward until they meet. In Python strings are immutable, so the in-place version works on a list of characters.
हिंदी: दोनों सिरों पर pointer रखो, swap करो और अंदर की तरफ बढ़ो जब तक वे मिल न जाएँ।

---

## ✅ Solution

```python
# ============================================
# APPROACH 1: Brute force — build a new list backwards
# O(n) time, O(n) space (not in place)
# ============================================
def reverse_new(s: list[str]) -> list[str]:
    out: list[str] = []                                  # new list
    for i in range(len(s) - 1, -1, -1):                  # walk from the end
        out.append(s[i])                                 # copy character
    return out                                           # reversed copy


# ============================================
# APPROACH 2: Two pointers ✅ PREFERRED (in place)
# O(n) time, O(1) space
# ============================================
def reverse_string(s: list[str]) -> None:
    left, right = 0, len(s) - 1                          # pointers at both ends
    while left < right:                                  # until they meet / cross
        s[left], s[right] = s[right], s[left]            # swap ends (tuple swap, no temp)
        left += 1                                        # move left inward
        right -= 1                                       # move right inward


# ============================================
# APPROACH 3: Recursion
# O(n) time, O(n) call-stack space
# ============================================
def reverse_rec(s: list[str], left: int = 0, right: int | None = None) -> None:
    if right is None:                                    # first call
        right = len(s) - 1                               # start at the end
    if left >= right:                                    # base case: met in the middle
        return                                           # done
    s[left], s[right] = s[right], s[left]                # swap ends
    reverse_rec(s, left + 1, right - 1)                  # solve the inner part


# ============================================
# TEST CASES
# ============================================
print(reverse_new(list("hello")))                        # ['o', 'l', 'l', 'e', 'h']
a = list("hello")
reverse_string(a)
print(a)                                                 # ['o', 'l', 'l', 'e', 'h']
b = list("Hannah!")
reverse_rec(b)
print("".join(b))                                        # !hannaH
c = ["a"]
reverse_string(c)
print(c)                                                 # ['a']
d: list[str] = []
reverse_string(d)
print(d)                                                 # []
e = list("ab")
reverse_string(e)
print(e)                                                 # ['b', 'a']
```

---

## 🔍 Why It Works
```
h e l l o      swap(0,4) -> o e l l h
^       ^      swap(1,3) -> o l l e h
  ^   ^        left=2, right=2 -> stop (middle stays)
```
हिंदी: बीच का element अपनी जगह पर रहता है, इसलिए `left < right` तक ही चलना है।

---

## 📊 Complexity
```
New list:     Time O(n) | Space O(n)
Two pointers: Time O(n) | Space O(1)  ← preferred
Recursion:    Time O(n) | Space O(n) stack (depth n/2)
```

---

## ⚡ Variations

```python
# VARIANT 1: Built-ins — list.reverse() is in place, s[::-1] makes a copy
x = list("hello")
x.reverse()                                              # in place, returns None
print(x)                                                 # ['o', 'l', 'l', 'e', 'h']
print("hello"[::-1])                                     # olleh
print("".join(reversed("hello")))                        # olleh

# VARIANT 2: Assign through slice to keep the same list object
y = list("abc")
y[:] = y[::-1]                                           # O(n) extra, but in the same list object
print(y)                                                 # ['c', 'b', 'a']

# VARIANT 3: Reverse words in a sentence (see Q052) / Reverse only letters (skip non-letters)
def reverse_only_letters(s: str) -> str:
    chars = list(s)                                      # mutable copy
    i, j = 0, len(chars) - 1                             # two pointers
    while i < j:                                         # until they meet
        if not chars[i].isalpha():                       # skip non-letter on the left
            i += 1
        elif not chars[j].isalpha():                     # skip non-letter on the right
            j -= 1
        else:                                            # both are letters
            chars[i], chars[j] = chars[j], chars[i]      # swap them
            i += 1
            j -= 1
    return "".join(chars)                                # rebuild string

print(reverse_only_letters("a-bC-dEf-ghIj"))             # j-Ih-gfE-dCba
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: assigning to a string index -> strings are immutable
word = "hello"
try:
    word[0] = "H"
except TypeError as e:
    print(e)                                             # 'str' object does not support item assignment

# ❌ Wrong: `s = s[::-1]` inside a function only rebinds the local name (caller's list unchanged)

# ✅ Correct: swap in place on a list (or s[:] = s[::-1] / s.reverse())
```

---

## 🎯 Interview Tip
Say: "Strings are immutable in Python, so the in-place version operates on a list of chars. Two pointers swap until they meet; `list.reverse()` is the built-in." Mention `[::-1]` allocates a copy.

---

## 🔗 Related Problems
→ D016 (Valid Palindrome) | D010 (Rotate Array) | D011 (Move Zeroes)
