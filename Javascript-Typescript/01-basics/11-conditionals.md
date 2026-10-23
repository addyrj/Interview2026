# 11. if/else + switch Statement
# हिंदी में: Conditional Logic — if/else और switch

---

## 🔵 Simple Definition (English)
`if/else` runs code based on a **condition** (truthy/falsy). `switch` matches a **value** against multiple cases. Both control the flow of your program — which code runs and which doesn't.

## 🔵 सरल परिभाषा (Hindi)
`if/else` condition (truthy/falsy) के हिसाब से code चलाता है। `switch` एक value को multiple cases से match करता है। दोनों program का flow control करते हैं।

---

## 🔴 Problem it Solves
Without conditionals, programs would run all code linearly — no decisions, no branching. Conditions let you handle different scenarios: user logged in or not, order successful or failed, etc.

## 🔴 यह क्यों बना? (Hindi)
बिना conditionals के program सब कुछ linearly चलाएगा। Conditions से: user login है या नहीं, order success हुआ या नहीं — अलग-अलग scenarios handle होते हैं।

---

## 🟢 How it Works — Step by Step

```
if (condition) {
  // runs if condition is TRUTHY
} else if (anotherCondition) {
  // runs if above was falsy AND this is TRUTHY
} else {
  // runs if ALL above were falsy
}

switch (value) {
  case "A":
    // runs if value === "A" (strict!)
    break;  // IMPORTANT: stop fall-through
  case "B":
    // runs if value === "B"
    break;
  default:
    // runs if no case matched
}
```

## 🟢 कैसे काम करता है? (Hindi)
- `if`: condition truthy है तो block चलता है, नहीं तो skip
- `else if`: पहला false था, यह check करो
- `else`: सब false थे, यह चलता है
- `switch`: value को सब cases से `===` से compare करता है; `break` न हो तो अगला case भी चलता है (fall-through)

---

## 🟡 Real World Example
```javascript
// Food delivery order status
function getOrderStatus(status) {
  switch (status) {
    case "placed":    return "🛒 Order received";
    case "confirmed": return "✅ Restaurant confirmed";
    case "preparing": return "👨‍🍳 Being prepared";
    case "picked_up": return "🛵 On the way";
    case "delivered": return "✅ Delivered!";
    case "cancelled": return "❌ Cancelled";
    default:          return "❓ Unknown status";
  }
}

// User role permissions
function canAccess(role, feature) {
  if (role === "admin") {
    return true; // admin can do everything
  } else if (role === "moderator" && feature !== "billing") {
    return true; // moderator can't access billing
  } else if (role === "user" && feature === "profile") {
    return true; // users can only access own profile
  } else {
    return false;
  }
}
```

---

## 💻 Code Example — Basic
```javascript
// ── if / else if / else ───────────────

const temperature = 35;

if (temperature > 40) {
  console.log("Extreme heat! Stay inside");
} else if (temperature > 30) {
  console.log("Very hot day");   // this runs (35 > 30)
} else if (temperature > 20) {
  console.log("Warm day");
} else if (temperature > 10) {
  console.log("Cool day");
} else {
  console.log("Cold day");
}

// ── SWITCH ────────────────────────────

const day = "Monday";

switch (day) {
  case "Saturday":
  case "Sunday":                // fall-through intentional: both go to same code
    console.log("Weekend! 🎉");
    break;
  case "Monday":
    console.log("Start of week 😴");
    break;
  case "Friday":
    console.log("Almost weekend! 😊");
    break;
  default:                      // like else — if nothing matched
    console.log("Regular workday");
}
// Output: "Start of week 😴"

// ── SWITCH with return (in function) ──
function getDayType(day) {
  switch (day) {
    case "Saturday":
    case "Sunday":
      return "weekend";
    default:
      return "weekday";
  }
}
```

## 💻 Code Example — Advanced
```javascript
// ── NESTED if (with guard clauses — better) ──

// BAD: deeply nested (arrow anti-pattern)
function processOrder_bad(order) {
  if (order) {
    if (order.items) {
      if (order.items.length > 0) {
        if (order.userId) {
          // actual logic buried 4 levels deep
          return "Processing...";
        }
      }
    }
  }
  return "Invalid order";
}

// GOOD: guard clauses (early returns flatten nesting)
function processOrder(order) {
  if (!order) return "No order";           // guard 1
  if (!order.items) return "No items";     // guard 2
  if (!order.items.length) return "Empty cart"; // guard 3
  if (!order.userId) return "Not logged in"; // guard 4

  // actual logic at normal indent level
  const total = order.items.reduce((sum, item) => sum + item.price, 0);
  return `Processing ₹${total}...`;
}

// ── SWITCH vs OBJECT MAP ──────────────

// Switch (verbose for many cases):
function getIconSwitch(status) {
  switch (status) {
    case "success":  return "✅";
    case "error":    return "❌";
    case "warning":  return "⚠️";
    case "info":     return "ℹ️";
    default:         return "❓";
  }
}

// Object map (cleaner, more extensible):
const ICONS = {
  success: "✅",
  error:   "❌",
  warning: "⚠️",
  info:    "ℹ️",
};

function getIcon(status) {
  return ICONS[status] ?? "❓"; // ?? for default
}

// ── SWITCH FALL-THROUGH ────────────────

// INTENTIONAL fall-through:
function getPermissions(role) {
  const permissions = [];
  
  switch (role) {
    case "admin":
      permissions.push("delete");   // admin gets all
      // fall-through to moderator
    case "moderator":
      permissions.push("edit");     // moderator gets edit + view
      // fall-through to user
    case "user":
      permissions.push("view");     // all users get view
      break;
    default:
      permissions.push("none");
  }
  
  return permissions;
}

console.log(getPermissions("admin"));     // ["delete", "edit", "view"]
console.log(getPermissions("moderator")); // ["edit", "view"]
console.log(getPermissions("user"));      // ["view"]

// ── TERNARY FOR SIMPLE if/else ─────────
const age = 20;
const status = age >= 18 ? "adult" : "minor"; // one line
console.log(status); // "adult"

// Nested ternary (avoid, hard to read):
const grade = score >= 90 ? "A" : score >= 80 ? "B" : score >= 70 ? "C" : "F";
// Better: use if/else for this
```

---

## 🟠 React/Next.js Connection
```jsx
// ── CONDITIONAL RENDERING IN JSX ──────

function OrderStatus({ status, user }) {
  // if no user, show login — early return pattern
  if (!user) {
    return <LoginPrompt />;
  }

  // switch in function, return JSX
  function renderStatus() {
    switch (status) {
      case "pending":   return <span className="yellow">⏳ Pending</span>;
      case "confirmed": return <span className="blue">✅ Confirmed</span>;
      case "delivered": return <span className="green">📦 Delivered</span>;
      case "cancelled": return <span className="red">❌ Cancelled</span>;
      default:          return <span>Unknown</span>;
    }
  }

  return (
    <div>
      {/* ternary for if/else */}
      <h2>{user.isPremium ? "Premium Order" : "Standard Order"}</h2>

      {/* && for simple show/hide */}
      {user.isPremium && <PriorityBadge />}

      {/* function call for complex switch */}
      {renderStatus()}
    </div>
  );
}

// Next.js API route conditional
// app/api/order/route.js
export async function POST(request) {
  const { action } = await request.json();

  switch (action) {
    case "place":
      return Response.json(await placeOrder(request));
    case "cancel":
      return Response.json(await cancelOrder(request));
    case "track":
      return Response.json(await trackOrder(request));
    default:
      return Response.json({ error: "Unknown action" }, { status: 400 });
  }
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting `break` in switch
```javascript
// WRONG: falls through unintentionally
switch (color) {
  case "red":
    console.log("Stop");    // runs
  case "yellow":            // falls through! also runs
    console.log("Slow");    // also runs
  case "green":
    console.log("Go");      // also runs
}

// CORRECT: break each case
switch (color) {
  case "red":
    console.log("Stop");
    break;    // ← important
  case "yellow":
    console.log("Slow");
    break;
  case "green":
    console.log("Go");
    break;
}
```

❌ **Mistake 2:** Using switch for ranges (use if/else instead)
```javascript
// WRONG: switch doesn't work for ranges
switch (score) {
  case > 90: return "A"; // SyntaxError!
}

// CORRECT: use if/else for ranges
if (score >= 90) return "A";
else if (score >= 80) return "B";
else return "C";
```

❌ **Mistake 3:** Deep nesting instead of guard clauses
```javascript
// WRONG: deeply nested
if (user) {
  if (user.address) {
    if (user.address.city) {
      return user.address.city;
    }
  }
}

// CORRECT: guard clauses or optional chaining
return user?.address?.city ?? "Unknown city";
```

---

## 🧠 Tricky Interview Output Question
```javascript
const x = "1";

switch (x) {
  case 1:
    console.log("number 1");
    break;
  case "1":
    console.log("string 1"); // ?
    break;
  default:
    console.log("default");
}
```
**Answer:** `"string 1"`
**Why:** `switch` uses **strict equality** (`===`). `x` is string `"1"`, not number `1`. So `case 1` doesn't match, but `case "1"` does.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between if/else and switch?**
A1: `if/else` can evaluate any boolean expression or range (>, <, ===). `switch` compares one value against multiple specific values using strict equality. Use `switch` when checking one variable against many exact values (cleaner, faster). Use `if/else` for ranges, complex conditions, or multiple variables.

**Q2: Does switch use == or ===?**
A2: `===` (strict equality). `switch ("1")` will not match `case 1` (number). This is why type matters in switch cases.

**Q3: What is fall-through in switch?**
A3: When a case doesn't have a `break`, execution continues into the next case — this is fall-through. It can be intentional (multiple cases sharing logic) or accidental (bug). Always add `break` unless fall-through is deliberate, and add a comment explaining why.

**Q4: What are guard clauses and why use them?**
A4: Guard clauses are early `return` statements at the top of a function that handle invalid/edge cases. They flatten deeply nested if/else by handling the "bad paths" first, leaving the main logic at the normal indentation level. This improves readability significantly.

**Q5: When would you use an object map instead of switch?**
A5: When you have many cases mapping a value to a result (status → text, code → message), an object map `{ key: value }` with bracket notation `map[key] ?? default` is cleaner and more maintainable than a long switch. It also allows the map to be defined separately from the logic and even dynamically updated.

---

## 🔷 Trade-offs / When to Use
✅ Use `if/else` when:
- Checking ranges or complex conditions
- Multiple different variables
- Guard clauses (early returns)

✅ Use `switch` when:
- One variable, many exact value matches
- Want fall-through behavior
- HTTP status codes, action types, status strings

✅ Use object map when:
- Value → result mapping (like switch but cleaner)
- Cases defined at module level

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Condition | Expression that evaluates to truthy/falsy | Truthy/falsy expression |
| Branch | Path of code execution | Code execution का रास्ता |
| Fall-through | Switch case without break flows to next | Break न हो तो अगला case चले |
| Guard clause | Early return for invalid state | शुरू में ही invalid check |
| Object map | Key-value pairs as switch alternative | Switch का alternative |
| Ternary | Short one-line if/else | एक-line if/else |

---

## ⚡ 3-Line Summary
**English:**
1. `if/else` evaluates any boolean expression; use for ranges, complex conditions, and guard clauses.
2. `switch` uses `===` to match one value against multiple cases — always add `break`, or fall-through will run the next case.
3. For value-to-result mappings with many cases, an object map `{ key: value }[key]` is cleaner than switch.

**Hindi:**
1. `if/else` कोई भी boolean expression check करता है — ranges और guard clauses के लिए।
2. `switch` `===` से value match करता है — `break` लगाना मत भूलो, नहीं तो अगला case भी चलेगा।
3. बहुत सारे cases mapping के लिए object map `{ key: value }[key]` switch से साफ़ है।

---

## ➡️ Next Topic
**12. Ternary Operator** — Short if/else in one line, nested ternary कब avoid करें, React में conditional rendering।
