---

# 475. Implement Trie
# हिंदी में: Trie बनाना (Prefix Tree)

Runnable solution with tests: [main.py](./main.py) (run: `python main.py`, verified on Python 3.13).

---

## 🔵 Simple Definition (English)
A trie is a tree where each edge is a character. Words that share a prefix share the same path from the root. A flag on a node marks "a word ends here".

## 🔵 सरल परिभाषा (Hindi)
Trie एक tree है जिसमें हर edge एक अक्षर है। जिन शब्दों का prefix एक जैसा है, वे root से एक ही रास्ता साझा करते हैं। Node पर एक flag बताता है कि "यहाँ एक शब्द खत्म होता है"।

---

## 🔴 Problem it Solves
Checking "does any word start with `ca`?" in a list of a million words costs O(n * L). A hash set answers exact matches fast but cannot do prefix queries. A trie answers `search`, `starts_with`, and autocomplete in O(L), where L is the length of the word, regardless of how many words are stored.

## 🔴 यह क्यों बना? (Hindi)
दस लाख शब्दों की list में "क्या कोई शब्द `ca` से शुरू होता है?" जाँचना O(n * L) है। Hash set exact match तो तेज़ करता है पर prefix query नहीं कर सकता। Trie `search`, `starts_with` और autocomplete O(L) में कर देता है, जहाँ L शब्द की लंबाई है, चाहे कितने भी शब्द रखे हों।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Root is an empty node with children = {} and is_end = False
Step 2 → insert("car"): for each char, go to child[char] (create if missing)
Step 3 → After the last char set is_end = True
Step 4 → search(w): walk the path; True only if it exists AND is_end is True
Step 5 → starts_with(p): walk the path; True if it exists (is_end not needed)
Step 6 → autocomplete(p): walk to the prefix node, then DFS and collect words
Step 7 → delete(w): clear is_end, then prune nodes that have no children and no word
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Root खाली node है: children = {} और is_end = False
Step 2 → insert("car"): हर अक्षर के लिए child[char] पर जाओ (न हो तो बनाओ)
Step 3 → आखिरी अक्षर के बाद is_end = True करो
Step 4 → search(w): रास्ता चलो; True तभी जब रास्ता हो और is_end True हो
Step 5 → starts_with(p): रास्ता चलो; मौजूद हो तो True (is_end ज़रूरी नहीं)
Step 6 → autocomplete(p): prefix node तक जाओ, फिर DFS करके शब्द इकट्ठे करो
Step 7 → delete(w): is_end साफ़ करो, फिर बिना children और बिना word वाले nodes हटाओ
```

---

## 🟡 Real World Example
Google/Swiggy search-bar suggestions ("pizz" -> "pizza", "pizza hut"), phone-keyboard autocomplete, spell checkers, IP routing tables (longest prefix match), and blocklists of URL prefixes. A FastAPI search endpoint can keep a trie of restaurant names in memory for instant suggestions.

## 🟡 Real Example Hindi mein
Google/Swiggy search-bar के सुझाव ("pizz" -> "pizza", "pizza hut"), phone keyboard autocomplete, spell checker, IP routing table (longest prefix match) और URL prefix blocklists। FastAPI search endpoint रेस्तराँ के नामों का trie memory में रखकर तुरंत सुझाव दे सकता है।

---

## 💻 Code Example — Basic
```python
# Basic trie using nested dicts
END: str = "$"                                 # special key marking end of a word
root: dict = {}                                # the trie is just a dict of dicts

def insert(word: str) -> None:
    node: dict = root                          # start at the root
    for ch in word:                            # for each letter
        node = node.setdefault(ch, {})         # go down, creating the branch if needed
    node[END] = True                           # mark a word end

def search(word: str) -> bool:
    node: dict = root                          # start at the root
    for ch in word:                            # follow each letter
        if ch not in node:                     # path breaks -> not present
            return False
        node = node[ch]                        # go deeper
    return END in node                         # must be a complete word

for w in ("car", "card", "cat"):               # insert some words
    insert(w)
print(search("car"), search("ca"), search("card"))   # exact checks

# Output:
# True False True
```

## 💻 Code Example — Advanced
```python
# Production style: typed nodes, prefix check, autocomplete (full class + delete in main.py)
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class TrieNode:
    children: dict[str, "TrieNode"] = field(default_factory=dict)   # char -> child
    is_end: bool = False                       # a word ends here


class Trie:
    def __init__(self) -> None:
        self.root = TrieNode()                 # empty root

    def insert(self, word: str) -> None:
        node = self.root                       # start at the root
        for ch in word:                        # walk / build the path
            node = node.children.setdefault(ch, TrieNode())
        node.is_end = True                     # mark the end

    def _walk(self, s: str) -> TrieNode | None:
        node = self.root                       # start at the root
        for ch in s:                           # follow characters
            nxt = node.children.get(ch)        # next node or None
            if nxt is None:
                return None                    # path broke
            node = nxt
        return node                            # node for the full string

    def search(self, word: str) -> bool:
        n = self._walk(word)                   # find the node
        return n is not None and n.is_end      # exists and is a word

    def autocomplete(self, prefix: str, limit: int = 5) -> list[str]:
        start = self._walk(prefix)             # jump to the prefix node
        out: list[str] = []                    # results
        if start is None:
            return out                         # nothing starts with prefix
        stack: list[tuple[TrieNode, str]] = [(start, prefix)]   # iterative DFS
        while stack and len(out) < limit:      # stop at the limit
            node, path = stack.pop()           # take one node
            if node.is_end:
                out.append(path)               # a complete word
            for ch in sorted(node.children, reverse=True):   # reversed so pop gives A-Z
                stack.append((node.children[ch], path + ch))
        return out


t = Trie()
for w in ["car", "card", "care", "cat", "dog"]:
    t.insert(w)                                # build the trie
print(t.search("car"), t.search("ca"))         # exact
print(t.autocomplete("car"))                   # suggestions
print(t.autocomplete("ca", limit=2))           # limited suggestions
print(t.autocomplete("x"))                     # no match

# Output:
# True False
# ['car', 'card', 'care']
# ['car', 'card']
# []
```

---

## 🟠 JavaScript vs Python Comparison
Same structure; in JS you would use `Map` or a plain object for `children`. Python's `dict.setdefault` is a compact way to "get or create".

```python
# Python way
node = root
for ch in word:
    node = node.setdefault(ch, {})
```
```javascript
// JavaScript way
let node = root;
for (const ch of word) {
  if (!node[ch]) node[ch] = {};
  node = node[ch];
}
```

---

## 🟠 FastAPI Connection
Build the trie once at startup (lifespan) and share it read-only across requests. A search-suggestion endpoint then costs O(L + k) per request.

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query

trie: dict = {}                                  # simplified dict-trie; use the Trie class in real code

@asynccontextmanager
async def lifespan(app: FastAPI):
    for name in ["pizza", "pizza hut", "pasta"]: # load names once (from DB in real life)
        node = trie
        for ch in name:
            node = node.setdefault(ch, {})
        node["$"] = True
    yield                                        # app runs here

app = FastAPI(lifespan=lifespan)

@app.get("/suggest")
def suggest(q: str = Query(min_length=1)) -> list[str]:
    node = trie
    for ch in q:                                 # walk the prefix
        if ch not in node:
            return []
        node = node[ch]
    out: list[str] = []
    def dfs(n: dict, path: str) -> None:         # collect completions
        if "$" in n: out.append(path)
        for ch, child in sorted(n.items()):
            if ch != "$": dfs(child, path + ch)
    dfs(node, q)
    return out[:5]
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `search` returns True for a prefix (forgetting `is_end`).
✅ Correct: check `node.is_end`; only `starts_with` ignores it.

```python
# Wrong
return n is not None          # "ca" would be "found"
# Right
return n is not None and n.is_end
```

❌ Mistake 2: using a fixed array of 26 children for unicode text (breaks on Hindi, emoji, uppercase).
✅ Correct: a `dict` per node handles any character.

❌ Mistake 3: deep recursion on very long words (Python's limit is about 1000).
✅ Correct: iterative loops for insert/search/DFS.

---

## 🧠 Tricky Interview Question
```python
root: dict = {}
for w in ("a", "ab"):
    node = root
    for ch in w:
        node = node.setdefault(ch, {})
    node["$"] = True
print(root)
```
Answer: `{'a': {'$': True, 'b': {'$': True}}}`. "a" is both a complete word and a prefix of "ab", so node `a` has the end marker and a child `b`. This is why `is_end` must be a separate flag, not "has no children".

---

## ⚫ Interview Questions + Answers

Q1: Time and space complexity?
A1: insert/search/starts_with are O(L). Space is O(total characters) in the worst case, less when prefixes are shared.

Q2: Trie vs hash set?
A2: Hash set: O(L) exact lookup (hashing the string), no prefix queries. Trie: exact and prefix queries, sorted traversal, but more memory per character.

Q3: How do you reduce trie memory?
A3: Compress chains into a radix/Patricia tree, use `__slots__`, or store children in arrays for small alphabets.

Q4: How to rank autocomplete results?
A4: Store a frequency/score at word-end nodes, and use a heap (`heapq.nlargest`) while collecting, or cache the top-k at each node.

Q5: How would you implement delete?
A5: Recursively walk down, unset `is_end`, then on the way back prune any child with no children and no `is_end`. See `Trie.delete` in main.py.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Prefix search, autocomplete, spell-check, longest-prefix match
- Many strings share prefixes
- You need sorted iteration over keys

❌ Avoid when:
- You only need exact lookups (set/dict is simpler and lighter)
- The data is huge and memory is tight (use a DB index or a compressed trie)
- Search is fuzzy (use edit distance / search engines)

---

## 📊 Visual Diagram
```
 words: car, card, care, cat, dog

 root
  |-- c
  |    '-- a
  |         |-- r*  (word "car")
  |         |    |-- d*  ("card")
  |         |    '-- e*  ("care")
  |         '-- t*  ("cat")
  '-- d
       '-- o
            '-- g*  ("dog")

 * = is_end True
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Trie | Prefix tree | उपसर्ग वृक्ष |
| Prefix | Starting part of a word | शब्द का शुरुआती भाग |
| is_end | Flag: a word ends at this node | शब्द-समाप्ति चिह्न |
| Autocomplete | Suggest completions of a prefix | स्वतः पूर्ति |
| Radix tree | Compressed trie | संकुचित trie |
| Pruning | Removing unused branches | अनुपयोगी शाखाएँ हटाना |

---

## ⚡ 3-Line Summary
English: A trie stores strings character by character so shared prefixes share nodes.
English: insert, search and prefix checks cost O(length of the word), not O(number of words).
English: Keep a separate end flag, use dict children, and prune on delete.

Hindi: Trie strings को अक्षर-दर-अक्षर रखता है ताकि साझा prefix के nodes साझा हों।
Hindi: insert, search और prefix check शब्द की लंबाई के अनुसार O(L) लेते हैं, शब्दों की संख्या से नहीं।
Hindi: अलग end flag रखो, children के लिए dict इस्तेमाल करो, और delete पर शाखाएँ हटाओ।

---

## ➡️ Next Topic
**476. Implement Decorator** — switching from data structures to Python's function-wrapping superpower.

---
