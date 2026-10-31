---

# Q152. Complete LRU Cache
# Category: Complete the Code
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Fill in the blanks. A Map remembers insertion order, so the first key is the least recently used.

```javascript
class LRUCache {
  constructor(capacity) { this.cap = capacity; this.map = new Map(); }
  get(key) {
    if (!this.map.____(key)) return -1;           // missing
    const val = this.map.get(key);
    this.map.____(key);                           // remove old position
    this.map.set(key, val);                       // re-add as newest
    return val;
  }
  put(key, val) {
    if (this.map.has(key)) this.map.delete(key);
    this.map.set(key, val);
    if (this.map.size > this.____) {              // over capacity
      this.map.delete(this.map.keys().____().value); // evict oldest
    }
  }
}
```

---

## 💡 Quick Concept (2 lines only)
Re-inserting a key on every access moves it to the end of the Map, so the first key is always the least recently used.
हिंदी: हर access पर key दोबारा डालने से सबसे पुरानी key Map में सबसे आगे रहती है और वही हटती है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

class LRUCache {
  constructor(capacity) { this.cap = capacity; this.map = new Map(); } // Step 1: capacity + store
  get(key) {
    if (!this.map.has(key)) return -1;               // blank 1: miss
    const val = this.map.get(key);                   // read value
    this.map.delete(key);                            // blank 2: remove old slot
    this.map.set(key, val);                          // add as most recent
    return val;
  }
  put(key, val) {
    if (this.map.has(key)) this.map.delete(key);     // refresh existing key
    this.map.set(key, val);                          // insert as newest
    if (this.map.size > this.cap) {                  // blank 3: capacity check
      this.map.delete(this.map.keys().next().value); // blank 4: evict least recent
    }
  }
}

// ============================================
// TEST CASES
// ============================================

const c = new LRUCache(2);
c.put(1, 'a'); c.put(2, 'b');
console.log(c.get(1));      // Expected: a
c.put(3, 'c');              // evicts key 2
console.log(c.get(2));      // Expected: -1
console.log(c.get(3));      // Expected: c
```

---

## 🔍 Why This Works (3 lines max)
Map iteration order equals insertion order, so deleting and re-setting moves a key to the end. Eviction removes the first key, giving O(1) get/put.
हिंदी: Map insertion order याद रखता है, इसलिए पहली key हमेशा सबसे कम इस्तेमाल हुई होती है।

---

## ⚡ Alternative Solution
```javascript
// Classic: doubly linked list + hash map (same O(1)), more code but language-agnostic
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: not refreshing order on get() -> becomes FIFO, not LRU
// ✅ Correct: delete + set on every get
```

---

## 🎯 Interview Tip (1 line)
Say: "O(1) LRU = hash map + order structure; in JS a Map gives both."

---

## 🔗 Related Questions
→ Q099 (LRU cache) | Q144 (complete memoize) | Q185 (cache with TTL) | Q155 (complete linked list)
