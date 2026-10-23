# 18. Rest Parameters (...args)
# हिंदी में: Rest Parameters — अनजान Number of Arguments को Array में Collect करना

---

## 🔵 Simple Definition (English)
The **rest parameter** (`...args`) collects all remaining function arguments into a **real array**. It must be the **last parameter**. Unlike the old `arguments` object, rest params are a true Array with all array methods.

## 🔵 सरल परिभाषा (Hindi)
Rest parameter (`...args`) बाकी बचे सभी arguments को एक **real Array** में collect करता है। यह हमेशा **last parameter** होना चाहिए। `arguments` object से बेहतर — real Array है, सारे array methods मिलते हैं।

---

## 🔴 Problem it Solves
Old `arguments` object issues:
```javascript
function sum() {
  // arguments is array-LIKE (not a real array)
  return arguments.reduce((t, n) => t + n); // ❌ TypeError! No .reduce on arguments
}
```
Rest params give a real array with `.map`, `.filter`, `.reduce` etc.

---

## 🟢 How it Works
```javascript
function fn(first, second, ...rest) {
  // first = arg1, second = arg2
  // rest = [arg3, arg4, arg5, ...] — all remaining as array
}

fn(1, 2, 3, 4, 5);
// first = 1, second = 2, rest = [3, 4, 5]

fn(1, 2);
// first = 1, second = 2, rest = [] (empty array, not undefined)

// ❌ WRONG: rest must be last
function wrong(...rest, last) {} // SyntaxError!
```

---

## 🟡 Real World Example
```javascript
// Shopping cart: add multiple items at once
function addToCart(cartId, ...items) {
  console.log(`Cart: ${cartId}`);
  items.forEach(item => console.log(`  + ${item.name}: ₹${item.price}`));
  return items.reduce((total, item) => total + item.price, 0);
}

const total = addToCart("cart-001",
  { name: "Pizza", price: 299 },
  { name: "Burger", price: 149 },
  { name: "Coke", price: 49 }
);
console.log(`Total: ₹${total}`); // ₹497
```

---

## 💻 Code Example — Basic
```javascript
// ── BASIC REST PARAMS ─────────────────

// Sum any number of arguments
function sum(...numbers) {
  return numbers.reduce((total, n) => total + n, 0);
}

console.log(sum(1, 2, 3));          // 6
console.log(sum(10, 20, 30, 40));   // 100
console.log(sum());                 // 0 (empty array)

// First param fixed, rest collected
function log(level, ...messages) {
  const prefix = `[${level.toUpperCase()}]`;
  messages.forEach(msg => console.log(`${prefix} ${msg}`));
}

log("info", "Server started", "Listening on port 3000");
// [INFO] Server started
// [INFO] Listening on port 3000

log("error", "Connection failed");
// [ERROR] Connection failed

// ── REST vs arguments ─────────────────

// Old way — arguments object (array-like, NOT a real array)
function oldSum() {
  // console.log(arguments.reduce(...)); // ❌ TypeError
  return Array.from(arguments).reduce((t, n) => t + n, 0); // must convert first
}

// New way — rest params (real Array)
function newSum(...nums) {
  return nums.reduce((t, n) => t + n, 0); // ✅ works directly
}

// Arrow functions don't have 'arguments', must use rest:
const arrowSum = (...nums) => nums.reduce((t, n) => t + n, 0);
```

## 💻 Code Example — Advanced
```javascript
// ── REST IN DIFFERENT POSITIONS ────────

// Only rest (collect all):
const joinStrings = (...strings) => strings.join(", ");
console.log(joinStrings("a", "b", "c", "d")); // "a, b, c, d"

// Fixed + rest:
function createTag(tagName, ...children) {
  const content = children.join("");
  return `<${tagName}>${content}</${tagName}>`;
}

console.log(createTag("div", "Hello", " ", "World"));
// <div>Hello World</div>

console.log(createTag("ul",
  "<li>Item 1</li>",
  "<li>Item 2</li>",
  "<li>Item 3</li>"
));
// <ul><li>Item 1</li><li>Item 2</li><li>Item 3</li></ul>

// ── REST WITH DESTRUCTURING ────────────

// Array destructuring + rest:
const [first, second, ...remaining] = [10, 20, 30, 40, 50];
console.log(first);     // 10
console.log(second);    // 20
console.log(remaining); // [30, 40, 50]

// Object destructuring + rest:
const { name, age, ...otherDetails } = {
  name: "Aditya",
  age: 25,
  city: "Mumbai",
  role: "developer",
  company: "TechCorp"
};
console.log(name);         // "Aditya"
console.log(age);          // 25
console.log(otherDetails); // { city: "Mumbai", role: "developer", company: "TechCorp" }

// ── PRACTICAL: API MIDDLEWARE ──────────

// Variadic utility functions
function pipe(...functions) {
  // pipe(f, g, h)(x) = h(g(f(x)))
  return (value) => functions.reduce((acc, fn) => fn(acc), value);
}

const processPrice = pipe(
  price => price * 1.18,           // add GST
  price => Math.round(price * 100) / 100, // round to 2 decimals
  price => `₹${price}`             // format
);

console.log(processPrice(299)); // "₹352.82"

// Function composition with rest:
function compose(...fns) {
  return (x) => fns.reduceRight((acc, fn) => fn(acc), x);
}

// Event system with multiple listeners:
function createEventBus() {
  const listeners = {};

  return {
    on(event, ...handlers) { // multiple handlers at once
      if (!listeners[event]) listeners[event] = [];
      listeners[event].push(...handlers); // spread handlers into array
    },
    emit(event, ...args) {   // emit with multiple data args
      (listeners[event] || []).forEach(handler => handler(...args));
    }
  };
}

const bus = createEventBus();
bus.on("order", 
  (order) => console.log("Email:", order.id),
  (order) => console.log("SMS:", order.id),
  (order) => console.log("Dashboard:", order.id)
);
bus.emit("order", { id: "ORD-001", total: 299 });
```

---

## 🟠 React/Next.js Connection
```jsx
// ── FORWARDING PROPS WITH REST ──────────

// Spread remaining props to child (very common pattern)
const Button = ({ children, variant = "primary", size = "md", ...restProps }) => {
  // restProps contains: onClick, disabled, className, etc.
  return (
    <button
      className={`btn btn-${variant} btn-${size}`}
      {...restProps} // spread all remaining to native button
    >
      {children}
    </button>
  );
};

// Usage:
// <Button onClick={handleClick} disabled={loading} aria-label="Submit">
//   Submit Order
// </Button>
// variant and size are extracted; onClick, disabled, aria-label go via ...restProps

// ── CUSTOM HOOK WITH REST ─────────────
// Variadic class names (like clsx/cn utility)
function cn(...classes) {
  return classes.filter(Boolean).join(" ");
}

const MyComponent = ({ isActive, isError }) => {
  return (
    <div className={cn(
      "base-class",
      isActive && "active",
      isError && "error",
      "another-class"
    )}>
      Content
    </div>
  );
};

// ── API ROUTE WITH MULTIPLE MIDDLEWARE ─
function applyMiddleware(handler, ...middlewares) {
  return middlewares.reduceRight(
    (acc, middleware) => middleware(acc),
    handler
  );
}

const protectedRoute = applyMiddleware(
  handleRequest,
  authMiddleware,
  rateLimitMiddleware,
  logMiddleware
);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Rest param not last
```javascript
// WRONG: SyntaxError
function fn(...rest, last) {} // rest must be LAST

// CORRECT:
function fn(first, ...rest) {} // ✅ rest is last
```

❌ **Mistake 2:** Confusing rest params with spread operator
```javascript
// REST: collects arguments INTO an array (function definition)
function sum(...nums) { /* nums is array */ }

// SPREAD: expands array FROM an array (function call / array literal)
const nums = [1, 2, 3];
console.log(sum(...nums)); // spreads array as individual args

// Same ... symbol, opposite operations:
// REST: many → one (collect)
// SPREAD: one → many (expand)
```

❌ **Mistake 3:** Using `arguments` in arrow functions
```javascript
// WRONG: arrows don't have 'arguments'
const fn = () => {
  console.log(arguments); // ❌ ReferenceError
};

// CORRECT: use rest params in arrows
const fn = (...args) => {
  console.log(args); // ✅
};
```

---

## 🧠 Tricky Interview Output Question
```javascript
function test(a, b, ...rest) {
  console.log(a);
  console.log(b);
  console.log(rest);
  console.log(rest.length);
}

test(1, 2, 3, 4, 5);
test(1);
```
**Answer:**
```
// test(1, 2, 3, 4, 5):
1
2
[3, 4, 5]
3

// test(1):
1
undefined
[]
0
```
**Why:** `rest` always gets an array — empty `[]` if no extra args. `b` gets `undefined` since only one arg was passed.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between rest params and the `arguments` object?**
A1: (1) Rest params collect only the "rest" of arguments; `arguments` has all of them. (2) Rest params produce a **real Array** with all array methods; `arguments` is an array-like object — needs `Array.from()` to convert. (3) Arrow functions have no `arguments` but support rest params. (4) Rest params is a modern ES6 feature; `arguments` is legacy.

**Q2: Can you have multiple rest parameters?**
A2: No — only one rest parameter per function, and it must be the last. `function fn(...a, ...b)` and `function fn(...a, b)` are SyntaxErrors.

**Q3: What is the difference between rest and spread?**
A3: Same `...` syntax, opposite operations. **Rest** (in function parameters) *collects* multiple values into an array. **Spread** (in function calls or array/object literals) *expands* an array/object into individual values. Rest = many → one. Spread = one → many.

**Q4: Does rest work with destructuring?**
A4: Yes. In array destructuring: `const [a, b, ...rest] = [1,2,3,4]` — `rest` is `[3,4]`. In object destructuring: `const { a, ...rest } = obj` — `rest` gets all remaining properties. In both cases, the rest element must be last.

**Q5: How is rest useful in component design?**
A5: The "prop forwarding" pattern — extract named props and collect the rest: `const Input = ({ label, error, ...inputProps }) => <input {...inputProps} />`. This lets wrapper components handle their own props while passing everything else to the native element, enabling clean composition.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Rest parameter | Collects remaining args into array | बाकी args को array में |
| arguments object | Old array-like args holder | पुराना, real array नहीं |
| Variadic function | Takes any number of args | कितने भी args लेने वाली |
| Rest in destructuring | Collect remaining array/object elements | Destructuring में बाकी collect |
| Prop forwarding | Pass remaining props to child | React में बाकी props forward |

---

## ⚡ 3-Line Summary
**English:**
1. `...rest` collects all remaining function arguments into a real Array — usable with map/filter/reduce.
2. Must be the last parameter; only one rest param per function.
3. Arrow functions lack `arguments` — always use `...rest` in arrows for variable arguments.

**Hindi:**
1. `...rest` बाकी arguments को real Array में collect करता है — map/filter/reduce सब चलते हैं।
2. हमेशा last parameter होना चाहिए; एक function में एक ही rest param।
3. Arrow functions में `arguments` नहीं — arrows में variable args के लिए `...rest` use करो।

---

## ➡️ Next Topic
**19. Spread Operator (...)** — Rest का उल्टा — array/object expand करना, merge करना, copy करना।
