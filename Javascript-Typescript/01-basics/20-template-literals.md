# 20. Template Literals
# हिंदी में: Template Literals — Backtick Strings और Embedded Expressions

---

## 🔵 Simple Definition (English)
Template literals use **backticks** (`` ` ``) instead of quotes. They support **embedded expressions** (`${expression}`), **multi-line strings** (no `\n` needed), and **tagged templates** (advanced processing). Much cleaner than string concatenation.

## 🔵 सरल परिभाषा (Hindi)
Template literals backticks (`` ` ``) use करते हैं। इनसे: expressions embed होती हैं (`${}`), multi-line strings बनती हैं (no `\n`), और tagged templates से advanced processing होती है। String concatenation से बहुत clean।

---

## 🔴 Problem it Solves
Old string concatenation was messy:
```javascript
// Old:
const msg = "Hello, " + name + "! You have " + count + " items in cart.";

// Template literals:
const msg = `Hello, ${name}! You have ${count} items in cart.`;
```

---

## 🟢 How it Works
```javascript
`text ${expression} more text`

// expression can be:
// - variable: ${name}
// - math: ${price * 1.18}
// - ternary: ${isLoggedIn ? "Logout" : "Login"}
// - function call: ${formatDate(date)}
// - any JS expression that produces a value
```

---

## 🟡 Real World Example
```javascript
// Order confirmation message
const generateOrderMsg = (order) => `
  🛒 Order Confirmed!
  ─────────────────────
  Order ID: ${order.id}
  Items: ${order.items.length}
  Subtotal: ₹${order.subtotal}
  GST (18%): ₹${(order.subtotal * 0.18).toFixed(2)}
  Total: ₹${(order.subtotal * 1.18).toFixed(2)}
  
  Estimated delivery: ${order.deliveryTime} mins
  ${order.isPremium ? "🌟 Priority delivery active!" : ""}
`;

console.log(generateOrderMsg({
  id: "ORD-001", items: [1,2], subtotal: 498,
  deliveryTime: 30, isPremium: true
}));
```

---

## 💻 Code Example — Basic
```javascript
// ── BASIC USAGE ───────────────────────

const name = "Aditya";
const age = 25;
const city = "Mumbai";

// Old:
const old = "Name: " + name + ", Age: " + age + ", City: " + city;

// Template literal:
const modern = `Name: ${name}, Age: ${age}, City: ${city}`;
console.log(modern); // "Name: Aditya, Age: 25, City: Mumbai"

// ── EXPRESSIONS ──────────────────────

const price = 299;
const qty = 3;

console.log(`Total: ₹${price * qty}`);         // "Total: ₹897"
console.log(`With GST: ₹${(price * qty * 1.18).toFixed(2)}`); // "With GST: ₹1058.46"

const isLoggedIn = true;
console.log(`Status: ${isLoggedIn ? "Online" : "Offline"}`); // "Status: Online"

// Function calls inside:
const formatCurrency = (n) => new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" }).format(n);
console.log(`Price: ${formatCurrency(1234567)}`); // "Price: ₹12,34,567.00"

// ── MULTI-LINE STRINGS ────────────────

// Old (ugly):
const oldMultiline = "Line 1\n" +
                     "Line 2\n" +
                     "Line 3";

// Template literal:
const html = `
  <div class="card">
    <h2>${name}</h2>
    <p>Age: ${age}</p>
    <p>City: ${city}</p>
  </div>
`;
// Note: includes newlines at start/end — trim() if needed
console.log(html.trim());
```

## 💻 Code Example — Advanced
```javascript
// ── SQL QUERIES (readable) ────────────

function getUserQuery(userId, isActive = true) {
  return `
    SELECT id, name, email, created_at
    FROM users
    WHERE id = ${userId}
      AND is_active = ${isActive}
    ORDER BY created_at DESC
    LIMIT 1
  `.trim();
}

// ⚠️ WARNING: NEVER do this with user input — SQL injection!
// Use parameterized queries in production:
// db.query("SELECT * FROM users WHERE id = $1", [userId])

// ── EMAIL TEMPLATES ───────────────────

function generateEmail({ name, orderTotal, orderId, items }) {
  const itemList = items.map(item =>
    `  • ${item.name} × ${item.qty} — ₹${item.price * item.qty}`
  ).join("\n");

  return `
Dear ${name},

Your order #${orderId} has been confirmed! 🎉

Items ordered:
${itemList}

Total: ₹${orderTotal}

Thank you for shopping with us!

Best,
The Team
  `.trim();
}

// ── TAGGED TEMPLATES ──────────────────
// Advanced: function processes the template

// Tag function receives:
//   strings: array of string parts
//   ...values: array of interpolated values
function highlight(strings, ...values) {
  return strings.reduce((result, str, i) => {
    const value = values[i - 1];
    return result + (i > 0 ? `<mark>${value}</mark>` : "") + str;
  });
}

const product = "Pizza";
const discount = "20%";
const msg = highlight`Get ${product} at ${discount} off today!`;
console.log(msg);
// "Get <mark>Pizza</mark> at <mark>20%</mark> off today!"

// ── NESTING TEMPLATES ─────────────────
const data = [
  { name: "Aditya", score: 95 },
  { name: "Rajan", score: 87 },
];

const table = `
| Name   | Score | Grade |
|--------|-------|-------|
${data.map(row =>
  `| ${row.name.padEnd(6)} | ${String(row.score).padEnd(5)} | ${row.score >= 90 ? "A" : "B"}     |`
).join("\n")}
`;
console.log(table);

// ── CSS-IN-JS PATTERN (styled-components style) ──
function css(strings, ...values) {
  return strings.reduce((result, str, i) =>
    result + (values[i - 1] ?? "") + str
  );
}

const primaryColor = "#007bff";
const fontSize = 16;
const buttonStyles = css`
  background-color: ${primaryColor};
  font-size: ${fontSize}px;
  padding: 8px 16px;
  border-radius: 4px;
`;
```

---

## 🟠 React/Next.js Connection
```jsx
// ── DYNAMIC CLASSNAMES ────────────────
const Button = ({ variant, size, disabled, children }) => {
  const className = `
    btn
    btn-${variant}
    btn-${size}
    ${disabled ? "btn-disabled opacity-50" : ""}
  `.trim().replace(/\s+/g, " "); // normalize whitespace

  return <button className={className} disabled={disabled}>{children}</button>;
};

// ── API URLS ─────────────────────────
const API_BASE = process.env.NEXT_PUBLIC_API_URL;

const endpoints = {
  user: (id) => `${API_BASE}/users/${id}`,
  products: (category, page) => `${API_BASE}/products?category=${category}&page=${page}`,
  order: (id) => `${API_BASE}/orders/${id}`,
};

// Usage:
const user = await fetch(endpoints.user(123)).then(r => r.json());

// ── DYNAMIC SQL IN NODE.JS (safe way) ──
// WRONG: template literal (SQL injection!)
// const query = `SELECT * FROM users WHERE name = '${userInput}'`;

// CORRECT: parameterized
const { rows } = await pool.query(
  "SELECT * FROM users WHERE name = $1 AND city = $2",
  [userName, userCity]
);

// ── NOTIFICATION MESSAGES ─────────────
const notifications = {
  orderPlaced: (order) => `Your order #${order.id} for ₹${order.total} is confirmed!`,
  orderDelivered: (order) => `Order #${order.id} delivered! Rate your experience.`,
  lowStock: (product) => `Only ${product.stock} ${product.name}s left — order now!`,
};

// Push notification:
sendPush(notifications.orderPlaced({ id: "ORD-001", total: 499 }));
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** SQL injection via template literals
```javascript
// DANGEROUS: never put user input directly in SQL
const query = `SELECT * FROM users WHERE email = '${userEmail}'`;
// If userEmail = "'; DROP TABLE users; --" → disaster!

// CORRECT: parameterized queries always
pool.query("SELECT * FROM users WHERE email = $1", [userEmail]);
```

❌ **Mistake 2:** Unnecessary whitespace in template literals
```javascript
// WRONG: extra newlines/spaces in output
const greeting = `
  Hello, ${name}!
`;
// Has leading newline + spaces before "Hello"

// CORRECT: trim or use inline
const greeting = `Hello, ${name}!`;
// OR:
const greeting = `
  Hello, ${name}!
`.trim();
```

❌ **Mistake 3:** Using template literals for simple strings
```javascript
// Unnecessary (no interpolation needed):
const greeting = `Hello World`; // just use "Hello World"

// Template literals are for when you actually interpolate:
const greeting = `Hello, ${name}!`; // meaningful
```

---

## 🧠 Tricky Interview Output Question
```javascript
const a = 5;
const b = 10;
console.log(`${a} + ${b} = ${a + b}`);
console.log(`${a} * ${b} = ${a * b}`);

const items = ["Pizza", "Burger"];
console.log(`You ordered: ${items.join(", ")}`);

function tag(strings, ...vals) {
  return strings[0] + vals.map(v => v * 2).join(" + ") + strings[strings.length - 1];
}
console.log(tag`${3} and ${4}`);
```
**Answer:**
```
"5 + 10 = 15"
"5 * 10 = 50"
"You ordered: Pizza, Burger"
" 6 + 8"         ← tagged: doubles each value, "" + "6 + 8" + ""
```

---

## ⚫ Interview Questions + Answers

**Q1: What are template literals and what problem do they solve?**
A1: Template literals use backticks and support embedded expressions via `${}`, multi-line strings, and tagged templates. They solve the verbosity and error-prone nature of string concatenation — especially for long strings with many variables. They also naturally handle multi-line strings without `\n`.

**Q2: What is a tagged template literal?**
A2: A tagged template is a function call where the function processes the template. The function receives: an array of string parts, and the interpolated values as separate arguments. Used by: styled-components (CSS-in-JS), GraphQL (gql``), SQL libraries (for safe queries), i18n libraries. Allows complete control over how the string is assembled.

**Q3: Can you put any expression inside `${}`?**
A3: Yes — any JavaScript expression that produces a value. Variables, math, ternaries, function calls, array methods, nested template literals. Avoid complex expressions for readability — extract to a variable first if it's getting long.

**Q4: What is the difference between `'string'` and `` `string` ``?**
A4: Regular strings use single or double quotes. Template literals use backticks, support multi-line without escape sequences, and allow embedded expressions. Regular strings are fine for static text; template literals are preferred when you need interpolation or multi-line content.

**Q5: Are template literals slower than string concatenation?**
A5: Negligibly. Modern JS engines optimize both equally well. Never choose concatenation for performance — choose template literals for readability. The difference is unmeasurable in real applications.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Template literal | Backtick string with interpolation | Backtick string |
| Interpolation | Embed expression in string `${}` | Expression को string में डालना |
| Multi-line string | String spanning multiple lines | कई lines की string |
| Tagged template | Function processing a template | Template process करने वाली function |
| Expression | Code that produces a value | Value देने वाला code |

---

## ⚡ 3-Line Summary
**English:**
1. Template literals use backticks — embed any JS expression with `${}`, write multi-line strings naturally.
2. Much cleaner than string concatenation for messages, HTML, URLs, and SQL queries.
3. Tagged templates are powerful for libraries (styled-components, GraphQL) — the tag function controls how the string is built.

**Hindi:**
1. Template literals backticks use करते हैं — `${}` से कोई भी expression embed, multi-line naturally।
2. Messages, HTML, URLs, SQL queries के लिए string concatenation से बहुत clean।
3. Tagged templates libraries में use होते हैं (styled-components, GraphQL) — tag function string build करता है।

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [Web Dev Simplified — Template Literals](https://www.youtube.com/results?search_query=template+literals+javascript+web+dev+simplified) | Tagged templates, all use cases |
| 📝 Article | [javascript.info — Template strings](https://javascript.info/string#template-strings) | Complete guide with tagged templates |
| 📝 Article | [MDN — Template literals](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Template_literals) | Official reference, raw strings |
| 🐙 GitHub | [styled-components source](https://github.com/styled-components/styled-components) | See real-world tagged template usage |

---

## ➡️ Next Topic
**21. Arrays — Basic Methods** — Array creation, push/pop/shift/unshift, splice/slice, indexOf, includes, और common patterns।
