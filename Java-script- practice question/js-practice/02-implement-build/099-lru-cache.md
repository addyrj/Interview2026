---

# Q099. Implement LRU Cache
# Category: Implement / Build
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Implement an LRU (Least Recently Used) Cache with:
- `get(key)` — return value if key exists, else -1. Marks as recently used.
- `put(key, value)` — insert/update. If over capacity, evict least recently used item.

Both operations should run in O(1) time.

```javascript
const cache = new LRUCache(2);  // capacity = 2
cache.put(1, 1);
cache.put(2, 2);
cache.get(1);    // 1 (makes 1 most recently used)
cache.put(3, 3); // evicts key 2 (least recently used)
cache.get(2);    // -1 (evicted)
```

---

## 💡 Quick Concept (2 lines only)
LRU Cache keeps the most recently used items. Use a Map (ordered by insertion) + move accessed keys to end. Evict the first (oldest/least used) key when full.
हिंदी: LRU Cache recently used items रखता है — Map में access होने पर item end में move होता है, capacity पर पहला delete।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION — Using Map (insertion order preserved)
// ============================================

class LRUCache {
  constructor(capacity) {
    this.capacity = capacity;     // Step 1: max size
    this.cache = new Map();       // Step 2: Map maintains insertion order
  }
  
  get(key) {
    if (!this.cache.has(key)) return -1;   // Step 3: not found
    
    const value = this.cache.get(key);     // Step 4: get value
    this.cache.delete(key);                // Step 5: remove from current position
    this.cache.set(key, value);            // Step 6: re-insert at end (most recent)
    return value;
  }
  
  put(key, value) {
    if (this.cache.has(key)) {
      this.cache.delete(key);              // Step 7: remove old position
    } else if (this.cache.size >= this.capacity) {
      // Step 8: evict LRU — first key in Map (oldest)
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    this.cache.set(key, value);            // Step 9: insert at end (most recent)
  }
}

// ============================================
// TEST CASES
// ============================================

const cache = new LRUCache(2);

cache.put(1, 1);  // cache: {1:1}
cache.put(2, 2);  // cache: {1:1, 2:2}
console.log(cache.get(1));   // Expected: 1    — cache: {2:2, 1:1}  (1 moved to end)
cache.put(3, 3);  // evict 2 — cache: {1:1, 3:3}
console.log(cache.get(2));   // Expected: -1   — 2 was evicted
console.log(cache.get(3));   // Expected: 3    — cache: {1:1, 3:3}
cache.put(4, 4);  // evict 1 — cache: {3:3, 4:4}
console.log(cache.get(1));   // Expected: -1   — 1 was evicted
console.log(cache.get(3));   // Expected: 3
console.log(cache.get(4));   // Expected: 4
```

---

## 🔍 Why This Works (3 lines max)
JS `Map` preserves insertion order. "Move to end" = delete + re-insert. First key in Map = least recently used (LRU). All operations are O(1): Map get/set/delete are O(1).
हिंदी: Map insertion order preserve करता है — access पर delete+re-insert (end में); first key = LRU → evict।

---

## ⚡ Alternative Solution
```javascript
// Doubly Linked List + HashMap approach (explicit O(1)):
class Node {
  constructor(key, val) {
    this.key = key; this.val = val;
    this.prev = null; this.next = null;
  }
}

class LRUCacheDLL {
  constructor(capacity) {
    this.capacity = capacity;
    this.map = new Map();
    // Dummy head (LRU) and tail (MRU) nodes
    this.head = new Node(0, 0);
    this.tail = new Node(0, 0);
    this.head.next = this.tail;
    this.tail.prev = this.head;
  }
  
  remove(node) {
    node.prev.next = node.next;
    node.next.prev = node.prev;
  }
  
  insertAtTail(node) {
    const prev = this.tail.prev;
    prev.next = node;
    node.prev = prev;
    node.next = this.tail;
    this.tail.prev = node;
  }
  
  get(key) {
    if (!this.map.has(key)) return -1;
    const node = this.map.get(key);
    this.remove(node);
    this.insertAtTail(node);
    return node.val;
  }
  
  put(key, value) {
    if (this.map.has(key)) this.remove(this.map.get(key));
    else if (this.map.size >= this.capacity) {
      const lru = this.head.next;  // least recently used
      this.remove(lru);
      this.map.delete(lru.key);
    }
    const node = new Node(key, value);
    this.insertAtTail(node);
    this.map.set(key, node);
  }
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: using a plain object (no insertion order guarantee in older JS)
this.cache = {};
// ✅ Use Map — guaranteed insertion order in ES6+

// ❌ Wrong: O(n) approach with array
this.cache.sort(...)  // or indexOf — O(n) per operation

// ❌ Wrong: forgetting to check capacity on put when key already exists
put(key, value) {
  // Don't evict when updating existing key!
  if (this.cache.has(key)) {
    this.cache.delete(key);  // remove from old position
    this.cache.set(key, value);  // add to end — no eviction needed
    return;
  }
  // Only evict when inserting NEW key and at capacity
}
```

---

## 🎯 Interview Tip (1 line)
Say: "Map-based solution is cleanest — insert order + O(1) ops; for interview clarity, DLL + HashMap shows you understand the data structure design."

---

## 🔗 Related Questions
→ Q083 (memoize) | Q185 (cache with TTL) | Q100 (stack) | Q101 (queue)
