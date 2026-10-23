# 21. Arrays — Basic Methods
# हिंदी में: Arrays — Basic Methods जो हर Interview में पूछे जाते हैं

---

## 🔵 Simple Definition (English)
An **array** is an ordered list of values. JavaScript arrays are dynamic (grow/shrink), can hold any type, and have a rich set of built-in methods. Most important: mutating methods (`push`, `pop`, `splice`) vs non-mutating (`slice`, `concat`, `spread`).

## 🔵 सरल परिभाषा (Hindi)
Array ordered list है। JavaScript arrays dynamic हैं, कोई भी type hold कर सकती हैं। Key distinction: mutating methods (`push`, `pop`, `splice`) vs non-mutating (`slice`, `concat`, spread)।

---

## 🔴 Problem it Solves
Without arrays, you'd need separate variables for every item — `item1`, `item2`, `item3`. Arrays let you store, access, and manipulate collections of data efficiently.

---

## 🟢 Methods Overview

```
MUTATING (change original):          NON-MUTATING (return new):
  push()      — add to end             slice()    — extract portion
  pop()       — remove from end        concat()   — combine arrays
  unshift()   — add to start           [...arr]   — copy (spread)
  shift()     — remove from start      indexOf()  — find index
  splice()    — add/remove anywhere    includes() — check presence
  sort()      — sort in place          join()     — to string
  reverse()   — reverse in place       flat()     — flatten nested
  fill()      — fill with value
```

---

## 🟡 Real World Example
```javascript
// Shopping cart operations
let cart = [];

// Add item
cart.push({ id: 1, name: "Pizza", price: 299 });    // [pizza]
cart.push({ id: 2, name: "Burger", price: 149 });   // [pizza, burger]

// Remove last
const lastRemoved = cart.pop();                       // [pizza]

// Check if item exists
const hasPizza = cart.some(item => item.id === 1);   // true

// Find item
const pizza = cart.find(item => item.name === "Pizza");

// Remove specific item (immutable way):
cart = cart.filter(item => item.id !== 1); // []
```

---

## 💻 Code Example — Basic
```javascript
// ── CREATING ARRAYS ───────────────────
const fruits = ["apple", "banana", "mango"];
const mixed = [1, "hello", true, null, { x: 1 }]; // any types
const empty = [];
const matrix = [[1,2], [3,4], [5,6]]; // nested
const filled = new Array(5).fill(0);   // [0, 0, 0, 0, 0]

// ── ACCESSING ────────────────────────
console.log(fruits[0]);           // "apple" (first)
console.log(fruits[fruits.length - 1]); // "mango" (last)
console.log(fruits.at(-1));       // "mango" (modern, negative index)
console.log(fruits.at(-2));       // "banana"

// ── MUTATING METHODS ─────────────────

const arr = [1, 2, 3];

// push — add to end, returns new length
arr.push(4);         // arr = [1,2,3,4], returns 4
arr.push(5, 6);      // arr = [1,2,3,4,5,6], returns 6

// pop — remove from end, returns removed element
const last = arr.pop(); // last = 6, arr = [1,2,3,4,5]

// unshift — add to start, returns new length
arr.unshift(0);      // arr = [0,1,2,3,4,5], returns 6

// shift — remove from start, returns removed element
const first = arr.shift(); // first = 0, arr = [1,2,3,4,5]

// splice(start, deleteCount, ...items)
arr.splice(2, 1);    // remove 1 item at index 2: arr = [1,2,4,5]
arr.splice(2, 0, 3); // insert 3 at index 2: arr = [1,2,3,4,5]
arr.splice(1, 2, 10, 20); // replace 2 items from index 1: arr = [1,10,20,4,5]

// sort (mutates!) — converts to string by default!
const nums = [10, 2, 9, 1, 5];
nums.sort();                      // [1, 10, 2, 5, 9] WRONG (string sort!)
nums.sort((a, b) => a - b);       // [1, 2, 5, 9, 10] correct ascending
nums.sort((a, b) => b - a);       // [10, 9, 5, 2, 1] descending

// reverse (mutates!)
[1, 2, 3].reverse(); // [3, 2, 1]

// ── NON-MUTATING METHODS ─────────────

const original = [1, 2, 3, 4, 5];

// slice(start, end) — end is exclusive
console.log(original.slice(1, 3)); // [2, 3]
console.log(original.slice(2));    // [3, 4, 5]
console.log(original.slice(-2));   // [4, 5] (last 2)
console.log(original);             // [1,2,3,4,5] unchanged!

// concat — merge arrays
const a = [1, 2];
const b = [3, 4];
const merged = a.concat(b, [5, 6]); // [1,2,3,4,5,6]
// Modern: [...a, ...b, 5, 6]

// indexOf / lastIndexOf
const colors = ["red", "blue", "red", "green"];
console.log(colors.indexOf("red"));     // 0 (first)
console.log(colors.lastIndexOf("red")); // 2 (last)
console.log(colors.indexOf("yellow"));  // -1 (not found)

// includes
console.log(colors.includes("blue"));   // true
console.log(colors.includes("purple")); // false

// join
console.log(["a", "b", "c"].join("-")); // "a-b-c"
console.log(["a", "b", "c"].join(""));  // "abc"
console.log(["a", "b", "c"].join());    // "a,b,c" (default comma)
```

## 💻 Code Example — Advanced
```javascript
// ── ARRAY DESTRUCTURING ───────────────
const [first2, second2, ...rest2] = [10, 20, 30, 40, 50];
// first2=10, second2=20, rest2=[30,40,50]

// Swap variables:
let x = 1, y = 2;
[x, y] = [y, x]; // x=2, y=1

// ── REMOVE DUPLICATES ─────────────────
const dupes = [1, 2, 2, 3, 3, 3, 4];
const unique = [...new Set(dupes)]; // [1, 2, 3, 4]

// ── FLATTEN ARRAYS ────────────────────
const nested = [[1, 2], [3, 4], [5, [6, 7]]];
console.log(nested.flat());   // [1, 2, 3, 4, 5, [6, 7]] (1 level)
console.log(nested.flat(2));  // [1, 2, 3, 4, 5, 6, 7] (2 levels)
console.log(nested.flat(Infinity)); // fully flatten any depth

// ── ARRAY.FROM ───────────────────────
Array.from("hello");          // ["h","e","l","l","o"]
Array.from({ length: 5 }, (_, i) => i + 1); // [1, 2, 3, 4, 5]
Array.from(new Set([1,2,3])); // [1, 2, 3]
Array.from(document.querySelectorAll("li")); // NodeList to Array

// ── ARRAY.OF ─────────────────────────
Array.of(1, 2, 3); // [1, 2, 3] (vs new Array(3) which gives [,,] with holes)

// ── SORTING OBJECTS ───────────────────
const products = [
  { name: "Burger", price: 149 },
  { name: "Pizza", price: 299 },
  { name: "Coke", price: 49 },
];

// Sort by price ascending:
products.sort((a, b) => a.price - b.price);
// [Coke, Burger, Pizza]

// Sort by name alphabetically:
products.sort((a, b) => a.name.localeCompare(b.name));
// [Burger, Coke, Pizza]

// ── COPY METHODS ─────────────────────
const arr2 = [1, 2, 3];
const copy1 = [...arr2];           // spread (shallow copy)
const copy2 = arr2.slice();        // slice with no args (shallow copy)
const copy3 = Array.from(arr2);    // Array.from (shallow copy)
const copy4 = arr2.concat();       // concat with no args (shallow copy)
// All 4 give new arrays — mutating copy won't affect original
```

---

## 🟠 React/Next.js Connection
```jsx
// Arrays drive almost everything in React
function ShoppingCart({ items }) {
  // Immutable add:
  const addItem = (newItem) => setItems(prev => [...prev, newItem]);

  // Immutable remove:
  const removeItem = (id) => setItems(prev => prev.filter(i => i.id !== id));

  // Immutable update:
  const updateQty = (id, qty) => setItems(prev =>
    prev.map(item => item.id === id ? { ...item, qty } : item)
  );

  // Sort for display (don't mutate state!):
  const sorted = [...items].sort((a, b) => a.price - b.price); // copy then sort

  // Total:
  const total = items.reduce((sum, item) => sum + item.price * item.qty, 0);

  return (
    <div>
      <p>Total: ₹{total}</p>
      {sorted.map(item => (
        <div key={item.id}>
          {item.name} — ₹{item.price}
          <button onClick={() => removeItem(item.id)}>Remove</button>
        </div>
      ))}
    </div>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Sorting numbers without comparator
```javascript
// WRONG: sorts as strings!
[10, 9, 2, 100].sort(); // [10, 100, 2, 9]

// CORRECT:
[10, 9, 2, 100].sort((a, b) => a - b); // [2, 9, 10, 100]
```

❌ **Mistake 2:** Mutating state array directly in React
```javascript
// WRONG:
const newItems = items;
newItems.push(item); // mutates original!
setItems(newItems);  // same reference — no re-render!

// CORRECT:
setItems(prev => [...prev, item]); // new reference → re-render
```

❌ **Mistake 3:** Using `indexOf` for objects (reference equality)
```javascript
const users = [{ id: 1 }, { id: 2 }];
users.indexOf({ id: 1 }); // -1! different object reference

// CORRECT: use findIndex
users.findIndex(u => u.id === 1); // 0 ✅
```

---

## 🧠 Tricky Interview Output Question
```javascript
const arr = [1, 2, 3, 4, 5];
const result = arr.splice(1, 2);

console.log(arr);    // ?
console.log(result); // ?
```
**Answer:**
```
[1, 4, 5]   ← splice mutates original — items 2,3 removed
[2, 3]      ← splice returns the removed elements
```

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between splice and slice?**
A1: `slice(start, end)` is non-mutating — returns a new array with the selected elements, original unchanged. `splice(start, deleteCount, ...items)` is mutating — modifies the original array, removes and/or inserts elements, returns removed elements. Rule: "slice gives a piece, splice changes the array."

**Q2: How do you sort an array of numbers correctly?**
A2: Use a comparator function: `arr.sort((a, b) => a - b)` for ascending, `(a, b) => b - a` for descending. Without a comparator, `sort()` converts to strings — `[10, 2, 9]` becomes `[10, 2, 9]` (wrong). Also: `sort` mutates the original — use `[...arr].sort(comparator)` to preserve original.

**Q3: What is the difference between push and concat (or spread)?**
A3: `push` mutates the original array and returns new length. `concat` and spread return a new array without touching the original. In React state updates, always use concat or spread — never push on state arrays.

**Q4: How do you remove duplicates from an array?**
A4: `[...new Set(arr)]` — convert to Set (which rejects duplicates) then back to array with spread. Works for primitives. For objects (by property): `arr.filter((item, index, arr) => arr.findIndex(i => i.id === item.id) === index)`.

**Q5: What is Array.from useful for?**
A5: Converting array-like objects or iterables to real arrays: DOM NodeLists (`Array.from(document.querySelectorAll("li"))`), strings, Sets, Maps, function `arguments`. Also creates arrays with a mapping function: `Array.from({ length: 5 }, (_, i) => i + 1)` gives `[1,2,3,4,5]`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Mutating | Changes original array | Original array बदलना |
| Non-mutating | Returns new, original unchanged | नया return, original वैसे |
| push/pop | Add/remove from end | अंत में add/remove |
| shift/unshift | Remove/add from start | शुरू में remove/add |
| splice | Add/remove anywhere (mutates) | कहीं भी add/remove (mutates) |
| slice | Extract portion (non-mutating) | हिस्सा लेना (non-mutating) |
| flat | Flatten nested arrays | Nested arrays को flat करना |

---

## ⚡ 3-Line Summary
**English:**
1. Mutating methods (`push`, `pop`, `splice`, `sort`) change the original — avoid in React state updates.
2. Non-mutating (`slice`, `concat`, spread) return new arrays — use these for React state.
3. Always use a comparator with `sort()` — default converts to strings giving wrong results for numbers.

**Hindi:**
1. Mutating methods original array बदलते हैं — React state में avoid करो।
2. Non-mutating (slice, concat, spread) नई array return करते हैं — React state के लिए यही।
3. `sort()` में हमेशा comparator दो — default string sort देता है, numbers के लिए wrong।

---

## ➡️ Next Topic
**22. Array Methods — map, filter, reduce, forEach, find, findIndex** — सबसे ज़्यादा use होने वाले functional array methods।
