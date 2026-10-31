---

# Q266. Proxy Pattern
# Category: Design Patterns
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Wrap a user object in a Proxy that validates `age` on set, logs property reads, and hides keys starting with `_`.

---

## 💡 Quick Concept (2 lines only)
A Proxy sits in front of an object and intercepts operations like get/set for validation, logging or access control.
हिंदी: Proxy असली object के आगे खड़ा गार्ड है जो हर read/write को जांच सकता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Define handler traps (get, set, has)
// Step 2: Validate / log inside traps
// Step 3: Forward to the target using Reflect

const handler = {
  get(target, key, receiver) {
    if (typeof key === 'string' && key.startsWith('_')) return undefined; // hide private-looking keys
    console.log(`read ${String(key)}`);                // log every read
    return Reflect.get(target, key, receiver);         // forward to real object
  },
  set(target, key, value) {
    if (key === 'age' && (!Number.isInteger(value) || value < 0)) {
      throw new TypeError('age must be a non-negative integer'); // validation
    }
    return Reflect.set(target, key, value);            // forward write
  },
  has(target, key) {
    return !String(key).startsWith('_') && key in target; // hide `_` keys from `in`
  },
};

const user = new Proxy({ name: 'Asha', age: 20, _secret: 'xyz' }, handler); // wrap object

// ============================================
// TEST CASES
// ============================================

console.log(user.name);          // Expected: read name
                                 // Expected: Asha
console.log(user._secret);       // Expected: undefined
user.age = 25;                   // valid write
console.log('age' in user);      // Expected: true
console.log('_secret' in user);  // Expected: false
try { user.age = -5; } catch (e) { console.log(e.message); } // Expected: age must be a non-negative integer
```

---

## 🔍 Why This Works (3 lines max)
Proxy traps intercept fundamental operations before they hit the target. Reflect forwards the default behavior safely.
हिंदी: Trap में हम अपना logic डालते हैं और बाकी काम Reflect असली object को सौंप देता है।

---

## ⚡ Alternative Solution
```javascript
// Lazy-loading (virtual) proxy using a plain object
const heavy = { get data() { delete this.data; return (this.data = [1, 2, 3]); } }; // computes once on first access
console.log(heavy.data); // Expected: [ 1, 2, 3 ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: set trap that forgets to return true (throws TypeError in strict mode)
// set(t, k, v) { t[k] = v; }

// ✅ Correct: return Reflect.set(...) or true
```

---

## 🎯 Interview Tip (1 line)
Mention Vue 3 reactivity is built on Proxy, and Proxy has runtime cost so use sparingly.

---

## 🔗 Related Questions
→ Q172 (Proxy use case) | Q173 (Reflect) | Q251 (Proxy examples)
