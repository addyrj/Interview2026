---

# D068. Word Ladder
# Category: DSA — Graphs
# Difficulty: ⭐⭐⭐ Hard | LeetCode #127

---

## ❓ Problem
Given `beginWord`, `endWord` and a `wordList`, return the number of words in the shortest transformation sequence from `beginWord` to `endWord` where each step changes exactly one letter and every intermediate word must be in `wordList`. Return `0` if no such sequence exists.

```
Input:  begin = "hit", end = "cog", words = ["hot","dot","dog","lot","log","cog"]
Output: 5   (hit -> hot -> dot -> dog -> cog)
```

---

## 💡 Quick Concept (2 lines only)
Words are nodes; two words are connected if they differ by one letter. Shortest path in an unweighted graph = BFS. Generate neighbours by swapping each position with `a..z` and checking a set.
हिंदी: हर word एक node है, एक अक्षर बदलने पर edge; सबसे छोटा रास्ता चाहिए तो BFS चलाओ।

---

## ✅ Solution

```python
from collections import deque, defaultdict   # queue + pattern buckets
import string                                # string.ascii_lowercase


# ============================================
# APPROACH 1: Brute force — compare every pair of words to find neighbours during BFS
# O(N^2 * L) time (N words of length L)
# ============================================
def ladder_brute(begin: str, end: str, words: list[str]) -> int:
    pool = set(words)                        # allowed words
    if end not in pool:                      # target unreachable
        return 0                             # no ladder
    q = deque([(begin, 1)])                  # (word, length of path so far)
    seen = {begin}                           # visited words
    while q:                                 # BFS
        word, dist = q.popleft()             # current word
        if word == end:                      # reached target
            return dist                      # shortest length
        for other in pool:                   # try EVERY word as a neighbour
            if other in seen:                # already visited
                continue                     # skip
            if sum(a != b for a, b in zip(word, other)) == 1:   # differ by one letter
                seen.add(other)              # mark visited
                q.append((other, dist + 1))  # explore next
    return 0                                 # not reachable


# ============================================
# APPROACH 2: BFS with 26-letter neighbour generation ✅ PREFERRED
# O(N * L * 26) time, O(N * L) space
# ============================================
def ladder_length(begin: str, end: str, words: list[str]) -> int:
    pool = set(words)                        # O(1) membership
    if end not in pool:                      # target missing
        return 0                             # impossible
    q = deque([(begin, 1)])                  # (word, path length)
    pool.discard(begin)                      # begin must not be revisited
    while q:                                 # BFS
        word, dist = q.popleft()             # current word
        if word == end:                      # done
            return dist                      # shortest path length
        for i in range(len(word)):           # each position
            for ch in string.ascii_lowercase:   # each replacement letter
                nxt = word[:i] + ch + word[i + 1:]   # candidate word
                if nxt in pool:              # valid unvisited word
                    pool.remove(nxt)         # remove = mark visited
                    q.append((nxt, dist + 1))   # explore next
    return 0                                 # no ladder


# ============================================
# TEST CASES
# ============================================
w = ["hot", "dot", "dog", "lot", "log", "cog"]   # sample word list
print(ladder_brute("hit", "cog", w))         # Expected: 5
print(ladder_length("hit", "cog", w))        # Expected: 5
print(ladder_length("hit", "cog", ["hot", "dot", "dog", "lot", "log"]))   # Expected: 0
print(ladder_length("a", "c", ["a", "b", "c"]))   # Expected: 2
print(ladder_length("hot", "hot", ["hot"]))  # Expected: 1
```

---

## 🔍 Why It Works
```
hit -> hot -> dot -> dog -> cog     (5 words)
        \-> lot -> log -> cog
BFS reaches cog first through the shortest of these paths.
```
हिंदी: BFS level-by-level चलता है, इसलिए endWord जिस level पर पहली बार मिले वही सबसे छोटा रास्ता है।

---

## 📊 Complexity
```
Brute pairs:     Time O(N^2 * L)  | Space O(N)
26-letter BFS:   Time O(N * L * 26) | Space O(N * L) ← preferred
```

---

## ⚡ Variations

```python
# Alternative: wildcard buckets "h*t" -> [hot, hit]; neighbours without trying 26 letters
def ladder_buckets(begin: str, end: str, words: list[str]) -> int:
    if end not in words:                     # target missing
        return 0                             # impossible
    buckets: dict[str, list[str]] = defaultdict(list)   # pattern -> words
    for word in set(words) | {begin}:        # include the start word
        for i in range(len(word)):           # each position
            buckets[word[:i] + "*" + word[i + 1:]].append(word)   # register pattern
    q = deque([(begin, 1)])                  # BFS queue
    seen = {begin}                           # visited words
    while q:                                 # BFS
        word, dist = q.popleft()             # current word
        if word == end:                      # reached target
            return dist                      # length
        for i in range(len(word)):           # each position
            for nb in buckets[word[:i] + "*" + word[i + 1:]]:   # words sharing the pattern
                if nb not in seen:           # unvisited
                    seen.add(nb)             # mark
                    q.append((nb, dist + 1)) # explore
    return 0                                 # unreachable


print(ladder_buckets("hit", "cog", w))       # Expected: 5

# VARIANT 1: Bidirectional BFS -> expand from both ends, meet in the middle (much faster)
# VARIANT 2: Word Ladder II -> return all shortest paths (BFS for distances + DFS backtracking)
# VARIANT 3: Minimum Genetic Mutation -> same pattern, alphabet "ACGT"
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: using a list for the word pool -> `in` is O(N) and the solution times out
# ❌ Wrong: returning the number of EDGES (4) instead of number of WORDS (5)
# ❌ Wrong: forgetting to mark visited when enqueuing -> duplicates and exponential work

# ✅ Correct: set for the pool, remove words as you enqueue them, start the count at 1
```

---

## 🎯 Interview Tip
Say: "Shortest transformation in an unweighted graph means BFS; I generate neighbours by changing each letter and look them up in a set." Mention bidirectional BFS as the optimisation.

---

## 🔗 Related Problems
→ D067 (Rotting Oranges) | D070 (Shortest Path in Binary Matrix) | D066 (Course Schedule)
