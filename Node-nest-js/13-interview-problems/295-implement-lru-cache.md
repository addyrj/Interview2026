# 295. Implement LRU Cache
# हिंदी में: LRU Cache खुद बनाना (Implementation)

---

## 🔵 Simple Definition (English)
An **LRU (Least Recently Used) Cache** stores a fixed-size set of key-value pairs; when full, it evicts the item that hasn't been accessed in the longest time. The classic efficient implementation combines a `Map` (for O(1) key lookup) with a doubly linked list (for O(1) reordering on access), giving O(1) `get` and `put`.

## 🔵 सरल परिभाषा (Hindi)
**LRU (Least Recently Used) Cache** एक fixed-size key-value store है; जब full हो जाए, तो वह item evict करता है जो सबसे ज़्यादा समय से access नहीं हुआ। Classic efficient implementation `Map` (O(1) key lookup के लिए) और doubly linked list (O(1) reordering के लिए) combine करता है, जिससे `get` और `put` दोनों O(1) होते हैं।

---

## 🔴 Problem it Solves
Caching speeds up repeated reads by avoiding expensive DB/API calls, but memory is finite — you can't cache everything forever. LRU eviction is the most common strategy because it approximates "keep what's likely to be used again soon" cheaply, based on recency of access, without needing to predict the future.

## 🔴 यह क्यों बना? (Hindi)
Caching repeated reads को fast बनाती है expensive DB/API calls avoid करके, लेकिन memory limited है — सब कुछ हमेशा के लिए cache नहीं कर सकते। LRU eviction सबसे common strategy है क्योंकि यह cheaply "जो फिर से use हो सकता है उसे रखो" approximate करता है, access की recency के आधार पर, future predict किए बिना।

---

## 🟢 How it Works — Step by Step

Step 1 → Maintain a `Map<key, Node>` for O(1) lookup, where each `Node` holds `{key, value, prev, next}` for a doubly linked list.
Step 2 → Maintain `head` (most recently used) and `tail` (least recently used) pointers for the linked list.
Step 3 → `get(key)`: if found in Map, move that node to the head (mark as recently used), return its value; if not found, return -1/undefined.
Step 4 → `put(key, value)`: if key exists, update value and move to head. If new and cache is at capacity, remove the tail node (least recently used) from BOTH the Map and the list before inserting the new node at head.
Step 5 → All "move to head" / "remove tail" operations are O(1) because it's a doubly linked list — no array shifting required.
Step 6 → Map gives O(1) existence check + node reference, linked list gives O(1) reordering — together, O(1) get/put.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `Map<key, Node>` रखो O(1) lookup के लिए, हर `Node` में `{key, value, prev, next}` होता है doubly linked list के लिए।
Step 2 → `head` (सबसे recently used) और `tail` (सबसे least recently used) pointers रखो linked list के लिए।
Step 3 → `get(key)`: Map में मिले तो उस node को head पर move करो (recently used mark), value return करो; न मिले तो -1/undefined return करो।
Step 4 → `put(key, value)`: key already है तो value update करो और head पर move करो। नया key है और cache full है तो tail node (least recently used) को Map और list दोनों से हटाओ नया insert करने से पहले।
Step 5 → "move to head" / "remove tail" सारे operations O(1) हैं क्योंकि doubly linked list है — array shifting नहीं चाहिए।
Step 6 → Map से O(1) existence check + node reference, linked list से O(1) reordering — दोनों मिलकर O(1) get/put।

---

## 🟡 Real World Example
**Amazon's product page caching**: Thousands of distinct product pages are requested, but only a few thousand are "hot" at any moment (trending items, flash sale products). An LRU cache in front of the product-detail database keeps the most recently viewed products in fast memory (Redis with LRU eviction policy, or an in-process LRU cache per instance), automatically evicting stale/cold products to make room — without needing any manual cache invalidation logic.

## 🟡 Real Example Hindi mein
**Amazon का product page caching**: हज़ारों अलग-अलग product pages request होते हैं, लेकिन किसी भी moment पर सिर्फ कुछ हज़ार ही "hot" होते हैं (trending items, flash sale products)। Product-detail database के आगे एक LRU cache सबसे recently viewed products को fast memory में रखता है (Redis LRU eviction policy के साथ, या per-instance in-process LRU cache), stale/cold products को automatically evict करके जगह बनाता है — बिना manual cache invalidation logic के।

---

## 💻 Code Example — Basic

```javascript
// lru-basic.js
// LRU cache using JavaScript's Map, which preserves insertion order — a simpler (slightly less explicit) approach.
// Run: node lru-basic.js

class LRUCache {
  constructor(capacity) {
    this.capacity = capacity;
    // JS Map preserves insertion order; re-inserting a key moves it to the end.
    // We treat "end of Map" as "most recently used".
    this.cache = new Map();
  }

  get(key) {
    if (!this.cache.has(key)) return -1;
    const value = this.cache.get(key);
    // Re-insert to mark as most recently used: delete then set moves it to the end
    this.cache.delete(key);
    this.cache.set(key, value);
    return value;
  }

  put(key, value) {
    if (this.cache.has(key)) {
      this.cache.delete(key); // remove old position
    } else if (this.cache.size >= this.capacity) {
      // Map.keys().next().value gives the FIRST inserted key = least recently used
      const lruKey = this.cache.keys().next().value;
      this.cache.delete(lruKey);
      console.log(`Evicted LRU key: ${lruKey}`);
    }
    this.cache.set(key, value); // insert at the end = most recently used
  }
}

// --- Demo ---
const cache = new LRUCache(3);
cache.put('a', 1);
cache.put('b', 2);
cache.put('c', 3);
console.log(cache.get('a'));  // 1 -> 'a' is now most recently used
cache.put('d', 4);            // cache full -> evicts 'b' (least recently used, since 'a' was just touched)
console.log(cache.get('b'));  // -1 (evicted)
console.log(cache.get('c'));  // 3 (still present)
console.log(cache.get('d'));  // 4
```

## 💻 Code Example — Advanced

```javascript
// lru-advanced.js
// Explicit O(1) LRU cache using Map + doubly linked list — the classic interview-grade implementation.
// This is what you'd write on a whiteboard for "Design LRU Cache" (LeetCode 146).

class Node {
  constructor(key, value) {
    this.key = key;
    this.value = value;
    this.prev = null;
    this.next = null;
  }
}

class LRUCache {
  constructor(capacity) {
    this.capacity = capacity;
    this.map = new Map(); // key -> Node, for O(1) lookup

    // Sentinel head/tail nodes simplify edge cases (empty list, single node) — no null checks needed
    this.head = new Node(null, null); // head.next = most recently used
    this.tail = new Node(null, null); // tail.prev = least recently used
    this.head.next = this.tail;
    this.tail.prev = this.head;
  }

  // Remove a node from its current position in the linked list — O(1)
  _remove(node) {
    node.prev.next = node.next;
    node.next.prev = node.prev;
  }

  // Insert a node right after head (= mark as most recently used) — O(1)
  _insertAtHead(node) {
    node.next = this.head.next;
    node.prev = this.head;
    this.head.next.prev = node;
    this.head.next = node;
  }

  get(key) {
    if (!this.map.has(key)) return -1;
    const node = this.map.get(key);
    this._remove(node);       // take it out of its current position
    this._insertAtHead(node); // and put it back at the front (most recently used)
    return node.value;
  }

  put(key, value) {
    if (this.map.has(key)) {
      const node = this.map.get(key);
      node.value = value;     // update value
      this._remove(node);
      this._insertAtHead(node);
      return;
    }

    if (this.map.size >= this.capacity) {
      // Evict least recently used = node just before tail sentinel
      const lru = this.tail.prev;
      this._remove(lru);
      this.map.delete(lru.key);
    }

    const newNode = new Node(key, value);
    this.map.set(key, newNode);
    this._insertAtHead(newNode);
  }
}

module.exports = { LRUCache };

// --- Demo ---
if (require.main === module) {
  const cache = new LRUCache(2);
  cache.put(1, 'A');
  cache.put(2, 'B');
  console.log(cache.get(1));  // 'A' -> 1 is now most recently used
  cache.put(3, 'C');          // capacity full -> evicts key 2 (least recently used)
  console.log(cache.get(2));  // -1 (evicted)
  cache.put(4, 'D');          // evicts key 1 (now least recently used)
  console.log(cache.get(1));  // -1 (evicted)
  console.log(cache.get(3));  // 'C'
  console.log(cache.get(4));  // 'D'
}
```

---

## 🟠 Express.js Integration

```javascript
// server.js — using the LRU cache to cache expensive DB lookups in an Express API
const express = require('express');
const { LRUCache } = require('./lru-advanced');

const app = express();
const productCache = new LRUCache(500); // keep the 500 most recently viewed products in memory

// Simulated slow DB call
async function fetchProductFromDb(id) {
  await new Promise(r => setTimeout(r, 200)); // simulate 200ms DB latency
  return { id, name: `Product ${id}`, price: 999 };
}

app.get('/products/:id', async (req, res) => {
  const { id } = req.params;

  const cached = productCache.get(id);
  if (cached !== -1) {
    res.set('X-Cache', 'HIT');
    return res.json(cached);
  }

  const product = await fetchProductFromDb(id);
  productCache.put(id, product); // store for next time, evicting LRU item if full
  res.set('X-Cache', 'MISS');
  res.json(product);
});

app.listen(3000, () => console.log('LRU-cached product API on :3000'));
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using a plain object/array and scanning linearly to find/evict the LRU item
✅ Correct: Use Map + doubly linked list for O(1) operations — a naive array-based "find oldest" scan is O(n) per operation

```javascript
// Wrong — O(n) scan every time to find least recently used
let oldest = entries.reduce((a, b) => a.lastUsed < b.lastUsed ? a : b);

// Right — O(1) via tail pointer in doubly linked list
const lru = this.tail.prev;
```

❌ Mistake 2: Forgetting to move a node to the head on `get()`, breaking the "recently used" guarantee
✅ Correct: Every successful `get()` must reposition the accessed node to the front, not just `put()`

```javascript
// Wrong — get() doesn't update recency, so "LRU" eviction becomes effectively random/insertion-order
get(key) {
  return this.map.get(key)?.value ?? -1; // no reordering!
}

// Right
get(key) {
  const node = this.map.get(key);
  if (!node) return -1;
  this._remove(node);
  this._insertAtHead(node); // keeps it "fresh"
  return node.value;
}
```

---

## 🧠 Tricky Interview Question

```javascript
const cache = new LRUCache(2);
cache.put(1, 'A');
cache.put(2, 'B');
cache.get(1);        // touches key 1 -> now most recently used
cache.put(3, 'C');   // cache full, must evict -> which key?
console.log(cache.get(2)); // ?
console.log(cache.get(1)); // ?
```
Answer: `cache.get(2)` returns `-1` and `cache.get(1)` returns `'A'`. Reasoning: after `put(1,'A')` and `put(2,'B')`, order (most→least recent) is `[2, 1]`. Then `get(1)` touches key 1, moving it to the front: `[1, 2]` — meaning key `2` is now the LEAST recently used. `put(3, 'C')` triggers eviction since capacity is 2, and evicts the LRU item — key `2`, not key `1`. This trips up people who assume "oldest inserted" is evicted (FIFO) rather than "least recently accessed" (LRU) — `get()` calls change recency, not just `put()` calls.

---

## ⚫ Interview Questions + Answers

Q1: Why combine a Map with a doubly linked list instead of just one data structure?
A1: A Map alone gives O(1) key lookup but no cheap way to track/reorder "recency" without scanning. A linked list alone gives O(1) reordering (moving nodes) but O(n) key lookup to find the node. Combining both gives O(1) for everything: Map gives direct node references, linked list gives O(1) move-to-front/remove-from-tail.

Q2: Why use sentinel head/tail nodes instead of tracking head/tail as plain `null`-able references?
A2: Sentinels eliminate special-case code for empty lists or single-node lists — every real node always has both a `prev` and `next` (even if one points to a sentinel), so `_remove`/`_insertAtHead` never need null checks. This significantly simplifies and de-bugs the implementation.

Q3: How does Redis implement LRU-like eviction at scale, and is it exact LRU?
A3: Redis uses an **approximated LRU** by default — rather than tracking exact access order for every key (expensive at scale), it samples a small set of keys and evicts the one with the oldest access timestamp among the sample. This trades perfect accuracy for much lower memory/CPU overhead, which is acceptable because approximate LRU behaves statistically close to true LRU.

Q4: What's the time/space complexity of this LRU implementation?
A4: `get` and `put` are both O(1) time. Space is O(capacity) — one Map entry + one linked list node per cached item, bounded by the fixed capacity.

Q5: How would you make this LRU cache thread-safe / usable across concurrent async operations in Node.js?
A5: Node.js is single-threaded for JS execution, so this implementation is inherently safe from traditional race conditions within one process — operations complete synchronously without interleaving. The real concern is multi-process/distributed caching (multiple Node instances), which requires a shared external cache like Redis instead of this in-process structure.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Caching expensive, repeatedly-accessed data (DB query results, computed values, API responses) with a fixed memory budget
- Access patterns follow temporal locality (recently used items are likely to be used again soon)

❌ Avoid when:
- Access patterns are closer to uniform-random (LRU gives no advantage over simpler eviction like random replacement)
- You need persistence or cross-process sharing (use Redis instead of in-process LRU)

---

## 📊 Visual Diagram
```
 head (MRU) ◀───────────────────────────────▶ tail (LRU)
   sentinel ⇄ [key:3] ⇄ [key:1] ⇄ [key:2] ⇄ sentinel
                 ▲
            get(3) or put(3,...) moves node 3 here (to front)

 Map: { 3 -> Node3, 1 -> Node1, 2 -> Node2 }   (O(1) lookup to any node)

 Eviction on put() when full: remove tail.prev (key 2) from list AND map
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Eviction | Removing an item to free space | जगह बनाने के लिए item हटाना |
| Doubly linked list | Nodes with both prev and next pointers | Prev और next दोनों pointers वाले nodes |
| Sentinel node | Dummy node simplifying edge cases | Edge cases आसान बनाने वाला dummy node |
| O(1) | Constant time regardless of input size | Input size से independent constant time |
| Temporal locality | Recently used data likely used again soon | हाल में used data फिर जल्दी use होने की संभावना |

---

## ⚡ 3-Line Summary
English: An LRU cache evicts the least recently accessed item when full, implemented in O(1) by combining a Map (fast lookup) with a doubly linked list (fast reordering). Every `get()` must move the accessed node to the front to correctly track recency, not just `put()`.
Hindi: LRU cache full होने पर सबसे least recently accessed item evict करता है, O(1) में implement होता है Map (fast lookup) + doubly linked list (fast reordering) combine करके। हर `get()` को accessed node front पर move करना चाहिए recency सही track करने के लिए, सिर्फ `put()` नहीं।

---

## ➡️ Next Topic
**296. Implement Pub/Sub** — building a publish-subscribe system with topic-based routing, as used in Redis Pub/Sub and message brokers.
