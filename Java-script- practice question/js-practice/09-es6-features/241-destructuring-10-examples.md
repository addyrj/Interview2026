---

# Q241. Destructuring — 10 Examples
# Category: ES6+ Features
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Show 10 different destructuring patterns (array, object, rename, default, nested, rest, swap, params, computed key) with their output.

---

## 💡 Quick Concept (2 lines only)
Destructuring unpacks values from arrays/objects into variables using a pattern on the left side of `=`.
हिंदी: Destructuring से array/object की values सीधे variables में निकाल लेते हैं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Array patterns (basic, skip, swap)
// Step 2: Object patterns (basic, rename, default, nested, rest)
// Step 3: Function params + computed keys

// 1. Basic array destructuring
const [a1, a2] = [1, 2];                         // pick by position
console.log(a1, a2);                             // Expected: 1 2

// 2. Skip elements using empty slots
const [, second, , fourth] = [1, 2, 3, 4];       // commas skip items
console.log(second, fourth);                     // Expected: 2 4

// 3. Swap variables without temp
let x = 1, y = 2;                                // two variables
[x, y] = [y, x];                                 // swap in one line
console.log(x, y);                               // Expected: 2 1

// 4. Basic object destructuring
const { name, age } = { name: 'Aman', age: 25 }; // pick by key
console.log(name, age);                          // Expected: Aman 25

// 5. Rename while destructuring
const { name: userName } = { name: 'Aman' };     // key name -> variable userName
console.log(userName);                           // Expected: Aman

// 6. Default value when key is undefined
const { role = 'guest' } = {};                   // role missing -> default
console.log(role);                               // Expected: guest

// 7. Nested destructuring
const { address: { city } } = { address: { city: 'Delhi' } }; // go inside address
console.log(city);                               // Expected: Delhi

// 8. Rest in object destructuring
const { p, ...others } = { p: 1, q: 2, r: 3 };   // collect the remaining keys
console.log(others);                             // Expected: { q: 2, r: 3 }

// 9. Destructuring in function parameters (with default)
const greet = ({ name, greeting = 'Hi' }) => `${greeting} ${name}`; // unpack param
console.log(greet({ name: 'Ria' }));             // Expected: Hi Ria

// 10. Computed key destructuring
const key = 'color';                             // dynamic key
const { [key]: c } = { color: 'red' };           // read obj[key] into c
console.log(c);                                  // Expected: red

// ============================================
// TEST CASES
// ============================================

const [first = 10, next = 20] = [5];             // default for missing index
console.log(first, next);                        // Expected: 5 20
const { z = 1 } = { z: null };                   // null is NOT undefined
console.log(z);                                  // Expected: null
```

---

## 🔍 Why This Works (3 lines max)
The left side is a pattern matched against the right-side value; arrays match by position, objects by key. Defaults apply only when the value is `undefined`.
हिंदी: Array में position से और object में key से match होता है; default सिर्फ undefined पर लगता है।

---

## ⚡ Alternative Solution
```javascript
// Destructure from function return & loop entries
const getPoint = () => [3, 4];                   // returns an array
const [px, py] = getPoint();                     // unpack return value
console.log(px, py);                             // Expected: 3 4
for (const [k, v] of Object.entries({ m: 1 })) { // unpack each [key, value]
  console.log(k, v);                             // Expected: m 1
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: object destructuring assignment without parentheses
// let n; { n } = { n: 1 };   // SyntaxError: block, not a pattern

// ✅ Correct: wrap in parentheses
let n;                                           // declare first
({ n } = { n: 1 });                              // parentheses make it an expression
console.log(n);                                  // Expected: 1
```

---

## 🎯 Interview Tip (1 line)
Mention defaults only trigger on `undefined` (not `null`), and that nested destructuring throws if the parent is undefined.

---

## 🔗 Related Questions
→ Q042 (destructuring output) | Q178 (destructuring tricks) | Q242 (spread) | Q243 (rest)
