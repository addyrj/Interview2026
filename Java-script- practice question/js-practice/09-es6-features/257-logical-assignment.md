---

# Q257. Logical Assignment
# Category: ES6+ Features
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Explain and demonstrate `||=`, `&&=` and `??=` with outputs, including short-circuit behaviour.

---

## 💡 Quick Concept (2 lines only)
`a ||= b` assigns only if `a` is falsy, `a &&= b` only if truthy, `a ??= b` only if nullish.
हिंदी: Logical assignment तभी assign करता है जब condition पूरी हो, वरना कुछ नहीं करता।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: ||= assigns when current value is falsy
// Step 2: &&= assigns when current value is truthy
// Step 3: ??= assigns when current value is null/undefined

// ||= (falsy -> assign)
let a = 0;                                       // falsy
a ||= 5;                                         // same as a || (a = 5)
console.log(a);                                  // Expected: 5

// &&= (truthy -> assign)
let b = 'user';                                  // truthy
b &&= b.toUpperCase();                           // update only if exists
console.log(b);                                  // Expected: USER

let c = null;                                    // falsy
c &&= c.toUpperCase();                           // skipped (no TypeError)
console.log(c);                                  // Expected: null

// ??= (nullish -> assign)
let d = 0;                                       // valid value
d ??= 100;                                       // not nullish -> kept
console.log(d);                                  // Expected: 0

const opts = { retries: undefined };             // missing option
opts.retries ??= 3;                              // set default
console.log(opts);                               // Expected: { retries: 3 }

// ============================================
// TEST CASES
// ============================================

let calls = 0;                                   // side-effect counter
const val = 'set';                               // already truthy
let t = val;                                     // target
t ||= (calls++, 'x');                            // right side NOT evaluated
console.log(t, calls);                           // Expected: set 0

const cfg = { name: '' };                        // empty string
cfg.name ||= 'Anon';                             // '' is falsy -> assigned
cfg.title ??= 'Mr';                              // missing -> assigned
console.log(cfg);                                // Expected: { name: 'Anon', title: 'Mr' }
```

---

## 🔍 Why This Works (3 lines max)
These operators short-circuit: `x ||= y` behaves like `x || (x = y)`, so the right side (and any setter) runs only when needed. That avoids pointless writes.
हिंदी: Right side तभी चलता है जब असल में assignment की ज़रूरत हो।

---

## ⚡ Alternative Solution
```javascript
// Long form equivalents
let x;                                           // undefined
x = x ?? 'default';                              // old style ??=
console.log(x);                                  // Expected: default
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: ||= for numeric/boolean defaults
const s = { volume: 0 };                         // mute is valid
s.volume ||= 50;                                 // overwrites 0!
console.log(s.volume);                           // Expected: 50  (bug)

// ✅ Correct: ??=
const s2 = { volume: 0 };                        // same data
s2.volume ??= 50;                                // keeps 0
console.log(s2.volume);                          // Expected: 0
```

---

## 🎯 Interview Tip (1 line)
Say: "??= is the safe default-setter; ||= replaces any falsy value; &&= updates only existing values."

---

## 🔗 Related Questions
→ Q037 (short circuit) | Q256 (nullish coalescing) | Q255 (optional chaining) | Q072 (merge objects)
