---

# Q246. Map — 5 Use Cases
# Category: ES6+ Features
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Show 5 practical use cases of `Map`: object keys, insertion order/size, frequency counter, grouping, and caching.

---

## 💡 Quick Concept (2 lines only)
`Map` stores key-value pairs where keys can be ANY type, keeps insertion order, and has a built-in `size`.
हिंदी: Map में key कोई भी type की हो सकती है और order insert होने के हिसाब से रहता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Use non-string keys
// Step 2: Count / group data
// Step 3: Cache results

// 1. Object as key (plain objects would turn it into "[object Object]")
const meta = new Map();                          // create map
const el = { id: 'btn' };                        // object used as key
meta.set(el, { clicks: 0 });                     // store metadata for it
console.log(meta.get(el));                       // Expected: { clicks: 0 }

// 2. Insertion order + size
const m = new Map([['b', 1], ['a', 2]]);         // initial entries
m.set('c', 3);                                   // add another
console.log([...m.keys()], m.size);              // Expected: [ 'b', 'a', 'c' ] 3

// 3. Frequency counter
const freq = new Map();                          // char -> count
for (const ch of 'hello') freq.set(ch, (freq.get(ch) || 0) + 1); // increment
console.log(freq);                               // Expected: Map(4) { 'h' => 1, 'e' => 1, 'l' => 2, 'o' => 1 }

// 4. Group by property
const people = [{ n: 'A', t: 'x' }, { n: 'B', t: 'y' }, { n: 'C', t: 'x' }]; // data
const groups = new Map();                        // type -> names
for (const p of people) {
  if (!groups.has(p.t)) groups.set(p.t, []);     // create bucket
  groups.get(p.t).push(p.n);                     // add name
}
console.log(groups);                             // Expected: Map(2) { 'x' => [ 'A', 'C' ], 'y' => [ 'B' ] }

// 5. Memoization cache
const cache = new Map();                         // n -> result
const square = n => {
  if (cache.has(n)) return cache.get(n);         // cache hit
  const r = n * n;                               // compute
  cache.set(n, r);                               // store
  return r;                                      // return
};
console.log(square(4), square(4), cache.size);   // Expected: 16 16 1

// ============================================
// TEST CASES
// ============================================

console.log(new Map([[NaN, 'a']]).get(NaN));     // Expected: a
console.log(Object.fromEntries(new Map([['k', 1]]))); // Expected: { k: 1 }
console.log(new Map().set(1, 'a').has('1'));     // Expected: false
```

---

## 🔍 Why This Works (3 lines max)
Map uses SameValueZero equality, so `1` and `'1'` are different keys and `NaN` works as a key. Iteration follows insertion order.
हिंदी: Map में 1 और '1' अलग keys हैं, और NaN भी key बन सकता है।

---

## ⚡ Alternative Solution
```javascript
// Plain object works only for string/symbol keys
const o = {};                                    // object as dictionary
o[{ a: 1 }] = 'x';                               // key becomes "[object Object]"
console.log(Object.keys(o));                     // Expected: [ '[object Object]' ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: using bracket access on a Map
const bad = new Map();                           // map
bad['k'] = 1;                                    // sets a property, NOT an entry
console.log(bad.size);                           // Expected: 0

// ✅ Correct: use set/get
bad.set('k', 1);                                 // real entry
console.log(bad.size);                           // Expected: 1
```

---

## 🎯 Interview Tip (1 line)
Say: "Use Map for dynamic keys, non-string keys, frequent add/delete and ordered iteration; use object for fixed-shape records."

---

## 🔗 Related Questions
→ Q046 (Map vs Object) | Q247 (Set) | Q249 (WeakMap) | Q307 (memoization)
