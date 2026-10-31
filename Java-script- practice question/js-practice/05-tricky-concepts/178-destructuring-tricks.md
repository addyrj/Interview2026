---

# Q178. Explain Destructuring Tricks
# Category: Tricky Concepts
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Show the most useful and tricky destructuring patterns: renaming, defaults, nested, rest, swapping, function parameters and computed keys.

---

## 💡 Quick Concept (2 lines only)
Destructuring unpacks arrays by position and objects by key into variables. You can rename (`a: b`), set defaults (`a = 1`), nest patterns and collect leftovers with `...rest`.
हिंदी: Destructuring से array/object की values सीधे variables में निकलती हैं — rename, default और nested के साथ।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Arrays -> by position, objects -> by key
// Step 2: Add rename / default / nested as needed
// Step 3: Use in params and for swapping

const user = { id: 1, name: 'Aditya', address: { city: 'Delhi' }, tags: ['a', 'b', 'c'] };

// 1. Rename + default
const { name: userName, role = 'guest' } = user;   // rename name, default role
console.log(userName, role);                       // Aditya guest

// 2. Nested
const { address: { city } } = user;                // pull city from nested object
console.log(city);                                 // Delhi

// 3. Rest in object
const { id, ...others } = user;                    // others = everything except id
console.log(Object.keys(others));                  // [ 'name', 'address', 'tags' ]

// 4. Array: skip, rest
const [first, , third, ...remaining] = [1, 2, 3, 4, 5]; // skip 2nd element
console.log(first, third, remaining);              // 1 3 [ 4, 5 ]

// 5. Swap without temp
let a = 1, b = 2;                                  // two variables
[a, b] = [b, a];                                   // swap
console.log(a, b);                                 // 2 1

// 6. Function parameters with defaults
function connect({ host = 'localhost', port = 80 } = {}) { // default for whole arg
  return `${host}:${port}`;                        // build string
}
console.log(connect({ port: 3000 }), connect());   // localhost:3000 localhost:80

// 7. Computed key
const key = 'name';                                // dynamic key
const { [key]: dynamic } = user;                   // read user[key]
console.log(dynamic);                              // Aditya

// 8. Default only for undefined (not null)
const { x = 5, y = 5 } = { x: null, y: undefined }; // null does not trigger default
console.log(x, y);                                 // null 5

// 9. Destructure from iterables / return values
const [h, ...chars] = 'hey';                       // string is iterable
console.log(h, chars);                             // h [ 'e', 'y' ]

// ============================================
// TEST CASES
// ============================================
// Expected output:
// Aditya guest
// Delhi
// [ 'name', 'address', 'tags' ]
// 1 3 [ 4, 5 ]
// 2 1
// localhost:3000 localhost:80
// Aditya
// null 5
// h [ 'e', 'y' ]
```

---

## 🔍 Why This Works (3 lines max)
The left side is a pattern matched against the right value. Defaults apply only when the value is `undefined`. Array patterns use the iterator protocol, object patterns use property lookup.
हिंदी: Left side एक pattern है जो right value से match होता है; default सिर्फ undefined पर लगता है।

---

## ⚡ Alternative Solution
```javascript
// Same without destructuring (more verbose)
const n = user.name, c = user.address.city;        // manual access
console.log(n, c);                                 // Expected: Aditya Delhi
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Starting a statement with { for assignment -> parsed as a block
// let p; { p } = { p: 1 };   // SyntaxError

// ✅ Wrap in parentheses
let p; ({ p } = { p: 1 });
console.log(p); // 1
```

---

## 🎯 Interview Tip (1 line)
Say: "Defaults trigger on undefined only; rename uses `key: alias`; array swap is `[a, b] = [b, a]`."

---

## 🔗 Related Questions
→ Q042 (destructuring output) | Q241 (destructuring 10 examples) | Q179 (spread vs rest) | Q043 (default parameters)
