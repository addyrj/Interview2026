---

# 452. Check Palindrome
# हिंदी में: Palindrome जाँचना (उल्टा पढ़ने पर भी वही)

Runnable solution with asserts: `main.py` in this folder (`python3 main.py` prints `All palindrome tests passed`, verified on Python 3.13.3).

---

## 🔵 Simple Definition (English)
A palindrome reads the same forwards and backwards, like `madam` or `121`. The task: write a function that returns `True` or `False`, usually ignoring case, spaces and punctuation.

## 🔵 सरल परिभाषा (Hindi)
Palindrome वह है जो आगे से और पीछे से एक जैसा पढ़ा जाए, जैसे `madam` या `121`। Task: ऐसा function लिखना जो `True` या `False` दे, आमतौर पर case, spaces और punctuation को अनदेखा करके।

---

## 🔴 Problem it Solves
This is the classic warm-up that tests string handling, slicing, two pointers and edge cases (empty string, one character, punctuation). It also appears in real code: validating symmetric IDs, checking DNA reverse complements, and normalising user text before comparison.

## 🔴 यह क्यों बना? (Hindi)
यह classic warm-up string handling, slicing, two pointers और edge cases (empty string, एक अक्षर, punctuation) को परखता है। असली code में भी काम आता है: symmetric IDs जाँचना, DNA sequence की जाँच और comparison से पहले user text को normalise करना।

---

## 🟢 How it Works — Step by Step

```
Slice approach:
Step 1 → Clean: keep only letters/digits, lowercase everything
Step 2 → Reverse with [::-1]
Step 3 → Compare cleaned == reversed

Two-pointer approach (O(1) extra space):
Step 1 → left = 0, right = len - 1
Step 2 → Skip non-alphanumeric characters on both sides
Step 3 → Compare lower(s[left]) and lower(s[right]); mismatch -> False
Step 4 → Move both pointers inward until they cross -> True
```

## 🟢 कैसे काम करता है? (Hindi)
```
Slice तरीका:
Step 1 → साफ़ करो: सिर्फ़ letters/digits रखो, सब lowercase
Step 2 → [::-1] से उल्टा करो
Step 3 → साफ़ string और उल्टी string की तुलना करो

Two-pointer तरीका (O(1) extra space):
Step 1 → left = 0, right = len - 1
Step 2 → दोनों तरफ़ के non-alphanumeric characters छोड़ो
Step 3 → lower(s[left]) और lower(s[right]) मिलाओ; अलग हों तो False
Step 4 → pointers अंदर की ओर बढ़ाओ जब तक वे मिल न जाएँ -> True
```

---

## 🟡 Real World Example
A support chatbot for an Indian bank normalises user input before matching ("Yes!" vs "yes"). The same "clean then compare" idea is used in duplicate-detection of phone numbers and in coding rounds at Razorpay or Flipkart where the palindrome check is the opening question.

## 🟡 Real Example Hindi mein
किसी बैंक का support chatbot matching से पहले user input को normalise करता है ("Yes!" बनाम "yes")। वही "पहले साफ़ करो फिर तुलना करो" idea phone numbers की duplicate-detection में और Razorpay या Flipkart के coding rounds में दिखता है, जहाँ palindrome अक्सर पहला सवाल होता है।

---

## 💻 Code Example — Basic
```python
# Basic palindrome check (the full version with tests is in main.py)
def is_palindrome(s: str) -> bool:  # takes a string, returns a bool
    cleaned: str = "".join(ch.lower() for ch in s if ch.isalnum())  # keep letters/digits, lowercase
    return cleaned == cleaned[::-1]  # equal to its own reverse?


print(is_palindrome("madam"))  # simple case
# Output: True
print(is_palindrome("A man, a plan, a canal: Panama"))  # punctuation and case ignored
# Output: True
print(is_palindrome("hello"))  # not a palindrome
# Output: False
print(is_palindrome(""))  # empty string counts as a palindrome
# Output: True
```

## 💻 Code Example — Advanced
```python
# From main.py: two pointers, O(n) time and O(1) extra space, plus integer version
def is_palindrome_two_pointers(s: str) -> bool:
    """No new string is created."""
    left: int = 0  # start pointer
    right: int = len(s) - 1  # end pointer
    while left < right:  # until they meet
        while left < right and not s[left].isalnum():  # skip junk on the left
            left += 1
        while left < right and not s[right].isalnum():  # skip junk on the right
            right -= 1
        if s[left].lower() != s[right].lower():  # mismatch
            return False  # early exit
        left += 1  # move inward
        right -= 1
    return True  # every pair matched


def is_integer_palindrome(n: int) -> bool:
    """Reverse the digits mathematically (no str conversion)."""
    if n < 0:  # '-121' reads '121-' backwards
        return False
    original: int = n  # remember input
    reversed_n: int = 0  # reversed number being built
    while n > 0:  # peel digits
        reversed_n = reversed_n * 10 + n % 10  # append last digit
        n //= 10  # drop last digit
    return original == reversed_n  # compare


print(is_palindrome_two_pointers("No 'x' in Nixon"))  # Output: True
print(is_palindrome_two_pointers("race a car"))  # Output: False
print(is_integer_palindrome(121), is_integer_palindrome(-121), is_integer_palindrome(10))
# Output: True False False
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
def is_pal(s: str) -> bool:
    c = [ch.lower() for ch in s if ch.isalnum()]
    return c == c[::-1]          # list slicing reverses
```
```javascript
// JavaScript (strings have no reverse; go through an array)
const isPal = (s) => {
  const c = s.toLowerCase().replace(/[^a-z0-9]/g, "");
  return c === [...c].reverse().join("");
};
```

Key differences: Python reverses with `[::-1]` on any sequence; JavaScript needs `split("")/[...c]` + `reverse()` + `join("")`. `reverse()` in JS mutates the array while Python slicing returns a new object. Python's `str.isalnum()` also accepts Unicode letters such as Devanagari, whereas the JS regex above only matches ASCII.

---

## 🟠 FastAPI Connection
Expose the checker as an endpoint; useful as a small utility or a validation rule (for example, vanity codes must not be palindromes).

```python
# FastAPI: palindrome endpoint (pip install fastapi)
from fastapi import FastAPI, Query  # framework + query validation

app: FastAPI = FastAPI()  # create app


def is_palindrome(s: str) -> bool:  # same helper as above
    cleaned: str = "".join(ch.lower() for ch in s if ch.isalnum())
    return cleaned == cleaned[::-1]


@app.get("/palindrome")  # GET /palindrome?text=madam
def check(text: str = Query(..., max_length=1000)) -> dict[str, object]:  # cap input size
    return {"text": text, "is_palindrome": is_palindrome(text)}  # JSON response
```

Not run as a server here; the function logic is the same one verified in `main.py`.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Ignoring case and punctuation
✅ Correct: normalise first.

```python
s = "Aba"
print(s == s[::-1])                            # Wrong -> False
print(s.lower() == s.lower()[::-1])            # Right -> True
```

❌ Mistake 2: Forgetting edge cases (empty string, one char, negative numbers)
✅ Correct: the empty string and one character are palindromes; negative integers are not.

❌ Mistake 3: Using recursion for very long strings
✅ Correct: recursion depth is about n/2 and Python's limit is about 1000; use the loop or slicing version for long input.

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
s = "Aba"
print(s == s[::-1], s.lower() == s.lower()[::-1], "A man" == "A man"[::-1])
```

**Answer**: `False True False`. `"Aba"` reversed is `"abA"`, which differs from `"Aba"` by case; after lowercasing both sides match. `"A man"` reversed is `"nam A"`, so it is not a palindrome unless spaces are removed and case is folded (even then, `"aman"` reversed is `"nama"`).

---

## ⚫ Interview Questions + Answers

Q1: Time and space complexity of the slice version?
A1: O(n) time and O(n) space, since it creates a cleaned copy and a reversed copy.

Q2: How do you get O(1) extra space?
A2: Two pointers moving inward from both ends, skipping non-alphanumeric characters, comparing case-insensitively.

Q3: How would you check an integer palindrome without converting to string?
A3: Build the reverse by repeatedly taking `n % 10` and `n //= 10`, then compare with the original. Negative numbers return `False`.

Q4: What about Unicode (accents, Devanagari)?
A4: Use `str.casefold()` instead of `lower()` and normalise with `unicodedata.normalize("NFC", s)`; combining characters can make visually equal strings differ.

Q5: Can you find the longest palindromic substring?
A5: Yes, expand around each centre (2n-1 centres) in O(n^2) time and O(1) space; Manacher's algorithm does it in O(n).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You must compare text that reads the same in both directions
- Input is user text needing normalisation first
- You want a quick exercise in two-pointer logic

❌ Avoid when:
- You need fuzzy matching (use edit distance libraries instead)
- Text is huge and you need streaming (use two pointers over a file buffer)
- Locale rules matter (Turkish dotless i, accents) without proper normalisation

---

## 📊 Visual Diagram

```
 "A man, a plan, a canal: Panama"
   clean -> amanaplanacanalpanama

   a m a n a p l a n a c a n a l p a n a m a
   ↑                                       ↑
  left ───────────►         ◄─────────── right      equal? yes -> move inward
                         ... pointers meet in the middle -> True
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Palindrome | Same forwards and backwards | आगे-पीछे एक जैसा |
| Two pointers | Indices moving from both ends | दोनों सिरों से चलते indices |
| Slicing `[::-1]` | Reverse a sequence | sequence उलटना |
| Normalise | Clean text before compare | तुलना से पहले text साफ़ करना |
| isalnum | True for letters and digits | अक्षर या अंक है |
| Edge case | Unusual input | असामान्य input |

---

## ⚡ 3-Line Summary
English: Clean the text, then compare it with its reverse, or use two pointers for O(1) space. Handle empty strings, single characters and negative numbers. Use `casefold` and Unicode normalisation for international text.
Hindi: Text साफ़ करके उसकी उल्टी से तुलना करें, या O(1) space के लिए two pointers इस्तेमाल करें। Empty string, एक अक्षर और negative numbers का ध्यान रखें। International text के लिए `casefold` और Unicode normalisation लगाएँ।

---

## ➡️ Next Topic
**453. FizzBuzz** — the classic condition-ordering problem that tests `%` and `if/elif` logic.
