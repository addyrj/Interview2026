---

# Q256. Nullish Coalescing Tricks
# Category: ES6+ Features
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Show `??` tricks: difference from `||`, keeping `0`/`''`/`false`, chaining, mixing with `||`/`&&`, and use with `?.`.

---

## 💡 Quick Concept (2 lines only)
`a ?? b` returns `b` only when `a` is `null` or `undefined`; `||` falls back for ALL falsy values.
हिंदी: `??` सिर्फ null/undefined पर default देता है, `||` हर falsy value पर।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Compare ?? with ||
// Step 2: Chain defaults
// Step 3: Parenthesize when mixing with ||, &&

// Trick 1: ?? keeps valid falsy values
const count = 0;                                 // valid value
console.log(count || 10, count ?? 10);           // Expected: 10 0

// Trick 2: empty string and false
console.log('' || 'def', '' ?? 'def');           // Expected: def (second value is an empty string)
console.log(false || true, false ?? true);       // Expected: true false

// Trick 3: null/undefined trigger the default
console.log(null ?? 'x', undefined ?? 'y');      // Expected: x y

// Trick 4: chain multiple fallbacks
const cfg = { port: undefined, host: null };     // missing config
console.log(cfg.port ?? cfg.host ?? 3000);       // Expected: 3000

// Trick 5: mixing needs parentheses
// const bad = null || undefined ?? 'z';          // SyntaxError
console.log((null || undefined) ?? 'z');         // Expected: z

// Trick 6: with optional chaining
const settings = { theme: { size: 0 } };         // size is 0
console.log(settings?.theme?.size ?? 16);        // Expected: 0

// ============================================
// TEST CASES
// ============================================

console.log(NaN ?? 'n');                         // Expected: NaN
console.log(0 ?? null ?? 5);                     // Expected: 0
const fn = (v = 'default') => v;                 // default param only for undefined
console.log(fn(null), fn(undefined));            // Expected: null default
console.log(null ?? undefined);                  // Expected: undefined
```

---

## 🔍 Why This Works (3 lines max)
`??` checks strictly for nullish (`null`/`undefined`) instead of truthiness. That avoids bugs where legit `0`, `''` or `false` get replaced by a default.
हिंदी: `??` truthiness नहीं देखता, इसलिए 0 और false जैसी valid values safe रहती हैं।

---

## ⚡ Alternative Solution
```javascript
// Pre-ES2020 equivalent
const v = 0;                                     // value
const result = (v !== null && v !== undefined) ? v : 10; // manual nullish check
console.log(result);                             // Expected: 0
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: || for numeric defaults
const volume = 0;                                // user chose mute
console.log(volume || 50);                       // Expected: 50  (bug!)

// ✅ Correct: ??
console.log(volume ?? 50);                       // Expected: 0
```

---

## 🎯 Interview Tip (1 line)
Say: "Use ?? for defaults when 0, '' and false are valid; use || only when any falsy value should fall back."

---

## 🔗 Related Questions
→ Q038 (nullish output) | Q177 (explain nullish) | Q255 (optional chaining) | Q257 (logical assignment)
