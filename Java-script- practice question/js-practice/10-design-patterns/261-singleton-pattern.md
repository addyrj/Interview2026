---

# Q261. Singleton Pattern
# Category: Design Patterns
# Difficulty: ⭐ Easy

---

## ❓ Question
Implement a `Database` class such that no matter how many times you call `new Database()`, you always get the SAME instance.

---

## 💡 Quick Concept (2 lines only)
Singleton guarantees a class has exactly one instance and gives a global access point to it.
हिंदी: Singleton मतलब पूरे app में class का सिर्फ एक ही object बनेगा।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Keep a static slot to remember the first instance
// Step 2: In constructor, if instance exists, return it
// Step 3: Otherwise store `this` as the instance

class Database {
  static #instance = null;               // private static field holds the one instance

  constructor(url) {
    if (Database.#instance) {            // already created?
      return Database.#instance;         // returning an object from constructor overrides `new`
    }
    this.url = url;                      // first-time setup
    this.connectedAt = 'once';           // pretend expensive init
    Database.#instance = this;           // remember this instance
  }
}

// ============================================
// TEST CASES
// ============================================

const a = new Database('mongo://one');   // first call creates the instance
const b = new Database('mongo://two');   // second call returns the SAME instance
console.log(a === b);                    // Expected: true
console.log(b.url);                      // Expected: mongo://one
console.log(a.connectedAt);              // Expected: once
```

---

## 🔍 Why This Works (3 lines max)
A constructor that returns an object makes `new` yield that object instead of `this`. The private static field persists across calls, so the first instance is reused forever.
हिंदी: पहली बार बना object static field में रखा जाता है और हर बार वही लौटता है।

---

## ⚡ Alternative Solution
```javascript
// Module-level singleton (simplest in Node/ESM — modules are cached)
const config = Object.freeze({ env: 'prod' }); // one object created at module load
// every `import config` / require() gets this same object
console.log(config === config);                // Expected: true

// Closure-based getInstance
const Logger = (() => {                        // IIFE keeps instance private
  let instance;                                // hidden variable
  return { getInstance: () => (instance ??= { logs: [] }) }; // create lazily once
})();
console.log(Logger.getInstance() === Logger.getInstance()); // Expected: true
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: assuming each `new` shares state without guarding
class Bad { constructor() { this.id = Math.random(); } }
console.log(new Bad() === new Bad());   // false → two instances!

// ✅ Correct: guard with a stored instance (see solution) or export a single object
```

---

## 🎯 Interview Tip (1 line)
Mention ES modules are already singletons by caching, and that singletons hurt testability (global state).

---

## 🔗 Related Questions
→ Q262 (Factory) | Q269 (Module pattern) | Q161 (Closure)
