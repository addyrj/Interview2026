# 25. Object Methods — keys, values, entries, assign, freeze, create, fromEntries
# हिंदी में: Object Methods — Objects को Transform, Inspect और Control करना

---

## 🔵 Simple Definition (English)
JavaScript's `Object` has static utility methods for working with objects: inspecting properties (`keys/values/entries`), merging (`assign`), immutability (`freeze/seal`), prototypal creation (`create`), and rebuilding from pairs (`fromEntries`).

## 🔵 सरल परिभाषा (Hindi)
JavaScript के `Object` में static utility methods हैं: properties inspect करने के लिए (`keys/values/entries`), merge के लिए (`assign`), immutability के लिए (`freeze/seal`), prototype से बनाने के लिए (`create`), और pairs से rebuild के लिए (`fromEntries`)।

---

## 🟢 Quick Reference

```
Object.keys(obj)         → ["key1", "key2", ...]      (own enumerable keys)
Object.values(obj)       → [val1, val2, ...]           (own enumerable values)
Object.entries(obj)      → [["k1",v1],["k2",v2], ...]  (own enumerable pairs)
Object.assign(target, …) → target (merged, mutates target!)
Object.freeze(obj)       → obj (immutable — no add/edit/delete)
Object.seal(obj)         → obj (no add/delete, CAN edit existing)
Object.create(proto)     → new obj with proto as prototype
Object.fromEntries(iter) → object from [key,value] pairs
Object.hasOwn(obj, key)  → boolean (own property check, modern)
```

---

## 🟡 Real World Example
```javascript
// Transform price list using entries + fromEntries:
const prices = { pizza: 299, burger: 149, coke: 49 };

// Add 18% GST to all prices:
const pricesWithGST = Object.fromEntries(
  Object.entries(prices).map(([item, price]) => [item, +(price * 1.18).toFixed(2)])
);
// { pizza: 352.82, burger: 175.82, coke: 57.82 }

// Which items are under ₹200?
const affordable = Object.fromEntries(
  Object.entries(prices).filter(([, price]) => price < 200)
);
// { burger: 149, coke: 49 }
```

---

## 💻 Code Example — Basic
```javascript
const user = {
  name: "Aditya",
  age: 25,
  city: "Mumbai",
  role: "developer",
};

// ── OBJECT.KEYS ──────────────────────────
const keys = Object.keys(user);
// ["name", "age", "city", "role"]

// Common use: check number of properties:
console.log(Object.keys(user).length); // 4

// Iterate with for...of:
for (const key of Object.keys(user)) {
  console.log(`${key}: ${user[key]}`);
}

// ── OBJECT.VALUES ────────────────────────
const values = Object.values(user);
// ["Aditya", 25, "Mumbai", "developer"]

// Sum numeric values:
const scores = { math: 85, science: 92, english: 78 };
const total = Object.values(scores).reduce((sum, v) => sum + v, 0); // 255
const avg = total / Object.values(scores).length; // 85

// ── OBJECT.ENTRIES ───────────────────────
const entries = Object.entries(user);
// [["name","Aditya"],["age",25],["city","Mumbai"],["role","developer"]]

// Clean iteration with destructuring:
for (const [key, value] of Object.entries(user)) {
  console.log(`${key}: ${value}`);
}

// Build query string from object:
const params = { page: 1, limit: 10, sort: "price", order: "asc" };
const queryString = Object.entries(params)
  .map(([k, v]) => `${k}=${v}`)
  .join("&");
// "page=1&limit=10&sort=price&order=asc"

// ── OBJECT.ASSIGN ────────────────────────
const defaults = { theme: "light", lang: "en", notifications: true };
const userPrefs = { theme: "dark", fontSize: 16 };

// Merge (first arg is target — it gets mutated):
const config = Object.assign({}, defaults, userPrefs);
// { theme: "dark", lang: "en", notifications: true, fontSize: 16 }
// Note: {} is target — prevents mutating defaults

// Multiple sources — later overrides earlier:
const final = Object.assign({}, { a: 1 }, { b: 2 }, { a: 3 });
// { a: 3, b: 2 }

// ── OBJECT.FREEZE ────────────────────────
const CONFIG = Object.freeze({
  API_URL: "https://api.example.com",
  TIMEOUT: 5000,
  MAX_RETRIES: 3,
});

CONFIG.API_URL = "https://evil.com"; // silently fails (or throws in strict mode)
CONFIG.newKey = "value";             // silently fails
delete CONFIG.TIMEOUT;              // silently fails

console.log(CONFIG.API_URL); // "https://api.example.com" — unchanged
console.log(Object.isFrozen(CONFIG)); // true

// ── OBJECT.SEAL ──────────────────────────
const sealedUser = Object.seal({ name: "Aditya", age: 25 });
sealedUser.age = 26;       // ✅ can modify existing
sealedUser.city = "Mumbai"; // ❌ can't add new
delete sealedUser.name;    // ❌ can't delete

// ── OBJECT.FROMENTRIRES ──────────────────
// Rebuild object from entries array:

// Convert Map to object:
const map = new Map([["a", 1], ["b", 2], ["c", 3]]);
const obj = Object.fromEntries(map); // { a: 1, b: 2, c: 3 }

// Transform query string to object:
const query = "name=Aditya&age=25&city=Mumbai";
const parsed = Object.fromEntries(
  query.split("&").map(pair => pair.split("="))
);
// { name: "Aditya", age: "25", city: "Mumbai" }
```

## 💻 Code Example — Advanced
```javascript
// ── TRANSFORM OBJECTS WITH entries + fromEntries ──

// 1. Rename all keys to camelCase:
const snakeObj = { first_name: "Aditya", last_name: "Ranjan", user_id: 123 };

function toCamel(str) {
  return str.replace(/_([a-z])/g, (_, c) => c.toUpperCase());
}

const camelObj = Object.fromEntries(
  Object.entries(snakeObj).map(([k, v]) => [toCamel(k), v])
);
// { firstName: "Aditya", lastName: "Ranjan", userId: 123 }

// 2. Filter + transform in one pipeline:
const inventory = { pizza: 10, burger: 0, coke: 5, fries: 0, shake: 3 };

const availableMenu = Object.fromEntries(
  Object.entries(inventory)
    .filter(([, qty]) => qty > 0)    // only items with stock
    .map(([item, qty]) => [item, { qty, label: `${qty} left` }])
);
// { pizza: { qty:10, label:"10 left" }, coke: { qty:5, ... }, shake: { qty:3, ... } }

// 3. Invert object (swap keys and values):
const statusCode = { ok: 200, created: 201, notFound: 404, error: 500 };
const codeToStatus = Object.fromEntries(
  Object.entries(statusCode).map(([k, v]) => [v, k])
);
// { 200: "ok", 201: "created", 404: "notFound", 500: "error" }

// ── OBJECT.CREATE ────────────────────────
// Create object with specific prototype (prototypal inheritance)

const animal = {
  breathe() { return `${this.name} breathes`; },
  eat(food) { return `${this.name} eats ${food}`; },
};

const dog = Object.create(animal);
dog.name = "Rex";
dog.bark = function() { return "Woof!"; };

dog.breathe(); // "Rex breathes" — from prototype
dog.eat("bone"); // "Rex eats bone" — from prototype
dog.bark();    // "Woof!" — own method

// Check prototype:
Object.getPrototypeOf(dog) === animal; // true

// ── OBJECT.HASOWN (modern) ───────────────
// Better than hasOwnProperty for edge cases
const obj = Object.create({ inherited: true });
obj.own = "yes";

Object.hasOwn(obj, "own");       // true
Object.hasOwn(obj, "inherited"); // false (it's inherited)
"inherited" in obj;              // true (includes prototype chain)

// ── DEEP FREEZE UTILITY ──────────────────
// Object.freeze is shallow — nested objects aren't frozen
// Custom deep freeze:
function deepFreeze(obj) {
  Object.keys(obj).forEach(key => {
    if (typeof obj[key] === "object" && obj[key] !== null) {
      deepFreeze(obj[key]); // recurse into nested objects
    }
  });
  return Object.freeze(obj);
}

const config = deepFreeze({
  db: { host: "localhost", port: 5432 },
  cache: { ttl: 3600 },
});
config.db.host = "hacked"; // silently fails — deep frozen
```

---

## 🟠 React/Next.js Connection
```jsx
// ── DYNAMIC FORM RENDERING ───────────────
// Object.entries to render form fields dynamically

const FIELD_CONFIG = {
  name:  { label: "Full Name",    type: "text",     required: true },
  email: { label: "Email",        type: "email",    required: true },
  age:   { label: "Age",          type: "number",   required: false },
  city:  { label: "City",         type: "text",     required: false },
};

function DynamicForm() {
  const [values, setValues] = useState(
    Object.fromEntries(Object.keys(FIELD_CONFIG).map(k => [k, ""]))
  );
  // { name: "", email: "", age: "", city: "" }

  return (
    <form>
      {Object.entries(FIELD_CONFIG).map(([fieldName, config]) => (
        <div key={fieldName}>
          <label>{config.label}{config.required && " *"}</label>
          <input
            type={config.type}
            value={values[fieldName]}
            onChange={e => setValues(prev => ({ ...prev, [fieldName]: e.target.value }))}
          />
        </div>
      ))}
    </form>
  );
}

// ── BUILD API QUERY FROM STATE ────────────
function ProductFilter({ filters }) {
  // filters = { category: "food", minPrice: 100, inStock: true }

  const queryParams = Object.fromEntries(
    Object.entries(filters).filter(([, v]) => v !== "" && v !== null && v !== undefined)
  );
  // only non-empty filters

  const queryString = new URLSearchParams(queryParams).toString();
  const url = `/api/products?${queryString}`;

  return <a href={url}>Apply Filters</a>;
}

// ── CONSTANTS PATTERN ──────────────────────
// Object.freeze for enums/constants (common Next.js pattern)
export const ORDER_STATUS = Object.freeze({
  PENDING:   "pending",
  CONFIRMED: "confirmed",
  PREPARING: "preparing",
  DELIVERED: "delivered",
  CANCELLED: "cancelled",
});

// Usage: ORDER_STATUS.PENDING, ORDER_STATUS.DELIVERED
// Can't accidentally reassign: ORDER_STATUS.PENDING = "other" — fails
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** `Object.assign` without empty target
```javascript
const defaults = { theme: "light" };
const result = Object.assign(defaults, { theme: "dark" }); // MUTATES defaults!

// CORRECT: always use {} as first arg
const result = Object.assign({}, defaults, { theme: "dark" });
```

❌ **Mistake 2:** Expecting `freeze` to be deep
```javascript
const obj = Object.freeze({ nested: { value: 42 } });
obj.nested.value = 99; // ✅ works! nested is NOT frozen
console.log(obj.nested.value); // 99

// CORRECT: use deepFreeze utility or structuredClone + freeze
```

❌ **Mistake 3:** Using `Object.keys` on class instances (may miss inherited methods)
```javascript
class User {
  constructor(name) { this.name = name; }
  greet() { return `Hi ${this.name}`; } // on prototype, not own
}
const u = new User("Aditya");
Object.keys(u); // ["name"] — greet is NOT included (it's on prototype)

// If you need all methods: Object.getOwnPropertyNames(u)
```

---

## 🧠 Tricky Interview Output Question
```javascript
const obj = { a: 1, b: 2, c: 3 };

const doubled = Object.fromEntries(
  Object.entries(obj).map(([k, v]) => [k, v * 2])
);

const total = Object.values(doubled).reduce((s, v) => s + v, 0);

console.log(doubled); // ?
console.log(total);   // ?
console.log(Object.keys(obj).length === Object.keys(doubled).length); // ?
```
**Answer:**
```
{ a: 2, b: 4, c: 6 }  ← each value doubled
12                     ← 2+4+6
true                   ← both have 3 keys
```

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between Object.keys, values, and entries?**
A1: All three take an object and return an array of its **own enumerable** properties. `keys` → array of key strings. `values` → array of values. `entries` → array of `[key, value]` pairs. Use `entries` when you need both key and value (e.g., for transforming, filtering, or building query strings).

**Q2: What is Object.fromEntries and when would you use it?**
A2: `Object.fromEntries(iterable)` creates an object from an iterable of `[key, value]` pairs — the inverse of `Object.entries`. Common uses: (1) converting a Map to an object, (2) transforming all values of an object (`entries → map → fromEntries`), (3) filtering object keys, (4) parsing query strings.

**Q3: What is the difference between Object.freeze and Object.seal?**
A3: `freeze` = fully immutable — no add, no modify, no delete. `seal` = structure locked — no add/delete but you CAN modify existing values. Both are shallow (don't affect nested objects). Use `freeze` for constants/config; `seal` is rarely used in practice.

**Q4: What is Object.create used for?**
A4: Creates a new object with a specified prototype. `Object.create(proto)` gives the new object all of `proto`'s methods via the prototype chain. Used for prototypal inheritance patterns and creating objects without `new`. `Object.create(null)` creates a truly empty object with no prototype (no toString, no hasOwnProperty).

**Q5: Why prefer Object.hasOwn over hasOwnProperty?**
A5: `Object.hasOwn(obj, key)` is the modern alternative (ES2022+). `hasOwnProperty` can be shadowed if someone adds a property named `hasOwnProperty` to the object. `Object.hasOwn` also works on objects created with `Object.create(null)` which have no prototype at all. It's safer and cleaner.

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📝 Article | [javascript.info — Object methods](https://javascript.info/keys-values-entries) | keys/values/entries patterns |
| 📝 Article | [MDN — Object.fromEntries](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/fromEntries) | fromEntries use cases |
| 📝 Article | [MDN — Object.freeze](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/freeze) | Immutability deep dive |
| 📺 YouTube | [Akshay Saini — Objects in JS](https://www.youtube.com/results?search_query=objects+javascript+akshay+saini+namaste) | Objects deep dive |

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Object.keys | Array of own enumerable keys | Own keys की array |
| Object.entries | Array of [key,value] pairs | Key-value pairs की array |
| Object.assign | Merge objects (mutates target) | Objects merge करना |
| Object.freeze | Make object immutable | Object immutable बनाना |
| Object.fromEntries | Build object from pairs | Pairs से object बनाना |
| Object.create | Create with prototype | Prototype से बनाना |
| Enumerable | Property visible to for..in, Object.keys | दिखने वाली property |

---

## ⚡ 3-Line Summary
**English:**
1. `Object.keys/values/entries` — the trio for iteration; `entries` gives both, perfect for map/filter transforms with `fromEntries`.
2. `Object.assign({}, ...)` merges objects (spread preferred); `freeze` for immutable constants.
3. The power combo: `Object.fromEntries(Object.entries(obj).filter/map(...))` — transform any object cleanly.

**Hindi:**
1. `Object.keys/values/entries` — iteration trio; `entries` दोनों देता है, `fromEntries` के साथ transform के लिए perfect।
2. `Object.assign({}, ...)` merge करता है (spread बेहतर है); `freeze` immutable constants के लिए।
3. Power combo: `Object.fromEntries(Object.entries(obj).filter/map(...))` — कोई भी object cleanly transform करो।

---

## ➡️ Next Topic
**26. Destructuring — Arrays and Objects** — Clean extraction of values from arrays और objects।
