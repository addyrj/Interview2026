# 24. Objects — Basics
# हिंदी में: Objects — JavaScript की रीढ़, हर जगह use होते हैं

---

## 🔵 Simple Definition (English)
An **object** is a collection of **key-value pairs** (properties). Keys are strings (or Symbols), values can be anything. Objects are the most fundamental data structure in JavaScript — arrays, functions, DOM nodes are all objects.

## 🔵 सरल परिभाषा (Hindi)
Object key-value pairs का collection है। Keys strings होती हैं, values कुछ भी। JavaScript में objects सबसे fundamental data structure हैं — arrays, functions, DOM nodes सब objects ही हैं।

---

## 🔴 Problem it Solves
```javascript
// Without objects — messy separate variables:
const userName = "Aditya";
const userAge = 25;
const userCity = "Mumbai";

// With objects — grouped, organized, passable:
const user = { name: "Aditya", age: 25, city: "Mumbai" };
```

---

## 🟢 How it Works
```javascript
// Object literal (most common):
const obj = {
  key: value,
  key2: value2,
};

// Access:
obj.key       // dot notation
obj["key"]    // bracket notation (needed for dynamic/special keys)

// Add/update:
obj.newKey = value;

// Delete:
delete obj.key;
```

---

## 🟡 Real World Example
```javascript
// Zomato order object
const order = {
  id: "ORD-2024-001",
  customer: { name: "Aditya", phone: "9876543210" },
  restaurant: "Pizza Hut",
  items: [
    { name: "Margherita", qty: 1, price: 299 },
    { name: "Coke", qty: 2, price: 49 },
  ],
  status: "preparing",
  total: 397,
  address: {
    line1: "Flat 302",
    area: "Bandra",
    city: "Mumbai",
    pincode: "400050",
  },
  createdAt: new Date(),
};

// Access nested:
console.log(order.customer.name);       // "Aditya"
console.log(order.items[0].name);       // "Margherita"
console.log(order.address.city);        // "Mumbai"
```

---

## 💻 Code Example — Basic
```javascript
// ── CREATING OBJECTS ─────────────────────

// 1. Object literal (most common):
const user = {
  name: "Aditya",
  age: 25,
  city: "Mumbai",
  isLoggedIn: true,
};

// 2. new Object() (avoid — more verbose):
const user2 = new Object();
user2.name = "Rajan";

// 3. Object.create() (prototypal inheritance):
const base = { greet() { return `Hi, ${this.name}`; } };
const derived = Object.create(base);
derived.name = "Priya";
derived.greet(); // "Hi, Priya"

// ── PROPERTY ACCESS ──────────────────────

// Dot notation:
console.log(user.name);  // "Aditya"
console.log(user.age);   // 25

// Bracket notation (dynamic keys):
const key = "city";
console.log(user[key]);  // "Mumbai" — can't do user.key (would look for "key")

// Undefined for missing:
console.log(user.email); // undefined (no error!)

// ── SHORTHAND PROPERTIES (ES6) ───────────

const name = "Aditya";
const age = 25;

// Old:
const oldUser = { name: name, age: age };

// Shorthand (same result):
const newUser = { name, age }; // same as { name: name, age: age }

// ── COMPUTED PROPERTY NAMES ──────────────

const field = "email";
const user3 = {
  [field]: "aditya@example.com",   // key is the VALUE of `field`
  [`${field}Verified`]: true,       // "emailVerified": true
};
console.log(user3.email);          // "aditya@example.com"
console.log(user3.emailVerified);  // true

// ── METHOD SHORTHAND ─────────────────────

// Old way:
const obj1 = {
  greet: function() { return "Hello!"; },
};

// Method shorthand (ES6):
const obj2 = {
  greet() { return "Hello!"; },        // cleaner
  async fetchData() { /* ... */ },      // async methods
  get fullName() { return `${this.firstName} ${this.lastName}`; }, // getter
};

// ── ADD / UPDATE / DELETE ────────────────

const product = { id: 1, name: "Pizza", price: 299 };

// Add new property:
product.category = "food";
product["inStock"] = true;

// Update:
product.price = 349;

// Delete:
delete product.category;
console.log(product); // { id: 1, name: "Pizza", price: 349, inStock: true }

// ── CHECK PROPERTY EXISTS ────────────────

console.log("name" in product);         // true (in operator)
console.log(product.hasOwnProperty("id")); // true (not inherited)
console.log(product.rating !== undefined);  // false (missing property)
// Prefer: "name" in obj over obj.name !== undefined (handles value = undefined)
```

## 💻 Code Example — Advanced
```javascript
// ── OBJECT DESTRUCTURING ─────────────────

const user = { name: "Aditya", age: 25, city: "Mumbai", role: "admin" };

// Basic:
const { name, age } = user;           // name="Aditya", age=25

// Rename while destructuring:
const { name: userName, age: userAge } = user;
// userName="Aditya", userAge=25

// Default values:
const { name: n, country = "India" } = user; // country="India" (missing key)

// Rest in destructuring:
const { name: n2, ...rest } = user;
// rest = { age: 25, city: "Mumbai", role: "admin" }

// Nested destructuring:
const order = { id: "ORD-001", customer: { name: "Priya", phone: "9999" } };
const { id, customer: { name: custName, phone } } = order;
// id="ORD-001", custName="Priya", phone="9999"

// ── OBJECT METHODS ───────────────────────

const obj = { a: 1, b: 2, c: 3 };

Object.keys(obj);    // ["a", "b", "c"]      — array of keys
Object.values(obj);  // [1, 2, 3]            — array of values
Object.entries(obj); // [["a",1],["b",2],["c",3]] — array of [key,value] pairs

// entries is great for iteration:
Object.entries(obj).forEach(([key, value]) => {
  console.log(`${key}: ${value}`);
});

// ── OBJECT.ASSIGN ────────────────────────

const defaults = { theme: "light", lang: "en", fontSize: 14 };
const userPrefs = { theme: "dark", fontSize: 16 };

// Merge (second arg overrides first):
const settings = Object.assign({}, defaults, userPrefs);
// { theme: "dark", lang: "en", fontSize: 16 }
// First arg {} prevents mutation — without it, defaults would be mutated!

// Modern equivalent with spread (preferred):
const settings2 = { ...defaults, ...userPrefs };

// ── OBJECT.FREEZE / OBJECT.SEAL ──────────

// freeze: no add, no modify, no delete
const config = Object.freeze({ API_KEY: "abc123", TIMEOUT: 5000 });
config.API_KEY = "hacked";  // silently fails in non-strict, throws in strict
console.log(config.API_KEY); // "abc123" — unchanged

// seal: no add/delete, but CAN modify existing
const sealed = Object.seal({ name: "Aditya", age: 25 });
sealed.age = 26;   // ✅ allowed
sealed.city = "Mumbai"; // ❌ silently fails
delete sealed.name; // ❌ silently fails

// ── OPTIONAL CHAINING ON OBJECTS ─────────

const order = { customer: { address: { city: "Mumbai" } } };

// Without optional chaining — crashes if customer is undefined:
const city = order && order.customer && order.customer.address && order.customer.address.city;

// With optional chaining:
const city2 = order?.customer?.address?.city; // "Mumbai"
const zip = order?.customer?.address?.zipcode; // undefined (no crash)
```

---

## 🟠 React/Next.js Connection
```jsx
// ── STATE AS OBJECTS ──────────────────────
function UserProfile() {
  const [user, setUser] = useState({
    name: "Aditya",
    age: 25,
    preferences: { theme: "dark", notifications: true },
  });

  // Update one field (immutable — must spread):
  const updateName = (name) => setUser(prev => ({ ...prev, name }));

  // Update nested field (spread both levels):
  const toggleTheme = () => setUser(prev => ({
    ...prev,
    preferences: {
      ...prev.preferences,
      theme: prev.preferences.theme === "dark" ? "light" : "dark",
    },
  }));

  return <div>{user.name} — {user.preferences.theme}</div>;
}

// ── DESTRUCTURING IN FUNCTION PARAMS ──────
// Very common React pattern — destructure props directly

// Without destructuring:
function ProductCard(props) {
  return <div>{props.name} — ₹{props.price}</div>;
}

// With destructuring (cleaner):
function ProductCard({ name, price, inStock, onAddToCart }) {
  return (
    <div>
      <h3>{name}</h3>
      <p>₹{price}</p>
      <button disabled={!inStock} onClick={() => onAddToCart({ name, price })}>
        {inStock ? "Add to Cart" : "Out of Stock"}
      </button>
    </div>
  );
}

// ── NEXT.JS API ROUTES ─────────────────────
export async function GET(request) {
  const { searchParams } = new URL(request.url);

  const filters = {
    category: searchParams.get("category"),
    minPrice: Number(searchParams.get("minPrice")) || 0,
    maxPrice: Number(searchParams.get("maxPrice")) || Infinity,
    inStock: searchParams.get("inStock") === "true",
  };

  // Object.entries to build dynamic query:
  const conditions = Object.entries(filters)
    .filter(([, value]) => value !== null && value !== undefined)
    .map(([key, value]) => `${key} = ${value}`)
    .join(" AND ");

  return Response.json({ filters, conditions });
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Mutating objects directly in React state
```javascript
// WRONG: same reference — React won't re-render
const handleUpdate = () => {
  user.name = "New Name"; // mutates!
  setUser(user);          // same reference, no re-render
};

// CORRECT: new object with spread
const handleUpdate = () => {
  setUser(prev => ({ ...prev, name: "New Name" }));
};
```

❌ **Mistake 2:** Forgetting `in` vs property access for existence check
```javascript
const obj = { count: 0, name: undefined };

// WRONG: both give wrong results
if (obj.count) { } // false! 0 is falsy — but key exists
if (obj.name !== undefined) { } // false! but key exists (value is undefined)

// CORRECT: use 'in' operator
if ("count" in obj) { }  // true ✅
if ("name" in obj) { }   // true ✅
if ("missing" in obj) { } // false ✅
```

❌ **Mistake 3:** `Object.assign` first arg mutation
```javascript
// WRONG: mutates 'defaults'!
const result = Object.assign(defaults, userPrefs);

// CORRECT: empty object as first arg
const result = Object.assign({}, defaults, userPrefs);
// OR use spread (cleaner):
const result = { ...defaults, ...userPrefs };
```

---

## 🧠 Tricky Interview Output Question
```javascript
const a = { x: 1 };
const b = a;
const c = { ...a };

b.x = 99;
c.x = 42;

console.log(a.x); // ?
console.log(b.x); // ?
console.log(c.x); // ?
```
**Answer:**
```
99   ← b is the SAME reference as a — b.x=99 changed a.x too
99   ← b and a are the same object
42   ← c is a SPREAD COPY — new object, independent
```

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between dot notation and bracket notation?**
A1: Dot notation (`obj.key`) is cleaner but the key must be a valid identifier. Bracket notation (`obj["key"]`) works for: dynamic keys (variables), keys with spaces/special characters, computed keys. Use bracket when the key is dynamic: `obj[someVariable]`. Dot notation otherwise.

**Q2: What are Object.keys, Object.values, Object.entries?**
A2: All three take an object and return arrays of its own enumerable properties. `keys` → array of keys. `values` → array of values. `entries` → array of `[key, value]` pairs. `entries` is most useful for iteration and conversion to Map. None include inherited (prototype) properties.

**Q3: What is the difference between `in` operator and `hasOwnProperty`?**
A3: `"key" in obj` returns true if the key exists on the object OR its prototype chain. `obj.hasOwnProperty("key")` returns true only for the object's own properties, not inherited ones. For plain objects, usually no difference. For objects with custom prototypes, `hasOwnProperty` is safer. Modern alternative: `Object.hasOwn(obj, "key")`.

**Q4: What is Object.freeze?**
A4: `Object.freeze(obj)` makes an object immutable — no adding, modifying, or deleting properties. In strict mode it throws; in non-strict it silently fails. Important: it's **shallow** — nested objects are NOT frozen. Use for constants: `const CONFIG = Object.freeze({ API_URL: "..." })`.

**Q5: How do you deep copy an object?**
A5: Several approaches: (1) `structuredClone(obj)` — modern, handles nested, most objects. (2) `JSON.parse(JSON.stringify(obj))` — simple but loses `undefined`, functions, Dates, Sets, Maps. (3) lodash `cloneDeep`. Spread (`{...obj}`) is shallow only — nested objects still share references.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Property | Key-value pair in an object | Object का key-value pair |
| Dot notation | obj.key — direct access | Direct access |
| Bracket notation | obj["key"] — dynamic access | Dynamic access |
| Destructuring | Extract properties into variables | Properties को variables में |
| Computed key | Key from expression `[expr]` | Expression से key |
| Shallow copy | Top-level copy only | सिर्फ ऊपरी level copy |
| Object.freeze | Make object immutable | Object को immutable बनाना |

---

## ⚡ 3-Line Summary
**English:**
1. Objects are key-value pairs — create with `{}`, access with `.` or `[]`, shorthand `{ name }` when variable matches key.
2. `Object.keys/values/entries` for iteration; spread for immutable merge/copy; destructuring for clean extraction.
3. Objects are reference types — `b = a` copies the reference; use spread or `structuredClone` for independent copies.

**Hindi:**
1. Objects key-value pairs हैं — `{}` से बनाओ, `.` या `[]` से access, shorthand `{ name }` जब variable = key।
2. Iteration के लिए `Object.keys/values/entries`; immutable merge के लिए spread; extraction के लिए destructuring।
3. Objects reference types हैं — `b = a` reference copy करता है; independent copy के लिए spread या `structuredClone` use करो।

---

## ➡️ Next Topic
**25. Object Methods — Object.keys, values, entries, assign, freeze, create** — Object manipulation के advanced methods।
