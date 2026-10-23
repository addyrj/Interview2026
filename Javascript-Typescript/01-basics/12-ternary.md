# 12. Ternary Operator
# हिंदी में: Ternary Operator — एक Line में if/else

---

## 🔵 Simple Definition (English)
The ternary operator `condition ? valueIfTrue : valueIfFalse` is a **one-line if/else** that returns a value. It's the only JavaScript operator with three operands — hence "ternary."

## 🔵 सरल परिभाषा (Hindi)
Ternary operator `condition ? valueIfTrue : valueIfFalse` एक line में if/else है जो value return करता है। तीन parts होते हैं इसीलिए "ternary" कहते हैं।

---

## 🔴 Problem it Solves
Without ternary, simple if/else requires 4+ lines just to assign a value:
```javascript
// Without ternary:
let label;
if (isLoggedIn) { label = "Logout"; }
else { label = "Login"; }

// With ternary:
const label = isLoggedIn ? "Logout" : "Login"; // 1 line!
```

## 🔴 यह क्यों बना? (Hindi)
Simple if/else के लिए 4+ lines लिखना verbose है। Ternary से एक line में काम हो जाता है, खासकर JSX और variable assignment में।

---

## 🟢 How it Works

```
condition ? expressionIfTrue : expressionIfFalse
    ↑              ↑                  ↑
  boolean       value when          value when
  expression    true                false

Evaluates condition → if truthy, returns left; if falsy, returns right
```

## 🟢 कैसे काम करता है? (Hindi)
1. Condition evaluate होती है (truthy/falsy)
2. Truthy है → `?` के बाद वाला return
3. Falsy है → `:` के बाद वाला return
4. यह एक expression है — value return करता है

---

## 🟡 Real World Example
```javascript
// Button label
const btnText = isLoggedIn ? "Logout" : "Login";

// Discount display
const price = 499;
const hasDiscount = true;
const displayPrice = hasDiscount ? `₹${price * 0.9} (10% off)` : `₹${price}`;

// Greeting
const hour = new Date().getHours();
const greeting = hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";
```

---

## 💻 Code Example — Basic
```javascript
// ── BASIC TERNARY ─────────────────────

const age = 20;
const access = age >= 18 ? "Allowed" : "Denied";
console.log(access); // "Allowed"

// Equivalent if/else:
// const access = age >= 18 ? "Allowed" : "Denied";
// if (age >= 18) { access = "Allowed"; } else { access = "Denied"; }

// ── IN TEMPLATE LITERALS ──────────────
const score = 85;
console.log(`Result: ${score >= 60 ? "Pass ✅" : "Fail ❌"}`);
// "Result: Pass ✅"

// ── FUNCTION RETURN ───────────────────
const isEven = n => n % 2 === 0 ? "even" : "odd";
console.log(isEven(4)); // "even"
console.log(isEven(7)); // "odd"

// ── NULL / FALLBACK ───────────────────
const username = null;
const display = username ? username : "Anonymous";
// Better with ??:
const display2 = username ?? "Anonymous";
```

## 💻 Code Example — Advanced
```javascript
// ── NESTED TERNARY (use carefully) ────

// Max 2 levels — more than this is unreadable
const score = 75;
const grade = score >= 90 ? "A"
            : score >= 80 ? "B"
            : score >= 70 ? "C"
            : score >= 60 ? "D"
            : "F";
console.log(grade); // "C"

// Better for 3+ levels: if/else or object map
function getGrade(score) {
  if (score >= 90) return "A";
  if (score >= 80) return "B";
  if (score >= 70) return "C";
  if (score >= 60) return "D";
  return "F";
}

// ── TERNARY WITH SIDE EFFECTS ─────────
// Not recommended but technically works:
const isAdmin = true;
isAdmin ? console.log("Show admin panel") : console.log("Hide admin panel");
// Better: use if/else for side effects (cleaner intent)

// ── TERNARY WITH FUNCTION CALLS ──────
const data = isReady
  ? processData(rawData)     // called if truthy
  : getCachedData();          // called if falsy

// ── PRACTICAL: REACT-STYLE PATTERNS ──

// Conditional className
const buttonClass = isActive ? "btn-active" : "btn-inactive";

// Conditional message
const message = errors.length > 0
  ? `${errors.length} error(s) found`
  : "All good ✅";

// Chained operations
const total = hasCoupon
  ? (basePrice * 0.9).toFixed(2)
  : basePrice.toFixed(2);
```

---

## 🟠 React/Next.js Connection
```jsx
// MOST COMMON USE: conditional rendering in JSX
function Navbar({ user, cartCount }) {
  return (
    <nav>
      {/* Simple if/else: user logged in */}
      <span>{user ? `Hello, ${user.name}` : "Guest"}</span>

      {/* Conditional button */}
      <button>{user ? "Logout" : "Login"}</button>

      {/* Conditional class */}
      <div className={cartCount > 0 ? "cart-active" : "cart-empty"}>
        Cart ({cartCount})
      </div>

      {/* Nested: role-based */}
      <span>{user?.role === "admin" ? "Admin" : user ? "User" : "Guest"}</span>
    </nav>
  );
}

// In className with CSS modules or Tailwind:
const btnClass = `px-4 py-2 ${isActive ? "bg-blue-500 text-white" : "bg-gray-200"}`;

// In Next.js API responses:
return Response.json({
  status: success ? "ok" : "error",
  message: success ? "Order placed" : "Order failed",
  data: success ? orderData : null,
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Too many nested ternaries (unreadable)
```javascript
// WRONG — very hard to read:
const val = a ? b ? c ? "x" : "y" : "z" : "w";

// CORRECT: use if/else or early returns
function getVal(a, b, c) {
  if (!a) return "w";
  if (!b) return "z";
  if (!c) return "y";
  return "x";
}
```

❌ **Mistake 2:** Using ternary for side effects
```javascript
// WRONG: ternary for side effects (confusing intent)
isAdmin ? deleteUser(id) : showError("No permission");

// CORRECT: if/else for actions/side effects
if (isAdmin) {
  deleteUser(id);
} else {
  showError("No permission");
}
```

❌ **Mistake 3:** Not handling null in React ternary
```jsx
// WRONG: can render "0" (number) on screen!
{items.length ? <ItemList /> : null}
// If items.length is 0, renders nothing — but 0 is falsy anyway...
// The real bug: {items.length && <ItemList />} renders "0" if length is 0

// CORRECT: explicit comparison
{items.length > 0 ? <ItemList /> : <EmptyCart />}
```

---

## 🧠 Tricky Interview Output Question
```javascript
const a = true;
const b = false;
const c = true;

const result = a ? b ? "AB" : "A only" : "not A";
console.log(result); // ?
```
**Answer:** `"A only"`
**Why:** `a` is true → evaluate `b ? "AB" : "A only"`. `b` is false → returns `"A only"`.

---

## ⚫ Interview Questions + Answers

**Q1: What is the ternary operator and when should you use it?**
A1: The ternary `condition ? true-value : false-value` is a concise if/else for returning a value. Use it for simple binary conditions (2 outcomes) in assignments, template literals, and JSX. Avoid for more than 2 levels of nesting or for side effects (use if/else then).

**Q2: What is the difference between ternary and if/else?**
A2: Ternary is an **expression** — it produces a value and can be used inside other expressions (template literals, JSX, function arguments). if/else is a **statement** — it executes code but can't be used inside expressions. Use ternary when you need a value; use if/else when you need to execute multiple statements.

**Q3: Can you use ternary in JSX?**
A3: Yes, it's the primary tool for conditional rendering in JSX. JSX allows expressions (not statements) inside `{}`, so `condition ? <A /> : <B />` works. For only-render-if-true cases, use `condition && <Component />`, but watch the number 0 issue.

**Q4: Can ternary operators be nested?**
A4: Technically yes, but limit to 2 levels max. Deep nesting is very hard to read and maintain. For 3+ branches, use if/else or an object map.

**Q5: Can the true/false parts of a ternary be function calls?**
A5: Yes. `condition ? functionA() : functionB()` is valid — only the matching function is called. This works for both pure functions returning values and for side effects (though if/else is cleaner for side effects).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Ternary | Three operands: condition, true, false | तीन parts वाला operator |
| Expression | Produces a value | Value produce करना |
| Statement | Executes code | Code execute करना |
| Conditional rendering | Show/hide JSX based on condition | Condition से JSX show/hide |
| Nested ternary | Ternary inside ternary | Ternary के अंदर ternary |

---

## ⚡ 3-Line Summary
**English:**
1. Ternary `condition ? a : b` is a one-line if/else expression — use for simple assignments and JSX.
2. Unlike if/else (statement), ternary is an expression that can appear inside template literals and JSX.
3. Avoid nesting more than 2 levels; use if/else for side effects or complex multi-branch logic.

**Hindi:**
1. Ternary `condition ? a : b` एक-line if/else expression है — assignments और JSX के लिए।
2. if/else statement है, ternary expression है — template literals और JSX में use हो सकता है।
3. 2 से ज़्यादा nesting avoid करो; side effects और complex logic के लिए if/else।

---

## ➡️ Next Topic
**13. Loops** — for, while, do-while, for-in, for-of — सभी loops कब use करें, और कौन से interview में पूछे जाते हैं।
