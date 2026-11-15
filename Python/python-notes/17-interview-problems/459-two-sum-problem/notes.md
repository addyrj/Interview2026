---

# 459. Two Sum Problem
# हिंदी में: Two Sum (ऐसी दो संख्याएँ जिनका जोड़ target हो)

Runnable solution with asserts: `main.py` in this folder (`python3 main.py` prints `(0, 1)`, `(1, 2)`, `(0, 1)`, `None` and `all tests passed`, verified on Python 3.13.3; it also cross-checks 500 random cases against brute force).

---

## 🔵 Simple Definition (English)
Given a list of numbers and a target, find the indices of two different elements whose sum equals the target. Example: `[2, 7, 11, 15]`, target `9` gives indices `(0, 1)` because `2 + 7 = 9`.

## 🔵 सरल परिभाषा (Hindi)
संख्याओं की list और एक target दिया है; दो अलग-अलग elements के indices ढूँढने हैं जिनका जोड़ target के बराबर हो। उदाहरण: `[2, 7, 11, 15]`, target `9` पर indices `(0, 1)` क्योंकि `2 + 7 = 9`।

---

## 🔴 Problem it Solves
The brute-force answer tries every pair (O(n^2)). The interview point is "trade memory for time": store what you have seen in a dictionary and look up the partner (`target - value`) in O(1). This lookup-the-complement idea appears in payment matching, ledger reconciliation and pair-finding queries.

## 🔴 यह क्यों बना? (Hindi)
Brute-force हर जोड़ी आज़माता है (O(n^2))। Interview का मुद्दा है "memory देकर समय बचाओ": जो देख चुके हैं उसे dictionary में रखो और partner (`target - value`) O(1) में ढूँढो। यही complement-lookup idea payment matching, ledger reconciliation और pair ढूँढने वाली queries में दिखता है।

---

## 🟢 How it Works — Step by Step

```
Hash map approach (O(n) time, O(n) space):
Step 1 → seen = {}  (value -> index)
Step 2 → For each index i, value v: need = target - v
Step 3 → If need is already in seen -> return (seen[need], i)
Step 4 → Otherwise store seen[v] = i
Step 5 → Loop ends without a match -> return None

Brute force: for i in range(n): for j in range(i + 1, n): if nums[i] + nums[j] == target
```

## 🟢 कैसे काम करता है? (Hindi)
```
Hash map तरीका (O(n) समय, O(n) space):
Step 1 → seen = {}  (value -> index)
Step 2 → हर index i और value v के लिए: need = target - v
Step 3 → अगर need पहले से seen में है -> (seen[need], i) लौटाओ
Step 4 → वरना seen[v] = i रखो
Step 5 → बिना match के loop खत्म हो -> None

Brute force: for i in range(n): for j in range(i + 1, n): अगर nums[i] + nums[j] == target
```

---

## 🟡 Real World Example
A reconciliation job at a payments company has a list of debit amounts and a credit amount, and needs to find which two debits add up to that credit. A budgeting app finds two expenses that exactly match a target sum. Both use the "remember what I have seen, look up the complement" approach.

## 🟡 Real Example Hindi mein
Payments कंपनी का reconciliation job debit amounts की list और एक credit amount लेता है, और पता करता है कि कौन-से दो debits मिलकर उस credit के बराबर हैं। Budgeting app ऐसे दो खर्च ढूँढता है जिनका जोड़ ठीक target हो। दोनों "जो देखा याद रखो, complement ढूँढो" तरीका इस्तेमाल करते हैं।

---

## 💻 Code Example — Basic
```python
# Basic: brute force vs hash map (full tests in main.py)
from typing import Optional  # for "might return None"


def two_sum_brute(nums: list[int], target: int) -> Optional[tuple[int, int]]:
    n: int = len(nums)  # number of items
    for i in range(n):  # first index
        for j in range(i + 1, n):  # second index is always after i
            if nums[i] + nums[j] == target:  # pair found
                return (i, j)  # return the indices
    return None  # no pair exists


def two_sum(nums: list[int], target: int) -> Optional[tuple[int, int]]:
    seen: dict[int, int] = {}  # value -> index
    for i, value in enumerate(nums):  # one pass
        need: int = target - value  # the partner we want
        if need in seen:  # partner already seen?
            return (seen[need], i)  # earlier index first
        seen[value] = i  # remember this value
    return None  # nothing matched


print(two_sum_brute([2, 7, 11, 15], 9))  # Output: (0, 1)
print(two_sum([2, 7, 11, 15], 9))  # Output: (0, 1)
print(two_sum([3, 2, 4], 6))  # Output: (1, 2)
print(two_sum([1, 2], 10))  # no pair -> Output: None
```

## 💻 Code Example — Advanced
```python
# Production style: all pairs, duplicates and negatives handled, typed, with a safety check
from collections import defaultdict  # value -> list of indices
from typing import DefaultDict, List, Tuple  # type hints


def two_sum_all_pairs(nums: List[int], target: int) -> List[Tuple[int, int]]:
    """Return every index pair (i < j) with nums[i] + nums[j] == target. O(n + pairs)."""
    seen: DefaultDict[int, List[int]] = defaultdict(list)  # value -> indices seen so far
    pairs: List[Tuple[int, int]] = []  # output
    for j, value in enumerate(nums):  # walk once
        for i in seen[target - value]:  # every earlier partner
            pairs.append((i, j))  # earlier index first
        seen[value].append(j)  # remember current value
    return pairs


print(two_sum_all_pairs([3, 3, 3], 6))  # duplicates produce all three pairs
# Output: [(0, 1), (0, 2), (1, 2)]
print(two_sum_all_pairs([-3, 4, 3, 90], 0))  # negatives work
# Output: [(0, 2)]
print(two_sum_all_pairs([], 5))  # empty input
# Output: []
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
def two_sum(nums, target):
    seen = {}
    for i, v in enumerate(nums):
        if target - v in seen:
            return seen[target - v], i
        seen[v] = i
```
```javascript
// JavaScript
function twoSum(nums, target) {
  const seen = new Map();
  for (let i = 0; i < nums.length; i++) {
    const need = target - nums[i];
    if (seen.has(need)) return [seen.get(need), i];
    seen.set(nums[i], i);
  }
}
```

Key differences: the algorithm is identical. Python returns a tuple and implicitly returns `None`; JS returns an array and `undefined`. Python's `enumerate` replaces the manual index loop. Python's dict is the hash map; JS needs `Map` for non-string keys.

---

## 🟠 FastAPI Connection
Expose "find a pair" as a POST endpoint. Return 404 when no pair exists and limit the input size so a client cannot force heavy work.

```python
# FastAPI: two-sum endpoint (pip install fastapi)
from fastapi import FastAPI, HTTPException  # framework + errors
from pydantic import BaseModel, Field  # validation

app: FastAPI = FastAPI()  # create app


class TwoSumRequest(BaseModel):  # request body
    nums: list[int] = Field(max_length=100_000)  # cap the size
    target: int  # wanted sum


@app.post("/two-sum")  # POST /two-sum
def solve(req: TwoSumRequest) -> dict[str, list[int]]:
    seen: dict[int, int] = {}  # value -> index
    for i, v in enumerate(req.nums):
        if req.target - v in seen:
            return {"indices": [seen[req.target - v], i]}  # found
        seen[v] = i
    raise HTTPException(status_code=404, detail="no pair found")  # none exists
```

Not run as a server here; the algorithm is verified in `main.py`.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using the same element twice
✅ Correct: check the dictionary BEFORE inserting the current value, so `[5]` with target `10` does not match itself.

```python
# Wrong: insert first, then look up
seen = {}
for i, v in enumerate([5]):
    seen[v] = i
    if 10 - v in seen: print("match with itself")   # prints, but is wrong
# Right: look up first, insert after (as in two_sum)
```

❌ Mistake 2: Building the whole dict first and breaking with duplicates
✅ Correct: with `[3, 3]` and target 6, `{v: i for i, v in enumerate(nums)}` keeps only the last index (`{3: 1}`), so a pair search over it loses the first 3. The single-pass method avoids this.

❌ Mistake 3: Returning values when indices were asked (or the reverse)
✅ Correct: read the problem; `list.index(x)` also returns only the first match.

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
nums = [3, 3]
print(nums.index(3))
print({v: i for i, v in enumerate(nums)})
print([(i, j) for i in range(2) for j in range(2) if nums[i] + nums[j] == 6 and i != j])
```

**Answer**:
```
0
{3: 1}
[(0, 1), (1, 0)]
```
`list.index` returns the first match only. A dict comprehension overwrites the earlier key, leaving index 1. Without `j > i` the nested loop counts each pair twice, once per order. The one-pass hash map approach returns `(0, 1)` correctly.

---

## ⚫ Interview Questions + Answers

Q1: What are the time and space complexities of each approach?
A1: Brute force O(n^2) time, O(1) space. Hash map O(n) time, O(n) space. Sort + two pointers O(n log n) time, O(1) extra space but it loses original indices unless you keep them.

Q2: Why does the hash map approach handle duplicates like `[3, 3]`?
A2: When the second 3 arrives, the first 3 is already stored, so the complement 3 is found before the second one is inserted.

Q3: How do you return the values instead of indices?
A3: Return `(need, value)` instead of the indices; with sorted input, two pointers needs no extra memory.

Q4: What if the array is sorted?
A4: Use two pointers from both ends: sum too small, move left up; too large, move right down. O(n) time and O(1) space.

Q5: How do you extend this to 3Sum?
A5: Sort, fix one element, and run two-pointer two-sum on the rest, skipping duplicates: O(n^2).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Input is unsorted and you need indices
- You can afford O(n) extra memory
- Many lookups of "does a complement exist?"

❌ Avoid when:
- Memory is tight and data is sorted (two pointers is better)
- The list is tiny (brute force is fine and simpler)
- You need all k-sum combinations (different technique)

---

## 📊 Visual Diagram

```
 nums = [2, 7, 11, 15], target = 9

 i=0 v=2  need=7   seen={}        -> store  seen={2:0}
 i=1 v=7  need=2   2 in seen!     -> return (0, 1)

 seen: value ──► index          lookup need = target - v   (O(1))
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Complement | `target - value` | target में से value घटाकर बचा हिस्सा |
| Hash map | Key-value store with O(1) lookup | तेज़ lookup वाला key-value store |
| Brute force | Try every possibility | हर संभावना आज़माना |
| Two pointers | Move indices from both ends | दोनों सिरों से indices चलाना |
| Time-space trade-off | Use memory to save time | memory देकर समय बचाना |
| Index | Position in a list | list में स्थान |

---

## ⚡ 3-Line Summary
English: Store each value's index in a dict and look up `target - value` as you scan, giving O(n) time. Check before inserting so an element is never paired with itself. Use two pointers if the data is sorted and memory matters.
Hindi: Scan करते समय हर value का index dict में रखें और `target - value` को खोजें, इससे O(n) समय लगता है। Insert से पहले check करें ताकि कोई element खुद से pair न हो। Data sorted हो और memory मायने रखे तो two pointers इस्तेमाल करें।

---

## ➡️ Next Topic
**460. Valid Parentheses** — use a stack to check that brackets open and close in the right order.
