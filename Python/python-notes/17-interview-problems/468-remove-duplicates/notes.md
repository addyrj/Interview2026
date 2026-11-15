---

# 468. Remove Duplicates
# हिंदी में: Duplicates हटाना

Full runnable solution (dict.fromkeys, set + order, sorted in-place, unhashable fallback): `main.py`. Run: `python3 main.py`.

---

## 🔵 Simple Definition (English)
Remove repeated items from a list. `list(set(x))` is quick but loses order. `list(dict.fromkeys(x))` removes duplicates and keeps the first occurrence in order.

## 🔵 सरल परिभाषा (Hindi)
List से दोहराए गए items हटाना। `list(set(x))` तेज़ है पर क्रम खो देता है। `list(dict.fromkeys(x))` duplicates हटाता है और पहली बार आने का क्रम बनाए रखता है।

---

## 🔴 Problem it Solves
Real data has repeated rows: duplicate emails in a signup file, repeated product IDs, double-submitted payments. You must dedupe fast (O(n), not O(n^2)) and often keep the original order.

## 🔴 यह क्यों बना? (Hindi)
असली data में दोहराव होता है: signup file में duplicate emails, repeated product IDs, दो बार submit हुए payments। इन्हें O(n) में (O(n^2) में नहीं) हटाना होता है और अक्सर पुराना क्रम रखना होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Keep a "seen" structure (set or dict keys)
Step 2 → Walk through the items in order
Step 3 → Item not in seen → keep it and add to seen
Step 4 → Item already in seen → skip it
Step 5 → Sorted input: two pointers (read/write) work in O(1) space
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → "seen" structure रखो (set या dict keys)
Step 2 → items को क्रम से देखो
Step 3 → seen में नहीं है तो रखो और seen में जोड़ो
Step 4 → पहले से seen में है तो छोड़ दो
Step 5 → sorted input में दो pointers (read/write) से O(1) space में हो जाता है
```

---

## 🟡 Real World Example
A marketing team uploads a CSV of 1 lakh emails with repeats. The backend dedupes them (case-insensitive) before sending a campaign. A payment service dedupes by `idempotency_key` so a double click does not charge twice.

## 🟡 Real Example Hindi mein
Marketing team 1 लाख emails की CSV upload करती है जिसमें repeats हैं। Backend campaign भेजने से पहले उन्हें (case-insensitive) dedupe करता है। Payment service `idempotency_key` से dedupe करती है ताकि double click पर दो बार charge न हो।

---

## 💻 Code Example — Basic
```python
# Basic ways to remove duplicates
nums: list[int] = [3, 1, 3, 2, 1]  # input with repeats

ordered: list[int] = list(dict.fromkeys(nums))  # dict keys are unique and keep insertion order
print(ordered)  # first occurrences, original order
# Output: [3, 1, 2]

unordered: list[int] = sorted(set(nums))  # set removes repeats, sorted gives a clear order
print(unordered)  # order is by value, not by input
# Output: [1, 2, 3]

seen: set[int] = set()  # items already kept
out: list[int] = []  # result list
for x in nums:  # explicit loop version
    if x not in seen:  # first time we see x
        seen.add(x)  # remember it
        out.append(x)  # keep it
print(out)  # same as dict.fromkeys
# Output: [3, 1, 2]
```

## 💻 Code Example — Advanced
```python
# Production style: key function, in-place sorted version, unhashable fallback
from typing import Callable, Hashable, Iterable, List, TypeVar  # type hints

T = TypeVar("T")  # element type


def dedupe_by(items: Iterable[T], key: Callable[[T], Hashable]) -> List[T]:
    """Keep the first item for every key (e.g. emails case-insensitive)."""
    seen: set = set()  # keys already used
    out: List[T] = []  # result
    for item in items:  # preserve order
        k = key(item)  # compute the identity of this item
        if k not in seen:  # new identity
            seen.add(k)  # mark it
            out.append(item)  # keep first occurrence
    return out  # deduped list


def dedupe_sorted_inplace(nums: List[int]) -> int:
    """LeetCode 26: O(1) space on a SORTED list, returns the new length."""
    if not nums:  # empty list
        return 0  # nothing to do
    write: int = 1  # next slot for a unique value
    for read in range(1, len(nums)):  # scan the rest
        if nums[read] != nums[read - 1]:  # a new value starts
            nums[write] = nums[read]  # copy it forward
            write += 1  # advance writer
    return write  # nums[:write] holds the unique values


emails = ["A@x.com", "b@x.com", "a@x.com"]  # case differs
print(dedupe_by(emails, key=str.lower))  # case-insensitive dedupe
# Output: ['A@x.com', 'b@x.com']

data = [1, 1, 2, 2, 2, 3]  # sorted input
k = dedupe_sorted_inplace(data)  # mutates data
print(k, data[:k])  # unique count and the unique prefix
# Output: 3 [1, 2, 3]

rows = [[1], [2], [1]]  # lists are unhashable
try:  # dict.fromkeys needs hashable items
    list(dict.fromkeys(rows))  # fails
except TypeError as exc:  # expected error
    print("TypeError:", exc)  # message
# Output: TypeError: unhashable type: 'list'
print(dedupe_by(rows, key=tuple))  # convert to tuple to make it hashable
# Output: [[1], [2]]
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: keeps order (dict preserves insertion order since 3.7)
unique = list(dict.fromkeys(items))
```

```javascript
// JavaScript: Set also keeps insertion order
const unique = [...new Set(items)];
// objects are compared by reference, so [[1],[1]] stays two items
```

Key difference: JS `Set` works with any value (objects by reference), while Python `set` needs hashable items, so lists and dicts raise `TypeError`. Convert to a tuple or a key first.

---

## 🟠 FastAPI Connection
Dedupe incoming IDs in a bulk endpoint so the database does not do the same work twice.

```python
# FastAPI: bulk delete with deduped ids (pip install fastapi)
from fastapi import FastAPI  # app

app: FastAPI = FastAPI()  # create app


@app.post("/bulk-lookup")  # POST /bulk-lookup with [1, 2, 2, 3]
def bulk_lookup(ids: list[int]) -> dict[str, list[int]]:
    unique_ids: list[int] = list(dict.fromkeys(ids))  # remove repeats, keep order
    return {"ids": unique_ids}  # [1, 2, 3]
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `set()` when order matters
```python
# Wrong - order is not guaranteed to match the input:
print(list(set(["b", "a", "b"])))   # may be ['a', 'b'] or ['b', 'a']

# Correct:
print(list(dict.fromkeys(["b", "a", "b"])))   # ['b', 'a']
```

❌ Mistake 2: O(n^2) membership on a list
```python
# Wrong - `x not in out` scans the list every time
# for x in items:
#     if x not in out: out.append(x)

# Correct - use a set for `seen`, O(1) lookups
```

❌ Mistake 3: Removing items while looping
```python
# Wrong:
nums = [1, 1, 2]
for x in nums:
    if nums.count(x) > 1:
        nums.remove(x)   # skips items, unpredictable

# Correct - build a new list
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
print(list(dict.fromkeys("banana")))
print({1, 1.0, True})
print(len({(1, 2), (1, 2), [1, 2].__class__}))
a = [1, 1, 2]
print(set(a) == {1, 2}, list(set(a)) == [1, 2])
```

**Answer**:
```
['b', 'a', 'n']
{1}
2
True True
```
`1 == 1.0 == True` and they have the same hash, so the set keeps only the first one (`1`). The tuple `(1, 2)` appears twice, so the set has one tuple plus the `list` class: size 2. The last `True` is a coincidence for small ints (they hash to themselves); never rely on set order.

---

## ⚫ Interview Questions + Answers

Q1: Time and space complexity?
A1: O(n) time and O(n) space with a set or dict. O(1) space for the sorted two-pointer version.

Q2: How do you keep order?
A2: `dict.fromkeys(items)` (guaranteed order since Python 3.7) or a loop with a `seen` set.

Q3: How do you dedupe a list of dicts?
A3: Use a key, for example `dedupe_by(rows, key=lambda r: r["id"])`, or convert each dict to a tuple of items if values are hashable.

Q4: Does `set` keep the first or last duplicate?
A4: The first inserted object is kept; later equal items are ignored.

Q5: How do you remove duplicates in pandas?
A5: `df.drop_duplicates(subset=["email"])`.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Cleaning input lists, IDs or emails
- You need first-occurrence order (`dict.fromkeys`)

❌ Avoid when:
- Items are unhashable and the list is large (convert to hashable keys instead of using `in` on a list)
- You need to know how many times each item appeared (use `Counter`)

---

## 📊 Visual Diagram

```
input:  [3, 1, 3, 2, 1]
seen:   {}        -> 3 new  keep   seen={3}
                  -> 1 new  keep   seen={3,1}
                  -> 3 seen skip
                  -> 2 new  keep   seen={3,1,2}
                  -> 1 seen skip
output: [3, 1, 2]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Duplicate | Repeated item | दोहराया हुआ item |
| Hashable | Can be used in set/dict key | set/dict में रखने योग्य |
| Idempotency key | Same request runs only once | एक request एक ही बार चले |
| Two pointers | Read and write indexes | दो pointers |
| Order-preserving | Keeps original sequence | मूल क्रम बनाए रखना |

---

## ⚡ 3-Line Summary
English: `list(dict.fromkeys(x))` removes duplicates in O(n) and keeps order. `set` is fast but unordered and needs hashable items. For sorted lists, use read/write pointers for O(1) space.
Hindi: `list(dict.fromkeys(x))` O(n) में duplicates हटाता है और क्रम रखता है। `set` तेज़ है पर बिना क्रम के और hashable items चाहिए। Sorted list में read/write pointers से O(1) space।

---

## ➡️ Next Topic
**469. Matrix Rotation** — rotate a 2D grid by 90 degrees using zip and reverse.
