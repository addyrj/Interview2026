---

# Q252. Reflect — 3 Examples
# Category: ES6+ Features
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Show 3 `Reflect` examples: functional alternatives to operators, `Reflect.ownKeys`/`defineProperty` return values, and forwarding inside a Proxy with the receiver.

---

## 💡 Quick Concept (2 lines only)
`Reflect` offers the default object operations as functions (get, set, has, deleteProperty...) that return booleans instead of throwing.
हिंदी: Reflect में object के default operations function बनकर मिलते हैं और ज्यादातर true/false लौटाते हैं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Operators as functions
// Step 2: Safe property definition + all keys
// Step 3: Forward correctly in Proxy with receiver

// Example 1: operators as functions
const o = { a: 1 };                              // sample object
console.log(Reflect.has(o, 'a'));                // Expected: true  (same as 'a' in o)
console.log(Reflect.get(o, 'a'));                // Expected: 1     (same as o.a)
console.log(Reflect.set(o, 'b', 2), o.b);        // Expected: true 2
console.log(Reflect.deleteProperty(o, 'a'));     // Expected: true  (same as delete o.a)

// Example 2: boolean results + ownKeys (includes symbols & non-enumerable)
const sym = Symbol('s');                         // symbol key
const t = { x: 1, [sym]: 2 };                    // object with both
Object.defineProperty(t, 'hidden', { value: 3, enumerable: false }); // non-enumerable
console.log(Reflect.ownKeys(t));                 // Expected: [ 'x', 'hidden', Symbol(s) ]
const frozen = Object.freeze({});                // frozen object
console.log(Reflect.defineProperty(frozen, 'k', { value: 1 })); // Expected: false (no throw)

// Example 3: Proxy + Reflect with receiver (getters keep correct this)
const base = { _n: 5, get double() { return this._n * 2; } }; // getter uses this
const proxy = new Proxy(base, {
  get(target, prop, receiver) {
    return Reflect.get(target, prop, receiver);  // receiver = proxy, so this = proxy
  },
});
console.log(proxy.double);                       // Expected: 10

// ============================================
// TEST CASES
// ============================================

console.log(Reflect.getPrototypeOf([]) === Array.prototype); // Expected: true
console.log(Reflect.apply(Math.max, null, [1, 5, 3]));       // Expected: 5
class P { constructor(v) { this.v = v; } }       // simple class
console.log(Reflect.construct(P, [7]).v);        // Expected: 7
```

---

## 🔍 Why This Works (3 lines max)
Reflect methods map 1:1 to Proxy traps, so inside a trap you can call the default behaviour with the same arguments. Many return `true/false` instead of throwing, making error handling simpler.
हिंदी: हर Proxy trap का एक Reflect method होता है, इसलिए default behaviour आसानी से forward होता है।

---

## ⚡ Alternative Solution
```javascript
// Without Reflect: Object.defineProperty throws on failure
try { Object.defineProperty(Object.freeze({}), 'k', { value: 1 }); }
catch (e) { console.log(e.constructor.name); }   // Expected: TypeError
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: target[prop] in a Proxy get trap ignores the receiver
const bad = new Proxy({ _n: 5, get double() { return this._n * 2; } }, {
  get: (t, p) => t[p],                           // this = target here
});

// ✅ Correct: pass receiver through Reflect.get
const good = new Proxy({ _n: 5, get double() { return this._n * 2; } }, {
  get: (t, p, r) => Reflect.get(t, p, r),        // this = proxy
});
console.log(bad.double, good.double);            // Expected: 10 10
```

---

## 🎯 Interview Tip (1 line)
Say: "Reflect mirrors Proxy traps; I always forward with Reflect and pass the receiver to keep `this` correct."

---

## 🔗 Related Questions
→ Q173 (Reflect use case) | Q251 (Proxy) | Q266 (Proxy pattern) | Q110 (implement new)
