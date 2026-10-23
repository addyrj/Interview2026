# 17. Default Parameters
# हिंदी में: Default Parameters — Function में Default Values

---

## 🔵 Simple Definition (English)
Default parameters let you specify **fallback values** for function arguments. If the argument is `undefined` (not passed or explicitly `undefined`), the default is used. ES6 feature — cleaner than the old `param || default` pattern.

## 🔵 सरल परिभाषा (Hindi)
Default parameters से function arguments के लिए fallback values set होती हैं। Argument pass नहीं हुआ या `undefined` है तो default use होगा। ES6 feature — पुराने `param || default` से बेहतर।

---

## 🔴 Problem it Solves
Old way was error-prone:
```javascript
function greet(name) {
  name = name || "Guest"; // WRONG if name = "" or 0
  return `Hello, ${name}`;
}
```
Default params are cleaner and only trigger for `undefined` (not for `""`, `0`, or `false`).

---

## 🟢 How it Works
```javascript
function fn(a, b = 10, c = a * 2) {
  // b defaults to 10 if undefined
  // c defaults to a * 2 (can use earlier params!)
}

fn(5);          // a=5, b=10, c=10
fn(5, 20);      // a=5, b=20, c=10
fn(5, 20, 30);  // a=5, b=20, c=30
fn(5, undefined, 30); // a=5, b=10 (undefined triggers default), c=30
fn(5, null, 30);      // a=5, b=null (null does NOT trigger default!), c=30
```

---

## 🟡 Real World Example
```javascript
// API request with sensible defaults
async function fetchProducts({
  page = 1,
  limit = 20,
  sortBy = "price",
  order = "asc",
  category = "all"
} = {}) { // {} default so calling with no args works
  const url = `/api/products?page=${page}&limit=${limit}&sortBy=${sortBy}&order=${order}&category=${category}`;
  const res = await fetch(url);
  return res.json();
}

fetchProducts();                    // all defaults
fetchProducts({ page: 2 });        // page=2, rest defaults
fetchProducts({ category: "electronics", limit: 10 }); // mixed
```

---

## 💻 Code Example — Basic
```javascript
// ── BASIC DEFAULT PARAMS ──────────────

function greet(name = "Guest", message = "Welcome!") {
  return `${message} ${name}`;
}

console.log(greet());                  // "Welcome! Guest"
console.log(greet("Aditya"));          // "Welcome! Aditya"
console.log(greet("Aditya", "Hello")); // "Hello Aditya"
console.log(greet(undefined, "Hi"));   // "Hi Guest" (undefined = default)
console.log(greet(null, "Hi"));        // "Hi null"  (null ≠ undefined!)

// ── DEFAULT PREVENTS OLD || PATTERN ──

// OLD WAY (buggy for 0, "", false):
function createPageOld(size) {
  size = size || 10; // if size=0 → 10 (wrong!)
  return `Page size: ${size}`;
}
console.log(createPageOld(0)); // "Page size: 10" ← BUG!

// NEW WAY with default param:
function createPage(size = 10) {
  return `Page size: ${size}`;
}
console.log(createPage(0));  // "Page size: 0" ← CORRECT
console.log(createPage());   // "Page size: 10" ← correct default
```

## 💻 Code Example — Advanced
```javascript
// ── DEFAULTS CAN USE EARLIER PARAMS ──

function createUser(
  name,
  role = "user",
  email = `${name.toLowerCase()}@example.com`, // uses 'name'!
  createdAt = new Date().toISOString()           // dynamic default
) {
  return { name, role, email, createdAt };
}

console.log(createUser("Aditya"));
// { name: "Aditya", role: "user", email: "aditya@example.com", createdAt: "2024-..." }

console.log(createUser("Admin", "admin", "admin@company.com"));
// { name: "Admin", role: "admin", email: "admin@company.com", ... }

// ── DEFAULT WITH DESTRUCTURING ────────

// Object destructuring with defaults:
function displayProduct({ name = "Unknown", price = 0, qty = 1, currency = "INR" } = {}) {
  return `${name}: ${currency} ${(price * qty).toFixed(2)}`;
}

displayProduct({ name: "Pizza", price: 299, qty: 2 }); // "Pizza: INR 598.00"
displayProduct({ name: "Burger", price: 149 });          // "Burger: INR 149.00"
displayProduct({});                                      // "Unknown: INR 0.00"
displayProduct();                                        // "Unknown: INR 0.00" (= {} default)

// ── DEFAULT WITH FUNCTION CALL ─────────
function generateId() {
  return Math.random().toString(36).slice(2, 9);
}

function createItem(name, id = generateId()) { // called only if id is undefined
  return { name, id };
}

console.log(createItem("Pizza"));  // { name: "Pizza", id: "k7x2m9q" }
console.log(createItem("Burger")); // { name: "Burger", id: "p3n8r1t" } (new id!)
console.log(createItem("Pasta", "fixed-id")); // { name: "Pasta", id: "fixed-id" }

// ── REQUIRED PARAM PATTERN ────────────
function required(paramName) {
  throw new Error(`Parameter "${paramName}" is required`);
}

function fetchUser(id = required("id"), token = required("token")) {
  // If id or token not passed → Error thrown immediately
  return fetch(`/api/user/${id}`, {
    headers: { Authorization: `Bearer ${token}` }
  });
}

// fetchUser();       // Error: Parameter "id" is required
// fetchUser(1);      // Error: Parameter "token" is required
// fetchUser(1, "tok"); // works fine
```

---

## 🟠 React/Next.js Connection
```jsx
// ── COMPONENT DEFAULT PROPS ──────────

// Old way (PropTypes):
// ProductCard.defaultProps = { currency: "INR", showRating: true };

// Modern way: default params in destructuring
const ProductCard = ({
  product,
  currency = "INR",
  showRating = true,
  maxDescLength = 100,
  onAddToCart = () => {}, // default no-op function
}) => {
  const description = product.description?.slice(0, maxDescLength) ?? "No description";

  return (
    <div>
      <h3>{product.name}</h3>
      <p>{description}</p>
      <span>{currency} {product.price}</span>
      {showRating && <StarRating value={product.rating ?? 0} />}
      <button onClick={() => onAddToCart(product.id)}>Add to Cart</button>
    </div>
  );
};

// Usage:
// <ProductCard product={p} />                    — all defaults
// <ProductCard product={p} currency="USD" />     — override currency
// <ProductCard product={p} showRating={false} /> — hide rating

// ── API HANDLER WITH DEFAULTS ──────────
// Next.js API route
export async function GET(request) {
  const { searchParams } = new URL(request.url);

  const page = Number(searchParams.get("page")) || 1;
  const limit = Math.min(Number(searchParams.get("limit")) || 20, 100);
  const sortBy = searchParams.get("sortBy") || "createdAt";
  const order = searchParams.get("order") || "desc";

  const products = await getProducts({ page, limit, sortBy, order });
  return Response.json({ products, page, limit });
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `||` instead of default params for numbers/booleans
```javascript
// WRONG: || fails for 0, "", false
function setVolume(level) {
  level = level || 50; // level=0 → 50 (wrong!)
}

// CORRECT: default param
function setVolume(level = 50) {
  // level=0 → 0 ✅, level=undefined → 50 ✅
}
```

❌ **Mistake 2:** Putting default param before required param
```javascript
// WRONG: SyntaxError or confusing behavior
function create(name = "default", id) { // id is required but comes after default
  // create("Pizza") → name="Pizza", id=undefined (confusing!)
}

// CORRECT: required params first, defaults last
function create(id, name = "default") {
  // create(1) → id=1, name="default" ✅
}
```

❌ **Mistake 3:** Forgetting `= {}` for object destructuring default
```javascript
// WRONG: calling with no args throws
function config({ theme, lang }) {
  // ...
}
config(); // ❌ TypeError: Cannot destructure property 'theme' of undefined

// CORRECT: default the entire object
function config({ theme = "dark", lang = "en" } = {}) {
  // ...
}
config();             // ✅ theme="dark", lang="en"
config({ lang: "hi" }); // ✅ theme="dark", lang="hi"
```

---

## 🧠 Tricky Interview Output Question
```javascript
function test(a = 1, b = a + 1, c = a + b) {
  console.log(a, b, c);
}

test();          // ?
test(5);         // ?
test(5, 10);     // ?
test(undefined, undefined, 20); // ?
```
**Answer:**
```
1 2 3     ← a=1, b=1+1=2, c=1+2=3
5 6 11    ← a=5, b=5+1=6, c=5+6=11
5 10 15   ← a=5, b=10, c=5+10=15
1 2 20    ← a=1(default), b=2(default), c=20(explicit)
```

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between default params and `param || default`?**
A1: Default params only trigger when the argument is `undefined`. `||` triggers for any falsy value (0, "", false, null). For numbers or booleans, `param || default` gives wrong results — `0 || 10` gives 10 when 0 is valid. Default params are always correct: `fn(0)` uses 0, `fn()` uses the default.

**Q2: Does `null` trigger a default parameter?**
A2: No. Only `undefined` triggers default params. `fn(null)` uses null, not the default. This is different from `||` (which treats null as falsy) and similar to `??` (which only treats null/undefined as "missing").

**Q3: Can a default parameter reference another parameter?**
A3: Yes, a default can reference parameters defined before it: `function fn(a, b = a * 2)`. Parameters are evaluated left to right, so `b` can use `a` but not the other way around.

**Q4: What does `= {}` mean in destructuring default params?**
A4: `function fn({ a = 1 } = {})` — the `= {}` at the end is a default for the entire argument, not for `a`. It lets you call `fn()` without passing any argument (otherwise destructuring `undefined` would throw). The `= 1` after `a` is the default for the property.

**Q5: Are default parameters evaluated every time the function is called?**
A5: Yes — default expressions are evaluated fresh on each call where the parameter is needed. `function fn(arr = [])` gives a new empty array each call — unlike the old pattern where a shared array could be mutated. Functions as defaults are also called fresh: `fn(id = generateId())` generates a new id each time.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Default parameter | Fallback value when arg is undefined | Argument न मिले तो default |
| Undefined trigger | Only undefined uses the default | सिर्फ undefined पर default |
| Destructuring default | `= {}` for entire object param | पूरे object का default |
| Required param pattern | Throw if missing | न मिले तो error throw |

---

## ⚡ 3-Line Summary
**English:**
1. Default params give fallback values when arguments are `undefined` (not passed or explicitly undefined).
2. Unlike `||`, they work correctly for `0`, `""`, and `false` — only `undefined` triggers the default.
3. For object params with destructuring, always add `= {}` at the end to handle missing arguments.

**Hindi:**
1. Default params `undefined` होने पर fallback value देते हैं।
2. `||` से बेहतर — `0`, `""`, `false` के लिए सही काम करते हैं, सिर्फ `undefined` पर default।
3. Destructuring params के लिए `= {}` add करो ताकि बिना argument call हो सके।

---

## ➡️ Next Topic
**18. Rest Parameters (...args)** — अनजान number of arguments collect करना, `arguments` object से कैसे better है।
