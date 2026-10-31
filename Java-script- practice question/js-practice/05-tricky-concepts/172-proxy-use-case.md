---

# Q172. Explain Proxy Use Case
# Category: Tricky Concepts
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
What is a Proxy? Show validation, default values and logging/reactivity using `get` and `set` traps.

---

## 💡 Quick Concept (2 lines only)
`new Proxy(target, handler)` wraps an object and intercepts operations (get, set, has, deleteProperty...) through trap functions in the handler.
हिंदी: Proxy किसी object को लपेटकर उसके read/write जैसे operations बीच में पकड़ लेता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Create target object
// Step 2: Define handler with traps (get/set/has...)
// Step 3: Use the proxy instead of the original object

// Use case 1: validation on set
const person = new Proxy({}, {                       // empty target
  set(target, key, value) {                          // intercept writes
    if (key === 'age' && !Number.isInteger(value)) { // validate age
      throw new TypeError('age must be integer');    // reject bad data
    }
    target[key] = value;                             // store valid value
    return true;                                     // signal success
  }
});
person.age = 25;                                     // allowed
console.log(person.age);                             // 25
try { person.age = 'x'; } catch (e) { console.log(e.message); } // age must be integer

// Use case 2: default value for missing keys
const withDefault = new Proxy({ a: 1 }, {
  get: (t, k) => (k in t ? t[k] : 'N/A')             // fallback on missing key
});
console.log(withDefault.a, withDefault.zzz);         // 1 N/A

// Use case 3: logging / reactivity
const logs = [];                                     // collect log lines
const state = new Proxy({ count: 0 }, {
  set(t, k, v) {
    logs.push(`${k}: ${t[k]} -> ${v}`);              // record change
    t[k] = v;                                        // apply change
    return true;                                     // success
  }
});
state.count++;                                       // triggers set trap
state.count += 5;                                    // triggers set trap
console.log(logs);                                   // [ 'count: 0 -> 1', 'count: 1 -> 6' ]

// Use case 4: hide private keys with has trap
const secret = new Proxy({ _pw: 1, name: 'x' }, {
  has: (t, k) => !k.startsWith('_') && k in t        // hide underscore keys
});
console.log('name' in secret, '_pw' in secret);      // true false

// ============================================
// TEST CASES
// ============================================
// Expected output:
// 25
// age must be integer
// 1 N/A
// [ 'count: 0 -> 1', 'count: 1 -> 6' ]
// true false
```

---

## 🔍 Why This Works (3 lines max)
Every operation on the proxy is routed to the matching trap, where you can add behaviour before forwarding to the target. This is how Vue 3 reactivity and validation layers are built.
हिंदी: Proxy पर हर operation trap से गुज़रता है, इसलिए validation, logging और reactivity आसान हो जाती है।

---

## ⚡ Alternative Solution
```javascript
// Use Reflect inside traps to keep default behaviour
const p = new Proxy({ n: 1 }, {
  get(t, k, r) { return Reflect.get(t, k, r); }      // forward correctly
});
console.log(p.n);                                    // Expected: 1
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Forgetting to return true from set trap (throws in strict mode)
// set(t, k, v) { t[k] = v; }   // TypeError in strict mode

// ✅ Always return true after a successful set
// set(t, k, v) { t[k] = v; return true; }
```

---

## 🎯 Interview Tip (1 line)
Say: "Proxy intercepts object operations with traps; it powers validation, logging and Vue 3 reactivity — pair it with Reflect."

---

## 🔗 Related Questions
→ Q173 (Reflect) | Q251 (Proxy 3 examples) | Q266 (Proxy pattern) | Q188 (state manager)
