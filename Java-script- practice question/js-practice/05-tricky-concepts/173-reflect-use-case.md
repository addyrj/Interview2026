---

# Q173. Explain Reflect Use Case
# Category: Tricky Concepts
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What is `Reflect` and why use it instead of operators like `in`, `delete` and `Object.defineProperty`? Show how it pairs with Proxy.

---

## 💡 Quick Concept (2 lines only)
`Reflect` is a built-in object with functions mirroring Proxy traps (`get`, `set`, `has`, `deleteProperty`, `ownKeys`...). They return booleans instead of throwing, and handle `this` (receiver) correctly.
हिंदी: Reflect में object operations के function versions हैं जो error की जगह true/false देते हैं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Use Reflect methods as function form of operators
// Step 2: Check boolean result instead of try/catch
// Step 3: Use inside Proxy traps to forward default behaviour

const obj = { a: 1 };                               // sample object

console.log(Reflect.has(obj, 'a'));                 // true  (same as 'a' in obj)
console.log(Reflect.get(obj, 'a'));                 // 1     (same as obj.a)
console.log(Reflect.set(obj, 'b', 2));              // true  (assignment succeeded)
console.log(Reflect.ownKeys(obj));                  // [ 'a', 'b' ]

// Boolean results instead of exceptions
const frozen = Object.freeze({ x: 1 });             // immutable object
console.log(Reflect.set(frozen, 'x', 99));          // false (no throw)
console.log(Reflect.deleteProperty(frozen, 'x'));   // false
console.log(Reflect.defineProperty(frozen, 'y', { value: 1 })); // false
// Object.defineProperty(frozen, 'y', {value:1}) would THROW TypeError

// Construct and apply as functions
class Point { constructor(x) { this.x = x; } }      // sample class
console.log(Reflect.construct(Point, [5]).x);       // 5  (same as new Point(5))
console.log(Reflect.apply(Math.max, null, [1, 9, 3])); // 9

// Proper Proxy forwarding with receiver (getters keep correct this)
const base = { _n: 'base', get name() { return this._n; } }; // getter uses this
const proxy = new Proxy(base, {
  get(t, k, receiver) {
    console.log('read', k);                         // log each access
    return Reflect.get(t, k, receiver);             // forward with correct this
  }
});
console.log(proxy.name);                            // logs read name, read _n, then base

// ============================================
// TEST CASES
// ============================================
// Expected output:
// true
// 1
// true
// [ 'a', 'b' ]
// false
// false
// false
// 5
// 9
// read name
// read _n
// base
```

---

## 🔍 Why This Works (3 lines max)
Reflect gives one consistent API for low-level operations with predictable return values. The `receiver` argument makes getters/setters run with the proxy as `this`, so inner accesses are also trapped.
हिंदी: Reflect operations का सीधा function रूप है, और receiver से getters में `this` सही रहता है।

---

## ⚡ Alternative Solution
```javascript
// Without Reflect: manual forwarding, loses receiver semantics
const p = new Proxy({ v: 1 }, { get: (t, k) => t[k] }); // works for simple cases
console.log(p.v);                                   // Expected: 1
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Ignoring set result in non-strict code (silent failure)
const f = Object.freeze({ a: 1 });
f.a = 2;                          // silently ignored
// ✅ Check the boolean
if (!Reflect.set(f, 'a', 2)) console.log('write failed'); // write failed
```

---

## 🎯 Interview Tip (1 line)
Say: "Reflect mirrors Proxy traps, returns booleans instead of throwing, and keeps receiver/this correct when forwarding."

---

## 🔗 Related Questions
→ Q172 (Proxy) | Q252 (Reflect 3 examples) | Q266 (Proxy pattern) | Q049 (delete operator)
