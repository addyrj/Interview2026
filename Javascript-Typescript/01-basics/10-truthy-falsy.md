# 10. Truthy vs Falsy Values
# हिंदी में: Truthy और Falsy — if() में कौन सी values true/false बनती हैं

---

## 🔵 Simple Definition (English)
In JavaScript, every value has an inherent **boolean interpretation**. **Falsy** values become `false` in a boolean context. **Truthy** values become `true`. There are only **8 falsy values** — everything else is truthy (including `[]`, `{}`, `"0"`).

## 🔵 सरल परिभाषा (Hindi)
JavaScript में हर value का एक boolean interpretation होता है। **Falsy** values if() में false बनती हैं। **Truthy** values true बनती हैं। सिर्फ 8 falsy values हैं — बाकी सब truthy हैं (जिसमें `[]`, `{}`, `"0"` भी शामिल हैं)।

---

## 🔴 Problem it Solves
Without knowing this:
```javascript
if ([]) { /* runs or not? */ }    // runs! [] is truthy
if ("0") { /* runs or not? */ }   // runs! "0" is truthy
if (0) { /* runs or not? */ }     // doesn't run! 0 is falsy
```
Knowing truthy/falsy prevents wrong conditions and enables cleaner code.

## 🔴 यह क्यों बना? (Hindi)
बिना जाने: `if([])` चलता है या नहीं? `if("0")` चलता है — `"0"` truthy है! `if(0)` नहीं चलता। यह जानना conditions लिखने के लिए ज़रूरी है।

---

## 🟢 Complete Falsy Values (only 8!)

```javascript
// THE 8 FALSY VALUES — memorize these
false        // boolean false
0            // zero
-0           // negative zero
0n           // BigInt zero
""           // empty string ('' or `` also)
null         // null
undefined    // undefined
NaN          // Not a Number

// EVERYTHING ELSE IS TRUTHY, including:
"0"          // ✅ non-empty string (even if "0")
"false"      // ✅ non-empty string
[]           // ✅ empty array
{}           // ✅ empty object
function(){} // ✅ function
-1           // ✅ negative number (not zero)
Infinity     // ✅ infinity
new Date()   // ✅ date object
```

## 🟢 कैसे काम करता है? (Hindi)
सिर्फ 8 falsy values याद रखो: `false, 0, -0, 0n, "", null, undefined, NaN`। बाकी सब truthy — `[]`, `{}`, `"0"`, `-1` सब true हैं।

---

## 🟡 Real World Example
```javascript
// Login check
const user = null; // not logged in
if (user) {
  showDashboard(); // won't run — null is falsy
} else {
  showLogin();     // runs
}

// Cart check
const cart = [];   // empty array — TRUTHY!
if (cart) {
  showCart(cart);  // RUNS! [] is truthy
}
// Correct check:
if (cart.length > 0) {
  showCart(cart);  // only if cart has items
}

// Username display
const username = "";  // empty string — FALSY
const displayName = username || "Anonymous"; // "Anonymous"

// Score display (0 is valid!)
const score = 0;
const display = score ?? "No score"; // "0" (correct with ??)
const wrong = score || "No score";   // "No score" (wrong! 0 is falsy)
```

## 🟡 Real Example Hindi mein
Zomato में `if(cart)` लिखा — `[]` truthy है तो always runs! Correct check है `if(cart.length)`. Login check के लिए `if(user)` काम करता है — null/undefined falsy हैं।

---

## 💻 Code Example — Basic
```javascript
// ── FALSY VALUES TEST ─────────────────
const falsyValues = [false, 0, -0, 0n, "", null, undefined, NaN];

falsyValues.forEach(val => {
  if (val) {
    console.log(val, "→ truthy"); // none will print
  } else {
    console.log(val, "→ falsy");  // all will print
  }
});

// ── TRUTHY SURPRISES ──────────────────
console.log(Boolean("0"));        // true  (non-empty string)
console.log(Boolean("false"));    // true  (non-empty string)
console.log(Boolean([]));         // true  (empty array)
console.log(Boolean({}));         // true  (empty object)
console.log(Boolean(-1));         // true  (non-zero number)
console.log(Boolean(Infinity));   // true
console.log(Boolean(new Date())); // true

// ── PRACTICAL USAGE ───────────────────

// User check
let user = null;
if (!user) {
  console.log("User not logged in"); // runs
}

// Default value with ||
const name = "" || "Anonymous";   // "Anonymous" (empty string → falsy)
const port = 0 || 3000;           // 3000 (0 is falsy — careful!)

// Safe default with ??
const port2 = 0 ?? 3000;          // 0 (0 is not null/undefined)
const name2 = null ?? "Anonymous"; // "Anonymous"

// Double negation !! = convert to boolean
console.log(!!0);        // false
console.log(!!"");       // false
console.log(!!null);     // false
console.log(!!{});       // true
console.log(!![]);       // true
console.log(!!"hello");  // true
```

## 💻 Code Example — Advanced
```javascript
// ── GUARD CLAUSES (early return pattern) ──
function processOrder(order) {
  // Guard: check required fields
  if (!order) return { error: "No order provided" };
  if (!order.items) return { error: "No items" };
  if (!order.items.length) return { error: "Empty cart" }; // length 0 is falsy
  if (!order.userId) return { error: "User not logged in" };

  // Safe to process now
  return calculateTotal(order);
}

// ── ARRAY LENGTH CHECK ────────────────
const products = [];
const users = [{ id: 1 }, { id: 2 }];

// WRONG: [] is truthy!
if (products) console.log("has products"); // runs even for empty array!

// CORRECT: check length
if (products.length) console.log("has products");        // won't run
if (products.length > 0) console.log("has products");    // explicit, clear
if (!products.length) console.log("cart is empty");      // runs

// ── CONDITIONAL RENDERING PATTERNS ───
function renderUserSection(user) {
  // Pattern 1: && (render if truthy)
  // user && <Profile user={user} />

  // Pattern 2: ternary
  // user ? <Profile /> : <LoginButton />

  // Pattern 3: null coalescing for display value
  const displayName = user?.name ?? "Guest";
  const avatar = user?.avatar || "/default-avatar.png";

  return { displayName, avatar };
}

// ── ALL FALSY CHECKS TABLE ───────────
function checkAllFalsy() {
  const values = {
    "false": false,
    "0": 0,
    "-0": -0,
    "0n": 0n,
    '""': "",
    "null": null,
    "undefined": undefined,
    "NaN": NaN,
    // These might seem falsy but are truthy:
    '"0"': "0",
    "[]": [],
    "{}": {},
    "-1": -1
  };

  Object.entries(values).forEach(([label, val]) => {
    console.log(`${label}: ${!!val ? "✅ truthy" : "❌ falsy"}`);
  });
}
checkAllFalsy();
/*
false:     ❌ falsy
0:         ❌ falsy
-0:        ❌ falsy
0n:        ❌ falsy
"":        ❌ falsy
null:      ❌ falsy
undefined: ❌ falsy
NaN:       ❌ falsy
"0":       ✅ truthy  ← surprise!
[]:        ✅ truthy  ← surprise!
{}:        ✅ truthy  ← surprise!
-1:        ✅ truthy
*/
```

---

## 🟠 React/Next.js Connection
```jsx
function ProductPage({ product, user, reviews }) {
  // ✅ Safe null check with truthiness
  if (!product) return <div>Loading...</div>;

  return (
    <div>
      {/* ✅ Render if user is logged in */}
      {user && <button>Add to Wishlist</button>}

      {/* ✅ Render if has reviews — check length! not just array */}
      {reviews?.length > 0 && (
        <ReviewList reviews={reviews} />
      )}
      {/* ❌ WRONG: reviews && <ReviewList /> — [] is truthy! */}

      {/* ✅ Display with fallback */}
      <p>{product.description || "No description available"}</p>

      {/* ✅ ?? for numeric values (0 is valid rating) */}
      <span>Rating: {product.rating ?? "Not rated"}</span>

      {/* ✅ isLoading: explicit boolean */}
      {product.stock === 0
        ? <span className="red">Out of Stock</span>
        : <button>Buy Now</button>
      }
    </div>
  );
}

// Common React bug with arrays:
// {items && items.map(...)} ← if items = [], renders nothing (fine)
// But if items = 0, renders "0" on screen! (number 0 is falsy but rendered as text)
// Fix: {items?.length > 0 && items.map(...)}
// Or:  {Boolean(items?.length) && items.map(...)}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Checking array existence without checking length
```javascript
const items = [];

// WRONG: [] is truthy, this always runs for any array
if (items) { showList(items); }

// CORRECT: check if array has items
if (items.length > 0) { showList(items); }
if (items.length) { showList(items); } // shorter, same thing
```

❌ **Mistake 2:** Using `||` for numeric defaults
```javascript
const score = 0; // valid score

// WRONG: 0 is falsy, so defaults to 100 even for valid score 0
const display = score || "No score"; // "No score" for score=0

// CORRECT: use ?? for null/undefined only
const display = score ?? "No score"; // 0 (correct!)
```

❌ **Mistake 3:** React rendering a 0 accidentally
```jsx
// WRONG: if items is [] (empty), renders fine
// But if items is 0, renders "0" as text on screen!
{items.length && <ItemList items={items} />}

// CORRECT: force boolean
{items.length > 0 && <ItemList items={items} />}
{!!items.length && <ItemList items={items} />}
{Boolean(items.length) && <ItemList items={items} />}
```

---

## 🧠 Tricky Interview Output Question
```javascript
const values = [0, "", null, undefined, NaN, false, "0", [], {}, -1];

let truthyCount = 0;
let falsyCount = 0;

values.forEach(v => {
  if (v) truthyCount++;
  else falsyCount++;
});

console.log("Truthy:", truthyCount);
console.log("Falsy:", falsyCount);
```
**Answer:**
```
Truthy: 4    ← "0", [], {}, -1
Falsy: 6     ← 0, "", null, undefined, NaN, false
```
**Why:** `"0"` (non-empty string), `[]` (empty array), `{}` (empty object), `-1` (non-zero number) are all truthy despite looking empty.

---

## ⚫ Interview Questions + Answers

**Q1: What are all the falsy values in JavaScript?**
A1: Exactly 8: `false`, `0`, `-0`, `0n` (BigInt zero), `""` (empty string), `null`, `undefined`, `NaN`. Everything else is truthy — notably `"0"`, `[]`, and `{}` are all truthy.

**Q2: Is an empty array truthy or falsy?**
A2: Truthy! `if ([]) { }` will execute. This surprises many developers. To check if an array is empty, use `array.length === 0` or `!array.length`, not just `!array`.

**Q3: Is an empty object truthy or falsy?**
A3: Truthy. `if ({}) { }` executes. To check if an object has no properties, use `Object.keys(obj).length === 0`.

**Q4: What is the difference between `||` and `??` for default values?**
A4: `||` returns the right side for any falsy left side (0, "", false, null, undefined, NaN). `??` only returns the right side for `null` or `undefined`. Use `??` when 0, empty string, or false are valid values — otherwise they'd incorrectly trigger the default.

**Q5: How do you explicitly convert a value to boolean?**
A5: Three ways: `Boolean(value)` (explicit, readable), `!!value` (double negation — concise), or `value ? true : false` (ternary — verbose). `!!` is most common in production code for brevity.

---

## 🔷 Trade-offs / When to Use
✅ Use truthiness checks for:
- Null/undefined checks: `if (user)` — clean and readable
- String presence: `if (title)` — empty string = no title
- Guard clauses: `if (!order) return;`

❌ Avoid truthiness checks for:
- Numbers where 0 is valid: use `value !== null && value !== undefined` or `value != null`
- Arrays: always check `.length > 0`
- Booleans that could be 0: use `=== false` explicitly

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Falsy | Becomes false in boolean context | Boolean में false बनता है |
| Truthy | Becomes true in boolean context | Boolean में true बनता है |
| Boolean context | if(), while(), ternary, !, && | Boolean के रूप में use होना |
| !! (Double negation) | Convert to boolean | Boolean में convert करना |
| Boolean() | Explicit conversion to boolean | Explicit boolean conversion |
| Guard clause | Early return if condition fails | शुरू में ही check करना |

---

## ⚡ 3-Line Summary
**English:**
1. Only 8 falsy values: `false, 0, -0, 0n, "", null, undefined, NaN` — everything else is truthy.
2. `[]` and `{}` are truthy — always check `.length` or `Object.keys().length` for emptiness.
3. Use `??` not `||` when 0, "", or false are valid values; use `!!value` to convert to boolean.

**Hindi:**
1. सिर्फ 8 falsy values: `false, 0, -0, 0n, "", null, undefined, NaN` — बाकी सब truthy।
2. `[]` और `{}` truthy हैं — emptiness के लिए `.length` check करो।
3. 0/""/false valid हों तो `||` नहीं `??` use करो; boolean बनाने के लिए `!!value`।

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [Akshay Saini — Truthy Falsy](https://www.youtube.com/results?search_query=truthy+falsy+javascript+akshay+saini) | Visual examples with all 8 falsy values |
| 📺 YouTube | [Web Dev Simplified — Truthy Falsy](https://www.youtube.com/results?search_query=truthy+falsy+javascript+web+dev+simplified) | Common mistakes and real-world usage |
| 📝 Article | [javascript.info — Logical operators](https://javascript.info/logical-operators) | Truthiness in &&, ||, ! operators |
| 📝 Article | [MDN — Falsy values](https://developer.mozilla.org/en-US/docs/Glossary/Falsy) | Complete reference |
| 🐙 GitHub | [getify/You-Dont-Know-JS — Coercion](https://github.com/getify/You-Dont-Know-JS/blob/1st-ed/types%20%26%20grammar/ch4.md) | Deepest treatment of truthy/falsy coercion |

---

## ➡️ Next Topic
**11. if/else + switch Statement** — Conditional logic, nested conditions, switch statement best practices, और fall-through behavior।
