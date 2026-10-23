# 13. Loops — for, while, do-while, for-in, for-of
# हिंदी में: JavaScript के सभी Loops — कब कौन Use करें

---

## 🔵 Simple Definition (English)
Loops repeat a block of code. JavaScript has 5 types: `for` (counter-based), `while` (condition-based), `do-while` (runs at least once), `for-in` (object keys), `for-of` (iterable values). Plus array methods (`forEach`, `map`) as functional alternatives.

## 🔵 सरल परिभाषा (Hindi)
Loops code को बार-बार चलाते हैं। JavaScript में 5 types: `for` (counter), `while` (condition), `do-while` (कम से कम एक बार), `for-in` (object keys), `for-of` (iterable values)। Plus array methods functional alternative हैं।

---

## 🔴 Problem it Solves
Without loops:
```javascript
console.log(items[0]);
console.log(items[1]);
console.log(items[2]);
// ... 1000 items?
```
Loops handle repetition, iteration, and processing collections.

---

## 🟢 All 5 Loops at a Glance

```
┌────────────┬──────────────────────────────────────────────────┐
│ Loop       │ Best used for                                    │
├────────────┼──────────────────────────────────────────────────┤
│ for        │ Known iteration count, index needed              │
│ while      │ Unknown count, runs while condition true         │
│ do-while   │ Must run at least once (user input retry)        │
│ for-in     │ Object keys (not arrays — use for-of)           │
│ for-of     │ Array/string/Set/Map values (modern, preferred)  │
│ forEach    │ Array iteration without index manipulation       │
│ map/filter │ Transform/filter arrays (functional style)      │
└────────────┴──────────────────────────────────────────────────┘
```

---

## 🟡 Real World Example
```javascript
// Zomato: display restaurant list
const restaurants = ["Biryani Hub", "Pizza Palace", "Dosa Corner"];

// for-of: most readable for arrays
for (const restaurant of restaurants) {
  console.log(restaurant);
}

// Process cart items
let total = 0;
for (const item of cart) {
  total += item.price * item.qty;
}

// Retry logic (do-while)
let attempts = 0;
do {
  response = await fetchData();
  attempts++;
} while (!response.success && attempts < 3);
```

---

## 💻 Code Example — Basic
```javascript
// ── FOR LOOP ──────────────────────────
// Best when you know the count and need the index
for (let i = 0; i < 5; i++) {
  console.log(`Step ${i + 1}`);
}
// Step 1, Step 2, Step 3, Step 4, Step 5

// Array with index:
const fruits = ["apple", "banana", "mango"];
for (let i = 0; i < fruits.length; i++) {
  console.log(`${i}: ${fruits[i]}`);
}
// 0: apple, 1: banana, 2: mango

// ── WHILE LOOP ────────────────────────
// Best when you don't know the count
let count = 0;
while (count < 5) {
  console.log(`Count: ${count}`);
  count++; // don't forget — infinite loop without this!
}

// ── DO-WHILE ─────────────────────────
// Runs at least once, THEN checks condition
let num;
do {
  num = Math.floor(Math.random() * 10);
  console.log(`Got: ${num}`);
} while (num !== 5); // keep trying until we get 5
console.log("Found 5!");

// ── FOR-IN (Object keys) ─────────────
const user = { name: "Aditya", age: 25, city: "Mumbai" };

for (const key in user) {
  console.log(`${key}: ${user[key]}`);
}
// name: Aditya
// age: 25
// city: Mumbai

// ⚠️ Avoid for-in on arrays (use for-of)
const arr = [10, 20, 30];
for (const key in arr) {
  console.log(key); // "0", "1", "2" — string keys, not values!
}

// ── FOR-OF (Iterable values) ──────────
// Works on: arrays, strings, Set, Map, arguments, NodeList

// Array:
for (const fruit of fruits) {
  console.log(fruit); // "apple", "banana", "mango"
}

// String:
for (const char of "Hello") {
  console.log(char); // H, e, l, l, o
}

// With index using entries():
for (const [index, fruit] of fruits.entries()) {
  console.log(`${index}: ${fruit}`);
}
```

## 💻 Code Example — Advanced
```javascript
// ── FOR-OF on different iterables ────

// Set (unique values):
const uniqueTags = new Set(["js", "react", "js", "node"]);
for (const tag of uniqueTags) {
  console.log(tag); // "js", "react", "node" (no duplicate)
}

// Map:
const prices = new Map([["pizza", 299], ["burger", 149]]);
for (const [item, price] of prices) {
  console.log(`${item}: ₹${price}`);
}

// ── NESTED LOOPS ──────────────────────
// Multiplication table
for (let i = 1; i <= 3; i++) {
  for (let j = 1; j <= 3; j++) {
    process.stdout.write(`${i * j}\t`); // tab-separated
  }
  console.log(); // new line
}
// 1   2   3
// 2   4   6
// 3   6   9

// ── LOOP CONTROL: break and continue ──
// (full topic 14, but shown here in context)

// break: exit loop early
for (let i = 0; i < 10; i++) {
  if (i === 5) break; // stop at 5
  console.log(i); // 0, 1, 2, 3, 4
}

// continue: skip iteration
for (let i = 0; i < 10; i++) {
  if (i % 2 === 0) continue; // skip even numbers
  console.log(i); // 1, 3, 5, 7, 9 (odd numbers only)
}

// ── forEach vs for-of ─────────────────
const numbers = [1, 2, 3, 4, 5];

// forEach — can't break early, can't use await directly
numbers.forEach((num, index) => {
  console.log(`${index}: ${num}`);
});

// for-of — supports break, await, more flexible
for (const num of numbers) {
  if (num === 3) break; // can break!
  console.log(num);
}

// for-of with async/await (common pattern):
async function processItems(items) {
  for (const item of items) {
    await saveToDatabase(item); // sequential async — one at a time
  }
}

// ── PERFORMANCE COMPARISON ────────────
// Cache length for large arrays in for loop:
const bigArray = new Array(1000000).fill(1);

// Slightly slower (checks .length each iteration):
for (let i = 0; i < bigArray.length; i++) { /* ... */ }

// Faster (caches length):
for (let i = 0, len = bigArray.length; i < len; i++) { /* ... */ }

// for-of is clean and modern — use this:
for (const item of bigArray) { /* ... */ }
```

---

## 🟠 React/Next.js Connection
```jsx
// In JSX: use .map() for rendering lists (not for loops)
function ProductList({ products }) {
  return (
    <ul>
      {/* .map() returns array of JSX elements */}
      {products.map((product) => (
        <li key={product.id}>
          {product.name} — ₹{product.price}
        </li>
      ))}
    </ul>
  );
}

// Server-side (Node.js/Next.js API): for-of for async operations
export async function GET(request) {
  const orders = await getOrders();
  const results = [];

  // Sequential async processing:
  for (const order of orders) {
    const enriched = await enrichOrderData(order); // await works in for-of!
    results.push(enriched);
  }

  // Parallel (if order doesn't matter):
  const parallel = await Promise.all(orders.map(enrichOrderData));

  return Response.json({ results });
}

// useEffect with async loop:
useEffect(() => {
  async function fetchAll() {
    for (const id of selectedIds) {
      const data = await fetchItem(id);
      setItems(prev => [...prev, data]); // add one at a time
    }
  }
  fetchAll();
}, [selectedIds]);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `for-in` on arrays
```javascript
const arr = [10, 20, 30];

// WRONG: for-in gives string keys, not values
for (const key in arr) {
  console.log(arr[key]); // works but gives "0","1","2" keys
  // Also iterates inherited properties if array prototype is modified!
}

// CORRECT: for-of for values
for (const val of arr) {
  console.log(val); // 10, 20, 30
}
```

❌ **Mistake 2:** Infinite loop (missing increment/wrong condition)
```javascript
// WRONG: infinite loop!
let i = 0;
while (i < 5) {
  console.log(i);
  // forgot i++ — never terminates!
}

// CORRECT:
while (i < 5) {
  console.log(i);
  i++; // always update the loop variable
}
```

❌ **Mistake 3:** Using `await` inside `forEach`
```javascript
// WRONG: forEach ignores returned promises!
items.forEach(async (item) => {
  await processItem(item); // doesn't wait! all run in parallel without control
});
console.log("done"); // prints before items finish processing!

// CORRECT: use for-of for sequential async
for (const item of items) {
  await processItem(item); // waits for each one
}
console.log("done"); // prints after all done ✅

// Or for parallel (when order doesn't matter):
await Promise.all(items.map(processItem));
```

---

## 🧠 Tricky Interview Output Question
```javascript
for (var i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 0);
}

for (let j = 0; j < 3; j++) {
  setTimeout(() => console.log(j), 0);
}
```
**Answer:**
```
3   ← var: all share same i, loop finished at 3
3
3
0   ← let: each iteration has own j
1
2
```
**Why:** `var` is function-scoped — one shared `i`. By the time setTimeout runs, loop is done, i=3. `let` is block-scoped — new `j` per iteration, closure captures each one's value.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between for-in and for-of?**
A1: `for-in` iterates over **keys** (property names) of an object — gives strings like "0","1","2" for arrays, and also inherited properties. `for-of` iterates over **values** of any iterable (arrays, strings, Set, Map, generators) — gives actual values. Always prefer `for-of` for arrays and other iterables; use `for-in` only for plain objects.

**Q2: When would you use while vs for?**
A2: Use `for` when you know the number of iterations (array index, countdown). Use `while` when the number of iterations is unknown and depends on a condition (retry logic, polling, reading until EOF). `do-while` when you need to run at least once before checking the condition (prompting user until valid input).

**Q3: Why doesn't await work properly inside forEach?**
A3: `forEach` is a synchronous function that calls its callback for each element but doesn't wait for returned promises. So `async/await` inside forEach runs all promises concurrently without proper control, and code after forEach doesn't wait for them. Use `for-of` for sequential async processing, or `Promise.all(array.map(...))` for parallel.

**Q4: What is the difference between forEach and map?**
A4: `forEach` executes a function for each element for side effects (console.log, push to another array, etc.) — returns `undefined`. `map` transforms each element and returns a **new array** — doesn't mutate original. In React, always use `map` to render lists (JSX is a transformation).

**Q5: How can you break out of a forEach loop?**
A5: You can't — there is no way to break out of `forEach`. Options: use a regular `for` loop (supports `break`), use `for-of` (supports `break`), use `Array.some()` (stops when callback returns true), or throw an exception (ugly hack, avoid). `Array.every()` also stops when callback returns false.

---

## 🔷 Trade-offs / When to Use
✅ `for` — index needed, fine control, performance-critical
✅ `while` — retry, polling, unknown iteration count
✅ `do-while` — input validation, must run once first
✅ `for-in` — plain object key iteration only
✅ `for-of` — default for arrays and iterables (modern, readable)
✅ `forEach` — array side effects, simple iteration
✅ `map/filter/reduce` — functional transformations (no mutation)

❌ Avoid:
- `for-in` on arrays
- `forEach` with async/await
- Modifying array while iterating it

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Iteration | One pass through a loop | Loop का एक चक्र |
| Iterable | Object that can be looped with for-of | for-of से loop होने वाला |
| Iterator | Object with next() method | next() method वाला object |
| break | Exit loop early | Loop जल्दी बंद करना |
| continue | Skip current iteration | Current iteration skip करना |
| Infinite loop | Loop that never stops | कभी न रुकने वाला loop |
| forEach | Array method for side effects | Side effects के लिए array method |

---

## ⚡ 3-Line Summary
**English:**
1. Use `for-of` as your default for arrays and iterables — clean, supports `break` and `await`.
2. Use `for-in` only for plain object keys; use `while` for condition-based or unknown-count loops.
3. Never use `forEach` with async/await — use `for-of` instead; forEach ignores returned promises.

**Hindi:**
1. Arrays के लिए `for-of` default use करो — clean, `break` और `await` support करता है।
2. `for-in` सिर्फ plain objects के लिए; `while` unknown count के loops के लिए।
3. `forEach` में `async/await` मत use करो — `for-of` use करो; forEach promises ignore करता है।

---

## ➡️ Next Topic
**14. break + continue** — Loop control keywords का deep dive, labeled loops, और कब use करें।
