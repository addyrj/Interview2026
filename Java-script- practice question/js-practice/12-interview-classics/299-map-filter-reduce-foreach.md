---

# Q299. map vs forEach vs filter vs reduce
# Category: Interview Classics
# Difficulty: ⭐ Easy

---

## ❓ Question
Explain the difference between `map`, `forEach`, `filter`, and `reduce`. Show practical examples for each. When would you use each one?

---

## 💡 Quick Concept (2 lines only)
map = transform (same length), filter = select (shorter), reduce = accumulate (single value), forEach = side effects (no return value).
हिंदी: map = transform करो, filter = select करो, reduce = एक value बनाओ, forEach = side effects (return नहीं)।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

const products = [
  { name: 'Phone', price: 500, category: 'Electronics', stock: 5 },
  { name: 'Laptop', price: 1200, category: 'Electronics', stock: 0 },
  { name: 'Chair', price: 200, category: 'Furniture', stock: 10 },
  { name: 'Desk', price: 350, category: 'Furniture', stock: 3 },
  { name: 'Tablet', price: 400, category: 'Electronics', stock: 8 },
];

// ─── MAP: Transform each element → returns new array (same length) ───
const prices = products.map(p => p.price);
console.log(prices);  // [500, 1200, 200, 350, 400]

const displayItems = products.map(p => ({
  label: `${p.name} — ₹${p.price}`,
  inStock: p.stock > 0
}));
// [{ label: 'Phone — ₹500', inStock: true }, ...]

// ─── FILTER: Select elements matching condition → shorter array ───
const inStock = products.filter(p => p.stock > 0);
console.log(inStock.map(p => p.name));  // ['Phone', 'Chair', 'Desk', 'Tablet']

const electronics = products.filter(p => p.category === 'Electronics');
const affordable = products.filter(p => p.price < 500);

// ─── REDUCE: Accumulate to single value ───
const totalValue = products.reduce((sum, p) => sum + p.price, 0);
console.log(totalValue);  // 2650

// Group by category:
const grouped = products.reduce((acc, p) => {
  if (!acc[p.category]) acc[p.category] = [];
  acc[p.category].push(p.name);
  return acc;
}, {});
// { Electronics: ['Phone', 'Laptop', 'Tablet'], Furniture: ['Chair', 'Desk'] }

// Max price:
const maxPrice = products.reduce((max, p) => p.price > max ? p.price : max, 0);
console.log(maxPrice);  // 1200

// ─── FOREACH: Side effects (logging, DOM updates, mutations) ───
products.forEach(p => {
  console.log(`${p.name}: ₹${p.price}`);  // side effect: console.log
});

// Update external state:
const cart = [];
inStock.forEach(p => cart.push(p.name));  // side effect: mutation

// ============================================
// KEY DIFFERENCES TABLE (as comments)
// ============================================

/*
Method      Returns           Original array   Use when
─────────────────────────────────────────────────────────
map         new array         unchanged        Transform each element
filter      new array         unchanged        Select elements
reduce      single value      unchanged        Accumulate/combine
forEach     undefined         unchanged        Side effects only

PERFORMANCE: all are O(n). forEach is slightly faster (no return value tracking).
CHAINING: map/filter return arrays so they chain; forEach doesn't.
*/

// CHAINING EXAMPLE (elegant data pipeline):
const result = products
  .filter(p => p.stock > 0)         // only in-stock
  .filter(p => p.price < 600)        // affordable
  .map(p => ({ name: p.name, price: p.price }))  // pick fields
  .sort((a, b) => a.price - b.price); // sort by price

console.log(result);
// [{ name: 'Chair', price: 200 }, { name: 'Tablet', price: 400 }, { name: 'Phone', price: 500 }]
```

---

## 🔍 Why This Works (3 lines max)
map/filter return new arrays (pure, chainable). reduce accumulates to any type (number, object, array). forEach is for side effects and returns undefined — cannot be chained. Never use forEach when you need the result.
हिंदी: map/filter chain हो सकते हैं; reduce single value देता है; forEach undefined return करता है — chain नहीं होता।

---

## ⚡ Alternative Solution
```javascript
// reduce CAN do everything (but less readable):
const prices2 = products.reduce((acc, p) => [...acc, p.price], []);  // like map
const inStock2 = products.reduce((acc, p) => p.stock > 0 ? [...acc, p] : acc, []);  // like filter

// Real React use case:
const ProductList = ({ products }) => (
  <div>
    {products
      .filter(p => p.stock > 0)
      .map(p => <ProductCard key={p.name} product={p} />)
    }
  </div>
);

// Reduce for state in React:
const [cart, dispatch] = useReducer((state, action) => {
  switch (action.type) {
    case 'ADD': return [...state, action.item];
    case 'REMOVE': return state.filter(item => item.id !== action.id);
    default: return state;
  }
}, []);

// find (like filter but returns first match):
const laptop = products.find(p => p.name === 'Laptop');
// findIndex, some, every also useful
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: using forEach to build a new array
const doubled = [];
[1,2,3].forEach(n => doubled.push(n * 2));  // works but ugly
// ✅ Use map: const doubled = [1,2,3].map(n => n * 2);

// ❌ Wrong: using map for side effects (wasteful — creates array you don't use)
users.map(user => console.log(user.name));  // creates [undefined, undefined, ...]
// ✅ Use forEach: users.forEach(user => console.log(user.name));

// ❌ Wrong: forgetting initial value in reduce
[1,2,3].reduce((sum, n) => sum + n);  // works but risky (crashes on empty array)
[].reduce((sum, n) => sum + n);       // ❌ TypeError: empty array with no initial value
// ✅ Always provide initial value:
[].reduce((sum, n) => sum + n, 0);   // 0 — safe
```

---

## 🎯 Interview Tip (1 line)
Say: "map = transform (returns new array), filter = select, reduce = accumulate, forEach = side effects only — chain map+filter, not forEach."

---

## 🔗 Related Questions
→ Q112 (implement Array.map) | Q113 (implement Array.filter) | Q114 (implement Array.reduce) | Q064 (group by property — reduce)
