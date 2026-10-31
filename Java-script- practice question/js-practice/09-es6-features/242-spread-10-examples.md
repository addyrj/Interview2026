---

# Q242. Spread — 10 Examples
# Category: ES6+ Features
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Show 10 practical uses of the spread operator (`...`) with arrays, strings, objects, Sets and function calls.

---

## 💡 Quick Concept (2 lines only)
Spread expands an iterable (or object) into individual elements/properties at the place where it is used.
हिंदी: Spread किसी array/object को खोलकर उसके अलग-अलग elements बना देता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Array uses (copy, concat, insert, string, Set)
// Step 2: Function-call uses (Math.max, args)
// Step 3: Object uses (copy, merge, immutable update)

// 1. Copy an array (shallow)
const orig = [1, 2];                             // original array
const copy = [...orig];                          // new array, same items
copy.push(3);                                    // mutate only the copy
console.log(orig, copy);                         // Expected: [ 1, 2 ] [ 1, 2, 3 ]

// 2. Concatenate arrays
console.log([...[1, 2], ...[3]]);                // Expected: [ 1, 2, 3 ]

// 3. String to characters
console.log([...'hey']);                         // Expected: [ 'h', 'e', 'y' ]

// 4. Pass array as arguments to Math.max
console.log(Math.max(...[3, 9, 2]));             // Expected: 9

// 5. Copy an object (shallow)
console.log({ ...{ a: 1 } });                    // Expected: { a: 1 }

// 6. Merge objects (later keys win)
console.log({ ...{ a: 1, b: 2 }, ...{ b: 3 } }); // Expected: { a: 1, b: 3 }

// 7. Immutable update of one property
const user = { name: 'Ria', age: 25 };           // original object
const older = { ...user, age: 26 };              // copy with changed age
console.log(user.age, older.age);                // Expected: 25 26

// 8. Set to array (dedupe)
console.log([...new Set([1, 1, 2])]);            // Expected: [ 1, 2 ]

// 9. Insert into the middle of an array
const arr = [1, 4];                              // original
console.log([...arr.slice(0, 1), 2, 3, ...arr.slice(1)]); // Expected: [ 1, 2, 3, 4 ]

// 10. Spread as function arguments
const sum = (a, b, c) => a + b + c;              // 3-arg function
console.log(sum(...[1, 2, 3]));                  // Expected: 6

// ============================================
// TEST CASES
// ============================================

const nested = [{ v: 1 }];                       // array with object inside
const shallow = [...nested];                     // shallow copy only
shallow[0].v = 99;                               // mutates shared inner object
console.log(nested[0].v);                        // Expected: 99
console.log({ ...null, ...undefined, ...'hi' }); // Expected: { '0': 'h', '1': 'i' }
```

---

## 🔍 Why This Works (3 lines max)
Spread calls the iterator (arrays/strings/Sets) or copies own enumerable properties (objects). The copy is shallow, so nested objects stay shared.
हिंदी: Spread सिर्फ shallow copy बनाता है, अंदर के objects का reference वही रहता है।

---

## ⚡ Alternative Solution
```javascript
// Older equivalents
const a = [1, 2].concat([3]);                    // concat instead of spread
const o = Object.assign({}, { x: 1 }, { y: 2 }); // assign instead of object spread
console.log(a, o);                               // Expected: [ 1, 2, 3 ] { x: 1, y: 2 }
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: spreading a plain object into an array
// const bad = [...{ a: 1 }];  // TypeError: object is not iterable

// ✅ Correct: spread values/entries instead
const good = [...Object.values({ a: 1 })];       // get iterable first
console.log(good);                               // Expected: [ 1 ]
```

---

## 🎯 Interview Tip (1 line)
Say: "Spread is a shallow copy; for deep copy use structuredClone" — and don't confuse it with rest.

---

## 🔗 Related Questions
→ Q040 (spread output) | Q179 (spread vs rest) | Q243 (rest) | Q260 (structuredClone)
