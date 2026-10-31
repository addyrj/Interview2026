---

# Q039. Optional Chaining Output
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```javascript
const user = { profile: null, greet() { return 'hi'; }, tags: ['js'] };
console.log(user.profile?.name);
console.log(user.address?.city);
console.log(user.greet?.());
console.log(user.missing?.());
console.log(user.tags?.[0]);
```

---

## 💡 Quick Concept (2 lines only)
`?.` stops and returns undefined if the left side is null/undefined instead of throwing a TypeError. Works for properties, methods and indexes.
हिंदी: ?. में left side null/undefined हो तो error की जगह undefined मिलता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: profile is null -> chain stops -> undefined
// Step 2: address is undefined -> chain stops -> undefined
// Step 3: greet exists -> called -> 'hi'
// Step 4: missing is undefined -> call skipped -> undefined
// Step 5: tags exists -> index 0 -> 'js'

const user = { profile: null, greet() { return 'hi'; }, tags: ['js'] }; // sample object
console.log(user.profile?.name);   // undefined (profile is null)
console.log(user.address?.city);   // undefined (address missing)
console.log(user.greet?.());       // hi (method exists)
console.log(user.missing?.());     // undefined (method missing, no call)
console.log(user.tags?.[0]);       // js (array index access)

// ============================================
// TEST CASES
// ============================================

try {
  console.log(user.profile.name);  // no ?. -> throws TypeError
} catch (e) {
  console.log(e instanceof TypeError); // Expected: true
}
console.log(user.profile?.a.b.c);  // Expected: undefined (whole chain short-circuits)
console.log(user.profile?.name ?? 'Anonymous'); // Expected: Anonymous

// ============================================
// OUTPUT:
// ============================================
// undefined
// undefined
// hi
// undefined
// js
// true
// undefined
// Anonymous
```

---

## 🔍 Why This Works (3 lines max)
When the value before `?.` is null/undefined, the rest of the chain is skipped entirely. Only null/undefined trigger it; other falsy values (0, "") continue normally.
हिंदी: null/undefined मिलते ही पूरी chain रुक जाती है; 0 या "" पर नहीं रुकती।

---

## ⚡ Alternative Solution
```javascript
// Old-school guard without optional chaining
const user = { profile: null };                                // sample
const name = user && user.profile && user.profile.name;        // guard chain
console.log(name); // null (note: returns null, not undefined)
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: using ?. on the assignment side
// user?.name = 'A';   // SyntaxError

// ✅ Correct: guard first
const user = {};                 // sample
if (user) user.name = 'A';       // normal assignment
console.log(user.name);          // A
```

---

## 🎯 Interview Tip (1 line)
Say: "?. short-circuits the whole chain on null/undefined, and I pair it with ?? for default values."

---

## 🔗 Related Questions
→ Q038 (nullish coalescing) | Q037 (short circuit) | Q176 (optional chaining explained)
