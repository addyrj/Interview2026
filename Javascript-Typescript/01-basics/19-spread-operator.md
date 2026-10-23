# 19. Spread Operator (...)
# हिंदी में: Spread Operator — Array/Object को Expand, Copy, और Merge करना

---

## 🔵 Simple Definition (English)
The **spread operator** (`...`) **expands** an iterable (array, string, Set) or object into individual elements. Same `...` syntax as rest params but **opposite direction**: rest collects many → one; spread expands one → many.

## 🔵 सरल परिभाषा (Hindi)
Spread operator (`...`) array/object को individual elements में **expand** करता है। Rest का उल्टा — rest: many → one; spread: one → many। Array copy, merge, function call — सब में use होता है।

---

## 🔴 Problem it Solves
Before spread:
```javascript
// Math.max doesn't accept array — old way:
Math.max.apply(null, [1, 5, 3]); // ugly

// Merge arrays — old way:
const merged = arr1.concat(arr2, arr3); // verbose

// Shallow copy:
const copy = Object.assign({}, original); // verbose
```
Spread makes all this clean and readable.

---

## 🟢 How it Works
```javascript
// In function calls: array → individual args
Math.max(...[1, 5, 3, 9, 2]) // = Math.max(1, 5, 3, 9, 2) → 9

// In array literals: combine arrays
const merged = [...arr1, ...arr2, "extra"]

// In object literals: merge/copy objects
const updated = { ...original, name: "New" }

// Spread a string:
[..."hello"] // ["h", "e", "l", "l", "o"]
```

---

## 🟡 Real World Example
```javascript
// React: immutable state updates
const cart = [{ id: 1, qty: 1 }, { id: 2, qty: 2 }];

// Add item:
const newCart = [...cart, { id: 3, qty: 1 }];

// Update item:
const updated = cart.map(item =>
  item.id === 2 ? { ...item, qty: item.qty + 1 } : item
);

// Merge user settings:
const defaults = { theme: "light", lang: "en", notifications: true };
const userPrefs = { theme: "dark", fontSize: 16 };
const settings = { ...defaults, ...userPrefs }; // user overrides defaults
// { theme: "dark", lang: "en", notifications: true, fontSize: 16 }
```

---

## 💻 Code Example — Basic
```javascript
// ── IN FUNCTION CALLS ─────────────────

const nums = [3, 1, 4, 1, 5, 9, 2, 6];

// Old way:
Math.max.apply(null, nums); // 9

// Spread way:
Math.max(...nums); // 9 ✅ clean!
Math.min(...nums); // 1

// Pass array as individual args:
function add(a, b, c) { return a + b + c; }
const args = [1, 2, 3];
add(...args); // same as add(1, 2, 3) → 6

// ── IN ARRAY LITERALS ────────────────

const fruits = ["apple", "banana"];
const veggies = ["carrot", "pea"];

// Merge arrays:
const food = [...fruits, ...veggies];
// ["apple", "banana", "carrot", "pea"]

// Add items:
const moreFruits = ["mango", ...fruits, "grape"];
// ["mango", "apple", "banana", "grape"]

// Shallow copy:
const fruitsCopy = [...fruits];
fruitsCopy.push("mango");
console.log(fruits);     // ["apple", "banana"] — unchanged
console.log(fruitsCopy); // ["apple", "banana", "mango"]

// ── IN OBJECT LITERALS ────────────────

const user = { name: "Aditya", age: 25 };

// Shallow copy:
const userCopy = { ...user };

// Override properties (later key wins):
const updatedUser = { ...user, age: 26, city: "Mumbai" };
// { name: "Aditya", age: 26, city: "Mumbai" }

// Merge objects:
const defaults = { theme: "light", lang: "en" };
const overrides = { theme: "dark", fontSize: 16 };
const config = { ...defaults, ...overrides };
// { theme: "dark", lang: "en", fontSize: 16 }

// ── SPREAD STRING ────────────────────
const chars = [..."hello"]; // ["h", "e", "l", "l", "o"]
const unique = [...new Set("mississippi")]; // ["m","i","s","p"] — unique chars!
```

## 💻 Code Example — Advanced
```javascript
// ── IMMUTABLE ARRAY OPERATIONS ────────

const items = [1, 2, 3, 4, 5];

// Immutable add at start:
const addedStart = [0, ...items]; // [0, 1, 2, 3, 4, 5]

// Immutable add at end:
const addedEnd = [...items, 6]; // [1, 2, 3, 4, 5, 6]

// Immutable add at index (insert at position 2):
const insertAt2 = [...items.slice(0, 2), 99, ...items.slice(2)];
// [1, 2, 99, 3, 4, 5]

// Immutable remove at index:
const removeAt2 = [...items.slice(0, 2), ...items.slice(3)];
// [1, 2, 4, 5]

// Convert Set to unique array:
const withDupes = [1, 2, 2, 3, 3, 3, 4];
const unique = [...new Set(withDupes)]; // [1, 2, 3, 4]

// ── SPREAD vs OBJECT.ASSIGN ───────────

// Object.assign and spread are mostly equivalent for shallow copy:
const copy1 = Object.assign({}, original);
const copy2 = { ...original }; // cleaner

// Difference: spread creates a plain object (no prototype methods)
class Person {
  constructor(name) { this.name = name; }
  greet() { return `Hi, I'm ${this.name}`; }
}
const p = new Person("Aditya");
const spread = { ...p };          // { name: "Aditya" } — greet() NOT copied!
const assigned = Object.assign({}, p); // { name: "Aditya" } — same, no prototype

// ── NESTED SPREAD (still shallow!) ────

const original = {
  name: "Aditya",
  address: { city: "Mumbai", pin: "400001" } // nested
};

const copy = { ...original };
copy.address.city = "Delhi"; // modifies original.address.city too!
// Spread is SHALLOW — nested objects still share reference

// Deep copy: use structuredClone or JSON trick
const deepCopy = structuredClone(original);
deepCopy.address.city = "Delhi"; // original unchanged ✅

// ── SPREAD WITH CONDITIONAL ──────────
const isAdmin = true;
const userObj = {
  name: "Aditya",
  role: "user",
  ...(isAdmin && { role: "admin", adminSince: "2024" }), // conditional spread!
};
// if isAdmin: { name, role: "admin", adminSince }
// else: { name, role: "user" }

// Conditional array items:
const showExtras = true;
const menu = [
  "Home",
  "Profile",
  ...(showExtras ? ["Admin", "Settings"] : []),
];
```

---

## 🟠 React/Next.js Connection
```jsx
// ── REACT STATE IMMUTABILITY ───────────

// Update nested state:
const [user, setUser] = useState({ name: "Aditya", address: { city: "Mumbai" } });

// Update top-level property:
setUser(prev => ({ ...prev, name: "Rajan" }));

// Update nested property (shallow spread isn't enough for deep nesting!):
setUser(prev => ({
  ...prev,
  address: { ...prev.address, city: "Delhi" } // spread both levels
}));

// ── PROP SPREADING ───────────────────
const buttonProps = {
  onClick: handleClick,
  disabled: isLoading,
  className: "btn-primary",
  "aria-label": "Submit order",
};

// Spread all props at once:
<button {...buttonProps}>Submit</button>

// ── MERGE DEFAULT WITH USER PROPS ─────
const defaultStyle = { color: "blue", fontSize: 16, fontWeight: "normal" };

const StyledText = ({ style, children }) => (
  <span style={{ ...defaultStyle, ...style }}> {/* user style overrides */}
    {children}
  </span>
);

// <StyledText style={{ color: "red" }}>Hello</StyledText>
// Result style: { color: "red", fontSize: 16, fontWeight: "normal" }

// ── NEXT.JS: MERGE METADATA ───────────
export const metadata = {
  ...defaultMetadata,  // spread shared defaults
  title: "Home Page",  // override title
  openGraph: {
    ...defaultMetadata.openGraph,
    title: "Home | MyApp",
  },
};
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Thinking spread does deep copy
```javascript
const original = { settings: { theme: "dark" } };
const copy = { ...original };

copy.settings.theme = "light"; // ALSO changes original.settings.theme!
// Spread is SHALLOW — nested objects still share reference

// CORRECT for deep:
const deepCopy = structuredClone(original);
```

❌ **Mistake 2:** Spread order for overrides
```javascript
const base = { color: "red", size: 10 };
const updates = { color: "blue" };

// WRONG order: base overrides updates
const wrong = { ...updates, ...base };    // color: "red" (base wins)

// CORRECT: later spread wins
const correct = { ...base, ...updates };  // color: "blue" (updates wins)
```

❌ **Mistake 3:** Spreading non-iterables in arrays
```javascript
// WRONG: numbers/booleans aren't iterable in array context
const bad = [...42];  // TypeError: 42 is not iterable
const bad2 = [...true]; // TypeError

// Objects aren't iterable for array spread:
const bad3 = [...{ a: 1 }]; // TypeError: not iterable

// CORRECT: Object spread only works in object literals
const good = { ...{ a: 1 } }; // { a: 1 } ✅
```

---

## 🧠 Tricky Interview Output Question
```javascript
const a = [1, 2, 3];
const b = [...a];
const c = a;

b.push(4);
c.push(5);

console.log(a); // ?
console.log(b); // ?
console.log(c); // ?
```
**Answer:**
```
[1, 2, 3, 5]   ← c is same reference as a, push(5) modified a too
[1, 2, 3, 4]   ← b is a new array (spread copy), push(4) only changed b
[1, 2, 3, 5]   ← c is same reference as a
```
**Why:** `b = [...a]` creates a new independent array (spread = shallow copy). `c = a` copies the reference — both point to same array.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between spread and rest?**
A1: Same `...` syntax, opposite operations. Rest (in function params/destructuring) **collects** multiple values into a single array. Spread (in function calls/array/object literals) **expands** one iterable/object into multiple individual values. Rest = gathering. Spread = scattering.

**Q2: Does spread do a deep or shallow copy?**
A2: Shallow. `{...obj}` copies the top-level properties, but nested objects/arrays still share the same reference. `[...arr]` copies the array but nested objects within it are still referenced. For deep copy, use `structuredClone()`, `JSON.parse(JSON.stringify())`, or lodash `cloneDeep`.

**Q3: How do you merge two objects with spread?**
A3: `const merged = { ...obj1, ...obj2 }`. Properties from later objects override earlier ones. Order matters: `{ ...defaults, ...userSettings }` lets user override defaults. This is the standard pattern for React state updates and config merging.

**Q4: Can you spread a string?**
A4: Yes. `[..."hello"]` gives `["h","e","l","l","o"]` since strings are iterable. Useful trick: `[...new Set("mississippi")]` gives unique characters.

**Q5: How is spread used in React?**
A5: Three main patterns: (1) Immutable state updates — `setState(prev => ({ ...prev, field: newValue }))`. (2) Prop spreading — `<Component {...props} />`. (3) Merging styles or class configs — `style={{ ...defaultStyle, ...customStyle }}`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Spread | Expand iterable into individual elements | Expand करना |
| Shallow copy | Copy top-level only | सिर्फ ऊपरी level copy |
| Merge | Combine arrays or objects | Combine करना |
| Override | Later property replaces earlier | बाद वाला पहले को replace करे |
| Iterable | Can be spread in array context | Array context में spread हो सके |

---

## ⚡ 3-Line Summary
**English:**
1. Spread `...` expands arrays/objects/strings — use for function args, array merging, and object copying/merging.
2. Later spread properties override earlier ones — `{...defaults, ...overrides}` for config merging.
3. Spread is **shallow** — nested objects still share references; use `structuredClone()` for deep copies.

**Hindi:**
1. Spread `...` arrays/objects/strings expand करता है — function args, array merge, object copy सब के लिए।
2. बाद वाले properties पहले को override करते हैं — `{...defaults, ...overrides}` config merging के लिए।
3. Spread **shallow** है — nested objects share होते हैं; deep copy के लिए `structuredClone()` use करो।

---

## ➡️ Next Topic
**20. Template Literals** — Backtick strings, embedded expressions, multi-line strings, tagged templates।
