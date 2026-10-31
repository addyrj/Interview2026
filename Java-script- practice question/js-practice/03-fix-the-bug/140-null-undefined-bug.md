---

# Q140. Fix Null/Undefined Bug
# Category: Fix the Bug
# Difficulty: ⭐ Easy

---

## ❓ Question
`getCity` crashes for users without an address, and `||` replaces a valid `0` quantity with 1. Fix both.

```javascript
// BUGGY CODE:
const getCity = (user) => user.address.city;     // TypeError if address missing
const getQty = (item) => item.qty || 1;          // 0 becomes 1 (wrong)

console.log(getCity({ name: 'A' }));
console.log(getQty({ qty: 0 }));
```

---

## 💡 Quick Concept (2 lines only)
Use optional chaining `?.` to stop on null/undefined and nullish coalescing `??` to default only for null/undefined (not 0 or '').
हिंदी: `?.` null पर रुक जाता है और `??` सिर्फ null/undefined पर default देता है, 0 पर नहीं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

const getCity = (user) => user?.address?.city ?? 'Unknown'; // Step 1 (FIX): safe access + default
const getQty = (item) => item?.qty ?? 1;                    // Step 2 (FIX): keeps 0, defaults null/undefined

// ============================================
// TEST CASES
// ============================================

console.log(getCity({ name: 'A' }));              // Expected: Unknown
console.log(getCity({ address: { city: 'Pune' } })); // Expected: Pune
console.log(getCity(null));                       // Expected: Unknown
console.log(getQty({ qty: 0 }));                  // Expected: 0
console.log(getQty({}));                          // Expected: 1
```

---

## 🔍 Why This Works (3 lines max)
`?.` returns undefined instead of throwing when a link is null/undefined. `??` falls back only for null/undefined, so valid falsy values like 0 survive.
हिंदी: `?.` error की जगह undefined देता है, और `??` 0 या '' जैसी valid values को नहीं बदलता।

---

## ⚡ Alternative Solution
```javascript
// Pre-ES2020 style
const getCity2 = (u) => (u && u.address && u.address.city) || 'Unknown';
console.log(getCity2({})); // Unknown
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: || treats 0, '', false as missing
console.log(0 || 10, '' || 'x');   // 10 'x'
// ✅ Correct
console.log(0 ?? 10, '' ?? 'x');   // 0 ''
```

---

## 🎯 Interview Tip (1 line)
Say: "?. for safe access, ?? for defaults — and || only when I really want all falsy values replaced."

---

## 🔗 Related Questions
→ Q028 (null == undefined) | Q038 (nullish coalescing) | Q039 (optional chaining) | Q293 (null vs undefined)
