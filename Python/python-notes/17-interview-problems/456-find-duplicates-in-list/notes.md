---

# 456. Find Duplicates in List
# हिंदी में: List में दोहराए गए (duplicate) items ढूँढना

Runnable solution with asserts: `main.py` in this folder (`python3 main.py` prints `duplicates: [2, 1]` and `All duplicate tests passed`, verified on Python 3.13.3).

---

## 🔵 Simple Definition (English)
Given a list, find the values that appear more than once (or just check whether any duplicate exists). The fastest common method uses a `set` or `Counter` to remember what has been seen.

## 🔵 सरल परिभाषा (Hindi)
एक list दी गई है; वे values ढूँढनी हैं जो एक से ज़्यादा बार आती हैं (या बस यह जाँचना कि कोई duplicate है या नहीं)। सबसे तेज़ आम तरीका `set` या `Counter` से देखे हुए items याद रखना है।

---

## 🔴 Problem it Solves
Duplicates break uniqueness rules: two users with the same email, the same payment processed twice, repeated rows in an import. Checking every pair is O(n^2) and unusable for a million rows, so interviewers test whether you reach for hashing to get O(n).

## 🔴 यह क्यों बना? (Hindi)
Duplicates uniqueness के नियम तोड़ते हैं: एक ही email के दो users, एक payment दो बार process होना, import में दोहराई पंक्तियाँ। हर जोड़ी जाँचना O(n^2) है और दस लाख rows पर बेकार है, इसलिए interviewer देखते हैं कि आप O(n) के लिए hashing अपनाते हैं या नहीं।

---

## 🟢 How it Works — Step by Step

```
Set approach (O(n) time, O(n) space):
Step 1 → seen = empty set
Step 2 → For each item: if item is already in seen -> it is a duplicate
Step 3 → Otherwise add it to seen
Counter approach: count every item, keep those with count > 1
Sort approach (O(n log n), tiny extra space): sort, then equal neighbours are duplicates
Brute force: compare every pair -> O(n^2)  (only to explain why we avoid it)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Set तरीका (O(n) समय, O(n) space):
Step 1 → seen = खाली set
Step 2 → हर item के लिए: अगर seen में पहले से है -> duplicate है
Step 3 → वरना उसे seen में जोड़ दो
Counter तरीका: सबकी गिनती करो, count > 1 वाले रखो
Sort तरीका (O(n log n), बहुत कम extra space): sort करो, बराबर पड़ोसी duplicates हैं
Brute force: हर जोड़ी तुलना -> O(n^2)  (सिर्फ़ यह समझाने के लिए कि क्यों नहीं)
```

---

## 🟡 Real World Example
A Razorpay reconciliation job scans a day's 2 million transaction ids and flags any `txn_id` that occurs twice, because a retry may have charged a customer twice. An onboarding service uses the same idea to reject a second signup with an email that already exists.

## 🟡 Real Example Hindi mein
Razorpay का reconciliation job दिन भर के 20 लाख transaction ids में हर उस `txn_id` को flag करता है जो दो बार आया, क्योंकि retry से customer से दो बार पैसे कट सकते हैं। Onboarding service वही idea इस्तेमाल करके ऐसे दूसरे signup को रोकती है जिसका email पहले से मौजूद है।

---

## 💻 Code Example — Basic
```python
# Basic: duplicates with a set (full version with more approaches in main.py)
def find_duplicates(items: list[int]) -> list[int]:  # returns each duplicated value once
    seen: set[int] = set()  # values met so far
    dupes: list[int] = []  # duplicates, in order of their 2nd appearance
    for item in items:  # single pass
        if item in seen and item not in dupes:  # second time we see it
            dupes.append(item)  # record it once
        seen.add(item)  # remember it
    return dupes


data: list[int] = [1, 2, 3, 2, 4, 5, 1, 2, 6]  # sample data
print(find_duplicates(data))  # 2 and 1 repeat
# Output: [2, 1]
print(len(data) != len(set(data)))  # quick yes/no check: any duplicate?
# Output: True
```

## 💻 Code Example — Advanced
```python
# From main.py: Counter keeps counts; sort approach uses almost no extra space
from collections import Counter  # frequency counting
from typing import Hashable, List, TypeVar  # type hints

T = TypeVar("T", bound=Hashable)  # items must be hashable to live in a set or dict


def duplicates_counter(items: List[T]) -> List[T]:
    counts: Counter[T] = Counter(items)  # item -> how many times
    return [item for item, c in counts.items() if c > 1]  # keep count > 1


def duplicates_sort(items: List[int]) -> List[int]:
    data: List[int] = sorted(items)  # copy then sort: O(n log n)
    out: List[int] = []  # result
    for i in range(1, len(data)):  # compare with the previous element
        if data[i] == data[i - 1] and (not out or out[-1] != data[i]):  # a new duplicate value
            out.append(data[i])
    return out


nums: List[int] = [1, 2, 3, 2, 4, 5, 1, 2, 6]
print(duplicates_counter(nums))  # order of first occurrence
# Output: [1, 2]
print(duplicates_sort(nums))  # sorted order
# Output: [1, 2]
print(Counter(nums).most_common(1))  # most repeated value with its count
# Output: [(2, 3)]
print(duplicates_counter(["a", "b", "a"]))  # works for any hashable type
# Output: ['a']
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
data = [1, 2, 3, 2, 1]
dupes = {x for x in data if data.count(x) > 1}      # simple, O(n^2)
has_dupes = len(data) != len(set(data))             # O(n)
```
```javascript
// JavaScript
const data = [1, 2, 3, 2, 1];
const hasDupes = new Set(data).size !== data.length;           // O(n)
const dupes = [...new Set(data.filter((x, i) => data.indexOf(x) !== i))];
```

Key differences: both use a hash set for O(n). Python has `collections.Counter`, which JS lacks. One gotcha: JS `Set` compares objects by reference (like Python's identity-based default hash for custom objects), but Python lists and dicts are unhashable and cannot go into a set at all.

---

## 🟠 FastAPI Connection
Pydantic can reject duplicate items in a request body, and the idea is how APIs enforce unique tags or ids.

```python
# FastAPI + Pydantic: reject duplicate tags in a request (pip install fastapi)
from fastapi import FastAPI  # framework
from pydantic import BaseModel, field_validator  # validation

app: FastAPI = FastAPI()  # create app


class Article(BaseModel):  # request body
    tags: list[str]  # list from the client

    @field_validator("tags")  # runs after type validation
    @classmethod
    def no_duplicates(cls, v: list[str]) -> list[str]:
        if len(v) != len(set(v)):  # O(n) duplicate check
            raise ValueError("duplicate tags are not allowed")  # becomes a 422 response
        return v


@app.post("/articles")  # POST /articles
def create(article: Article) -> dict[str, int]:
    return {"tags": len(article.tags)}  # success
```

Not run as a server here; the duplicate-check logic is verified in `main.py`.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `list.count()` inside a loop
✅ Correct: use a set or `Counter` (O(n) total instead of O(n^2)).

```python
# Wrong - O(n^2)
dupes = [x for x in data if data.count(x) > 1]       # also repeats each duplicate
# Right
from collections import Counter
dupes = [x for x, c in Counter(data).items() if c > 1]
```

❌ Mistake 2: Putting unhashable items (lists, dicts) into a set
✅ Correct: convert to tuples (`tuple(row)`) or serialise (`json.dumps(row, sort_keys=True)`) first.

❌ Mistake 3: Assuming `set()` keeps order
✅ Correct: sets are unordered; use `dict.fromkeys(items)` to remove duplicates while keeping order.

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
a = [1, 2, 2, 3, 3, 3]
print(len(a) != len(set(a)))
print(set([1, 1.0, True]))
print([x for x in a if a.count(x) > 1])
```

**Answer**:
```
True
{1}
[2, 2, 3, 3, 3]
```
`1`, `1.0` and `True` are equal and share the same hash, so a set keeps only one of them. The list comprehension returns every occurrence of repeated values, not each duplicate once, and is O(n^2).

---

## ⚫ Interview Questions + Answers

Q1: What is the most efficient way to check if a list has duplicates?
A1: `len(items) != len(set(items))`, O(n) time and O(n) space, or stop early with a `seen` set and return at the first repeat.

Q2: How can you find duplicates without extra memory?
A2: Sort the list in place and compare neighbours: O(n log n) time, O(1) extra space (but it changes the original order).

Q3: How do you remove duplicates but keep order?
A3: `list(dict.fromkeys(items))` (dicts preserve insertion order since Python 3.7).

Q4: How do you find duplicate rows in a list of dicts?
A4: Convert each dict to a hashable key such as `tuple(sorted(d.items()))` and count with `Counter`.

Q5: How does this relate to databases?
A5: `SELECT email, COUNT(*) FROM users GROUP BY email HAVING COUNT(*) > 1` finds duplicates, and a `UNIQUE` constraint prevents them.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Items are hashable (numbers, strings, tuples)
- You need counts as well as presence (`Counter`)
- Data fits in memory

❌ Avoid when:
- Items are unhashable and you cannot convert them (fall back to sorting with a key)
- Data is too big for memory (use database `GROUP BY` or external sort)
- Approximate answers are enough (use a Bloom filter)

---

## 📊 Visual Diagram

```
 data = [1, 2, 3, 2, 4, 5, 1, 2, 6]

 item  seen after step         action
  1    {1}                     add
  2    {1,2}                   add
  3    {1,2,3}                 add
  2    already in seen   ─────► duplicate!  dupes = [2]
  4,5  {1,2,3,4,5}             add
  1    already in seen   ─────► duplicate!  dupes = [2, 1]
  2    already (listed)        skip
  6    add
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Duplicate | Value that repeats | दोहराई गई value |
| Set | Unique-value collection | अद्वितीय values का संग्रह |
| Hashable | Can be used as dict/set key | dict/set key बन सकने वाला |
| Counter | Dict of counts | गिनती वाला dict |
| O(n) | Time grows linearly | समय सीधे बढ़ता है |
| Idempotency | Same request has same effect | एक ही request का एक जैसा असर |

---

## ⚡ 3-Line Summary
English: Track seen values in a set (or count with `Counter`) to find duplicates in O(n). Sorting needs less memory but costs O(n log n), and brute force is O(n^2). Only hashable items can go into sets.
Hindi: Duplicates O(n) में ढूँढने के लिए देखे हुए values set में रखें (या `Counter` से गिनें)। Sorting में memory कम लगती है पर O(n log n) समय लगता है, और brute force O(n^2) है। Sets में सिर्फ़ hashable items जा सकते हैं।

---

## ➡️ Next Topic
**457. Flatten Nested List** — recursion, generators (`yield from`) and an explicit stack for deep nesting.
