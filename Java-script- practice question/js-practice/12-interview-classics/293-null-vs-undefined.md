---

# Q293. null vs undefined
# Category: Interview Classics
# Difficulty: ⭐ Easy

---

## ❓ Question
What is the difference between `null` and `undefined`? Show where each one appears naturally, how they behave in `typeof`, JSON, math, and default parameters.

---

## 💡 Quick Concept (2 lines only)
`undefined` = "no value assigned yet" (set by JS). `null` = "intentionally empty" (set by the developer).
हिंदी: `undefined` मतलब value अभी दी ही नहीं गई; `null` मतलब हमने जानबूझकर खाली रखा है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: undefined appears automatically (uninitialized var, missing arg/property)
// Step 2: null is assigned manually to say "empty on purpose"
// Step 3: they are == equal but not === equal and have different typeof
// Step 4: they differ in JSON, Number() and default parameters

let declared;                         // declared, never assigned -> undefined
const user = { name: 'Asha' };        // object without an "age" key
function echo(x) { return x; }        // function that returns its argument
const emptyOnPurpose = null;          // developer-assigned empty value

// Default parameter: only undefined triggers the default, null does not
function greet(name = 'Guest') { return name; } // default applies to undefined only

// ============================================
// TEST CASES
// ============================================

console.log(declared);              // Expected: undefined
console.log(user.age);              // Expected: undefined (missing property)
console.log(echo());                // Expected: undefined (missing argument)
console.log(emptyOnPurpose);        // Expected: null
console.log(typeof undefined);      // Expected: undefined
console.log(typeof null);           // Expected: object  (famous legacy bug)
console.log(null == undefined);     // Expected: true
console.log(null === undefined);    // Expected: false
console.log(Number(null));          // Expected: 0
console.log(Number(undefined));     // Expected: NaN
console.log(JSON.stringify({ a: undefined, b: null })); // Expected: {"b":null}
console.log(greet(undefined));      // Expected: Guest
console.log(greet(null));           // Expected: null
console.log(null ?? 'fallback');    // Expected: fallback
```

---

## 🔍 Why This Works (3 lines max)
The engine assigns `undefined` whenever something has no value yet. `null` is a real value that means "nothing", so defaults and JSON treat it differently. `typeof null === 'object'` is a historical bug kept for compatibility.
हिंदी: `undefined` engine देता है, `null` हम देते हैं; इसलिए default param और JSON में दोनों अलग चलते हैं।

---

## ⚡ Alternative Solution
```javascript
// Safe check for "no value" — covers both
const v = null;                        // sample value
console.log(v == null);                // true  (loose check for both)
console.log(v ?? 'default');           // default (nullish coalescing)
console.log(v?.length);                // undefined (optional chaining, no crash)
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: typeof to detect null
if (typeof value === 'object') { /* also true for null, arrays! */ }

// ❌ Wrong: || treats 0 and '' as empty
const count = 0 || 10;     // 10 (bug, 0 was valid)

// ✅ Correct
if (value === null) { /* real null check */ }
const count2 = 0 ?? 10;    // 0 (only null/undefined fall back)
```

---

## 🎯 Interview Tip (1 line)
Say: "undefined is JS saying 'not assigned', null is me saying 'intentionally empty' — and I use `??` and `?.` to handle both."

---

## 🔗 Related Questions
→ Q028 (null == undefined) | Q038 (nullish coalescing) | Q039 (optional chaining) | Q140 (fix null/undefined bug)
