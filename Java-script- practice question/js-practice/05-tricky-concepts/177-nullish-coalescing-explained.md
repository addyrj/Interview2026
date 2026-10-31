---

# Q177. Explain Nullish Coalescing
# Category: Tricky Concepts
# Difficulty: ⭐ Easy

---

## ❓ Question
Explain the nullish coalescing operator `??` and how it differs from `||`. Include `??=` and the mixing rule with `||`/`&&`.

---

## 💡 Quick Concept (2 lines only)
`a ?? b` returns `b` only when `a` is `null` or `undefined`. `a || b` returns `b` for ANY falsy `a` (0, '', false, NaN).
हिंदी: `??` सिर्फ null/undefined पर default देता है, जबकि `||` हर falsy (0, '') पर देता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Use ?? when 0, '' and false are valid values
// Step 2: Use || only when every falsy value should fall back
// Step 3: Use ??= to assign only if currently null/undefined

const count = 0;                               // valid value zero
const name = '';                               // valid empty string
const flag = false;                            // valid boolean

console.log(count || 10);                      // 10  (wrong: 0 replaced)
console.log(count ?? 10);                      // 0   (correct)
console.log(name || 'guest');                  // guest
console.log(name ?? 'guest');                  // '' (empty kept)
console.log(flag ?? true);                     // false
console.log(null ?? 'default');                // default
console.log(undefined ?? 'default');           // default
console.log(NaN ?? 'x');                       // NaN (not nullish)

// Chaining
console.log(null ?? undefined ?? 'last');      // last

// Logical nullish assignment
const settings = { theme: null, size: 0 };     // sample config
settings.theme ??= 'dark';                     // assigned (was null)
settings.size ??= 16;                          // skipped (0 is not nullish)
console.log(settings);                         // { theme: 'dark', size: 0 }

// Mixing with || or && needs parentheses
// const bad = a || b ?? c;                    // SyntaxError
const ok = (null || undefined) ?? 'fine';      // parentheses make it legal
console.log(ok);                               // fine

// ============================================
// TEST CASES
// ============================================
// Expected output:
// 10
// 0
// guest
// 
// false
// default
// default
// NaN
// last
// { theme: 'dark', size: 0 }
// fine
```

---

## 🔍 Why This Works (3 lines max)
`??` checks strictly for `null` or `undefined`, so legitimate falsy values survive. It also short-circuits: the right side runs only when needed.
हिंदी: `??` सही falsy values (0, '', false) को बचाकर सिर्फ गायब values बदलता है।

---

## ⚡ Alternative Solution
```javascript
// Manual equivalent
const val = 0;                                 // input
const result = val !== null && val !== undefined ? val : 10; // same as val ?? 10
console.log(result);                           // Expected: 0
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Using || for defaults with numbers/booleans
const port = 0 || 3000;     // 3000 (bug: port 0 ignored)
const show = false || true; // true (bug)

// ✅ Use ??
const port2 = 0 ?? 3000;    // 0
```

---

## 🎯 Interview Tip (1 line)
Say: "?? falls back only for null/undefined; || falls back for all falsy — use ?? for config values like 0 and false."

---

## 🔗 Related Questions
→ Q038 (nullish output) | Q176 (optional chaining) | Q256 (nullish tricks) | Q257 (logical assignment)
