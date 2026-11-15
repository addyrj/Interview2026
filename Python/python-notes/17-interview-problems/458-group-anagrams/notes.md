---

# 458. Group Anagrams
# हिंदी में: Anagrams को group करना (एक ही अक्षरों वाले शब्द)

Runnable solution with asserts: `main.py` in this folder (`python3 main.py` prints `[['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]` and `All group-anagrams tests passed`, verified on Python 3.13.3).

---

## 🔵 Simple Definition (English)
Two words are anagrams if they use exactly the same letters the same number of times (`eat`, `tea`, `ate`). The task: given a list of words, group together the ones that are anagrams of each other.

## 🔵 सरल परिभाषा (Hindi)
दो शब्द anagram होते हैं अगर उनमें बिल्कुल वही अक्षर उतनी ही बार हों (`eat`, `tea`, `ate`)। Task: शब्दों की list में से एक-दूसरे के anagram शब्दों को एक group में रखना।

---

## 🔴 Problem it Solves
Comparing every word with every other word is O(n^2 x k). The trick is to give all anagrams the same "signature" (key) so a dictionary groups them in one pass. This hashing-by-canonical-form idea is used in search, spell checkers, deduplication and log grouping.

## 🔴 यह क्यों बना? (Hindi)
हर शब्द को हर दूसरे शब्द से मिलाना O(n^2 x k) है। चाल यह है कि सभी anagrams को एक ही "signature" (key) दो, ताकि dictionary एक ही pass में उन्हें group कर दे। Canonical form से hashing का यही idea search, spell checker, deduplication और log grouping में काम आता है।

---

## 🟢 How it Works — Step by Step

```
Sorted-key approach: O(n * k log k)
Step 1 → groups = defaultdict(list)
Step 2 → For each word compute key = "".join(sorted(word))   ("eat" -> "aet")
Step 3 → groups[key].append(word)
Step 4 → Return list(groups.values())

Count-key approach: O(n * k)
Step 1 → counts = [0] * 26 ; counts[ord(ch) - ord('a')] += 1 for every letter
Step 2 → key = tuple(counts) (lists are unhashable, tuples are fine)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Sorted-key तरीका: O(n * k log k)
Step 1 → groups = defaultdict(list)
Step 2 → हर शब्द की key = "".join(sorted(word))   ("eat" -> "aet")
Step 3 → groups[key].append(word)
Step 4 → list(groups.values()) लौटाओ

Count-key तरीका: O(n * k)
Step 1 → counts = [0] * 26 ; हर अक्षर के लिए counts[ord(ch) - ord('a')] += 1
Step 2 → key = tuple(counts) (list hashable नहीं, tuple है)
```

---

## 🟡 Real World Example
A log-analysis service at an Indian fintech groups error messages whose words are the same set but in different order, so "card declined bank" and "bank card declined" land in one bucket. The same "canonical key" idea groups duplicate product listings on an e-commerce site (same attributes, different order).

## 🟡 Real Example Hindi mein
किसी fintech की log-analysis service उन error messages को एक bucket में रखती है जिनमें शब्द वही हैं पर क्रम अलग है, जैसे "card declined bank" और "bank card declined"। वही "canonical key" idea e-commerce साइट पर duplicate product listings (वही attributes, अलग क्रम) को group करता है।

---

## 💻 Code Example — Basic
```python
# Basic: group anagrams with a sorted-letters key
from collections import defaultdict  # dict that creates missing lists automatically


def group_anagrams(words: list[str]) -> list[list[str]]:  # returns groups of words
    groups: defaultdict[str, list[str]] = defaultdict(list)  # key -> words
    for word in words:  # one pass
        key: str = "".join(sorted(word))  # 'eat' and 'tea' both become 'aet'
        groups[key].append(word)  # file the word under its key
    return list(groups.values())  # dicts keep insertion order


print(group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]))  # classic example
# Output: [['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]
print(group_anagrams([]))  # empty input
# Output: []
print(group_anagrams([""]))  # an empty string forms its own group
# Output: [['']]
```

## 💻 Code Example — Advanced
```python
# From main.py: 26-count key (O(n*k)) and order-independent test helper
from collections import defaultdict  # auto-creating lists
from typing import DefaultDict, List, Tuple  # type hints


def group_anagrams_count(words: List[str]) -> List[List[str]]:
    """Key = tuple of 26 letter counts. Assumes lowercase a-z only."""
    groups: DefaultDict[Tuple[int, ...], List[str]] = defaultdict(list)
    for word in words:
        counts: List[int] = [0] * 26  # one slot per letter
        for ch in word:
            counts[ord(ch) - ord("a")] += 1  # count each letter
        groups[tuple(counts)].append(word)  # tuples are hashable, lists are not
    return list(groups.values())


def normalise(groups: List[List[str]]) -> List[List[str]]:
    return sorted(sorted(g) for g in groups)  # sort inside and across groups


words: List[str] = ["eat", "tea", "tan", "ate", "nat", "bat"]
print(normalise(group_anagrams_count(words)))  # order-independent view
# Output: [['ate', 'eat', 'tea'], ['bat'], ['nat', 'tan']]
print(normalise(group_anagrams_count(["a", "a"])))  # duplicates are kept
# Output: [['a', 'a']]
print(len(group_anagrams_count(["abc", "bca", "cab", "xyz"])))  # two groups
# Output: 2
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
from collections import defaultdict
groups = defaultdict(list)
for w in words:
    groups["".join(sorted(w))].append(w)
```
```javascript
// JavaScript
const groups = new Map();
for (const w of words) {
  const key = [...w].sort().join("");           // sort letters
  if (!groups.has(key)) groups.set(key, []);    // no defaultdict in JS
  groups.get(key).push(w);
}
```

Key differences: Python's `defaultdict(list)` removes the "key missing" check; JS needs `Map` plus `has`/`set`. Python's `sorted(word)` returns a sorted list of characters; JS `sort()` mutates in place and, without a comparator, sorts by UTF-16 code units. Python tuples work as dict keys; in JS you would have to stringify the counts array.

---

## 🟠 FastAPI Connection
A "group by canonical key" endpoint is common for deduplicating tags or grouping search terms. Validate the list size before processing.

```python
# FastAPI: group anagrams endpoint (pip install fastapi)
from collections import defaultdict  # grouping

from fastapi import FastAPI  # framework
from pydantic import BaseModel, Field  # request validation

app: FastAPI = FastAPI()  # create app


class Words(BaseModel):  # request body
    words: list[str] = Field(max_length=1000)  # cap the list size


@app.post("/anagrams")  # POST /anagrams
def anagrams(body: Words) -> list[list[str]]:
    groups: defaultdict[str, list[str]] = defaultdict(list)  # key -> words
    for w in body.words:
        groups["".join(sorted(w))].append(w)  # sorted-letters key
    return list(groups.values())  # JSON list of lists
```

Not run as a server here; the grouping logic is verified in `main.py`.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using a list as a dictionary key
✅ Correct: use a tuple or a string.

```python
# Wrong
d = {}
d[["a", "e", "t"]] = 1          # TypeError: unhashable type: 'list'
# Right
d[tuple(["a", "e", "t"])] = 1   # or "".join(...)
```

❌ Mistake 2: Comparing `sorted(a) == sorted(b)` for every pair
✅ Correct: compute one key per word and group in a dict (O(n) lookups, not O(n^2) comparisons).

❌ Mistake 3: The 26-slot count key with uppercase, digits or Unicode
✅ Correct: normalise with `.lower()` and filter, or use `tuple(sorted(Counter(word).items()))` / the sorted-string key, which works for any characters.

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
d = {}
try:
    d[["a"]] = 1
except TypeError as e:
    print(e)
d[tuple(["a"])] = 1
print(d)
print(sorted("eat") == sorted("tea"), "".join(sorted("eat")))
```

**Answer**:
```
unhashable type: 'list'
{('a',): 1}
True aet
```
Mutable lists cannot be dictionary keys because their hash could change; tuples are immutable and hashable. `sorted("eat")` returns the list `['a', 'e', 't']`, so you join it back into a string to build a key.

---

## ⚫ Interview Questions + Answers

Q1: Time and space complexity of the sorted-key solution?
A1: O(n x k log k) time (n words of length k, sorting each) and O(n x k) space for the groups.

Q2: Can you do better than sorting?
A2: Yes. A 26-count tuple key gives O(n x k) time, but it only works for a fixed alphabet.

Q3: Why `defaultdict(list)` instead of a plain dict?
A3: It creates an empty list on first access of a missing key, so you avoid the `if key not in d` check.

Q4: Does the output order matter?
A4: Since Python 3.7 dicts keep insertion order, so groups appear in order of first occurrence. If an interviewer says "any order", sort or normalise in tests.

Q5: How do you handle Unicode words?
A5: Normalise first (`unicodedata.normalize("NFC", w).casefold()`) and use the sorted-string key; the fixed 26-slot array breaks for non-ASCII input.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You must group items sharing a canonical form
- The alphabet is small and fixed (count key) or any text (sorted key)
- You need a single pass with hashing

❌ Avoid when:
- You need "similar" words, not exact anagrams (use edit distance or n-grams)
- Words are extremely long and memory is tight
- The key is not stable (mutable keys)

---

## 📊 Visual Diagram

```
 eat ──sort──► aet ┐
 tea ──sort──► aet ├──► groups["aet"] = [eat, tea, ate]
 ate ──sort──► aet ┘
 tan ──sort──► ant ┐
 nat ──sort──► ant ┴──► groups["ant"] = [tan, nat]
 bat ──sort──► abt ────► groups["abt"] = [bat]

 result = list(groups.values())
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Anagram | Same letters, different order | वही अक्षर, अलग क्रम |
| Canonical key | One shared signature | साझा पहचान (key) |
| defaultdict | Dict with a default factory | default value बनाने वाला dict |
| Hashable | Usable as a dict key | dict key बन सकने वाला |
| Tuple | Immutable sequence | अपरिवर्तनीय sequence |
| Grouping | Bucketing by key | key के आधार पर बाँटना |

---

## ⚡ 3-Line Summary
English: Give every anagram the same key (sorted letters or a count tuple) and group with `defaultdict(list)`. Sorted keys cost O(n k log k); count keys cost O(n k) for a fixed alphabet. Lists cannot be dict keys, tuples can.
Hindi: हर anagram को एक ही key (sorted letters या count tuple) दें और `defaultdict(list)` से group करें। Sorted key का खर्च O(n k log k) है; fixed alphabet पर count key O(n k) है। List dict key नहीं बन सकती, tuple बन सकता है।

---

## ➡️ Next Topic
**459. Two Sum Problem** — find a pair adding to a target using a hash map in one pass.
