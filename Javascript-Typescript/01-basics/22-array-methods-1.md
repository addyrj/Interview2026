# 22. Array Methods — map, filter, reduce, forEach, find, findIndex
# हिंदी में: सबसे ज़्यादा Use होने वाले Array Methods — Interview Must-Know

---

## 🔵 Simple Definition (English)
These are the **most used** functional array methods — every interview asks about them. `map` transforms, `filter` selects, `reduce` accumulates, `forEach` iterates for side effects, `find/findIndex` searches.

## 🔵 सरल परिभाषा (Hindi)
ये सबसे ज़्यादा use होने वाले array methods हैं — हर interview में पूछे जाते हैं। `map` transform करता है, `filter` select करता है, `reduce` accumulate करता है, `forEach` side effects के लिए, `find/findIndex` search के लिए।

---

## 🟢 Quick Reference

```
arr.map(fn)          → new array, transformed values    (same length)
arr.filter(fn)       → new array, elements where fn=true (≤ length)
arr.reduce(fn, init) → single accumulated value
arr.forEach(fn)      → undefined, runs fn for side effects
arr.find(fn)         → first element where fn=true (or undefined)
arr.findIndex(fn)    → index of first match (or -1)

All take callback: (element, index, array) => ...
None mutate the original!
```

---

## 🟡 Real World Example
```javascript
const orders = [
  { id: 1, product: "Pizza",  price: 299, qty: 2, status: "delivered" },
  { id: 2, product: "Burger", price: 149, qty: 1, status: "cancelled" },
  { id: 3, product: "Coke",   price: 49,  qty: 3, status: "delivered" },
  { id: 4, product: "Fries",  price: 99,  qty: 2, status: "pending" },
];

// map: add total for each order
const withTotal = orders.map(o => ({ ...o, total: o.price * o.qty }));

// filter: only delivered orders
const delivered = orders.filter(o => o.status === "delivered");

// reduce: total revenue from delivered orders
const revenue = delivered.reduce((sum, o) => sum + o.price * o.qty, 0);

// find: first delivered order
const firstDelivered = orders.find(o => o.status === "delivered");

// findIndex: index of order 3
const idx = orders.findIndex(o => o.id === 3); // 2
```

---

## 💻 Code Example — Basic
```javascript
const products = [
  { id: 1, name: "Pizza",  price: 299, category: "food",     inStock: true  },
  { id: 2, name: "Laptop", price: 49999, category: "tech",  inStock: false },
  { id: 3, name: "Burger", price: 149, category: "food",    inStock: true  },
  { id: 4, name: "Phone",  price: 29999, category: "tech",  inStock: true  },
  { id: 5, name: "Coffee", price: 99,  category: "food",    inStock: true  },
];

// ── MAP ───────────────────────────────
// Transform each element → returns new array of SAME length

// Extract just names:
const names = products.map(p => p.name);
// ["Pizza", "Laptop", "Burger", "Phone", "Coffee"]

// Add GST to each price:
const withGST = products.map(p => ({
  ...p,
  priceWithGST: parseFloat((p.price * 1.18).toFixed(2))
}));

// Index is available too:
const indexed = products.map((p, i) => `${i + 1}. ${p.name}`);
// ["1. Pizza", "2. Laptop", "3. Burger", "4. Phone", "5. Coffee"]

// ── FILTER ───────────────────────────
// Keep elements where callback returns true → new array ≤ original length

// In-stock items only:
const inStock = products.filter(p => p.inStock);
// [Pizza, Burger, Phone, Coffee]

// Food items under ₹200:
const cheapFood = products.filter(p => p.category === "food" && p.price < 200);
// [Burger, Coffee]

// ── REDUCE ───────────────────────────
// Accumulate → single value (number, string, object, array)

// Total price of all products:
const total = products.reduce((sum, p) => sum + p.price, 0);
console.log(total); // 80545

// Count by category:
const byCategory = products.reduce((acc, p) => {
  acc[p.category] = (acc[p.category] || 0) + 1;
  return acc;
}, {});
// { food: 3, tech: 2 }

// ── FOREACH ──────────────────────────
// Like map but returns undefined — for side effects only

products.forEach((p, i) => {
  console.log(`${i + 1}. ${p.name}: ₹${p.price}`);
});
// Side effects only — don't use when you need return value

// ── FIND ─────────────────────────────
// Returns FIRST matching element (not all, not index)

const laptop = products.find(p => p.name === "Laptop");
// { id: 2, name: "Laptop", ... }

const notFound = products.find(p => p.name === "iPad");
// undefined (not found)

// ── FINDINDEX ────────────────────────
// Returns INDEX of first match (-1 if not found)

const laptopIndex = products.findIndex(p => p.name === "Laptop");
// 1

const notFoundIndex = products.findIndex(p => p.name === "iPad");
// -1
```

## 💻 Code Example — Advanced
```javascript
// ── CHAINING METHODS ─────────────────
const result = products
  .filter(p => p.inStock)              // keep in-stock
  .filter(p => p.category === "food") // keep food items
  .map(p => ({                         // transform
    name: p.name,
    price: `₹${p.price}`,
    withGST: `₹${(p.price * 1.18).toFixed(2)}`
  }))
  .sort((a, b) => a.name.localeCompare(b.name)); // sort by name

// ── REDUCE — ADVANCED PATTERNS ────────

// Group by property:
const grouped = products.reduce((groups, product) => {
  const key = product.category;
  if (!groups[key]) groups[key] = [];
  groups[key].push(product);
  return groups;
}, {});
// { food: [Pizza, Burger, Coffee], tech: [Laptop, Phone] }

// Flat map (flatten after map):
const tags = [
  { name: "Pizza",  tags: ["food", "italian"] },
  { name: "Burger", tags: ["food", "american"] },
];
const allTags = tags.flatMap(p => p.tags); // [food, italian, food, american]
const uniqueTags = [...new Set(allTags)];  // [food, italian, american]

// Build object from array:
const priceMap = products.reduce((map, p) => {
  map[p.id] = p.price;
  return map;
}, {});
// { 1: 299, 2: 49999, 3: 149, 4: 29999, 5: 99 }

// ── MAP vs FOREACH ────────────────────
// map: use when you want a new array
const doubled = [1,2,3].map(n => n * 2); // [2,4,6]

// forEach: use when you just want to do something (no new array needed)
const logs = [];
[1,2,3].forEach(n => logs.push(n * 2)); // side effect: mutating logs

// WRONG: using forEach when map is right
const wrongDoubled = [];
[1,2,3].forEach(n => wrongDoubled.push(n * 2)); // verbose, use map!

// ── REDUCE vs FILTER+MAP PERFORMANCE ─
// Single reduce vs chained filter+map:
// For large arrays, single reduce is faster (one pass)
// For readability, filter+map is often clearer

// Single pass with reduce:
const { total2, count } = products.reduce((acc, p) => {
  if (p.inStock) {
    acc.total2 += p.price;
    acc.count++;
  }
  return acc;
}, { total2: 0, count: 0 });

// Two passes (clearer):
const stockedProducts = products.filter(p => p.inStock);
const sum2 = stockedProducts.reduce((t, p) => t + p.price, 0);
```

---

## 🟠 React/Next.js Connection
```jsx
// These methods power virtually all React rendering

function ProductCatalog({ products, filters, sortBy }) {
  // Chain to derive display data
  const displayProducts = products
    .filter(p => !filters.category || p.category === filters.category)
    .filter(p => !filters.minPrice || p.price >= filters.minPrice)
    .filter(p => filters.inStock ? p.inStock : true)
    .map(p => ({ ...p, discount: p.originalPrice ? 
      Math.round((1 - p.price / p.originalPrice) * 100) : 0 
    }))
    .sort((a, b) => sortBy === "price" ? a.price - b.price : 
                    sortBy === "name" ? a.name.localeCompare(b.name) : 0);

  const totalValue = displayProducts.reduce((sum, p) => sum + p.price, 0);
  const avgPrice = displayProducts.length > 0 
    ? (totalValue / displayProducts.length).toFixed(2) 
    : 0;

  return (
    <div>
      <p>Showing {displayProducts.length} products, avg ₹{avgPrice}</p>
      {displayProducts.map(product => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}

// API: transform DB results
app.get("/api/orders", async (req, res) => {
  const orders = await db.query("SELECT * FROM orders");

  const response = orders.rows
    .filter(o => o.user_id === req.user.id)
    .map(o => ({
      id: o.id,
      total: o.items.reduce((sum, item) => sum + item.price, 0),
      status: o.status,
      createdAt: o.created_at,
    }));

  res.json(response);
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `forEach` when `map` is needed
```javascript
// WRONG: verbose, unnecessary mutation
const doubled = [];
[1,2,3].forEach(n => doubled.push(n * 2));

// CORRECT: use map
const doubled = [1,2,3].map(n => n * 2);
```

❌ **Mistake 2:** Forgetting initial value in `reduce`
```javascript
// WRONG: crashes on empty array!
[].reduce((sum, n) => sum + n); // TypeError: Reduce of empty array with no initial value

// CORRECT: always provide initial value
[].reduce((sum, n) => sum + n, 0); // 0 ✅
```

❌ **Mistake 3:** Not returning inside `reduce`
```javascript
// WRONG: accumulator becomes undefined after first iteration
const result = [1,2,3].reduce((acc, n) => {
  acc.push(n * 2);
  // forgot return acc!
});

// CORRECT: always return accumulator
const result = [1,2,3].reduce((acc, n) => {
  acc.push(n * 2);
  return acc; // ← essential
}, []);
```

---

## 🧠 Tricky Interview Output Question
```javascript
const arr = [1, 2, 3, 4, 5];

const result = arr
  .filter(n => n % 2 !== 0)   // step 1
  .map(n => n * 3)              // step 2
  .reduce((sum, n) => sum + n, 0); // step 3

console.log(result); // ?
```
**Answer:** `27`
**Why:** filter → `[1,3,5]`, map → `[3,9,15]`, reduce → `3+9+15 = 27`

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between map and forEach?**
A1: `map` returns a new array of the same length with transformed values — use when you need the result. `forEach` returns `undefined` — use for side effects only (logging, DOM manipulation). In React, always use `map` to render lists since JSX needs the returned array.

**Q2: Explain reduce with an example.**
A2: `reduce(callback, initialValue)` processes each element and accumulates a single result. The callback receives `(accumulator, currentValue, index, array)` and must return the next accumulator. Example: sum all prices — start with 0, add each price to the running total. The power of reduce: it can implement `map`, `filter`, `groupBy`, and more.

**Q3: What is the difference between find and filter?**
A3: `find` returns the **first matching element** (or undefined). `filter` returns **all matching elements** as a new array (or empty array). Use `find` for "get one item by ID," use `filter` for "get all items matching a condition."

**Q4: What is the difference between findIndex and indexOf?**
A4: `indexOf` finds a specific value using `===` — works for primitives, not useful for objects. `findIndex` takes a callback function — works for any condition including object properties. For arrays of objects, always use `findIndex(item => item.id === targetId)`.

**Q5: Can reduce replace map and filter?**
A5: Yes. `arr.reduce((acc, item) => { acc.push(transform(item)); return acc; }, [])` is equivalent to `map`. `arr.reduce((acc, item) => { if (condition(item)) acc.push(item); return acc; }, [])` is equivalent to `filter`. But using reduce for these is less readable — use map/filter unless you need a single pass for performance.

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [Akshay Saini — Array methods](https://www.youtube.com/results?search_query=map+filter+reduce+javascript+akshay+saini) | Deep dive with polyfills |
| 📺 YouTube | [Web Dev Simplified — Reduce](https://www.youtube.com/results?search_query=javascript+reduce+explained+web+dev+simplified) | All reduce patterns with examples |
| 📝 Article | [javascript.info — Array methods](https://javascript.info/array-methods) | Complete reference |
| 📝 Article | [MDN — Array.prototype.reduce](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/reduce) | All reduce use cases |

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| map | Transform each element → new array | हर element transform करना |
| filter | Keep matching elements → new array | Matching elements रखना |
| reduce | Accumulate to single value | एक value में accumulate |
| forEach | Side effects, returns undefined | Side effects के लिए |
| find | First matching element | पहला matching element |
| findIndex | Index of first match | पहले match का index |
| accumulator | Running total in reduce | Reduce में running total |
| callback | Function passed to array method | Array method को दी function |

---

## ⚡ 3-Line Summary
**English:**
1. `map` → new array (transform), `filter` → subset (select), `reduce` → single value (accumulate), `forEach` → side effects only.
2. Chain them: `products.filter(inStock).map(addGST).sort(byPrice)` — each returns a new array.
3. Always provide an initial value to `reduce` and always return the accumulator.

**Hindi:**
1. `map` → नई array (transform), `filter` → subset (select), `reduce` → single value, `forEach` → side effects।
2. Chain करो: `products.filter().map().sort()` — हर method नई array देता है।
3. `reduce` में initial value हमेशा दो और accumulator हमेशा return करो।

---

## ➡️ Next Topic
**23. Array Methods — some, every, flat, flatMap, includes** — और ज़रूरी array methods।
