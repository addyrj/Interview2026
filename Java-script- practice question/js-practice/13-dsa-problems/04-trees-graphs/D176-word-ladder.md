---

# D176. Word Ladder
# Category: DSA — Trees & Graphs
# Difficulty: ⭐⭐⭐ Hard | LeetCode #127 | Asked: Amazon, Google, Meta, Microsoft, Uber

---

## ❓ Problem
Given `beginWord`, `endWord` and a `wordList`, return the number of words in the shortest transformation sequence from `beginWord` to `endWord`, changing one letter at a time, where every intermediate word must be in `wordList`. Return 0 if none exists.

```
beginWord = "hit", endWord = "cog"
wordList = ["hot","dot","dog","lot","log","cog"]

hit -> hot -> dot -> dog -> cog   => 5 words

If "cog" is not in the list -> 0
```

---

## 💡 Quick Concept (2 lines only)
Words are nodes; two words are connected if they differ by one letter. Shortest path in an unweighted graph = BFS.
हिंदी: words = nodes, एक अक्षर का फ़र्क = edge; shortest path के लिए BFS।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1 (Brute force-ish): BFS comparing against every word in the list
// Time: O(N^2 * L) | Space: O(N)
// ============================================
function ladderLengthBrute(beginWord, endWord, wordList) {
  const diffOne = (a, b) => {                     // do a and b differ by exactly one letter?
    let d = 0;
    for (let i = 0; i < a.length; i++) if (a[i] !== b[i] && ++d > 1) return false;
    return d === 1;
  };
  const words = new Set(wordList);                // remaining unvisited words
  if (!words.has(endWord)) return 0;              // target unreachable
  let queue = [beginWord], steps = 1;             // level-by-level BFS
  while (queue.length) {
    const next = [];
    for (const w of queue) {
      if (w === endWord) return steps;            // reached target
      for (const cand of [...words]) {            // scan entire list
        if (diffOne(w, cand)) { words.delete(cand); next.push(cand); } // visit once
      }
    }
    queue = next;
    steps++;                                      // next level
  }
  return 0;
}

// ============================================
// APPROACH 2: BFS generating all 26*L neighbours (Optimal-ish)
// Time: O(N * L^2 * 26) | Space: O(N * L)
// ============================================
function ladderLength(beginWord, endWord, wordList) {
  const dict = new Set(wordList);                 // O(1) lookup
  if (!dict.has(endWord)) return 0;               // impossible
  const queue = [[beginWord, 1]];                 // [word, length so far]
  const seen = new Set([beginWord]);              // avoid revisiting
  let head = 0;                                   // index pointer instead of shift
  while (head < queue.length) {
    const [word, steps] = queue[head++];          // next word
    if (word === endWord) return steps;           // BFS: first hit is shortest
    for (let i = 0; i < word.length; i++) {
      for (let c = 97; c <= 122; c++) {           // 'a'..'z'
        const next = word.slice(0, i) + String.fromCharCode(c) + word.slice(i + 1); // change one letter
        if (dict.has(next) && !seen.has(next)) {  // valid unseen word
          seen.add(next);                         // mark on enqueue
          queue.push([next, steps + 1]);
        }
      }
    }
  }
  return 0;                                       // no path
}

// ============================================
// APPROACH 3: Bidirectional BFS (fastest in practice)
// Time: ~O(N * L^2 * 26) but explores far fewer nodes | Space: O(N * L)
// ============================================
function ladderLengthBi(beginWord, endWord, wordList) {
  const dict = new Set(wordList);
  if (!dict.has(endWord)) return 0;
  let front = new Set([beginWord]), back = new Set([endWord]); // two frontiers
  let steps = 1;
  while (front.size && back.size) {
    if (front.size > back.size) [front, back] = [back, front]; // expand smaller side
    const next = new Set();
    for (const word of front) {
      for (let i = 0; i < word.length; i++) {
        for (let c = 97; c <= 122; c++) {
          const nw = word.slice(0, i) + String.fromCharCode(c) + word.slice(i + 1);
          if (back.has(nw)) return steps + 1;     // frontiers meet
          if (dict.has(nw)) { dict.delete(nw); next.add(nw); } // visit once
        }
      }
    }
    front = next;
    steps++;
  }
  return 0;
}

// ============================================
// TEST CASES
// ============================================
const list = ["hot", "dot", "dog", "lot", "log", "cog"];
console.log(ladderLength("hit", "cog", list));                   // 5
console.log(ladderLength("hit", "cog", ["hot", "dot", "dog", "lot", "log"])); // 0
console.log(ladderLengthBi("hit", "cog", list));                 // 5
console.log(ladderLengthBi("hit", "cog", ["hot", "dot", "dog", "lot", "log"])); // 0
console.log(ladderLengthBrute("hit", "cog", list));              // 5
console.log(ladderLength("a", "c", ["a", "b", "c"]));            // 2
console.log(ladderLength("hot", "dog", ["hot", "dog"]));         // 0
```

---

## 🔍 Why It Works
Every move changes exactly one letter, so each move is an edge of weight 1. BFS explores words in increasing distance from `beginWord`, so the first time it reaches `endWord` is via the shortest sequence. Marking words visited prevents cycles and repeated work.
हिंदी: हर move का cost 1 है, इसलिए BFS में पहली बार endWord मिलना = shortest।

---

## 📊 Complexity

N = words, L = word length.

| Approach | Time | Space |
|---|---|---|
| Compare with all words | O(N^2 * L) | O(N) |
| Generate 26*L neighbours | O(N * L^2 * 26) | O(N * L) |
| Bidirectional BFS | same bound, much faster in practice | O(N * L) |

---

## ⚡ Variations

```javascript
// VARIANT 1: Wildcard buckets "h*t" -> [hot, hit]: precompute graph to skip the 26 loop
function ladderLengthBuckets(beginWord, endWord, wordList) {
  const buckets = new Map();                      // pattern -> words
  for (const w of [beginWord, ...wordList]) {
    for (let i = 0; i < w.length; i++) {
      const key = w.slice(0, i) + "*" + w.slice(i + 1); // e.g. "h*t"
      if (!buckets.has(key)) buckets.set(key, []);
      buckets.get(key).push(w);
    }
  }
  const queue = [[beginWord, 1]], seen = new Set([beginWord]);
  for (let h = 0; h < queue.length; h++) {
    const [w, d] = queue[h];
    if (w === endWord) return d;
    for (let i = 0; i < w.length; i++) {
      for (const nb of buckets.get(w.slice(0, i) + "*" + w.slice(i + 1)) || []) {
        if (!seen.has(nb)) { seen.add(nb); queue.push([nb, d + 1]); }
      }
    }
  }
  return 0;
}
console.log(ladderLengthBuckets("hit", "cog", list));            // 5

// VARIANT 2: Word Ladder II (LeetCode #126) — return all shortest paths (BFS + backtracking)
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: not checking endWord in wordList first (must be present)
// ❌ Wrong: DFS — finds a path, not the shortest; exponential
// ❌ Wrong: counting transformations instead of words (answer counts begin and end words)
// ❌ Wrong: using array.shift() + includes() on a list — O(N) each; use Set / index pointer
```

---

## 🎯 Interview Tip
Say: "Shortest path in an implicit unweighted graph -> BFS. I generate neighbours by changing one letter and look them up in a Set." Then offer bidirectional BFS as the optimization.

---

## 🔗 Related Problems
→ D175 (Rotting Oranges) | D167 (Level Order) | D172 (Number of Islands) | D174 (Course Schedule)
