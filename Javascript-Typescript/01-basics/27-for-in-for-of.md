# 27. for...in, for...of, forEach — Iteration Methods
# हिंदी में: for...in, for...of, forEach — तीनों का Difference और कब क्या Use करें

---

## 🔵 Simple Definition (English)
Three iteration approaches: `for...in` iterates over **object keys** (enumerable properties), `for...of` iterates over **iterable values** (arrays, strings, Maps, Sets), `forEach` is an **array method** for running a function on each element (no break/continue).

## 🔵 सरल परिभाषा (Hindi)
तीन iteration approaches: `for...in` object keys पर iterate करता है, `for...of` iterable values (arrays, strings, Maps, Sets) पर, `forEach` array method है जो हर element पर function run करता है (break/continue नहीं होता)।

---

## 🟢 Quick Comparison

```
                  for...in      for...of         forEach
Works on:         Objects       Iterables        Arrays only
Gives you:        Keys          Values           Value + Index
Break/continue:   ✅ yes        ✅ yes           ❌ no
Return value:     undefined     undefined        undefined
Async/await:      ✅ works      ✅ works         ❌ buggy!
Use for:          Object keys   Array/Set/Map    Array side-effects
Skip inherited:   ⚠️ careful    N/A              ✅ own elements
```

---

## 🟡 Real World Example
```javascript
const order = { id: "ORD-001", total: 499, status: "preparing" };
const items = ["Pizza", "Burger", "Coke"];

// for...in — iterate object keys:
for (const key in order) {
  console.log(`${key}: ${order[key]}`);
}
// id: ORD-001 | total: 499 | status: preparing

// for...of — iterate array values:
for (const item of items) {
  console.log(`Item: ${item}`);
}
// Item: Pizza | Item: Burger | Item: Coke

// forEach — side effect per element:
items.forEach((item, index) => {
  console.log(`${index + 1}. ${item}`);
});
// 1. Pizza | 2. Burger | 3. Coke
```

---

## 💻 Code Example — Basic
```javascript
// ── FOR...IN ─────────────────────────────
// Iterates over ENUMERABLE KEYS of an object (and prototype chain!)

const user = { name: "Aditya", age: 25, city: "Mumbai" };

for (const key in user) {
  console.log(key, user[key]);
}
// name Aditya
// age 25
// city Mumbai

// WARNING: for...in includes inherited properties
function Person(name) { this.name = name; }
Person.prototype.greet = function() { return "Hi"; };

const p = new Person("Aditya");
for (const key in p) {
  console.log(key); // "name" AND "greet" (inherited!)
}

// Safe way: filter own properties:
for (const key in p) {
  if (Object.hasOwn(p, key)) { // or p.hasOwnProperty(key)
    console.log(key); // only "name"
  }
}

// ── FOR...OF ─────────────────────────────
// Iterates over VALUES of ANY iterable

// Array:
const fruits = ["apple", "banana", "mango"];
for (const fruit of fruits) {
  console.log(fruit); // apple, banana, mango
}

// String (character by character):
for (const char of "hello") {
  console.log(char); // h, e, l, l, o
}

// Set:
const uniqueIds = new Set([1, 2, 3, 2, 1]);
for (const id of uniqueIds) {
  console.log(id); // 1, 2, 3 (unique!)
}

// Map:
const scores = new Map([["math", 85], ["science", 92]]);
for (const [subject, score] of scores) {
  console.log(`${subject}: ${score}`);
}

// With index — use entries():
for (const [index, fruit] of fruits.entries()) {
  console.log(`${index}: ${fruit}`); // 0: apple, 1: banana...
}

// Break/continue work:
for (const num of [1, 2, 3, 4, 5]) {
  if (num === 3) break;    // stops at 3
  console.log(num);        // 1, 2
}

// ── FOREACH ──────────────────────────────
// Array method — callback runs for each element, no return value

const nums = [10, 20, 30, 40, 50];

nums.forEach((num, index, array) => {
  console.log(`[${index}] ${num} (of ${array.length})`);
});

// Cannot break out of forEach:
nums.forEach(num => {
  if (num === 30) return; // just skips this iteration (like continue)
  // NOT like break — loop continues with next element
  console.log(num); // 10, 20, 40, 50 (30 is skipped)
});
// If you need break, use for...of instead
```

## 💻 Code Example — Advanced
```javascript
// ── ASYNC AWAIT WITH LOOPS ────────────────

const orderIds = [1, 2, 3, 4];

// ❌ WRONG: forEach with async — promises not awaited
orderIds.forEach(async (id) => {
  const order = await fetchOrder(id); // runs concurrently, not sequentially!
  console.log(order); // random order
});

// ✅ CORRECT: for...of for sequential async:
for (const id of orderIds) {
  const order = await fetchOrder(id); // waits for each
  console.log(order); // 1, 2, 3, 4 in order
}

// ✅ CORRECT: if order doesn't matter — use Promise.all (faster):
const orders = await Promise.all(orderIds.map(id => fetchOrder(id)));

// ── FOR...IN FOR DYNAMIC OBJECT ACCESS ────
function printConfig(config) {
  for (const key in config) {
    if (Object.hasOwn(config, key)) { // guard against inherited
      console.log(`${key.toUpperCase()}: ${config[key]}`);
    }
  }
}

printConfig({ theme: "dark", lang: "en", fontSize: 16 });

// ── ITERATING OBJECTS WITH for...of ──────
// Objects are NOT iterable — can't do `for...of obj`
// Must convert first:

const user = { name: "Aditya", age: 25, city: "Mumbai" };

// Iterate keys:
for (const key of Object.keys(user)) {
  console.log(key);
}

// Iterate values:
for (const value of Object.values(user)) {
  console.log(value);
}

// Iterate pairs:
for (const [key, value] of Object.entries(user)) {
  console.log(`${key}: ${value}`);
}

// ── CUSTOM ITERABLES ─────────────────────
// Objects can be made iterable with [Symbol.iterator]

const range = {
  from: 1,
  to: 5,
  [Symbol.iterator]() {
    let current = this.from;
    const last = this.to;
    return {
      next() {
        return current <= last
          ? { value: current++, done: false }
          : { value: undefined, done: true };
      }
    };
  }
};

for (const num of range) {
  console.log(num); // 1, 2, 3, 4, 5
}
// [...range] // [1, 2, 3, 4, 5] — spread works too!
```

---

## 🟠 React/Next.js Connection
```jsx
// ── RENDER LISTS ────────────────────────
// Use .map() for rendering (not forEach — map returns array, forEach doesn't)

function MenuList({ categories }) {
  return (
    <nav>
      {/* for...of can't be used in JSX directly — use map */}
      {categories.map(cat => (
        <div key={cat.id}>
          <h3>{cat.name}</h3>
          <ul>
            {cat.items.map(item => (
              <li key={item.id}>{item.name} — ₹{item.price}</li>
            ))}
          </ul>
        </div>
      ))}
    </nav>
  );
}

// ── LOG/DEBUG IN DEVELOPMENT ─────────────
// forEach for side effects in event handlers or useEffect

useEffect(() => {
  // Log all state keys for debugging:
  for (const [key, value] of Object.entries(formState)) {
    if (!value) console.warn(`Field "${key}" is empty`);
  }
}, [formState]);

// ── NODE.JS: PROCESS RECORDS ─────────────
// Sequential async processing:
app.post("/api/bulk-order", async (req, res) => {
  const { orders } = req.body;
  const results = [];

  // Sequential — each waits for previous:
  for (const order of orders) {
    const result = await processOrder(order); // awaits each
    results.push(result);
  }

  res.json({ processed: results.length, results });
});

// Parallel — all at once (faster):
const results = await Promise.all(orders.map(processOrder));
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `for...in` on arrays
```javascript
const arr = ["a", "b", "c"];

// WRONG: for...in gives indices as strings, may include prototype props
for (const i in arr) {
  console.log(i); // "0", "1", "2" (strings, not numbers!)
}

// CORRECT: for...of for arrays
for (const item of arr) {
  console.log(item); // "a", "b", "c"
}
```

❌ **Mistake 2:** Expecting `forEach` to work with async/await
```javascript
// WRONG: forEach doesn't await callbacks
const ids = [1, 2, 3];
ids.forEach(async (id) => {
  await saveToDb(id); // fires all 3 at once, order not guaranteed
});

// CORRECT: for...of for sequential async
for (const id of ids) {
  await saveToDb(id); // sequential, guaranteed order
}
```

❌ **Mistake 3:** Using `return` in `forEach` expecting to exit the loop
```javascript
function findFirst(arr) {
  arr.forEach(item => {
    if (item > 3) return item; // ❌ only exits this callback, not the outer function!
  });
  // function always returns undefined
}

// CORRECT: use for...of with break, or .find()
function findFirst(arr) {
  for (const item of arr) {
    if (item > 3) return item; // ✅ exits the outer function
  }
}
// OR: arr.find(item => item > 3)
```

---

## 🧠 Tricky Interview Output Question
```javascript
const obj = { a: 1, b: 2 };
Object.prototype.extra = 99; // adds to prototype

const keys = [];
for (const key in obj) {
  keys.push(key);
}

const keys2 = [];
for (const key in obj) {
  if (Object.hasOwn(obj, key)) keys2.push(key);
}

console.log(keys);  // ?
console.log(keys2); // ?
```
**Answer:**
```
["a", "b", "extra"]  ← for...in includes inherited "extra"!
["a", "b"]           ← hasOwn filter removes inherited
```

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between for...in and for...of?**
A1: `for...in` iterates over **enumerable property keys** (strings) of an object, including inherited ones — use with `Object.hasOwn` guard. `for...of` iterates over **values** of any **iterable** (arrays, strings, Maps, Sets, generators). Plain objects are not iterable and will throw with `for...of`. Use `for...in` for objects, `for...of` for arrays and iterables.

**Q2: Why shouldn't you use forEach with async/await?**
A2: `forEach` doesn't return or handle the Promise returned by an async callback — it fires all callbacks simultaneously without waiting. Result: all async operations start at the same time in random completion order. Use `for...of` for sequential async (each waits for previous), or `Promise.all(arr.map(...))` for parallel async (all fire, but wait for all to complete).

**Q3: Can you break out of a forEach loop?**
A3: No — `forEach` has no way to break. A `return` inside the callback only exits the callback (equivalent to `continue`), not the loop. If you need early exit: use `for...of` with `break`, use `Array.some()` (return true to stop), or use `Array.find()` for "find first" scenarios.

**Q4: What iterables can for...of loop over?**
A4: Arrays, Strings (character by character), Maps, Sets, NodeLists (DOM), generators, any object with `[Symbol.iterator]`. Plain objects `{}` are NOT iterable — use `Object.entries(obj)` to make them iterable: `for (const [k, v] of Object.entries(obj))`.

**Q5: Which loop should you use in different scenarios?**
A5: `map/filter/reduce` for transforming arrays (functional, returns new arrays). `for...of` for arrays when you need break/continue, or for async iteration. `forEach` for side effects on arrays (logging, DOM updates) when you don't need break. `for...in` for iterating object keys (with `hasOwn` guard). `for` classic loop for precise index control.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| for...in | Iterates object keys | Object keys पर iterate |
| for...of | Iterates iterable values | Iterable values पर iterate |
| forEach | Array method, side effects | Array method, side effects |
| Iterable | Has [Symbol.iterator] | Iterate किया जा सके |
| Enumerable | Visible to for...in | for...in को दिखे |
| Inherited property | From prototype chain | Prototype से आई property |
| Sequential async | Await one by one | एक-एक करके await |

---

## ⚡ 3-Line Summary
**English:**
1. `for...in` = object keys (watch for inherited); `for...of` = iterable values (arrays, Maps, Sets, strings); `forEach` = array side-effects only.
2. For async: never use `forEach` — use `for...of` for sequential, `Promise.all(map)` for parallel.
3. In React: use `.map()` for rendering lists — `forEach` returns undefined so can't be used in JSX.

**Hindi:**
1. `for...in` = object keys (inherited से बचो); `for...of` = iterable values; `forEach` = array side-effects only।
2. Async में forEach कभी नहीं — sequential के लिए `for...of`, parallel के लिए `Promise.all(map)`।
3. React में rendering के लिए `.map()` — `forEach` undefined return करता है तो JSX में नहीं चलता।

---

## ➡️ Next Topic
**28. Scope — Global, Function, Block, Lexical** — Variables कहाँ accessible हैं और क्यों।
