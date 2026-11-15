---

# 467. Count Word Frequency
# हिंदी में: शब्दों की गिनती (Word Frequency)

Full runnable solution (tokenizer, dict, defaultdict, Counter, top-n, tests): `main.py`. Run: `python3 main.py`.

---

## 🔵 Simple Definition (English)
Count how many times each word appears in a text. The standard answer is a dictionary mapping `word -> count`, or `collections.Counter` which does the same in one line.

## 🔵 सरल परिभाषा (Hindi)
Text में हर शब्द कितनी बार आया, यह गिनना है। मानक तरीका dictionary `शब्द -> गिनती` है, या `collections.Counter` जो यही एक line में कर देता है।

---

## 🔴 Problem it Solves
Search engines, spam filters, tag clouds and AI text pipelines (TF-IDF, bag of words) all start with word counts. Looking up and updating a count must be O(1), which is exactly what a hash map gives.

## 🔴 यह क्यों बना? (Hindi)
Search engine, spam filter, tag cloud और AI text pipelines (TF-IDF, bag of words) सब की शुरुआत word count से होती है। गिनती देखना और बढ़ाना O(1) होना चाहिए, जो hash map देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Normalise: lowercase the text
Step 2 → Tokenise: split into words (regex removes punctuation)
Step 3 → For each word: count[word] = count.get(word, 0) + 1
Step 4 → To get top n: sort by count descending (Counter.most_common)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → text को lowercase करो
Step 2 → शब्दों में बाँटो (regex से punctuation हटाओ)
Step 3 → हर शब्द के लिए count[word] = count.get(word, 0) + 1
Step 4 → top n के लिए count के हिसाब से घटते क्रम में sort (Counter.most_common)
```

---

## 🟡 Real World Example
A Swiggy review dashboard shows the most common words in 1 lakh reviews ("late", "cold", "tasty"). An AI app counts tokens per document before building a keyword index for RAG.

## 🟡 Real Example Hindi mein
Swiggy review dashboard 1 लाख reviews में सबसे ज़्यादा आने वाले शब्द ("late", "cold", "tasty") दिखाता है। AI app RAG के keyword index से पहले हर document के tokens गिनती है।

---

## 💻 Code Example — Basic
```python
# Basic dict-based word count
text: str = "the cat and the hat and the bat"  # sample text
words: list[str] = text.split()  # split on whitespace
freq: dict[str, int] = {}  # word -> count
for w in words:  # visit each word
    freq[w] = freq.get(w, 0) + 1  # get default 0, then add one
print(freq)  # insertion ordered by first appearance
# Output: {'the': 3, 'cat': 1, 'and': 2, 'hat': 1, 'bat': 1}
best: str = max(freq, key=freq.get)  # word with the highest count
print(best, freq[best])  # most common word
# Output: the 3
```

## 💻 Code Example — Advanced
```python
# Production style: regex tokenizer, Counter, top-n, stopwords
import re  # tokenizing
from collections import Counter  # specialised dict for counting
from typing import Iterable, List, Set, Tuple  # type hints

STOPWORDS: Set[str] = {"the", "and", "a", "is"}  # words we ignore


def tokenize(text: str) -> List[str]:
    """Lowercase words; keep apostrophes, drop other punctuation."""
    return re.findall(r"[a-z0-9']+", text.lower())  # list of tokens


def top_words(text: str, n: int, ignore: Iterable[str] = ()) -> List[Tuple[str, int]]:
    """Return the n most common words (ties keep first-seen order)."""
    skip: Set[str] = set(ignore)  # fast lookups
    counts: Counter[str] = Counter(w for w in tokenize(text) if w not in skip)  # count filtered words
    return counts.most_common(n)  # sorted by count, descending


sample: str = "The cat and the hat. The cat's hat, the END!"  # sample
print(tokenize(sample))  # tokens after cleaning
# Output: ['the', 'cat', 'and', 'the', 'hat', 'the', "cat's", 'hat', 'the', 'end']
print(top_words(sample, 2))  # includes stopwords
# Output: [('the', 4), ('hat', 2)]
print(top_words(sample, 2, ignore=STOPWORDS))  # stopwords removed
# Output: [('hat', 2), ('cat', 1)]
c1, c2 = Counter("aab"), Counter("abc")  # Counters support math
print(c1 + c2, c1 - c2)  # add counts, subtract (drops zero/negative)
# Output: Counter({'a': 3, 'b': 2, 'c': 1}) Counter({'a': 1})
print(Counter()["missing"])  # unknown keys give 0, not KeyError
# Output: 0
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
from collections import Counter
counts = Counter(text.lower().split())
top = counts.most_common(3)
```

```javascript
// JavaScript
const counts = {};
for (const w of text.toLowerCase().split(/\s+/)) {
  counts[w] = (counts[w] || 0) + 1;
}
const top = Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, 3);
// better: use a Map to avoid keys like "constructor" or "__proto__"
```

Key difference: a plain JS object can collide with built-in keys like `constructor`. Python's `dict` and `Counter` have no such problem for string keys.

---

## 🟠 FastAPI Connection
An endpoint that returns word statistics for submitted text. Limit input size so nobody sends 1 GB.

```python
# FastAPI: word stats endpoint (pip install fastapi)
import re  # tokenizer
from collections import Counter  # counting
from fastapi import FastAPI  # app
from pydantic import BaseModel, Field  # validation

app: FastAPI = FastAPI()  # create app


class TextIn(BaseModel):  # request body
    text: str = Field(max_length=10_000)  # reject very large input
    top: int = Field(default=5, ge=1, le=50)  # how many words to return


@app.post("/words")  # POST /words
def words(body: TextIn) -> list[tuple[str, int]]:
    tokens = re.findall(r"[a-z0-9']+", body.text.lower())  # clean tokens
    return Counter(tokens).most_common(body.top)  # [(word, count), ...]
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: KeyError on a new word
```python
# Wrong:
# freq[w] += 1   # KeyError the first time

# Correct:
# freq[w] = freq.get(w, 0) + 1    # or defaultdict(int) / Counter
```

❌ Mistake 2: Ignoring case and punctuation
```python
# Wrong - "The", "the" and "the," are three different words:
print("The the, the".split())   # ['The', 'the,', 'the']

# Correct - lower() then regex tokenizer
```

❌ Mistake 3: Calling `.count()` for every word
```python
# Wrong - O(n^2): words.count(w) scans the whole list each time
# {w: words.count(w) for w in words}

# Correct - one pass with Counter, O(n)
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
from collections import Counter, defaultdict

d = defaultdict(int)
print(d["x"], len(d))
c = Counter()
print(c["x"], len(c))
print(Counter("aabbbc").most_common(2))
print(Counter("ab") == Counter("ba"))
```

**Answer**:
```
0 1
0 0
[('b', 3), ('a', 2)]
True
```
Reading a missing key from `defaultdict` creates the key (length becomes 1). `Counter` returns 0 without creating it (length stays 0). Counters ignore order, so `Counter("ab") == Counter("ba")` is `True`; that is the anagram check.

---

## ⚫ Interview Questions + Answers

Q1: Time complexity of counting words?
A1: O(n) for n words, because each dict update is O(1) on average.

Q2: `Counter.most_common(k)` complexity?
A2: It uses `heapq.nlargest` for small k, so about O(n log k). With no argument it sorts everything: O(n log n).

Q3: dict vs defaultdict vs Counter?
A3: `dict.get(w, 0) + 1` is plain. `defaultdict(int)` removes the `get`. `Counter` adds `most_common`, arithmetic and takes an iterable directly.

Q4: How do you count words in a huge file?
A4: Read line by line and update one Counter, so memory depends on unique words, not file size.

Q5: How do you make it case-insensitive?
A5: Use `text.lower()`, or `str.casefold()` for non-English text.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- You need frequencies, top-k or anagram checks
- Keys are hashable (strings, numbers, tuples)

❌ Avoid when:
- You need fuzzy matching or stemming (use NLP libraries like NLTK/spaCy)
- Counts must be shared across processes (use Redis or a DB)

---

## 📊 Visual Diagram

```
"the cat and the hat"
   |
 lower + regex tokens
   |
 [the, cat, and, the, hat]
   |
 Counter -> { the:2, cat:1, and:1, hat:1 }
   |
 most_common(1) -> [('the', 2)]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Token | One word after splitting | शब्द का टुकड़ा |
| Hash map | Key to value lookup in O(1) | key-value तालिका |
| Counter | dict subclass for counting | गिनती वाला dict |
| Stopword | Very common word you skip | बहुत आम शब्द जिसे छोड़ते हैं |
| Frequency | How often something occurs | आवृत्ति |

---

## ⚡ 3-Line Summary
English: Lowercase, tokenize, then count with `dict.get`, `defaultdict(int)` or `Counter`. Counting is O(n) and `most_common(k)` gives the top words. Prefer `Counter` in real code.
Hindi: Lowercase करो, tokens बनाओ, फिर `dict.get`, `defaultdict(int)` या `Counter` से गिनो। गिनती O(n) है और `most_common(k)` top शब्द देता है। असली code में `Counter` बेहतर है।

---

## ➡️ Next Topic
**468. Remove Duplicates** — remove repeated items while keeping order.
