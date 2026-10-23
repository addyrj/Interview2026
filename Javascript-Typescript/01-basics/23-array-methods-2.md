# 23. Array Methods — some, every, flat, flatMap, includes, at
# हिंदी में: और ज़रूरी Array Methods — Interview में ये भी पूछे जाते हैं

---

## 🔵 Simple Definition (English)
`some` checks if **at least one** element passes. `every` checks if **all** elements pass. `flat` flattens nested arrays. `flatMap` maps then flattens. `includes` checks presence. `at` accesses by positive/negative index.

## 🔵 सरल परिभाषा (Hindi)
`some` — कम से कम एक pass हो। `every` — सब pass हों। `flat` — nested arrays को flatten करे। `flatMap` — map करो फिर flatten। `includes` — element है या नहीं। `at` — positive/negative index से access।

---

## 🟢 Quick Reference

```
arr.some(fn)      → boolean: true if ANY element matches
arr.every(fn)     → boolean: true if ALL elements match
arr.flat(depth)   → new array, nested arrays flattened
arr.flatMap(fn)   → map() then flat(1), in one pass
arr.includes(val) → boolean, uses === 
arr.at(index)     → element at index, supports negative (-1 = last)

Early exit: some() stops at first true, every() stops at first false
```

---

## 🟡 Real World Example
```javascript
const cartItems = [
  { id: 1, name: "Pizza",  price: 299, inStock: true,  tags: ["food", "italian"] },
  { id: 2, name: "Laptop", price: 49999, inStock: false, tags: ["tech", "electronics"] },
  { id: 3, name: "Burger", price: 149, inStock: true,  tags: ["food", "american"] },
];

// Can we checkout? All items must be in stock
const canCheckout = cartItems.every(item => item.inStock);
// false (Laptop is out of stock)

// Is any item out of stock? Show warning
const hasOutOfStock = cartItems.some(item => !item.inStock);
// true

// Get all tags as flat list:
const allTags = cartItems.flatMap(item => item.tags);
// ["food", "italian", "tech", "electronics", "food", "american"]

const uniqueTags = [...new Set(allTags)];
// ["food", "italian", "tech", "electronics", "american"]
```

---

## 💻 Code Example — Basic
```javascript
const scores = [85, 92, 78, 95, 60, 88];
const products = [
  { id: 1, name: "Pizza",  price: 299, inStock: true  },
  { id: 2, name: "Burger", price: 149, inStock: true  },
  { id: 3, name: "Laptop", price: 49999, inStock: false },
];

// ── SOME ────────────────────────────────
// Returns true if at least ONE element passes — early exit on first true

const hasPassing = scores.some(s => s >= 90);   // true (92 and 95 pass)
const hasExpensive = products.some(p => p.price > 10000); // true (Laptop)
const allOutOfStock = products.some(p => !p.inStock);     // true (Laptop)

// Good for existence checks:
const hasAdmin = ["user", "admin", "viewer"].some(role => role === "admin"); // true

// ── EVERY ───────────────────────────────
// Returns true if ALL elements pass — early exit on first false

const allPassing = scores.every(s => s >= 60);   // true (all ≥ 60)
const allInStock = products.every(p => p.inStock); // false (Laptop)
const allAffordable = products.every(p => p.price < 1000); // false

// Good for validation:
const isFormValid = [
  "name".length > 0,
  "email@test.com".includes("@"),
  "1234567890".length === 10,
].every(Boolean); // true (all conditions met)

// ── FLAT ────────────────────────────────
// Flatten nested arrays by depth

const nested1 = [1, [2, 3], [4, [5, 6]]];
console.log(nested1.flat());     // [1, 2, 3, 4, [5, 6]] (depth 1, default)
console.log(nested1.flat(2));    // [1, 2, 3, 4, 5, 6]   (depth 2)
console.log(nested1.flat(Infinity)); // fully flatten any depth

// Remove empty slots (holes):
const sparse = [1, 2, , 4, , 6]; // holes at index 2, 4
console.log(sparse.flat()); // [1, 2, 4, 6] — removes holes!

// ── FLATMAP ─────────────────────────────
// map() then flat(1) — more efficient than chaining

const sentences = ["Hello World", "Good Morning", "JavaScript Rocks"];

// Without flatMap:
const words1 = sentences.map(s => s.split(" ")).flat();
// [["Hello","World"], ["Good","Morning"], ["JavaScript","Rocks"]] then flat
// → ["Hello","World","Good","Morning","JavaScript","Rocks"]

// With flatMap — same result in one pass:
const words2 = sentences.flatMap(s => s.split(" "));
// ["Hello","World","Good","Morning","JavaScript","Rocks"]

// ── INCLUDES ────────────────────────────
// Check if value exists (uses ===)

const colors = ["red", "green", "blue"];
console.log(colors.includes("green")); // true
console.log(colors.includes("purple")); // false
console.log(colors.includes("RED"));   // false (case-sensitive!)

// includes finds NaN (unlike indexOf!):
const nums = [1, 2, NaN, 4];
console.log(nums.includes(NaN));    // true ✅
console.log(nums.indexOf(NaN));     // -1 ❌ (indexOf can't find NaN)

// ── AT ──────────────────────────────────
// Access by index — supports negative (from end)

const arr = ["a", "b", "c", "d", "e"];
console.log(arr.at(0));   // "a"  (first)
console.log(arr.at(1));   // "b"
console.log(arr.at(-1));  // "e"  (last)
console.log(arr.at(-2));  // "d"  (second from end)

// Old way to get last element:
arr[arr.length - 1];  // "e" — verbose
// New way:
arr.at(-1);           // "e" — clean ✅
```

## 💻 Code Example — Advanced
```javascript
// ── FORM VALIDATION WITH every ──────────
function validateOrder(order) {
  const validations = [
    { check: () => order.items.length > 0,        msg: "Cart is empty" },
    { check: () => order.items.every(i => i.inStock), msg: "Some items out of stock" },
    { check: () => order.address?.pincode?.length === 6, msg: "Invalid pincode" },
    { check: () => order.total > 0,               msg: "Invalid total" },
    { check: () => order.paymentMethod !== null,  msg: "Select payment method" },
  ];

  const failed = validations.filter(v => !v.check());
  return { valid: failed.length === 0, errors: failed.map(v => v.msg) };
}

// ── EXPAND + FLATTEN PATTERN ────────────
// flatMap is powerful for "expand each item into multiple items"

const orders = [
  { id: "ORD-1", items: ["Pizza", "Coke"] },
  { id: "ORD-2", items: ["Burger"] },
  { id: "ORD-3", items: ["Fries", "Shake", "Burger"] },
];

// All items across all orders:
const allItems = orders.flatMap(order => order.items);
// ["Pizza", "Coke", "Burger", "Fries", "Shake", "Burger"]

// Count each item:
const itemCount = allItems.reduce((acc, item) => {
  acc[item] = (acc[item] || 0) + 1;
  return acc;
}, {});
// { Pizza: 1, Coke: 1, Burger: 2, Fries: 1, Shake: 1 }

// ── FLATTEN API RESPONSE ────────────────
// API returns paginated results:
const pages = [
  { page: 1, data: [{ id: 1, name: "A" }, { id: 2, name: "B" }] },
  { page: 2, data: [{ id: 3, name: "C" }, { id: 4, name: "D" }] },
  { page: 3, data: [{ id: 5, name: "E" }] },
];

const allItems2 = pages.flatMap(page => page.data);
// [{ id:1 }, { id:2 }, { id:3 }, { id:4 }, { id:5 }]

// ── SOME/EVERY IN PERMISSIONS ──────────
const userPermissions = ["read", "write", "comment"];
const requiredPerms = ["read", "write"];
const adminPerms = ["admin", "delete"];

// Has ALL required permissions:
const canEdit = requiredPerms.every(p => userPermissions.includes(p)); // true

// Has ANY admin permission:
const isAdmin = adminPerms.some(p => userPermissions.includes(p)); // false

// ── FLATMAP TO FILTER AND MAP ────────────
// flatMap can conditionally include items (return [] to exclude):
const users = [
  { name: "Aditya", age: 25, isPremium: true  },
  { name: "Rajan",  age: 17, isPremium: false },
  { name: "Priya",  age: 22, isPremium: true  },
];

// Only premium adults, mapped to names:
const premiumAdultNames = users.flatMap(u =>
  u.age >= 18 && u.isPremium ? [u.name] : []  // [] excludes, [name] includes
);
// ["Aditya", "Priya"]

// This is equivalent to:
// users.filter(u => u.age >= 18 && u.isPremium).map(u => u.name)
// but in one pass
```

---

## 🟠 React/Next.js Connection
```jsx
// ── CHECKOUT BUTTON DISABLE ─────────────
function Cart({ items }) {
  const canCheckout = items.length > 0 && items.every(item => item.inStock);
  const hasOutOfStock = items.some(item => !item.inStock);

  return (
    <div>
      {hasOutOfStock && (
        <p className="text-red-500">
          Some items are out of stock. Remove them to continue.
        </p>
      )}
      <button disabled={!canCheckout} onClick={handleCheckout}>
        {canCheckout ? "Proceed to Checkout" : "Items Unavailable"}
      </button>
    </div>
  );
}

// ── NESTED CATEGORIES → FLAT LIST ────────
function CategoryMenu({ categories }) {
  // categories = [{ name: "Food", sub: ["Pizza", "Burger"] }, ...]
  const allSubcategories = categories.flatMap(cat =>
    cat.sub.map(s => ({ category: cat.name, name: s }))
  );
  // [{ category: "Food", name: "Pizza" }, { category: "Food", name: "Burger" }, ...]

  return (
    <select>
      {allSubcategories.map(item => (
        <option key={`${item.category}-${item.name}`} value={item.name}>
          {item.category} → {item.name}
        </option>
      ))}
    </select>
  );
}

// ── LAST N ITEMS WITH at() ────────────────
function RecentOrders({ orders }) {
  const lastOrder = orders.at(-1);    // most recent
  const secondLast = orders.at(-2);   // one before that

  return (
    <div>
      <h3>Latest: {lastOrder?.id}</h3>
      {secondLast && <p>Previous: {secondLast.id}</p>}
    </div>
  );
}

// ── API ROUTE: FLATTEN PERMISSIONS ────────
app.get("/api/user/:id/permissions", async (req, res) => {
  const user = await User.findById(req.params.id).populate("roles");

  // Each role has an array of permissions — flatten all:
  const allPermissions = user.roles.flatMap(role => role.permissions);
  const uniquePermissions = [...new Set(allPermissions)];

  // Check if user can access requested resource:
  const canAccess = req.query.required
    ? req.query.required.split(",").every(p => uniquePermissions.includes(p))
    : true;

  res.json({ permissions: uniquePermissions, canAccess });
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `every` on empty array (always returns true!)
```javascript
// GOTCHA: every() on empty array returns true (vacuous truth)
[].every(x => x > 100); // true! — because there are no counterexamples

// This can cause bugs in validation:
const items = [];
const allValid = items.every(i => i.price > 0); // true — but cart is empty!

// CORRECT: check length too
const isValidCart = items.length > 0 && items.every(i => i.price > 0);
```

❌ **Mistake 2:** Expecting `flat` to deep-flatten by default
```javascript
const data = [1, [2, [3, [4]]]];
data.flat();         // [1, 2, [3, [4]]] — only 1 level!
data.flat(Infinity); // [1, 2, 3, 4]    — fully flat
```

❌ **Mistake 3:** Using `includes` for objects (reference equality)
```javascript
const users = [{ id: 1 }, { id: 2 }];
users.includes({ id: 1 }); // false! Different reference

// CORRECT for objects: use some
users.some(u => u.id === 1); // true ✅
```

---

## 🧠 Tricky Interview Output Question
```javascript
const arr = [[1, 2], [3, 4], [5]];

const result1 = arr.flatMap(x => x);
const result2 = arr.flat();

console.log(result1); // ?
console.log(result2); // ?
console.log(result1.every(n => n % 2 === 0)); // ?
console.log(result1.some(n => n > 4));        // ?
```
**Answer:**
```
[1, 2, 3, 4, 5]   ← flatMap(x => x) = flat(1), same result
[1, 2, 3, 4, 5]   ← flat() defaults to depth 1
false              ← not ALL are even (1,3,5 are odd)
true               ← 5 > 4 is true, so some passes
```

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between some and every?**
A1: `some` returns true if **at least one** element passes — it stops (early exit) as soon as it finds a match. `every` returns true only if **all** elements pass — it stops as soon as it finds a failure. Think: `some` = OR logic, `every` = AND logic. Both return `false` / `true` for empty arrays respectively (vacuous truth).

**Q2: What is the difference between flat and flatMap?**
A2: `flat(depth)` only flattens without transforming. `flatMap(fn)` is `map(fn)` followed by `flat(1)` in one efficient pass. Use `flatMap` when each element should become multiple elements (e.g., split a string into words, expand tags, normalize nested data). Important: `flatMap` only flattens one level — for deeper flattening, chain with `.flat(n)`.

**Q3: How is includes different from indexOf for checking presence?**
A3: Both check if a value exists. Key differences: (1) `includes` returns a boolean; `indexOf` returns the index or -1. (2) `includes` can find `NaN` in an array; `indexOf` cannot (NaN !== NaN). (3) `includes` is cleaner to read for existence checks: `arr.includes(val)` vs `arr.indexOf(val) !== -1`.

**Q4: What is the `at()` method and why was it added?**
A4: `at(index)` accesses an element by index with support for negative indices. `arr.at(-1)` = last element, `arr.at(-2)` = second from last. It was added because `arr[-1]` doesn't work in JavaScript (it would look for a property named `"-1"`), and the old workaround `arr[arr.length - 1]` is verbose. `at` works on strings and TypedArrays too.

**Q5: Can flatMap return fewer items than the original array?**
A5: Yes — if the callback returns `[]` (empty array) for some elements, those are excluded from the result. This is a concise filter+map in one pass: `arr.flatMap(x => condition(x) ? [transform(x)] : [])`. Return `[value]` to include, `[]` to exclude, `[a, b]` to expand one item into two.

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [Akshay Saini — flatMap explained](https://www.youtube.com/results?search_query=flatmap+javascript+akshay+saini) | flatMap intuition |
| 📝 Article | [javascript.info — Iterables](https://javascript.info/array-methods#arr-some-every) | some/every/flat patterns |
| 📝 Article | [MDN — Array.prototype.flat](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/flat) | flat with depth |
| 📝 Article | [MDN — Array.prototype.flatMap](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/flatMap) | flatMap as filter+map |

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| some | At least one element matches | कम से कम एक match |
| every | All elements match | सब match हों |
| flat | Flatten nested arrays | Nested arrays को flatten |
| flatMap | Map then flat in one pass | Map + flatten एक साथ |
| includes | Check value presence | Value है या नहीं |
| at | Access by positive/negative index | Positive/negative index से access |
| vacuous truth | every() on empty = true | Empty array पर every() हमेशा true |

---

## ⚡ 3-Line Summary
**English:**
1. `some` = OR check (any match?), `every` = AND check (all match?) — both exit early.
2. `flat(depth)` flattens nested arrays; `flatMap(fn)` maps + flattens in one efficient pass.
3. `at(-1)` = last element; `includes` finds `NaN` (unlike `indexOf`).

**Hindi:**
1. `some` = OR check (कोई एक?), `every` = AND check (सब?) — दोनों early exit करते हैं।
2. `flat(depth)` nested flatten करता है; `flatMap` map + flatten एक pass में।
3. `at(-1)` = last element; `includes` NaN ढूंढ सकता है (indexOf नहीं)।

---

## ➡️ Next Topic
**24. Objects — Basics** — Object creation, property access, shorthand syntax, computed keys, और deletion।
