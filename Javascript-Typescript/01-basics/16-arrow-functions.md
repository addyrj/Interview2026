# 16. Arrow Functions
# हिंदी में: Arrow Functions — Concise Syntax और Lexical `this`

---

## 🔵 Simple Definition (English)
Arrow functions (`=>`) are a **shorter syntax** for function expressions. Key difference: they **don't have their own `this`** — they inherit `this` from the surrounding lexical scope. They also lack `arguments`, can't be used as constructors, and have implicit return for single expressions.

## 🔵 सरल परिभाषा (Hindi)
Arrow functions (`=>`) function expressions का short syntax हैं। Key difference: इनका खुद का `this` नहीं होता — surrounding scope से `this` लेते हैं (lexical)। React/Node.js में सबसे ज़्यादा use होने वाला syntax।

---

## 🔴 Problem it Solves
Before arrow functions, callbacks lost `this` context:
```javascript
function Timer() {
  this.seconds = 0;
  setInterval(function() {
    this.seconds++; // WRONG! 'this' is window/undefined here
    console.log(this.seconds);
  }, 1000);
}
```
Arrow functions fix this by capturing `this` from the outer scope.

## 🔴 यह क्यों बना? (Hindi)
Regular functions में `this` caller के हिसाब से बदलता था — callbacks में context खो जाता था। Arrow functions outer scope का `this` लेते हैं — Timer, React event handlers, array methods सब fix हो जाते हैं।

---

## 🟢 Syntax Variations

```javascript
// 1. Multiple params, body with return
const add = (a, b) => {
  return a + b;
};

// 2. Multiple params, implicit return (no braces)
const add = (a, b) => a + b;

// 3. Single param (parentheses optional)
const double = n => n * 2;
const double = (n) => n * 2; // same thing

// 4. No params (parentheses required)
const greet = () => "Hello!";

// 5. Return object (must wrap in parentheses!)
const getUser = () => ({ name: "Aditya", age: 25 });
// Without (): () => { name: "Aditya" } looks like a block!

// 6. Multi-line body (explicit return needed)
const processOrder = (order) => {
  const total = order.price * order.qty;
  const withGST = total * 1.18;
  return { total, withGST }; // explicit return needed
};
```

---

## 🟡 Real World Example
```javascript
// Array transformations (most common use)
const prices = [299, 499, 199, 999];
const withGST = prices.map(p => p * 1.18);         // [352.82, ...]
const expensive = prices.filter(p => p > 400);     // [499, 999]
const total = prices.reduce((sum, p) => sum + p, 0); // 1996

// React onClick handler
const handleDelete = (id) => () => {  // curried arrow function
  deleteItem(id);
};

// API fetch
const fetchUser = async (id) => {
  const res = await fetch(`/api/user/${id}`);
  return res.json();
};
```

---

## 💻 Code Example — Basic
```javascript
// ── SYNTAX ───────────────────────────

// Regular function:
function square(n) { return n * n; }

// Arrow function (equivalent):
const square = (n) => { return n * n; };

// Arrow — implicit return (shortest):
const square = n => n * n;

// Multiple operations:
const greetUser = (name, time) => {
  const period = time < 12 ? "morning" : "evening";
  return `Good ${period}, ${name}!`;
};
console.log(greetUser("Aditya", 10)); // "Good morning, Aditya!"

// ── AS CALLBACKS ──────────────────────
const nums = [1, 2, 3, 4, 5, 6];

// Old way (verbose):
const evens = nums.filter(function(n) { return n % 2 === 0; });

// Arrow (clean):
const evens = nums.filter(n => n % 2 === 0); // [2, 4, 6]

// Chained:
const result = nums
  .filter(n => n % 2 === 0)        // [2, 4, 6]
  .map(n => n * 10)                 // [20, 40, 60]
  .reduce((sum, n) => sum + n, 0);  // 120

console.log(result); // 120

// ── OBJECT RETURN ────────────────────
const users = [
  { id: 1, name: "Aditya", age: 25 },
  { id: 2, name: "Rajan", age: 30 },
];

// Map to simpler objects:
const summaries = users.map(({ id, name }) => ({ id, name }));
// [{ id:1, name:"Aditya" }, { id:2, name:"Rajan" }]
```

## 💻 Code Example — Advanced
```javascript
// ── THIS BINDING — THE KEY DIFFERENCE ─

// Problem with regular function in setTimeout:
function Timer_broken() {
  this.seconds = 0;
  setInterval(function() {
    this.seconds++; // 'this' is window (or undefined in strict mode)
    console.log(this.seconds); // NaN or error!
  }, 1000);
}

// Fixed with arrow function:
function Timer_fixed() {
  this.seconds = 0;
  setInterval(() => {
    this.seconds++; // 'this' = Timer instance (lexical from constructor)
    console.log(this.seconds); // 1, 2, 3...
  }, 1000);
}

// ── CLASS METHODS ────────────────────
class Counter {
  constructor() {
    this.count = 0;
  }

  // Regular method — 'this' depends on how called
  increment() {
    this.count++;
    return this.count;
  }

  // Arrow class field — 'this' always bound to instance
  incrementArrow = () => {
    this.count++;
    return this.count;
  };

  startCounting() {
    // Arrow: 'this' = Counter instance (works!)
    setInterval(() => {
      this.increment(); // safe to call as this is bound
    }, 1000);

    // Regular: 'this' = undefined in strict mode (broken)
    // setInterval(function() {
    //   this.increment(); // TypeError!
    // }, 1000);
  }
}

// ── WHAT ARROW FUNCTIONS DON'T HAVE ──

// 1. No 'arguments' object:
const showArgs = () => {
  // console.log(arguments); // ❌ ReferenceError
};

function showArgsRegular() {
  console.log(arguments); // ✅ works — [1, 2, 3]
}
showArgsRegular(1, 2, 3);

// Arrow alternative: use rest params
const showArgsArrow = (...args) => {
  console.log(args); // [1, 2, 3] ✅
};
showArgsArrow(1, 2, 3);

// 2. Cannot be used as constructor:
const Person = (name) => { this.name = name; };
// new Person("Aditya"); // ❌ TypeError: Person is not a constructor

// 3. No prototype:
console.log((() => {}).prototype); // undefined

// ── CURRIED ARROW FUNCTIONS ───────────
// Function returning a function (common pattern)
const multiply = (a) => (b) => a * b;
const double = multiply(2);
const triple = multiply(3);

console.log(double(5));  // 10
console.log(triple(5));  // 15

// React: click handler with parameter
const handleClick = (id) => (event) => {
  event.preventDefault();
  deleteItem(id); // id is captured from outer scope
};

// <button onClick={handleClick(item.id)}>Delete</button>
```

---

## 🟠 React/Next.js Connection
```jsx
import { useState, useEffect } from "react";

// ✅ React components as arrow functions
const ProductCard = ({ product, onAddToCart }) => {
  const [count, setCount] = useState(0);

  // ✅ Event handlers as arrows (lexical this, clean)
  const handleAdd = () => {
    setCount(c => c + 1);
    onAddToCart(product.id);
  };

  // ✅ useEffect with arrow cleanup
  useEffect(() => {
    const timer = setInterval(() => {
      // 'this' doesn't matter in function components, but arrows are clean
      console.log("Still mounted");
    }, 1000);

    return () => clearInterval(timer); // cleanup arrow
  }, []);

  // ✅ Inline arrows in JSX (fine for simple cases)
  return (
    <div>
      <h3>{product.name}</h3>
      <button onClick={handleAdd}>Add ({count})</button>
      {/* Inline arrow — acceptable for simple logic */}
      <button onClick={() => onAddToCart(product.id, 1)}>Buy Now</button>
      {/* Avoid complex inline arrows for performance (re-creates on render) */}
    </div>
  );
};

// ✅ Custom hooks are arrow functions
const useLocalStorage = (key, initialValue) => {
  const [value, setValue] = useState(() => {
    // Arrow IIFE-style initialization
    try {
      return JSON.parse(localStorage.getItem(key)) ?? initialValue;
    } catch {
      return initialValue;
    }
  });

  const setStoredValue = (newValue) => {
    setValue(newValue);
    localStorage.setItem(key, JSON.stringify(newValue));
  };

  return [value, setStoredValue];
};
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Arrow function as object method
```javascript
// WRONG: arrow captures 'this' from outer scope (global/undefined)
const user = {
  name: "Aditya",
  greet: () => {
    console.log(`Hi, ${this.name}`); // undefined or error!
  }
};

// CORRECT: regular function or shorthand method
const user = {
  name: "Aditya",
  greet() {  // method shorthand
    console.log(`Hi, ${this.name}`); // "Hi, Aditya" ✅
  }
};
```

❌ **Mistake 2:** Forgetting parentheses when returning object
```javascript
// WRONG: {} looks like a block to JS
const getUser = () => { name: "Aditya" }; // undefined! (empty block with label)

// CORRECT: wrap object in ()
const getUser = () => ({ name: "Aditya" }); // ✅ { name: "Aditya" }
```

❌ **Mistake 3:** Arrow in `addEventListener` when you need `this`
```javascript
// WRONG: 'this' inside arrow is NOT the element
button.addEventListener("click", () => {
  console.log(this); // window, not the button!
  this.classList.add("active"); // error
});

// CORRECT: regular function
button.addEventListener("click", function() {
  console.log(this); // the button element ✅
  this.classList.add("active"); // works!
});

// OR: use event.currentTarget
button.addEventListener("click", (event) => {
  event.currentTarget.classList.add("active"); // works with arrow too
});
```

---

## 🧠 Tricky Interview Output Question
```javascript
const obj = {
  value: 42,
  getValue: function() {
    const inner = () => this.value; // arrow inside regular method
    return inner();
  },
  getValueArrow: () => {
    return this.value; // arrow as method
  }
};

console.log(obj.getValue());      // ?
console.log(obj.getValueArrow()); // ?
```
**Answer:**
```
42         ← inner arrow inherits 'this' from getValue (which is obj)
undefined  ← getValueArrow is an arrow — 'this' is global (or undefined strict)
```

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between arrow functions and regular functions?**
A1: (1) Syntax: arrow is shorter. (2) `this`: arrow has lexical `this` (from outer scope), regular has dynamic `this` (from caller). (3) `arguments`: regular has it, arrow doesn't. (4) Constructor: regular can be used with `new`, arrow cannot. (5) Prototype: regular has `prototype`, arrow doesn't.

**Q2: What is lexical `this` in arrow functions?**
A2: Arrow functions don't have their own `this` binding. When you use `this` inside an arrow, it refers to the `this` of the enclosing lexical scope — where the arrow was defined, not where it's called. This makes arrows ideal for callbacks and methods where you need to access the outer object's `this`.

**Q3: Why can't arrow functions be used as constructors?**
A3: Arrow functions don't have their own `this` binding and have no `prototype` property. The `new` keyword requires both: a `this` to initialize and a `prototype` to set on the new object's `__proto__`. Since arrows have neither, `new ArrowFn()` throws a TypeError.

**Q4: When should you use arrow functions vs regular functions?**
A4: Use arrows for callbacks, array methods, React components/hooks/handlers, and any place you need lexical `this`. Use regular functions for object methods (need their own `this`), constructor functions, functions needing `arguments` object, and generators.

**Q5: What is the implicit return in arrow functions?**
A5: When an arrow function body has no `{}` braces, the expression result is automatically returned — no `return` keyword needed. `const double = n => n * 2` is equivalent to `const double = n => { return n * 2; }`. For objects, use `() => ({ key: value })` since `{}` would be parsed as a block.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Arrow function | `() => {}` — concise, lexical this | Concise function, lexical this |
| Lexical this | this from surrounding scope | Outer scope का this |
| Implicit return | Auto-return without `return` keyword | Automatic return |
| Curried arrow | Arrow returning arrow | Arrow जो arrow return करे |
| Dynamic this | this depends on how function is called | Caller के हिसाब से this |
| Constructor | Function used with `new` | new के साथ use होने वाली function |

---

## ⚡ 3-Line Summary
**English:**
1. Arrow functions are shorter expressions with implicit return for single expressions.
2. Key difference: no own `this` — they use lexical `this` from the enclosing scope, making them perfect for callbacks.
3. Avoid as object methods or constructors; use for everything else — array methods, React components, and event handlers.

**Hindi:**
1. Arrow functions short expressions हैं — single expression के लिए implicit return।
2. Key difference: खुद का `this` नहीं — outer scope का `this` लेते हैं — callbacks के लिए perfect।
3. Object methods और constructors में avoid करो; बाकी सब में use करो — array methods, React, event handlers।

---

## ➡️ Next Topic
**17. Default Parameters** — Function parameters के लिए default values कैसे set करें, और पुराने `|| default` pattern से कैसे बेहतर है।
