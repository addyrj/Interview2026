---

# Q260. structuredClone
# Category: ES6+ Features
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Use `structuredClone` to deep copy objects (Date, Map, Set, circular refs) and show what it cannot clone compared to `JSON.parse(JSON.stringify())`.

---

## 💡 Quick Concept (2 lines only)
`structuredClone(value)` makes a true deep copy, supporting Date, Map, Set, RegExp and circular references.
हिंदी: `structuredClone` असली deep copy बनाता है, Date/Map/Set और circular reference भी संभालता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Deep copy nested data
// Step 2: Clone special types (Date, Map, Set)
// Step 3: Handle circular refs; know the limits

// 1. Deep copy: nested change does not affect original
const orig = { a: 1, nested: { b: 2 } };         // original
const copy = structuredClone(orig);              // deep clone
copy.nested.b = 99;                              // modify the copy
console.log(orig.nested.b, copy.nested.b);       // Expected: 2 99

// 2. Special types preserved
const rich = { when: new Date(0), tags: new Set([1]), m: new Map([['k', 1]]) }; // rich data
const rc = structuredClone(rich);                // clone
console.log(rc.when instanceof Date, rc.tags.has(1), rc.m.get('k')); // Expected: true true 1

// 3. Circular reference works
const loop = { name: 'loop' };                   // object
loop.self = loop;                                // points to itself
const lc = structuredClone(loop);                // JSON would throw here
console.log(lc.self === lc, lc !== loop);        // Expected: true true

// 4. Functions cannot be cloned
try { structuredClone({ fn() {} }); } catch (e) { console.log(e.name); } // Expected: DataCloneError

// ============================================
// TEST CASES
// ============================================

const j = JSON.parse(JSON.stringify({ d: new Date(0), u: undefined })); // JSON round trip
console.log(typeof j.d, 'u' in j);               // Expected: string false
console.log(structuredClone([1, [2]])[1]);       // Expected: [ 2 ]
class A { constructor() { this.x = 1; } get hi() { return 'hi'; } } // class with getter
console.log(structuredClone(new A()) instanceof A); // Expected: false (prototype lost)
console.log(structuredClone(NaN), structuredClone(undefined)); // Expected: NaN undefined
```

---

## 🔍 Why This Works (3 lines max)
It uses the structured clone algorithm: it walks the value graph, tracks visited objects (so cycles work) and copies supported types. Functions, DOM nodes and class prototypes are not preserved.
हिंदी: Functions clone नहीं होते और class का prototype खो जाता है, बाकी सब deep copy होता है।

---

## ⚡ Alternative Solution
```javascript
// JSON trick (loses Date, undefined, Map, Set, functions; fails on cycles)
const viaJson = JSON.parse(JSON.stringify({ a: [1, 2] })); // simple data only
console.log(viaJson);                            // Expected: { a: [ 1, 2 ] }
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: spread thinks it's a deep copy
const o = { n: { v: 1 } };                       // nested data
const bad = { ...o };                            // shallow
bad.n.v = 2;                                     // mutates original too
console.log(o.n.v);                              // Expected: 2

// ✅ Correct: structuredClone
const good = structuredClone({ n: { v: 1 } });   // deep
good.n.v = 2;                                    // original unaffected
```

---

## 🎯 Interview Tip (1 line)
Say: "structuredClone is the built-in deep copy (Node 17+/modern browsers); it can't copy functions and drops prototypes."

---

## 🔗 Related Questions
→ Q071 (deep clone object) | Q294 (shallow vs deep copy) | Q136 (fix object mutation) | Q242 (spread)
