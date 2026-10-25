# 186. Implement LRU Cache
# हिंदी में: LRU Cache बनाना — सबसे कम हाल में इस्तेमाल हुए item को हटाने वाला Cache

---

## 🔵 Simple Definition (English)
An LRU (Least Recently Used) cache stores a fixed number of items. When it is full and a new item must be added, it removes the item that has not been read or written for the longest time. Reads and writes both count as "use".

## 🔵 सरल परिभाषा (Hindi)
LRU (Least Recently Used) cache में एक तय संख्या तक items रखे जाते हैं। Cache भर जाए और नया item डालना हो, तो वह item हटाया जाता है जो सबसे लंबे समय से पढ़ा या लिखा नहीं गया। Read और write, दोनों को "इस्तेमाल" माना जाता है।

---

## 🔴 Problem it Solves
**Problem Statement:** Implement `LRUCache` with a fixed `capacity`, `get(key)`, and `set(key, value)`. `get` returns the value or `undefined` for a miss. `set` on a full cache evicts the least recently used key. Both `get` and `set` must run in O(1) time.

Without a cache, every request hits the slow source: a database or a remote API. Memory is limited, so the cache cannot grow forever. LRU is a simple rule that keeps the hot items and drops the cold ones. Swiggy's restaurant menu cache, Flipkart's product page cache, and Razorpay's merchant config lookups all need this behaviour.

## 🔴 यह क्यों बना? (Hindi)
**Problem Statement:** `LRUCache` बनाओ जिसमें fixed `capacity`, `get(key)` और `set(key, value)` हों। Miss पर `get` `undefined` लौटाए। Cache भरा हो और `set` हो, तो सबसे कम इस्तेमाल हुई key हटाओ। `get` और `set` दोनों O(1) time में चलने चाहिए।

Cache के बिना हर request धीमे source तक जाती है: database या remote API। Memory सीमित है, इसलिए cache अनंत नहीं बढ़ सकता। LRU एक सरल नियम है: गर्म (hot) items रखो, ठंडे (cold) items हटाओ। Swiggy का restaurant menu cache, Flipkart का product page cache और Razorpay के merchant config lookups, सबको यही चाहिए।

---

## 🟢 How it Works — Step by Step

Step 1 → Store entries in a `Map`. A `Map` remembers insertion order.
Step 2 → The first key in the Map is the least recently used; the last key is the most recent.
Step 3 → On `get`, if the key exists, delete it and set it again so it moves to the end.
Step 4 → On `set`, if the key exists, delete it first so it moves to the end, then set the new value.
Step 5 → On a new key with a full cache, remove the first key (the least recently used) before inserting.
Step 6 → Every operation touches only a few Map entries, so the cost is O(1).

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → Entries को `Map` में रखो। `Map` insertion order याद रखता है।
Step 2 → Map की पहली key सबसे कम इस्तेमाल हुई है; आखिरी key सबसे ताज़ा है।
Step 3 → `get` पर अगर key है, तो उसे delete करके दोबारा set करो ताकि वह आखिर में पहुँचे।
Step 4 → `set` पर अगर key पहले से है, तो पहले delete करो ताकि वह आखिर में जाए, फिर नई value set करो।
Step 5 → नई key और cache भरा है, तो insert से पहले पहली key (सबसे कम इस्तेमाल) हटाओ।
Step 6 → हर operation कुछ ही Map entries छूता है, इसलिए cost O(1) है।

---

## 🟡 Real World Example
Flipkart's product page service keeps the last 1000 product details in memory. A customer who opens the same phone listing five times in a minute gets it from the cache each time. Products nobody has opened recently fall out of the cache, which keeps memory bounded.

Scenario: The cache holds 2 items. A user opens `product:101` and `product:202`. Then they open `product:101` again (refreshing it). A new visitor opens `product:303`. The cache evicts `product:202`, because `product:101` was used more recently.

## 🟡 Real Example Hindi mein
Flipkart की product page service हाल की 1000 product details memory में रखती है। कोई customer एक मिनट में एक ही phone listing पाँच बार खोले, तो हर बार cache से मिलती है। जिन products को हाल में किसी ने नहीं खोला, वे cache से बाहर हो जाते हैं, जिससे memory सीमित रहती है।

उदाहरण: Cache में 2 items हैं। User `product:101` और `product:202` खोलता है। फिर `product:101` दोबारा खोलता है (ताज़ा करता है)। नया visitor `product:303` खोलता है। Cache `product:202` हटाता है, क्योंकि `product:101` ज़्यादा हाल में इस्तेमाल हुआ।

---

## 💻 Code Example — Basic
```javascript
// Basic: an array keeps the key order; index 0 is the least recently used key
class BasicLRU {
  constructor(capacity) {
    this.capacity = capacity;                    // the maximum number of items
    this.keys = [];                              // key order: index 0 = oldest, last index = newest
    this.data = {};                              // key -> value storage
  }

  get(key) {
    if (!(key in this.data)) return undefined;   // miss: the key is not in the cache
    this.keys.splice(this.keys.indexOf(key), 1); // remove the key from its old position
    this.keys.push(key);                         // mark it as the most recently used
    return this.data[key];                       // return the stored value
  }

  set(key, value) {
    if (key in this.data) {                      // key already exists: just update it
      this.keys.splice(this.keys.indexOf(key), 1); // remove its old position
    } else if (this.keys.length === this.capacity) { // new key and the cache is full
      const oldest = this.keys.shift();          // remove index 0, the least recently used key
      delete this.data[oldest];                  // remove its value as well
    }
    this.keys.push(key);                         // the key is now the newest
    this.data[key] = value;                      // store the value
  }
}

const small = new BasicLRU(2);                   // a cache that holds 2 items
small.set("a", 1);                               // cache: a
small.set("b", 2);                               // cache: a, b
console.log(small.get("a"));                     // Expected output: 1 (a is now newest)
small.set("c", 3);                               // full: evicts b, the least recently used
console.log(small.get("b"));                     // Expected output: undefined
console.log(small.get("c"));                     // Expected output: 3
```

## 💻 Code Example — Advanced
```javascript
// Advanced: a Map-based LRU cache with O(1) get and set
class LRUCache {
  constructor(capacity) {
    // Guard: capacity must be a positive whole number
    if (!Number.isInteger(capacity) || capacity <= 0) {
      throw new RangeError("capacity must be a positive integer");
    }
    this.capacity = capacity;                    // maximum number of entries
    this.map = new Map();                        // Map keeps insertion order: first = least recent
  }

  get size() {
    return this.map.size;                        // current number of entries
  }

  has(key) {
    return this.map.has(key);                    // checks presence without changing recency
  }

  get(key) {
    if (!this.map.has(key)) return undefined;    // miss: nothing to return
    const value = this.map.get(key);            // read the stored value
    this.map.delete(key);                        // remove the key from its old position
    this.map.set(key, value);                    // insert it again, so it moves to the end (most recent)
    return value;                                // return the value
  }

  set(key, value) {
    if (this.map.has(key)) {                     // existing key: refresh its position first
      this.map.delete(key);                      // Map.set alone would NOT move it to the end
    } else if (this.map.size >= this.capacity) { // new key and no room left
      const oldestKey = this.map.keys().next().value; // first key in insertion order
      this.map.delete(oldestKey);                // evict the least recently used entry
    }
    this.map.set(key, value);                    // store the new or updated entry at the end
    return this;                                 // return this so calls can be chained
  }

  delete(key) {
    return this.map.delete(key);                 // true if something was removed
  }

  toArray() {
    return [...this.map.entries()];              // [key, value] pairs, least recent first
  }
}

// ---- Tests: run with plain node ----
const cache = new LRUCache(2);                   // capacity of 2
cache.set("user:1", "Aditya").set("user:2", "Riya"); // chained sets: user:1 is oldest
console.log(cache.get("user:1"));                // Expected output: Aditya (user:1 becomes newest)
cache.set("user:3", "Kabir");                    // full: evicts user:2, the least recently used
console.log(cache.get("user:2"));                // Expected output: undefined
console.log(cache.has("user:3"), cache.size);    // Expected output: true 2
console.log(cache.toArray().map(([k]) => k).join(" > ")); // Expected output: user:1 > user:3
try {
  new LRUCache(0);                               // invalid capacity must throw
} catch (err) {
  console.log(err.name);                         // Expected output: RangeError
}

// Time:  get, set, has, delete are O(1) on average (Map hashing and delete are constant time)
// Space: O(capacity) entries
```

### Edge Cases
- `capacity = 1`: every new key evicts the only existing key, so `set("a")` then `set("b")` leaves only `b`.
- Updating an existing key (`set` on a present key) never evicts anything, because the size does not grow.
- `get` on a missing key returns `undefined` and does not change the order or the size.
- A `null` or `undefined` value is still a stored entry; use `has` to tell "stored as undefined" from "missing".
- A non-integer or zero capacity throws `RangeError` at construction time, so the bug is caught early.

---

## 🟠 Express.js Integration
A product detail endpoint can use the LRU cache in front of a slow database call. The cache is per process and holds a bounded number of items, so memory stays predictable. Express sends the cached response when it can, and sets an `X-Cache` header so you can see hits and misses while testing.

```javascript
// Express.js: product details cached with LRU in front of a slow database lookup
const express = require("express");               // import Express
const app = express();                            // create the app

// Pretend slow database: wait 200 ms and return the product or null
const fakeDb = {
  products: { 101: { id: 101, name: "Phone X" }, 202: { id: 202, name: "Laptop Y" } }, // sample rows
  findById(id) {
    return new Promise((resolve) => {             // return a promise, like a real driver
      setTimeout(() => resolve(this.products[id] || null), 200); // simulate network latency
    });
  },
};

// The same LRUCache class as the advanced example (kept here so the snippet is readable)
class LRUCache {
  constructor(capacity) { this.capacity = capacity; this.map = new Map(); } // store capacity and the Map
  get(key) {                                      // read with recency update
    if (!this.map.has(key)) return undefined;     // miss
    const v = this.map.get(key);                  // value
    this.map.delete(key); this.map.set(key, v);   // move to the most recent end
    return v;                                     // hit
  }
  set(key, value) {                               // write with eviction
    if (this.map.has(key)) this.map.delete(key);  // refresh existing key
    else if (this.map.size >= this.capacity) this.map.delete(this.map.keys().next().value); // evict oldest
    this.map.set(key, value);                     // store
  }
}

const productCache = new LRUCache(100);           // keep at most 100 products in memory

// GET /api/products/:id
app.get("/api/products/:id", async (req, res) => {
  const id = Number(req.params.id);               // convert the URL text to a number
  if (!Number.isInteger(id) || id <= 0) {         // validate the id
    return res.status(400).json({ error: "id must be a positive integer" }); // 400 Bad Request
  }
  const cached = productCache.get(id);            // try the cache first
  if (cached !== undefined) {                     // hit: return immediately
    res.set("X-Cache", "HIT");                    // tell the client it came from the cache
    return res.json(cached);                      // 200 OK from memory
  }
  const product = await fakeDb.findById(id);      // miss: ask the slow database
  if (!product) return res.status(404).json({ error: "not found" }); // 404 Not Found
  productCache.set(id, product);                  // store for the next request
  res.set("X-Cache", "MISS");                     // tell the client this was a database read
  res.json(product);                              // 200 OK
});

// Start the server on PORT from the environment, or 3000 by default
app.listen(process.env.PORT || 3000, () => {
  console.log("Product API running");             // ready message
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Refreshing recency only on `set`, not on `get`, so the cache behaves like FIFO
✅ **Correct:** Move the key to the end on every successful `get` as well

```javascript
// Wrong: reading "x" does not change its position, so "x" is still the first key and gets evicted first
const wrongOrder = new Map([["x", 1], ["y", 2]]); // insertion order: x, y
wrongOrder.get("x");                              // read x, but the order is untouched
console.log([...wrongOrder.keys()].join(","));    // Expected output: x,y

// Right: delete and set again on read, so x moves to the end
const rightOrder = new Map([["x", 1], ["y", 2]]); // same starting order
const v = rightOrder.get("x");                    // read the value of x
rightOrder.delete("x");                           // remove x from the front
rightOrder.set("x", v);                           // add x back at the end (most recent)
console.log([...rightOrder.keys()].join(","));    // Expected output: y,x
```

❌ **Mistake 2:** Using a plain object for the cache and expecting insertion order
✅ **Correct:** Use a `Map`, which keeps insertion order for every key type

```javascript
// Wrong: integer-like keys in a plain object are listed in ascending number order first
const obj = {};                                   // plain object as a cache
obj["b"] = 1;                                     // insert "b" first
obj["10"] = 2;                                    // insert "10" second
obj["2"] = 3;                                     // insert "2" third
console.log(Object.keys(obj).join(","));          // Expected output: 2,10,b

// Right: a Map keeps the exact insertion order
const map = new Map([["b", 1], ["10", 2], ["2", 3]]); // same keys, same order
console.log([...map.keys()].join(","));           // Expected output: b,10,2
```

---

## 🧠 Tricky Interview Question
```javascript
const m = new Map([["x", 1], ["y", 2]]);          // order: x, y
m.set("x", 10);                                   // update an existing key
console.log([...m.keys()]);                       // ?

const seen = new Map([["x", 1], ["y", 2]]);       // order: x, y
seen.delete("x");                                 // remove x
seen.set("x", 10);                                // add x back
console.log([...seen.keys()]);                    // ?
```
Answer: `[ 'x', 'y' ]` and then `[ 'y', 'x' ]`.
`Map.set` on an existing key updates the value but keeps the key in its original position, so `x` stays first and would be evicted first. That is the classic LRU bug. Deleting and setting again moves the key to the end, which is why the advanced class calls `delete` before `set` in both `get` and `set`.

---

## ⚫ Interview Questions + Answers

**Q1: Why is a plain object not a good base for an LRU cache?**
A1: Object keys have their own ordering rules. Integer-like keys come first in ascending order, so insertion order is lost. A `Map` keeps insertion order exactly.

**Q2: What data structure gives O(1) for both get and move-to-front?**
A2: A hash map with a doubly linked list. A `Map` works in JavaScript because it is a hash table that also keeps insertion order, so delete and re-insert act as move-to-end in O(1) on average.

**Q3: Why does `get` need to change the order?**
A3: LRU means "least recently used", and a read is a use. If `get` did not refresh recency, the cache would evict items in insertion order (FIFO), which is a different policy.

**Q4: How do you find the least recently used key in a Map?**
A4: `map.keys().next().value` returns the first key in insertion order. Because the order always puts the least recent item first, that is the one to evict.

**Q5: How do you handle a stored value of `undefined`?**
A5: Use `has(key)` to check presence. `get` returning `undefined` is ambiguous on its own, because a missing key and a stored `undefined` look the same.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Some keys are read far more often than others (hot products, popular users, recent searches)
- Memory must stay bounded inside one process
- The data is expensive to compute or fetch and can be a little stale

❌ Avoid when:
- All keys are read about equally; LRU gains little and the cache adds complexity
- You run many Node processes and need one shared cache; use Redis or Memcached so every process sees the same data
- Stale data is unacceptable (payments, balances); cache with explicit invalidation or do not cache

---

## 📊 Visual Diagram
```
capacity = 2

set("user:1")  ->  [ user:1 ]
set("user:2")  ->  [ user:1, user:2 ]        oldest --> newest
get("user:1")  ->  [ user:2, user:1 ]        user:1 moved to the end
set("user:3")  ->  full: evict user:2
                   [ user:1, user:3 ]

Map order is the LRU order:  first key = evict next,  last key = used most recently
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| LRU | Least Recently Used: evict the item used longest ago | सबसे लंबे समय से इस्तेमाल न हुआ item |
| Eviction | Removing an item to make room | जगह बनाने के लिए item हटाना |
| Capacity | Maximum number of items the cache holds | Cache में अधिकतम items |
| Cache hit | The requested key is already in memory | Key पहले से memory में है |
| Cache miss | The key is not in memory and must be fetched | Key memory में नहीं है |
| Recency | How recently a key was used | Key कितनी ताज़ा इस्तेमाल हुई |
| Hash map | Key-to-value lookup in constant average time | Constant time में key से value खोजने वाली संरचना |

---

## ⚡ 3-Line Summary
English:
1. An LRU cache holds a fixed number of items and evicts the least recently used one when full.
2. A `Map` does it in O(1): delete and re-set a key to move it to the end, and evict the first key.
3. Refresh recency on both `get` and `set`, and use `has` when `undefined` is a valid value.

Hindi:
1. LRU cache तय संख्या में items रखता है और भरने पर सबसे कम इस्तेमाल हुआ item हटाता है।
2. `Map` से यह O(1) में होता है: key को delete करके फिर set करो ताकि वह आखिर में जाए, और पहली key हटाओ।
3. `get` और `set`, दोनों पर ताज़गी अपडेट करो, और `undefined` valid value हो तो `has` इस्तेमाल करो।

---

## ➡️ Next Topic
**187. Implement call, apply, bind** — the cache taught you to control which entries stay alive; the next problem controls which object `this` refers to, which is the core idea behind method borrowing and Express route handlers.
