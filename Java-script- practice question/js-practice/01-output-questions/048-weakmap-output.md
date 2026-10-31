---

# Q048. WeakMap Output
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```javascript
const wm = new WeakMap();
const key = { id: 1 };
wm.set(key, 'secret');
console.log(wm.get(key), wm.has(key), wm.has({ id: 1 }));
try {
  wm.set('str', 1);
} catch (e) {
  console.log(e.name);
}
console.log(wm.size);
```

---

## 💡 Quick Concept (2 lines only)
WeakMap keys must be objects and are held weakly, so they can be garbage-collected. It is not iterable and has no `size`.
हिंदी: WeakMap की keys सिर्फ objects होती हैं, weak रहती हैं (GC हो सकती हैं), और इसमें size या iteration नहीं होता।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: set/get by the exact same object reference works
// Step 2: a different object literal {id:1} is a different key -> false
// Step 3: primitive key (string) throws TypeError
// Step 4: WeakMap has no size property -> undefined

const wm = new WeakMap();                          // create WeakMap
const key = { id: 1 };                             // object key
wm.set(key, 'secret');                             // store private data
console.log(wm.get(key), wm.has(key), wm.has({ id: 1 })); // secret true false
try {
  wm.set('str', 1);                                // invalid key
} catch (e) {
  console.log(e.name);                             // TypeError
}
console.log(wm.size);                              // undefined

// ============================================
// TEST CASES
// ============================================

console.log(typeof wm[Symbol.iterator]);           // Expected: undefined (not iterable)
console.log(wm.delete(key), wm.has(key));          // Expected: true false

const priv = new WeakMap();                        // private data pattern
class User {
  constructor(name) { priv.set(this, { name }); }  // hide data outside the class
  getName() { return priv.get(this).name; }        // read private data
}
console.log(new User('Aditya').getName());         // Expected: Aditya

// ============================================
// OUTPUT:
// ============================================
// secret true false
// TypeError
// undefined
// undefined
// true false
// Aditya
```

---

## 🔍 Why This Works (3 lines max)
WeakMap holds keys weakly: once no other reference to the key object exists, the entry can be collected. Because collection timing is unpredictable, size and iteration are not exposed.
हिंदी: Key का कोई और reference न बचे तो entry GC हो जाती है, इसलिए size और iteration नहीं दिए गए।

---

## ⚡ Alternative Solution
```javascript
// Cache computed results per object without leaking memory
const cache = new WeakMap();                 // auto-cleans with the object
function area(shape) {
  if (cache.has(shape)) return cache.get(shape); // cache hit
  const r = shape.w * shape.h;                   // compute
  cache.set(shape, r);                           // cache result
  return r;
}
console.log(area({ w: 2, h: 3 })); // 6
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: using a normal Map as an object cache (leaks memory)
const leaky = new Map();
leaky.set({ big: new Array(1e5) }, 1); // entry stays forever

// ✅ Correct: WeakMap lets the key be garbage collected
const safe = new WeakMap();
safe.set({ big: new Array(1e5) }, 1);  // collectable
console.log('ok');
```

---

## 🎯 Interview Tip (1 line)
Say: "WeakMap is for metadata or private data tied to an object's lifetime; keys must be objects and it cannot be iterated."

---

## 🔗 Related Questions
→ Q046 (Map vs Object) | Q170 (WeakMap use case) | Q249 (WeakMap use cases)
