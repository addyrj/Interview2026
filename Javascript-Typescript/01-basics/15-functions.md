# 15. Functions — Declaration vs Expression
# हिंदी में: Function Declaration vs Function Expression — अंतर और Use Cases

---

## 🔵 Simple Definition (English)
A **function declaration** (`function greet() {}`) is hoisted — usable before definition. A **function expression** (`const greet = function() {}`) is not hoisted — must define before use. Arrow functions (`const greet = () => {}`) are a concise form of function expression with different `this` behavior.

## 🔵 सरल परिभाषा (Hindi)
**Function Declaration** (`function greet() {}`) hoist होती है — define करने से पहले call कर सकते हैं। **Function Expression** (`const greet = function() {}`) hoist नहीं होती — पहले define करो फिर call करो। Arrow functions expression का concise form हैं।

---

## 🔴 Problem it Solves
Different function syntaxes solve different problems:
- Declaration: hoisting allows organizing code top-down (main logic at top, helpers below)
- Expression: control execution order, pass as arguments, assign conditionally
- Arrow: shorter syntax, `this` from surrounding context (vital for React)

---

## 🟢 Three Ways to Define a Function

```javascript
// 1. Function Declaration
function add(a, b) {
  return a + b;
}

// 2. Function Expression (anonymous)
const add = function(a, b) {
  return a + b;
};

// 3. Arrow Function (concise expression)
const add = (a, b) => a + b;

// 4. Named Function Expression
const factorial = function fact(n) {
  return n <= 1 ? 1 : n * fact(n - 1); // fact = self-reference
};
```

### Key Differences
```
┌─────────────────┬─────────────────────┬────────────────────────┐
│ Feature         │ Declaration         │ Expression/Arrow       │
├─────────────────┼─────────────────────┼────────────────────────┤
│ Hoisting        │ ✅ Yes (fully)      │ ❌ No (TDZ for let/const)│
│ Use before def  │ ✅ Yes              │ ❌ No                  │
│ this binding    │ Dynamic (caller)    │ Arrow: lexical (outer) │
│ arguments obj   │ ✅ Has it           │ Arrow: ❌ No           │
│ Can be named    │ Always named        │ Optional               │
│ As callback     │ Verbose             │ ✅ Clean               │
└─────────────────┴─────────────────────┴────────────────────────┘
```

---

## 🟡 Real World Example
```javascript
// Declaration: helper utilities (order doesn't matter due to hoisting)
console.log(formatPrice(299)); // ✅ works before definition!

function formatPrice(price) {
  return `₹${price.toFixed(2)}`;
}

// Expression: assigned conditionally
const processPayment = isUPI
  ? function upiPayment(amount) { return processUPI(amount); }
  : function cardPayment(amount) { return processCard(amount); };

// Arrow: callbacks, React components
const prices = [299, 499, 199];
const withGST = prices.map(p => p * 1.18); // arrow as callback
```

---

## 💻 Code Example — Basic
```javascript
// ── FUNCTION DECLARATION ──────────────

// ✅ Called BEFORE definition (hoisting!)
console.log(greet("Aditya")); // "Hello, Aditya!"

function greet(name) {
  return `Hello, ${name}!`; // returns string
}

// Recursive declaration (fibonacci)
function fibonacci(n) {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2); // self-reference works
}
console.log(fibonacci(7)); // 13

// ── FUNCTION EXPRESSION ───────────────

// ❌ Called BEFORE definition (TDZ error!)
// console.log(multiply(3, 4)); // ReferenceError!

const multiply = function(a, b) {
  return a * b;
};
console.log(multiply(3, 4)); // 12 ✅

// Named function expression (name only visible inside)
const factorial = function fact(n) {
  if (n <= 1) return 1;
  return n * fact(n - 1); // 'fact' only accessible here
};
console.log(factorial(5)); // 120
// console.log(fact(5));   // ❌ ReferenceError — 'fact' not outside

// ── FIRST-CLASS FUNCTIONS ─────────────
// Functions can be:
// 1. Stored in variables (done above)
// 2. Passed as arguments
function applyOperation(a, b, operation) {
  return operation(a, b); // calling passed function
}
const sum = applyOperation(5, 3, (a, b) => a + b);    // 8
const product = applyOperation(5, 3, (a, b) => a * b); // 15

// 3. Returned from functions
function makeMultiplier(factor) {
  return function(num) { // returning a function!
    return num * factor;
  };
}
const double = makeMultiplier(2);
const triple = makeMultiplier(3);
console.log(double(5));  // 10
console.log(triple(5));  // 15
```

## 💻 Code Example — Advanced
```javascript
// ── HOISTING DEEP DIVE ────────────────

// Function declarations are fully hoisted (callable before definition)
sayHi(); // ✅ "Hi!" — works!

function sayHi() {
  console.log("Hi!");
}

// var function expression: hoisted as undefined
console.log(typeof sayBye); // "undefined" (var hoisted)
// sayBye();                // ❌ TypeError: sayBye is not a function

var sayBye = function() { console.log("Bye!"); };

// let/const expression: in TDZ
// console.log(greetUser); // ❌ ReferenceError
const greetUser = function() { console.log("Hello!"); };

// ── IIFE (Immediately Invoked) ─────────
// Execute immediately, no name needed
(function() {
  const secret = "Private scope!"; // contained, won't pollute global
  console.log(secret);
})();
// secret not accessible here

// Arrow IIFE:
(() => {
  console.log("Arrow IIFE");
})();

// ── FUNCTION PARAMETERS DEEP DIVE ─────
function createOrder(item, qty = 1, discount = 0) {  // default params
  const subtotal = item.price * qty;
  const total = subtotal * (1 - discount);
  return { item, qty, subtotal, total };
}

console.log(createOrder({ name: "Pizza", price: 299 }));
// qty defaults to 1, discount defaults to 0

// Destructuring in params:
function displayUser({ name, age, city = "Unknown" }) {
  console.log(`${name}, ${age}, ${city}`);
}
displayUser({ name: "Aditya", age: 25 }); // "Aditya, 25, Unknown"

// Rest params:
function sum(...numbers) {  // ...numbers = all remaining args as array
  return numbers.reduce((total, n) => total + n, 0);
}
console.log(sum(1, 2, 3, 4, 5)); // 15

// ── PURE vs IMPURE FUNCTIONS ──────────
// Pure: same input → same output, no side effects
function pureAdd(a, b) {
  return a + b; // predictable, testable
}

// Impure: depends on/modifies external state
let total = 0;
function impureAdd(amount) {
  total += amount; // side effect: modifies external variable
  return total;
}
// Prefer pure functions for predictability and testability
```

---

## 🟠 React/Next.js Connection
```jsx
// React components are function expressions (or declarations)
// Modern React: always function expressions with const

// Declaration style (also valid):
function ProductCard({ product }) {
  return <div>{product.name}</div>;
}

// Expression style (more common with TypeScript):
const ProductCard = ({ product }: { product: Product }) => {
  return <div>{product.name}</div>;
};

// Custom Hook (expression, always starts with "use"):
const useCounter = (initialValue = 0) => {
  const [count, setCount] = useState(initialValue);
  const increment = () => setCount(c => c + 1); // arrow: no 'this' issues
  const decrement = () => setCount(c => c - 1);
  const reset = () => setCount(initialValue);
  return { count, increment, decrement, reset };
};

// Event handlers — arrow functions preferred (lexical this):
const Button = () => {
  const handleClick = () => { // arrow: captures component context
    console.log("Clicked!");
  };

  return <button onClick={handleClick}>Click me</button>;
};

// Next.js API route handlers:
export async function GET(request) {  // function declaration
  // handler code
}

export const POST = async (request) => { // or expression
  // handler code
};
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Calling function expression before declaration
```javascript
// WRONG:
const result = double(5); // ❌ ReferenceError (TDZ)
const double = n => n * 2;

// CORRECT: define before use
const double = n => n * 2;
const result = double(5); // ✅ 10
```

❌ **Mistake 2:** Forgetting return in arrow function bodies
```javascript
// WRONG (implicit undefined):
const double = n => {
  n * 2; // missing return!
};
console.log(double(5)); // undefined

// CORRECT — option 1: explicit return
const double = n => {
  return n * 2;
};

// CORRECT — option 2: implicit return (no braces)
const double = n => n * 2;

// CORRECT — option 3: return object (wrap in parentheses!)
const getUser = () => ({ name: "Aditya", age: 25 });
// Without () it would look like a block: () => { name: "Aditya" }
```

❌ **Mistake 3:** Using arrow function as method (wrong `this`)
```javascript
// WRONG: arrow function as object method
const user = {
  name: "Aditya",
  greet: () => {
    console.log(`Hello, ${this.name}`); // undefined! arrow has no own 'this'
  }
};

// CORRECT: regular function as method
const user = {
  name: "Aditya",
  greet() {            // shorthand method (same as function keyword)
    console.log(`Hello, ${this.name}`); // "Aditya" ✅
  }
};
```

---

## 🧠 Tricky Interview Output Question
```javascript
console.log(typeof foo);  // ?
console.log(typeof bar);  // ?

function foo() {}
var bar = function() {};
```
**Answer:**
```
"function"   ← function declaration is fully hoisted
"undefined"  ← var bar is hoisted but as undefined (not as function)
```
**Why:** Function declarations are hoisted with their full definition. `var bar` is hoisted as a variable with `undefined` — the assignment (`= function() {}`) hasn't happened yet.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between function declaration and function expression?**
A1: A function declaration (`function name() {}`) is fully hoisted — the entire function is available before its definition in code. A function expression (`const name = function() {}`) is not hoisted as a function — for `const`/`let`, it's in TDZ; for `var`, it's `undefined`. Use declarations for standalone utilities; use expressions for callbacks, conditional assignment, and arrow functions.

**Q2: What is hoisting for functions?**
A2: Function declarations are "hoisted" — the JS engine moves them to the top of their scope before execution, making them callable from anywhere in the scope. Function expressions are not hoisted as callable — `const`/`let` expressions are in TDZ, `var` expressions are hoisted as `undefined`.

**Q3: What is a first-class function?**
A3: In JavaScript, functions are "first-class citizens" — they can be assigned to variables, passed as arguments to other functions, returned from functions, and stored in arrays/objects. This enables higher-order functions, callbacks, closures, and functional programming patterns.

**Q4: When would you use a named function expression?**
A4: Named function expressions are useful for: (1) self-referencing recursion inside the function, (2) better stack traces in errors (the name appears in stack traces instead of "anonymous"), (3) clarity about what the function does. The name is only accessible inside the function itself.

**Q5: What is the difference between a method and a function?**
A5: A method is a function that belongs to an object and is called on it (`user.greet()`). The key difference is `this` — a method's `this` refers to the object it's called on. A standalone function's `this` is `undefined` (strict mode) or the global object (non-strict). Arrow functions don't have their own `this` and inherit it from the lexical scope.

---

## 🔷 Trade-offs / When to Use
✅ Use function declaration when:
- Standalone utility functions
- Hoisting helps organize code (main logic first)
- Named for clarity in stack traces

✅ Use arrow function expression when:
- Callbacks and array methods
- React components and hooks
- When you need lexical `this`
- Short, concise transformations

✅ Use regular function expression when:
- Need own `this` binding (object methods — use method shorthand though)
- Need `arguments` object

❌ Avoid arrow functions for:
- Object methods (wrong `this`)
- Constructors (can't use `new` with arrows)
- Functions needing their own `arguments` object

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [Akshay Saini — Functions in JS](https://www.youtube.com/results?search_query=functions+in+javascript+akshay+saini+namaste) | Hoisting, first-class functions, closures |
| 📺 YouTube | [Web Dev Simplified — Arrow Functions](https://www.youtube.com/results?search_query=arrow+functions+javascript+web+dev+simplified) | Arrow vs regular function, this binding |
| 📝 Article | [javascript.info — Functions](https://javascript.info/function-basics) | Complete guide with interactive examples |
| 📝 Article | [MDN — Functions](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Functions) | All function types, closures, scopes |
| 🐙 GitHub | [getify/You-Dont-Know-JS — Scope & Closures](https://github.com/getify/You-Dont-Know-JS/blob/2nd-ed/scope-closures/README.md) | Deep dive into function scope and hoisting |

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Function declaration | `function name() {}` — hoisted | Hoisted function syntax |
| Function expression | `const fn = function() {}` — not hoisted | Not hoisted function |
| Arrow function | `() => {}` — lexical this | Lexical this, concise |
| First-class function | Function as value (storable, passable) | Function एक value की तरह |
| Higher-order function | Takes/returns functions | Functions लेने/देने वाली function |
| Pure function | Same input → same output, no side effects | Predictable, no side effects |
| IIFE | Immediately Invoked Function Expression | तुरंत execute होने वाली function |

---

## ⚡ 3-Line Summary
**English:**
1. Function declarations are fully hoisted (usable before definition); function expressions are not (use after declaration).
2. Arrow functions have lexical `this` (from surrounding scope) — use for callbacks and React; avoid for object methods.
3. Functions are first-class in JS — can be stored, passed, and returned, enabling higher-order functions and closures.

**Hindi:**
1. Function declarations fully hoist होती हैं; expressions नहीं — पहले define, फिर use करो।
2. Arrow functions का `this` lexical है (surrounding scope से) — callbacks और React के लिए; object methods के लिए avoid।
3. Functions first-class हैं — store, pass, और return हो सकती हैं — higher-order functions और closures enable करता है।

---

## ➡️ Next Topic
**16. Arrow Functions** — Arrow function syntax, implicit return, `this` binding का detailed explanation, और कब avoid करना है।
