---

# Q251. Proxy — 3 Examples
# Category: ES6+ Features
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Show 3 `Proxy` examples: validation on set, default values on get, and read-only/logging protection.

---

## 💡 Quick Concept (2 lines only)
A Proxy wraps an object and intercepts operations (get, set, has, delete...) through handler "traps".
हिंदी: Proxy किसी object को wrap करके उसके get/set जैसे operations को बीच में पकड़ लेता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Validation with set trap
// Step 2: Default values with get trap
// Step 3: Read-only object

// Example 1: Validation
const person = new Proxy({}, {
  set(target, prop, value) {
    if (prop === 'age' && typeof value !== 'number') {
      throw new TypeError('age must be a number'); // reject bad data
    }
    target[prop] = value;                        // store valid data
    return true;                                 // must return true in strict mode
  },
});
person.age = 30;                                 // valid assignment
console.log(person.age);                         // Expected: 30
try { person.age = 'x'; } catch (e) { console.log(e.message); } // Expected: age must be a number

// Example 2: Default value for missing keys
const withDefault = new Proxy({ a: 1 }, {
  get: (t, p) => (p in t ? t[p] : 'N/A'),        // fallback when key missing
});
console.log(withDefault.a, withDefault.zzz);     // Expected: 1 N/A

// Example 3: Read-only + logging
const frozen = new Proxy({ x: 1 }, {
  get(t, p) { console.log('read', p); return t[p]; },   // log reads
  set() { console.log('blocked'); return true; },       // ignore writes silently
});
frozen.x;                                        // Expected: read x
frozen.x = 5;                                    // Expected: blocked
console.log(frozen.x);                           // Expected: read x \n 1

// ============================================
// TEST CASES
// ============================================

const p = new Proxy({}, { has: (t, k) => k.startsWith('_') }); // hide-all-but-underscore
console.log('_a' in p, 'b' in p);                // Expected: true false
const del = new Proxy({ k: 1 }, { deleteProperty: () => false }); // block delete
console.log(delete del.k);                       // Expected: false
```

---

## 🔍 Why This Works (3 lines max)
Every operation on the proxy goes to the handler first; the trap can change, block or log it, then optionally forward to the target. Reflect is the clean way to forward.
हिंदी: Trap में तय होता है कि operation target तक जाए, बदले या रुक जाए।

---

## ⚡ Alternative Solution
```javascript
// Forward with Reflect (best practice)
const logged = new Proxy({ n: 1 }, {
  get(t, p, r) { return Reflect.get(t, p, r); }, // forward safely
});
console.log(logged.n);                           // Expected: 1
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: set trap that forgets to return true (throws TypeError in strict mode)
// const bad = new Proxy({}, { set(t, p, v) { t[p] = v; } });

// ✅ Correct: always return true
const good = new Proxy({}, { set(t, p, v) { t[p] = v; return true; } }); // returns true
good.a = 1;                                      // works
console.log(good.a);                             // Expected: 1
```

---

## 🎯 Interview Tip (1 line)
Say: "Vue 3 reactivity uses Proxy; I use traps for validation, logging, defaults and observable state."

---

## 🔗 Related Questions
→ Q172 (Proxy use case) | Q252 (Reflect) | Q266 (Proxy pattern) | Q098 (observable)
