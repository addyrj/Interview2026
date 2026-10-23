# 08. Operators
# हिंदी में: JavaScript के सभी Operators — Arithmetic, Comparison, Logical, Assignment

---

## 🔵 Simple Definition (English)
Operators are **symbols/keywords** that perform operations on values. JavaScript has: arithmetic (`+`, `-`, `*`, `/`, `%`, `**`), comparison (`==`, `===`, `!=`, `!==`, `>`, `<`), logical (`&&`, `||`, `!`, `??`), assignment (`=`, `+=`, `-=`), and others (ternary, spread, optional chaining).

## 🔵 सरल परिभाषा (Hindi)
Operators वो symbols/keywords हैं जो values पर operations करते हैं। JavaScript में arithmetic, comparison, logical, assignment, और special operators होते हैं।

---

## 🔴 Problem it Solves
Operators are the building blocks of every condition, calculation, and logic in your code. Knowing edge cases like `%` for even/odd, `??` vs `||`, and `**` for powers avoids bugs.

## 🔴 यह क्यों बना? (Hindi)
Operators के बिना कोई logic नहीं — हर condition, calculation, और assignment operator से ही होती है। Edge cases जानना ज़रूरी है।

---

## 🟢 How it Works — Complete Reference

```javascript
// ── ARITHMETIC ───────────────────────
+   // addition / string concatenation
-   // subtraction
*   // multiplication
/   // division
%   // modulo (remainder): 7 % 3 = 1
**  // exponentiation: 2 ** 10 = 1024
++  // increment (prefix/postfix)
--  // decrement (prefix/postfix)

// ── COMPARISON ───────────────────────
==  // loose equality (type coercion)
=== // strict equality (no coercion)  ← use this
!=  // loose inequality
!== // strict inequality              ← use this
>   // greater than
<   // less than
>=  // greater than or equal
<=  // less than or equal

// ── LOGICAL ─────────────────────────
&&  // AND — true if both true
||  // OR  — true if any true
!   // NOT — inverts boolean
??  // Nullish Coalescing — default for null/undefined only

// ── ASSIGNMENT ──────────────────────
=   // assign
+=  // add and assign:   x += 5  → x = x + 5
-=  // subtract and assign
*=  // multiply and assign
/=  // divide and assign
%=  // modulo and assign
**= // exponent and assign
&&= // logical AND assign (ES2021)
||= // logical OR assign  (ES2021)
??= // nullish assign     (ES2021)

// ── SPECIAL ─────────────────────────
?:  // ternary
?.  // optional chaining
??  // nullish coalescing
... // spread / rest
typeof // type check
instanceof // instance check
in  // property existence check
delete // remove property
void // evaluates and returns undefined
```

## 🟢 कैसे काम करता है? (Hindi)
हर category के operators अलग काम करते हैं। Key ones: `%` बाकी देता है (even/odd check), `**` power, `??` null/undefined के लिए default, `?.` safe property access।

---

## 🟡 Real World Example
```javascript
// E-commerce calculations
const price = 499;
const qty = 3;
const discount = 0.10;

const subtotal = price * qty;                    // 1497
const discountAmount = subtotal * discount;      // 149.7
const total = subtotal - discountAmount;         // 1347.3
const gst = total * 0.18;                        // 242.514
const finalPrice = total + gst;                  // 1589.814

// Pagination
const totalItems = 97;
const perPage = 10;
const totalPages = Math.ceil(totalItems / perPage);  // 10
const lastPageItems = totalItems % perPage;          // 7 items on last page
```

---

## 💻 Code Example — Basic
```javascript
// ── ARITHMETIC ───────────────────────
console.log(10 + 3);   // 13
console.log(10 - 3);   // 7
console.log(10 * 3);   // 30
console.log(10 / 3);   // 3.333...
console.log(10 % 3);   // 1  (remainder)
console.log(2 ** 8);   // 256 (2 to the power 8)

// Increment / Decrement
let a = 5;
console.log(a++);  // 5  — returns THEN increments (postfix)
console.log(a);    // 6  — now incremented
console.log(++a);  // 7  — increments THEN returns (prefix)

// ── COMPARISON ───────────────────────
console.log(5 == "5");   // true  (loose: coercion)
console.log(5 === "5");  // false (strict: different types)
console.log(5 != "5");   // false (loose: they're "equal")
console.log(5 !== "5");  // true  (strict: different types)
console.log(10 > 5);     // true
console.log(10 >= 10);   // true
console.log("b" > "a");  // true (string comparison by char codes)

// ── LOGICAL ─────────────────────────
console.log(true && true);   // true
console.log(true && false);  // false
console.log(false || true);  // true
console.log(false || false); // false
console.log(!true);          // false
console.log(!false);         // true
console.log(!!0);            // false (double negation = toBoolean)

// ── ASSIGNMENT ──────────────────────
let x = 10;
x += 5;   // x = 15
x -= 3;   // x = 12
x *= 2;   // x = 24
x /= 4;   // x = 6
x **= 2;  // x = 36
x %= 10;  // x = 6
console.log(x); // 6
```

## 💻 Code Example — Advanced
```javascript
// ── SHORT-CIRCUIT EVALUATION ──────────
// && returns first falsy value OR last truthy value
console.log(0 && "hello");     // 0     (first falsy)
console.log(1 && "hello");     // "hello" (last value, all truthy)
console.log(1 && 2 && 3);      // 3
console.log(null && doWork()); // null (doWork never called!)

// || returns first truthy value OR last falsy value
console.log(0 || "default");   // "default"
console.log("name" || "anon"); // "name"
console.log(null || undefined || 0); // 0 (all falsy, returns last)

// Real use: default values
const username = userInput || "Anonymous"; // if userInput is falsy
const port = process.env.PORT || 3000;

// ── NULLISH COALESCING (??) ────────────
// Returns right side ONLY if left is null or undefined
// (NOT for 0, "", false — those are valid values)
const score = 0;
console.log(score || 100);   // 100 — WRONG! 0 is falsy
console.log(score ?? 100);   // 0   — CORRECT! 0 is not null/undefined

const config = {
  retries: 0,
  timeout: null,
  name: ""
};
console.log(config.retries ?? 3);   // 0   (0 is valid)
console.log(config.timeout ?? 5000); // 5000 (null → default)
console.log(config.name ?? "unnamed"); // "" (empty string is valid)

// ── OPTIONAL CHAINING (?.) ────────────
const user = {
  profile: {
    address: {
      city: "Mumbai"
    }
  }
};

// WRONG (throws if any property missing):
// const city = user.profile.address.city; // TypeError if address is null!

// CORRECT:
const city = user?.profile?.address?.city; // "Mumbai" or undefined (safe)
const zip = user?.profile?.address?.zip;   // undefined (no error)

// With functions:
const result = user?.getSettings?.(); // calls only if method exists

// With arrays:
const firstTag = post?.tags?.[0]; // safe array access

// ── LOGICAL ASSIGNMENT (ES2021) ────────
let a = null;
a ??= "default";   // a = "default" (was null)
console.log(a);    // "default"

let b = 0;
b ??= 100;         // b stays 0 (0 is not null/undefined)
console.log(b);    // 0

let c = "";
c ||= "fallback";  // c = "fallback" (empty string is falsy)
console.log(c);    // "fallback"

let d = "value";
d &&= d.toUpperCase(); // d = "VALUE" (d is truthy, so assigns)
console.log(d);    // "VALUE"

// ── TYPEOF AND INSTANCEOF ─────────────
console.log(typeof 42);          // "number"
console.log(typeof "hello");     // "string"
console.log(typeof true);        // "boolean"
console.log(typeof undefined);   // "undefined"
console.log(typeof null);        // "object" (bug!)
console.log(typeof []);          // "object"
console.log(typeof {});          // "object"
console.log(typeof function(){}); // "function"

// instanceof — checks prototype chain
console.log([] instanceof Array);   // true
console.log([] instanceof Object);  // true (arrays are objects)
console.log({} instanceof Object);  // true
console.log("hi" instanceof String); // false (primitive, not String object)

// ── IN OPERATOR ──────────────────────
const car = { brand: "Toyota", speed: 120 };
console.log("brand" in car);   // true
console.log("color" in car);   // false
console.log("toString" in car); // true (inherited from Object.prototype)

// ── MODULO USE CASES ─────────────────
// Even/Odd check
const isEven = (n) => n % 2 === 0;
console.log(isEven(4));  // true
console.log(isEven(7));  // false

// Wrap around (circular array, clock)
const hours = [9, 10, 11, 12, 1, 2, 3];
let index = 0;
// Next item, wrapping around:
index = (index + 1) % hours.length;
```

---

## 🟠 React/Next.js Connection
```jsx
function ProductCard({ product, user }) {
  // ── Logical && for conditional rendering ──
  return (
    <div>
      {/* Renders only if isNew is truthy */}
      {product.isNew && <span className="badge">NEW</span>}

      {/* ternary for if/else */}
      {user ? (
        <button onClick={addToCart}>Add to Cart</button>
      ) : (
        <button onClick={openLogin}>Login to Buy</button>
      )}

      {/* ?? for null/undefined defaults */}
      <p>{product.description ?? "No description available"}</p>

      {/* Optional chaining for nested data */}
      <span>{product?.seller?.name ?? "Unknown Seller"}</span>

      {/* Display price */}
      <h2>₹{(product.price * 1.18).toFixed(2)}</h2>

      {/* Star rating: repeat based on Math.round */}
      <div>{"⭐".repeat(Math.round(product.rating))}</div>
    </div>
  );
}

// Node.js: common operator patterns
const pageNumber = parseInt(req.query.page) || 1;  // default page 1
const limit = Math.min(parseInt(req.query.limit) ?? 10, 100); // max 100
const offset = (pageNumber - 1) * limit;

// Validation with &&
const isValidOrder = amount > 0 && items.length > 0 && userId;
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `||` for default when 0 or "" are valid
```javascript
// WRONG: kills valid 0 value
const retries = config.retries || 3; // 0 → 3 (wrong!)
const name = user.name || "anon";     // "" → "anon" (wrong if empty is valid)

// CORRECT: ?? only triggers for null/undefined
const retries = config.retries ?? 3;
const name = user.name ?? "anon";
```

❌ **Mistake 2:** Forgetting `++` prefix vs postfix
```javascript
let i = 5;
let a = i++;  // a = 5, i = 6 (returns then increments)
let b = ++i;  // b = 7, i = 7 (increments then returns)

// In loops, doesn't matter: i++ and ++i both work
// In expressions, prefix vs postfix gives different results
```

❌ **Mistake 3:** `==` comparison surprises
```javascript
// These are ALL true with ==:
console.log(0 == false);   // true
console.log("" == false);  // true
console.log(null == undefined); // true
console.log("1" == 1);     // true

// Always use === to avoid surprises
```

---

## 🧠 Tricky Interview Output Question
```javascript
let x = 5;
console.log(x++);     // ?
console.log(x);       // ?
console.log(++x);     // ?

console.log(null ?? "default");    // ?
console.log(0 ?? "default");       // ?
console.log(0 || "default");       // ?
console.log("" ?? "default");      // ?
```
**Answer:**
```
5      ← postfix: returns 5, then x becomes 6
6      ← x is now 6
7      ← prefix: x becomes 7, returns 7
"default" ← null → right side
0         ← 0 is not null/undefined, ?? keeps it
"default" ← 0 is falsy, || gives right side
""        ← "" is not null/undefined, ?? keeps it
```

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between || and ???**
A1: `||` returns the right operand if the left is **falsy** (false, 0, "", null, undefined, NaN). `??` returns the right operand only if the left is **null or undefined**. Use `??` when 0, empty string, or false are valid values you want to keep.

**Q2: What is short-circuit evaluation?**
A2: Logical operators `&&` and `||` evaluate the right side only if necessary. `&&` stops at the first falsy value. `||` stops at the first truthy value. This allows patterns like `user && user.profile.name` (safe access) and `config.timeout || 5000` (default values), and prevents unnecessary function calls: `isAdmin && performExpensiveCheck()`.

**Q3: Explain prefix (++i) vs postfix (i++) increment.**
A3: Postfix `i++` returns the current value then increments — so `let a = i++` gives `a` the old value. Prefix `++i` increments first then returns — `let a = ++i` gives `a` the new value. In a standalone statement like `i++` or `++i` alone, both do the same thing.

**Q4: When would you use the `in` operator?**
A4: To check if a property (own or inherited) exists on an object: `"name" in user`. More inclusive than `hasOwnProperty` as it checks the prototype chain too. Also used in `for...in` loops. For array index checks: `0 in [1,2,3]` is true.

**Q5: What does the optional chaining operator `?.` do?**
A5: It safely accesses nested properties — if any part of the chain is null or undefined, it returns undefined instead of throwing a TypeError. `user?.address?.city` safely accesses city without crashing if user or address is null. Works for methods too: `obj?.method?.()`, and array access: `arr?.[0]`.

---

## 🔷 Trade-offs / When to Use
✅ Use `??` over `||` for defaults when 0/""/false are valid
✅ Use `?.` for deeply nested data from APIs (could have missing fields)
✅ Use `===` always over `==`
✅ Use `**` instead of `Math.pow()` for cleaner code

❌ Avoid:
- `==` (except `!= null` for null/undefined check combined)
- Prefix `++` in complex expressions (confusing)
- Chaining too many `?.` — might hide real errors

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Operand | Value that operator acts on | Operator जिस पर काम करे |
| Unary operator | One operand (`!x`, `typeof x`) | एक operand वाला |
| Binary operator | Two operands (`a + b`) | दो operand वाला |
| Short circuit | Stop early if result determined | जल्दी रोकना |
| Nullish coalescing | Default for null/undefined only | Null/undefined के लिए default |
| Optional chaining | Safe nested access | Safe nested access |
| Modulo | Remainder of division | भाग का बाकी |

---

## ⚡ 3-Line Summary
**English:**
1. Use `===`/`!==` always — `==` coerces types and causes surprising bugs.
2. Use `??` (not `||`) for default values when 0, "", or false are valid.
3. Use `?.` for safe nested property access on data from APIs that may have missing fields.

**Hindi:**
1. हमेशा `===`/`!==` use करो — `==` type coercion करता है और bugs देता है।
2. Default values के लिए `??` use करो (not `||`) — 0, "", false valid values हैं।
3. API data के nested access के लिए `?.` use करो — null/undefined पर crash नहीं होगा।

---

## ➡️ Next Topic
**09. == vs === (Loose vs Strict Equality)** — Deep dive into equality comparison, coercion algorithm, और वो सारे edge cases जो interviews में पूछे जाते हैं।
