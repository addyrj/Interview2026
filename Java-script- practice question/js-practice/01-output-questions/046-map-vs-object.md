---

# Q046. Map vs Object Output
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```javascript
const obj = {};
const map = new Map();
const k1 = { id: 1 };
const k2 = { id: 2 };
obj[k1] = 'one';
obj[k2] = 'two';
map.set(k1, 'one');
map.set(k2, 'two');
console.log(Object.keys(obj).length, map.size);
console.log(obj[k1], map.get(k1));
```

---

## 💡 Quick Concept (2 lines only)
Object keys are always strings or symbols, so objects as keys collapse into "[object Object]". Map accepts any value as a key and keeps insertion order.
हिंदी: Object में key string बन जाती है, जबकि Map में कोई भी value key हो सकती है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: obj[k1] -> key "[object Object]" = 'one'
// Step 2: obj[k2] -> same key, overwritten with 'two'
// Step 3: Map keeps k1 and k2 as separate keys
// Step 4: obj[k1] reads the overwritten value 'two'

const obj = {};                      // plain object
const map = new Map();               // Map
const k1 = { id: 1 };                // object key 1
const k2 = { id: 2 };                // object key 2
obj[k1] = 'one';                     // stored under "[object Object]"
obj[k2] = 'two';                     // overwrites same key
map.set(k1, 'one');                  // separate entry
map.set(k2, 'two');                  // separate entry
console.log(Object.keys(obj).length, map.size); // 1 2
console.log(obj[k1], map.get(k1));              // two one

// ============================================
// TEST CASES
// ============================================

const m = new Map([[1, 'a'], ['1', 'b']]);   // number and string keys differ
console.log(m.size);                         // Expected: 2
const o = { 1: 'a' };                        // number key becomes string
console.log(o['1'], Object.keys(o));         // Expected: a [ '1' ]
console.log(new Map([[NaN, 'x']]).get(NaN)); // Expected: x
console.log([...new Map([['b', 1], ['a', 2]]).keys()]); // Expected: [ 'b', 'a' ]

// ============================================
// OUTPUT:
// ============================================
// 1 2
// two one
// 2
// a [ '1' ]
// x
// [ 'b', 'a' ]
```

---

## 🔍 Why This Works (3 lines max)
Property keys on objects pass through ToPropertyKey (string). Map uses SameValueZero, so object identity, numbers vs strings and even NaN work as distinct keys. Map also has `.size` and guaranteed insertion order.
हिंदी: Object keys string बनती हैं, Map identity से compare करता है और उसमें .size भी मिलता है।

---

## ⚡ Alternative Solution
```javascript
// Use WeakMap when keys are objects and should be garbage-collectable
const wm = new WeakMap();        // keys must be objects
const key = {};                  // object key
wm.set(key, 'data');             // store metadata
console.log(wm.get(key));        // data
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: using a plain object as a dictionary with user keys
const cache = {};
console.log('toString' in cache);          // true (inherited!)

// ✅ Correct: use Map (or Object.create(null))
console.log(new Map().has('toString'));    // false
```

---

## 🎯 Interview Tip (1 line)
Say: "Map allows any key type, preserves order, has size and no prototype keys; objects are better for fixed-shape records and JSON."

---

## 🔗 Related Questions
→ Q047 (Set output) | Q048 (WeakMap) | Q246 (Map use cases)
