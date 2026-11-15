---

# Q052. Reverse Words in a Sentence
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Implement `reverse_words(sentence: str) -> str` that reverses the order of words and collapses extra spaces.

```python
reverse_words("the sky is blue")      # "blue is sky the"
reverse_words("  hello   world  ")    # "world hello"
```

---

## 💡 Quick Concept (2 lines only)
`str.split()` with no argument splits on any run of whitespace and drops empty strings. Reverse that list of words and `" ".join` it back.
हिंदी: `split()` बिना argument के extra spaces हटा देता है — words उलटो और `join` करो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

def reverse_words(sentence: str) -> str:
    words = sentence.split()                  # Step 1: split on any whitespace, no empty strings
    left, right = 0, len(words) - 1           # Step 2: two pointers over the word list
    while left < right:                       # Step 3: until pointers meet
        words[left], words[right] = words[right], words[left]  # swap words
        left += 1                             # move left inward
        right -= 1                            # move right inward
    return " ".join(words)                    # Step 4: single spaces between words

# ============================================
# TEST CASES
# ============================================
print(reverse_words("the sky is blue"))       # Expected: blue is sky the
print(reverse_words("  hello   world  "))     # Expected: world hello
print(reverse_words("single"))                # Expected: single
print(repr(reverse_words("")))                # Expected: ''
```

---

## 🔍 Why This Works (3 lines max)
`split()` normalizes spacing, so leading/trailing/multiple spaces vanish. Reversing the list reverses word order; `join` rebuilds with one space. Time and space are O(n).
हिंदी: `split()` spacing ठीक करता है, list उलटने से words का order उलटता है।

---

## ⚡ Alternative Solution
```python
print(" ".join(reversed("the sky is blue".split())))   # Output: blue is sky the
print(" ".join("the sky is blue".split()[::-1]))       # Output: blue is sky the

# Variation: reverse the letters inside each word, keep word order
print(" ".join(w[::-1] for w in "the sky is blue".split()))  # Output: eht yks si eulb
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: split(" ") keeps empty strings for repeated spaces
print("  hello   world  ".split(" "))
# Output: ['', '', 'hello', '', '', 'world', '', '']
print(repr(" ".join("  hello   world  ".split(" ")[::-1])))
# Output: '  world   hello  '   (extra spaces preserved/misplaced)

# ✅ Correct: split() with no argument
print(" ".join("  hello   world  ".split()[::-1]))     # Output: world hello
```

---

## 🎯 Interview Tip (1 line)
Say: "Use `split()` with no args to handle messy whitespace; mention O(n) time/space and ask whether punctuation or spacing must be preserved."

---

## 🔗 Related Questions
→ Q051 (reverse a string) | Q053 (palindrome) | Q257 (string method tricks) | Q022 (string slicing)
