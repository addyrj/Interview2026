---

# Q040. Spread Operator Output
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```javascript
const a = { x: 1, nested: { y: 2 } };
const b = { ...a, x: 9 };
b.nested.y = 99;
console.log(a.x, a.nested.y);
console.log([...'hi'], [...[1, 2], ...[3]]);
```

---

## 💡 Quick Concept (2 lines only)
Spread copies own enumerable properties/elements one level deep (shallow copy). Later keys override earlier ones.
हिंदी: Spread सिर्फ एक level की shallow copy बनाता है; nested object वही reference रहता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: b copies a's keys, then x is overridden to 9
// Step 2: a.x stays 1 (top-level primitive copied by value)
// Step 3: nested is shared by reference, so changing b.nested changes a.nested
// Step 4: strings and arrays spread into individual elements

const a = { x: 1, nested: { y: 2 } };       // original object
const b = { ...a, x: 9 };                   // shallow copy with x overridden
b.nested.y = 99;                            // mutates the SHARED nested object
console.log(a.x, a.nested.y);               // 1 99
console.log([...'hi'], [...[1, 2], ...[3]]); // [ 'h', 'i' ] [ 1, 2, 3 ]

// ============================================
// TEST CASES
// ============================================

console.log({ ...{ a: 1 }, ...{ a: 2 } });  // Expected: { a: 2 }
console.log(Math.max(...[3, 7, 5]));        // Expected: 7
console.log({ ...null, ...undefined });     // Expected: {}

// ============================================
// OUTPUT:
// ============================================
// 1 99
// [ 'h', 'i' ] [ 1, 2, 3 ]
// { a: 2 }
// 7
// {}
```

---

## 🔍 Why This Works (3 lines max)
Spread creates a new top-level container but copies nested references as-is. Primitive values are independent; objects inside are shared. Last-wins ordering decides duplicate keys.
हिंदी: Top-level नया बनता है पर अंदर के objects का reference वही रहता है, इसलिए a भी बदल जाता है।

---

## ⚡ Alternative Solution
```javascript
// True deep copy with structuredClone
const a = { x: 1, nested: { y: 2 } };  // original
const deep = structuredClone(a);       // fully independent copy
deep.nested.y = 99;                    // change copy only
console.log(a.nested.y);               // 2
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: thinking spread deep clones (React state bug)
const state = { user: { name: 'A' } };
const next = { ...state };
next.user.name = 'B';
console.log(state.user.name); // B (original mutated!)

// ✅ Correct: spread each nested level
const safe = { ...state, user: { ...state.user, name: 'C' } };
console.log(state.user.name, safe.user.name); // B C
```

---

## 🎯 Interview Tip (1 line)
Say: "Spread is a shallow copy, so for nested data I spread each level or use structuredClone."

---

## 🔗 Related Questions
→ Q041 (rest parameter) | Q071 (deep clone) | Q179 (spread vs rest)
