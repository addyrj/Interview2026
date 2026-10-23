# 26. Destructuring — Arrays and Objects
# हिंदी में: Destructuring — Values को Clean तरीके से Extract करना

---

## 🔵 Simple Definition (English)
**Destructuring** is a syntax for extracting values from arrays or properties from objects into separate variables. It makes code shorter and cleaner — especially in function parameters, React component props, and API response handling.

## 🔵 सरल परिभाषा (Hindi)
Destructuring arrays से values या objects से properties को अलग variables में extract करने का syntax है। Code shorter और clean बनता है — especially React props, function parameters, और API response handling में।

---

## 🔴 Problem it Solves
```javascript
// Without destructuring — repetitive, verbose:
const user = { name: "Aditya", age: 25, city: "Mumbai" };
const name = user.name;
const age = user.age;
const city = user.city;

// With destructuring — one line:
const { name, age, city } = user;
```

---

## 🟢 How it Works

```javascript
// ARRAY DESTRUCTURING — position-based
const [first, second, third] = [10, 20, 30];
// first=10, second=20, third=30

// OBJECT DESTRUCTURING — name-based
const { name, age } = { name: "Aditya", age: 25 };
// name="Aditya", age=25

// Key rule: array = position matters; object = key name matters
```

---

## 🟡 Real World Example
```javascript
// useState returns array — destructuring:
const [count, setCount] = useState(0);
const [user, setUser] = useState(null);

// API response object — destructuring:
const { data, error, loading } = useFetch("/api/products");

// Function returning multiple values (array):
function getMinMax(arr) {
  return [Math.min(...arr), Math.max(...arr)];
}
const [min, max] = getMinMax([3, 1, 4, 1, 5, 9, 2]); // min=1, max=9

// Component props destructuring:
function ProductCard({ name, price, inStock, onAddToCart }) {
  // Clean — no `props.name`, `props.price` everywhere
}
```

---

## 💻 Code Example — Basic
```javascript
// ── ARRAY DESTRUCTURING ──────────────────

// Basic positional extraction:
const [a, b, c] = [10, 20, 30];
console.log(a, b, c); // 10 20 30

// Skip elements with comma:
const [first, , third] = [1, 2, 3];
console.log(first, third); // 1 3

const [,, last] = [10, 20, 30];
console.log(last); // 30

// Default values:
const [x = 0, y = 0, z = 0] = [5, 10];
console.log(x, y, z); // 5 10 0 (z uses default)

// Rest in array destructuring:
const [head, ...tail] = [1, 2, 3, 4, 5];
console.log(head); // 1
console.log(tail); // [2, 3, 4, 5]

// Swap variables (classic trick!):
let m = 1, n = 2;
[m, n] = [n, m]; // m=2, n=1

// ── OBJECT DESTRUCTURING ─────────────────

const user = { name: "Aditya", age: 25, city: "Mumbai", role: "admin" };

// Basic:
const { name, age } = user;
// name="Aditya", age=25

// Rename variables:
const { name: userName, age: userAge } = user;
// userName="Aditya", userAge=25

// Default values:
const { name: n, country = "India" } = user;
// country="India" (key doesn't exist in user)

// Rest in object destructuring:
const { name: n2, ...rest } = user;
// n2="Aditya", rest={ age:25, city:"Mumbai", role:"admin" }

// ── NESTED DESTRUCTURING ─────────────────

// Nested object:
const order = {
  id: "ORD-001",
  customer: {
    name: "Aditya",
    address: { city: "Mumbai", pincode: "400001" }
  },
  total: 499,
};

const { id, customer: { name: cName, address: { city, pincode } } } = order;
// id="ORD-001", cName="Aditya", city="Mumbai", pincode="400001"
// Note: 'customer' is NOT a variable here — it's just the path

// Nested array of objects:
const products = [
  { id: 1, name: "Pizza", price: 299 },
  { id: 2, name: "Burger", price: 149 },
];

const [{ name: firstName, price: firstPrice }, { name: secondName }] = products;
// firstName="Pizza", firstPrice=299, secondName="Burger"
```

## 💻 Code Example — Advanced
```javascript
// ── FUNCTION PARAMETER DESTRUCTURING ─────

// Old — must access via param name:
function greet(user) {
  return `Hello, ${user.name}! You're ${user.age} years old.`;
}

// Destructure in params:
function greet({ name, age, greeting = "Hello" }) {
  return `${greeting}, ${name}! You're ${age} years old.`;
}

greet({ name: "Aditya", age: 25 });                        // "Hello, Aditya! You're 25 years old."
greet({ name: "Priya", age: 22, greeting: "Namaste" });    // "Namaste, Priya! You're 22 years old."

// ── MIXED ARRAY + OBJECT ──────────────────

// API response:
const response = {
  status: 200,
  data: {
    users: [
      { id: 1, name: "Aditya", scores: [85, 92, 78] },
      { id: 2, name: "Priya",  scores: [90, 88, 95] },
    ],
    total: 2,
  },
};

const { status, data: { users: [firstUser, secondUser], total } } = response;
const { name: u1Name, scores: [s1, s2] } = firstUser;
// u1Name="Aditya", s1=85, s2=92

// ── IMPORT DESTRUCTURING ─────────────────
// (How you import named exports from modules)
import { useState, useEffect, useCallback } from "react";
// This IS destructuring — pulling named exports from the module object

// ── FOR...OF WITH ENTRIES ─────────────────
const scores = { math: 85, science: 92, english: 78 };

for (const [subject, score] of Object.entries(scores)) {
  console.log(`${subject}: ${score}`); // destructuring in for..of!
}

// ── DESTRUCTURING IN .map() ───────────────
const users = [
  { id: 1, name: "Aditya", role: "admin" },
  { id: 2, name: "Priya",  role: "user"  },
];

// Without destructuring:
const names1 = users.map(user => user.name);

// With destructuring in callback:
const names2 = users.map(({ name }) => name); // cleaner

const formatted = users.map(({ id, name, role }) =>
  `${id}. ${name} (${role})`
);
// ["1. Aditya (admin)", "2. Priya (user)"]

// ── DYNAMIC KEY DESTRUCTURING ─────────────
const key = "name";
const { [key]: extractedName } = { name: "Aditya" };
// extractedName = "Aditya"

// Useful when key is dynamic:
function getField(obj, fieldName) {
  const { [fieldName]: value } = obj;
  return value;
}
getField(user, "city"); // "Mumbai"
```

---

## 🟠 React/Next.js Connection
```jsx
// ── PROPS DESTRUCTURING ───────────────────
// The most common React pattern

// Without destructuring:
function ProductCard(props) {
  return (
    <div>
      <h2>{props.product.name}</h2>
      <p>₹{props.product.price}</p>
      {props.product.inStock ? <span>In Stock</span> : <span>Sold Out</span>}
      <button onClick={() => props.onAddToCart(props.product)}>Add</button>
    </div>
  );
}

// With destructuring (much cleaner):
function ProductCard({ product: { name, price, inStock }, onAddToCart }) {
  return (
    <div>
      <h2>{name}</h2>
      <p>₹{price}</p>
      {inStock ? <span>In Stock</span> : <span>Sold Out</span>}
      <button onClick={() => onAddToCart({ name, price })}>Add</button>
    </div>
  );
}

// ── USESTATE PATTERN ─────────────────────
const [count, setCount] = useState(0);
const [{ name, email }, setUser] = useState({ name: "", email: "" });

// ── API HOOK RETURN ───────────────────────
// Custom hooks typically return arrays (like useState):
function usePagination(initialPage = 1) {
  const [page, setPage] = useState(initialPage);
  const next = () => setPage(p => p + 1);
  const prev = () => setPage(p => Math.max(1, p - 1));
  return [page, next, prev]; // return array for flexibility
}

const [currentPage, goNext, goPrev] = usePagination(1);

// ── NEXT.JS ROUTE PARAMS ──────────────────
// App Router:
export default function ProductPage({ params, searchParams }) {
  const { slug } = params;             // /products/[slug]
  const { sort = "price" } = searchParams; // ?sort=name
  // ...
}

// ── REDUCE RESULT DESTRUCTURING ──────────
function analyzeOrders(orders) {
  const { total, count, avgPrice } = orders.reduce((acc, order) => {
    acc.total += order.price;
    acc.count++;
    acc.avgPrice = acc.total / acc.count;
    return acc;
  }, { total: 0, count: 0, avgPrice: 0 });

  return { total, count, avgPrice };
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Destructuring nested that doesn't exist (crashes!)
```javascript
const user = { name: "Aditya" }; // no 'address' property

// WRONG: crashes if address is undefined
const { address: { city } } = user; // TypeError: Cannot destructure 'city' of undefined

// CORRECT: use default value or optional chaining
const { address: { city } = {} } = user; // city = undefined (no crash)
// OR:
const city = user?.address?.city; // undefined (no crash)
```

❌ **Mistake 2:** Confusing rename syntax
```javascript
const { name: username } = user;
// username = "Aditya"
// name is NOT a variable! (just the source key)
console.log(name);     // ❌ ReferenceError (or global)
console.log(username); // ✅ "Aditya"
```

❌ **Mistake 3:** Destructuring without `const/let/var`
```javascript
// WRONG: { is parsed as block, not destructuring
let a, b;
{ a, b } = { a: 1, b: 2 }; // SyntaxError!

// CORRECT: wrap in parentheses
({ a, b } = { a: 1, b: 2 }); // ✅
// OR use const/let:
const { a, b } = { a: 1, b: 2 }; // ✅
```

---

## 🧠 Tricky Interview Output Question
```javascript
const [a, b, ...c] = [1, 2, 3, 4, 5];
const { x: p, y: q = 10 } = { x: 5 };

console.log(a);  // ?
console.log(b);  // ?
console.log(c);  // ?
console.log(p);  // ?
console.log(q);  // ?
```
**Answer:**
```
1         ← a = first element
2         ← b = second element
[3, 4, 5] ← c = rest as array
5         ← p = value of x (renamed to p)
10        ← q = default (y doesn't exist in source)
```

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between array and object destructuring?**
A1: Array destructuring is **position-based** — the variable names are arbitrary, positions matter. `const [a, b] = [1, 2]` — `a` gets index 0, `b` gets index 1. Object destructuring is **name-based** — the variable names must match the keys (unless you rename). `const { name } = user` — pulls the `name` key. You can mix both for nested structures.

**Q2: How do you provide default values in destructuring?**
A2: Use `= defaultValue`. For arrays: `const [a = 0, b = 0] = [5]` → `a=5, b=0`. For objects: `const { name = "Guest" } = user` → uses "Guest" if `name` key is missing or `undefined`. Note: defaults only trigger for `undefined`, not `null`.

**Q3: How do you rename variables while destructuring?**
A3: In object destructuring, use `: newName` syntax: `const { name: userName } = user` creates `userName`, not `name`. This is the colon meaning "renamed to" (different from how colon works in object literals where it means "value is").

**Q4: What is nested destructuring and what are its risks?**
A4: Nested destructuring extracts from nested structures in one go: `const { a: { b: { c } } } = obj`. Risk: if any intermediate level is `null` or `undefined`, it throws. Always provide defaults for nullable levels: `const { address: { city } = {} } = user` prevents crashes when `address` is undefined.

**Q5: How is destructuring used in React?**
A5: (1) Props destructuring in function components: `function Card({ title, price })`. (2) `useState` returns `[value, setter]` — always destructured. (3) Importing named exports: `import { useState } from "react"`. (4) API responses — `const { data, error, loading } = useQuery(...)`. (5) `for...of Object.entries()` — `for (const [key, val] of ...)`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Destructuring | Extract values into variables | Values को variables में extract |
| Array destructuring | Position-based extraction | Position से extract |
| Object destructuring | Key name-based extraction | Key name से extract |
| Rename | `: newName` syntax | नया नाम देना |
| Default value | `= value` for missing/undefined | Missing के लिए default |
| Rest in destructuring | Collect remaining into array/obj | बाकी को collect करना |
| Nested destructuring | Extract from nested structures | Nested से extract |

---

## ⚡ 3-Line Summary
**English:**
1. Array destructuring = position-based; object destructuring = key name-based — use `= default` for missing values, `: rename` to rename.
2. Nested destructuring works but add `= {}` defaults for nullable levels to prevent crashes.
3. React uses it everywhere: props (`{ name, price }`), state (`[count, setCount]`), hooks, API responses.

**Hindi:**
1. Array destructuring = position से; object destructuring = key name से — missing के लिए `= default`, rename के लिए `: newName`।
2. Nested destructuring में nullable levels के लिए `= {}` default दो — crash रोको।
3. React में हर जगह: props (`{ name, price }`), state (`[count, setCount]`), hooks, API responses।

---

## ➡️ Next Topic
**27. for...in, for...of, forEach — Object और Array Iteration** — तीनों loops के differences और कब क्या use करें।
