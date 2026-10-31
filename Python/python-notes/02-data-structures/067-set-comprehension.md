---

# 067. Set Comprehension
# हिंदी में: Set Comprehension

---

## 🔵 Simple Definition (English)
A set comprehension builds a set in one expression: `{expression for item in iterable if condition}`. It works like a list comprehension, but with curly braces, and the result automatically contains only unique items.

## 🔵 सरल परिभाषा (Hindi)
Set comprehension एक expression में set बनाता है: `{expression for item in iterable if condition}`। यह list comprehension जैसा है पर curly braces के साथ, और result में अपने-आप सिर्फ unique items रहते हैं।

---

## 🔴 Problem it Solves
When you need unique values from transformed data (unique domains from emails, unique cities from orders), a list comprehension followed by `set(...)` builds a temporary list first. A set comprehension does both in one pass, is easier to read, and removes duplicates immediately.

## 🔴 यह क्यों बना? (Hindi)
Transformed data से unique values चाहिए (emails से unique domains, orders से unique cities) तो list comprehension + `set(...)` पहले temporary list बनाता है। Set comprehension एक pass में दोनों करता है, पढ़ने में आसान, और duplicates तुरंत हट जाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python creates an empty set
Step 2 → Takes the next item from the iterable
Step 3 → If there is an `if` filter and it is False, skip the item
Step 4 → Evaluates the expression for the item
Step 5 → Adds the result to the set (duplicates are ignored)
Step 6 → Repeats, then returns the set (order is not guaranteed)
```

## 🟢 कैसे काम करता है? (Hindi)
```
खाली set → अगला item → `if` filter → expression evaluate → set में add (duplicate ignore)
अंत में set लौटता है (order की guarantee नहीं)
```

---

## 🟡 Real World Example
Razorpay analytics: `{txn.merchant_id for txn in txns if txn.amount > 10000}` gives the unique merchants with large payments. For a FastAPI signup check: `{e.lower() for e in emails}` normalizes and de-duplicates a batch of email addresses before inserting them into the database.

## 🟡 Real Example Hindi mein
Razorpay analytics में `{txn.merchant_id for txn in txns if txn.amount > 10000}` बड़े payments वाले unique merchants देता है। FastAPI signup में `{e.lower() for e in emails}` emails को normalize और de-duplicate करता है, database में डालने से पहले।

---

## 💻 Code Example — Basic
```python
# Basic: set comprehension
nums: list[int] = [1, 2, 2, 3, 3, 3, 4]      # data with duplicates

unique_squares: set[int] = {n * n for n in nums}           # squares, duplicates vanish
print(sorted(unique_squares))                # Output: [1, 4, 9, 16]

evens: set[int] = {n for n in nums if n % 2 == 0}          # filter with if
print(evens)                                 # Output: {2, 4}

words: list[str] = ["Apple", "apple", "BANANA", "banana", "Cherry"]   # mixed case
normalized: set[str] = {w.lower() for w in words}          # case-insensitive unique
print(sorted(normalized))                    # Output: ['apple', 'banana', 'cherry']

first_letters: set[str] = {w[0].upper() for w in words}    # unique first letters
print(sorted(first_letters))                 # Output: ['A', 'B', 'C']

emails: list[str] = ["a@x.com", "b@y.com", "c@x.com"]      # sample emails
domains: set[str] = {e.split("@")[1] for e in emails}      # unique domains
print(sorted(domains))                       # Output: ['x.com', 'y.com']

print(type({x for x in range(3)}).__name__)  # Output: set
print(type({}).__name__)                     # Output: dict  (empty {} is NOT a set)
```

## 💻 Code Example — Advanced
```python
# Advanced: validation, nested sets, set math on comprehension results
from __future__ import annotations           # modern hints
import re                                    # for email regex

EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.]+$")   # simple email pattern


def clean_emails(raw: list[str]) -> set[str]:
    """Normalize, validate and de-duplicate emails."""
    return {
        e.strip().lower()                    # normalize each email
        for e in raw
        if EMAIL_RE.match(e.strip())         # keep only valid ones
    }


def invalid_emails(raw: list[str]) -> set[str]:
    """Return the entries that failed validation."""
    return {e for e in raw if not EMAIL_RE.match(e.strip())}   # invalid ones


raw: list[str] = [" A@x.com", "a@x.com ", "bad-email", "b@y.com", ""]
print(sorted(clean_emails(raw)))             # Output: ['a@x.com', 'b@y.com']
print(sorted(invalid_emails(raw)))           # Output: ['', 'bad-email']

# Nested comprehension: flatten and de-duplicate tags in one expression
posts: list[dict[str, list[str]]] = [
    {"tags": ["python", "api"]},
    {"tags": ["api", "fastapi"]},
]
all_tags: set[str] = {tag for post in posts for tag in post["tags"]}   # flatten + unique
print(sorted(all_tags))                      # Output: ['api', 'fastapi', 'python']

# Set elements must be hashable -> use tuples, not lists
pairs: set[tuple[int, int]] = {(x, y) for x in range(2) for y in range(2) if x != y}
print(sorted(pairs))                         # Output: [(0, 1), (1, 0)]

try:                                         # list as an element is invalid
    bad = {[x] for x in range(3)}            # type: ignore
except TypeError as err:                     # catch the error
    print("Error:", err)                     # Output: Error: unhashable type: 'list'

# Combine with set operations: users in both groups
group_a: set[int] = {u for u in range(1, 8)}         # 1..7
group_b: set[int] = {u for u in range(5, 12)}        # 5..11
print(sorted(group_a & group_b))             # Output: [5, 6, 7]

# Order is not preserved; use dict.fromkeys to keep first-seen order
items: list[str] = ["b", "a", "b", "c", "a"]
print(list(dict.fromkeys(items)))            # Output: ['b', 'a', 'c']

# Memory trade-off: generator + set() avoids a huge intermediate list
big: set[int] = set(x % 100 for x in range(1_000_000))   # only 100 unique values kept
print(len(big))                              # Output: 100
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
unique_lengths = {len(w) for w in ["a", "bb", "cc"]}       # one expression
print(unique_lengths)                                       # {1, 2}
```

```javascript
// JavaScript
const uniqueLengths = new Set(["a", "bb", "cc"].map(w => w.length)); // map, then Set
console.log(uniqueLengths);                                          // Set(2) {1, 2}
const evens = new Set([1, 2, 3, 4].filter(n => n % 2 === 0));        // filter, then Set
```

Key difference: JS builds an array first (`map/filter`) and wraps it in `new Set(...)`; Python writes the whole thing in one set comprehension with the filter inside. FastAPI link: use set comprehensions to normalize list inputs (tags, ids, emails) from request bodies before checking or saving them.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `{}` for an empty set / confusing with dict
```python
x = {}                    # dict, not set
x = set()                 # correct for an empty set
y = {k for k in "ab"}     # set comprehension (no colon)
z = {k: 1 for k in "ab"}  # dict comprehension (colon)
```

❌ Mistake 2: Expecting order
```python
s = {c for c in "hello"}
# print(s)  -> order is arbitrary and can change between runs (string hash randomization)
# Correct: sorted(s) when you need stable output
```

❌ Mistake 3: Putting unhashable items inside
```python
# {[x, x] for x in range(3)}   # TypeError: unhashable type: 'list'
# Correct: {(x, x) for x in range(3)}
```

---

## 🧠 Tricky Interview Question

**Q**: "What does `{i % 3 for i in range(10)}` contain, and how many times is the expression evaluated?"

**Answer**: It contains `{0, 1, 2}`. The expression `i % 3` is evaluated 10 times, once for every `i`, even though only 3 unique results are kept. The set only removes duplicates AFTER evaluation, so an expensive expression (like a database call) is not skipped for repeated inputs. To avoid repeated work, de-duplicate the inputs first: `{f(x) for x in set(data)}`.

---

## ⚫ Interview Questions + Answers

Q1: What is the syntax difference between list, set and dict comprehension?
A1: List: `[x for x in it]`. Set: `{x for x in it}` (curly braces, single expression). Dict: `{k: v for ...}` (curly braces with a colon). Tuple parentheses `(x for x in it)` make a generator, not a tuple.

Q2: Set comprehension vs `set(list_comp)`?
A2: Same result. `{...}` is one pass and avoids creating an intermediate list, so it is slightly faster and uses less memory. `set(x for x in ...)` with a generator is almost the same. Prefer the set comprehension for clarity.

Q3: Can a set comprehension have conditions and nested loops?
A3: Yes: `{(x, y) for x in a for y in b if x != y}`. Items must be hashable. For readability, keep it to one or two clauses; use a normal loop for complex logic.

Q4: Why does the order differ between runs?
A4: Sets are hash tables; positions depend on hash values. Strings use randomized hashing per process (PYTHONHASHSEED), so the iteration order of a string set can differ between runs. Ints are stable, but order is still not guaranteed. Use `sorted()` for deterministic output.

Q5: How would you find unique items that appear in two lists using comprehension?
A5: `{x for x in a if x in set_b}` where `set_b = set(b)` for O(1) checks. Or simply `set(a) & set(b)`. Always convert the lookup list to a set first, otherwise `x in list_b` makes it O(n*m).

---

## 🔷 When to Use Set Comprehension

✅ Use when:
- You need unique values from transformed or filtered data
- Normalizing inputs (lowercase, strip) and de-duplicating
- Flattening nested lists into unique items

❌ Avoid when:
- Order matters (use `dict.fromkeys`)
- Items are unhashable
- You need duplicate counts (use `Counter`)

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Comprehension | One-line collection builder | एक line में collection बनाना |
| Unique | No repeated values | Repeat नहीं |
| Hashable | Usable inside a set | Set में रखने लायक |
| Normalization | Convert to a standard form | Standard रूप में बदलना |
| Generator | Lazy item producer | Lazy items बनाने वाला |
| Flatten | Turn nested lists into one level | Nested को एक level में लाना |

---

## ⚡ 3-Line Summary
English: `{expr for x in it if cond}` builds a set of unique results in one pass. Items must be hashable, order is not guaranteed, and the expression still runs for every input. Use `set()` for an empty set, never `{}`.
Hindi: `{expr for x in it if cond}` एक pass में unique results का set बनाता है। Items hashable हों, order guarantee नहीं, और expression हर input पर चलता है। खाली set के लिए `set()`, `{}` नहीं।

---

## ➡️ Next Topic
**072. String Formatting** — f-strings, `format()`, `%` formatting, number and date formatting, padding and alignment.
