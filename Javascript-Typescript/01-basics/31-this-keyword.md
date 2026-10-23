# 31. `this` Keyword
# हिंदी में: `this` — JavaScript का सबसे Confusing Concept, आसान बनाते हैं

---

## 🔵 Simple Definition (English)
`this` refers to the **object that is executing the current function**. Its value is NOT fixed — it depends on **how the function is called**, not where it's defined (except arrow functions, which inherit `this` from where they're defined).

## 🔵 सरल परिभाषा (Hindi)
`this` उस **object को refer करता है जो current function को execute कर रहा है**। इसकी value fixed नहीं है — यह depend करती है **function को कैसे call किया गया** (arrow functions except — वो define होने वाली जगह से `this` लेते हैं)।

---

## 🟢 The 5 Rules of `this`

```
1. GLOBAL context:      this = window (browser) / global (Node) / undefined (strict)
2. METHOD call:         obj.method()  → this = obj
3. FUNCTION call:       fn()          → this = undefined (strict) / window (non-strict)
4. CONSTRUCTOR call:    new Fn()      → this = new object being created
5. EXPLICIT binding:    .call/.apply/.bind → this = whatever you pass
6. ARROW FUNCTION:      No own this  → inherits from enclosing scope
```

---

## 🟡 Real World Example
```javascript
const restaurant = {
  name: "Zomato Kitchen",
  orders: [],

  // Regular method — this = restaurant
  addOrder(item) {
    this.orders.push(item); // ✅ this is restaurant
    console.log(`${this.name}: Added ${item}`);
  },

  // Arrow — this from enclosing scope (module/global)
  badAdd: () => {
    // this.orders is undefined! (arrow doesn't get restaurant as this)
    console.log(this); // window or undefined
  },

  // Fix: use regular function for methods
  printOrders() {
    // Inside callback: need arrow to keep this = restaurant
    this.orders.forEach(order => {
      console.log(`${this.name} order: ${order}`); // ✅ arrow inherits this
    });
  },
};

restaurant.addOrder("Pizza");
restaurant.printOrders();
```

---

## 💻 Code Example — Basic
```javascript
// ── RULE 1: GLOBAL CONTEXT ───────────────

// Non-strict mode:
function showThis() {
  console.log(this); // window (browser) / global (Node)
}
showThis();

// Strict mode:
"use strict";
function showThisStrict() {
  console.log(this); // undefined
}
showThisStrict();

// Arrow at global level:
const arrow = () => console.log(this); // window (inherits global this)

// ── RULE 2: METHOD CALL ──────────────────

const user = {
  name: "Aditya",
  greet() {
    return `Hello, I'm ${this.name}`; // this = user
  },
  getName() {
    return this.name; // this = user
  },
};

user.greet();   // "Hello, I'm Aditya"
user.getName(); // "Aditya"

// Method detached from object — this changes!
const detached = user.greet; // copy of function, not bound to user
// detached(); // this = undefined (strict) / window (non-strict)

// ── RULE 3: CONSTRUCTOR ──────────────────

function Person(name, age) {
  this.name = name; // this = new object
  this.age = age;
  this.greet = function() {
    return `Hi, I'm ${this.name}, ${this.age} years old`;
  };
}

const p1 = new Person("Aditya", 25); // this = new Person object
const p2 = new Person("Priya", 22);

p1.greet(); // "Hi, I'm Aditya, 25 years old"
p2.greet(); // "Hi, I'm Priya, 22 years old"

// ── RULE 4: EXPLICIT BINDING ─────────────

function introduce() {
  return `Hi, I'm ${this.name} from ${this.city}`;
}

const aditya = { name: "Aditya", city: "Mumbai" };
const priya  = { name: "Priya",  city: "Delhi" };

// .call — immediate call, args as comma-separated
introduce.call(aditya); // "Hi, I'm Aditya from Mumbai"
introduce.call(priya);  // "Hi, I'm Priya from Delhi"

// .apply — immediate call, args as array
function greetWithPrefix(prefix, punctuation) {
  return `${prefix}, ${this.name}${punctuation}`;
}
greetWithPrefix.apply(aditya, ["Hello", "!"]); // "Hello, Aditya!"

// .bind — returns a new function with fixed this
const adityaIntro = introduce.bind(aditya);
adityaIntro(); // "Hi, I'm Aditya from Mumbai" (this always = aditya)

// Bind with preset args (partial application):
const greetAditya = greetWithPrefix.bind(aditya, "Namaste");
greetAditya("!"); // "Namaste, Aditya!"
greetAditya("?"); // "Namaste, Aditya?"

// ── RULE 5: ARROW FUNCTION ───────────────

const obj = {
  name: "Aditya",

  // Regular method: this = obj
  regularMethod() {
    console.log("regular:", this.name); // "Aditya"
  },

  // Arrow method: this = outer scope (NOT obj!)
  arrowMethod: () => {
    console.log("arrow:", this?.name); // undefined
    // 'this' here is the outer scope (global/window)
  },

  delayedRegular() {
    // setTimeout with regular function: this = window/undefined!
    setTimeout(function() {
      console.log("delayed regular:", this?.name); // undefined
    }, 100);
  },

  delayedArrow() {
    // setTimeout with arrow: this = obj (lexically inherited!)
    setTimeout(() => {
      console.log("delayed arrow:", this.name); // "Aditya" ✅
    }, 100);
  },
};

obj.regularMethod(); // "Aditya"
obj.arrowMethod();   // undefined
obj.delayedArrow();  // "Aditya" ✅ — arrow inherits this from delayedArrow
```

## 💻 Code Example — Advanced
```javascript
// ── CLASS SYNTAX AND this ────────────────

class Order {
  constructor(id, item) {
    this.id = id;
    this.item = item;
    this.status = "pending";
  }

  // Regular method: this = instance
  updateStatus(newStatus) {
    this.status = newStatus;
    return this; // enables chaining
  }

  // Arrow as class field: this = instance (always)
  getInfo = () => {
    return `Order ${this.id}: ${this.item} (${this.status})`;
  };
}

const order1 = new Order("ORD-1", "Pizza");
order1.updateStatus("preparing");
console.log(order1.getInfo()); // "Order ORD-1: Pizza (preparing)"

// ── EVENT HANDLERS — THE CLASSIC THIS PROBLEM ──

class Timer {
  constructor() {
    this.seconds = 0;
  }

  // WRONG: regular function loses this in setTimeout
  startWrong() {
    setInterval(function() {
      this.seconds++; // ❌ this = undefined (strict) or window
      console.log(this.seconds);
    }, 1000);
  }

  // FIX 1: arrow function (inherits this from startCorrect)
  startArrow() {
    setInterval(() => {
      this.seconds++; // ✅ this = Timer instance
      console.log(this.seconds);
    }, 1000);
  }

  // FIX 2: bind
  startBind() {
    setInterval(function() {
      this.seconds++; // ✅ this = Timer (bound)
    }.bind(this), 1000);
  }

  // FIX 3: save reference
  startSelf() {
    const self = this; // old pattern, avoid
    setInterval(function() {
      self.seconds++; // ✅ self is Timer
    }, 1000);
  }
}

// ── LOSING this IN CALLBACKS ─────────────

class ProductService {
  constructor() {
    this.products = [{ id: 1, name: "Pizza", active: true }];
  }

  // WRONG: method passed as callback loses this
  fetchAndProcess() {
    // If someone calls: db.find(service.processResults)
    // 'this' inside processResults = undefined!
  }

  processResults(data) {
    return data.filter(item => this.products.includes(item)); // this = undefined!
  }

  // FIX: bind in constructor
  constructor2() {
    this.processResults = this.processResults.bind(this); // bind once
    // OR: use arrow class fields (recommended):
  }

  // Arrow class field — always bound:
  processResultsArrow = (data) => {
    return data.filter(item => this.products.includes(item)); // ✅
  };
}

// ── CALL/APPLY PRACTICAL USE ──────────────

// Borrow methods:
const arrayLike = { 0: "a", 1: "b", 2: "c", length: 3 };

// arrayLike.map(...) — doesn't work (not a real array)
// Borrow Array.prototype.map:
const result = Array.prototype.map.call(arrayLike, item => item.toUpperCase());
// ["A", "B", "C"]

// Math.max with array:
Math.max.apply(null, [1, 5, 3, 9, 2]); // 9
// OR (modern):
Math.max(...[1, 5, 3, 9, 2]); // 9
```

---

## 🟠 React/Next.js Connection
```jsx
// ── REACT CLASSES — BIND ISSUE ────────────

// Old class component:
class SearchBar extends React.Component {
  constructor(props) {
    super(props);
    this.state = { query: "" };

    // Must bind or arrow functions for event handlers:
    this.handleChange = this.handleChange.bind(this); // explicit bind
  }

  handleChange(e) {
    this.setState({ query: e.target.value }); // this = component (bound)
  }

  // Arrow class field — auto-bound (modern approach):
  handleSubmit = (e) => {
    e.preventDefault();
    console.log(this.state.query); // this always = component
  };

  render() {
    return (
      <form onSubmit={this.handleSubmit}>
        <input onChange={this.handleChange} value={this.state.query} />
      </form>
    );
  }
}

// ── FUNCTION COMPONENTS — this NOT USED ──

// Modern React (function components): no this issues!
// useState/hooks replace all this patterns
function SearchBarFn() {
  const [query, setQuery] = useState("");
  // No 'this' needed — hooks give us state management
  return <input value={query} onChange={e => setQuery(e.target.value)} />;
}

// ── WHEN this MATTERS IN MODERN REACT ─────
// Still matters in: class components, utility classes, OOP services

class ApiService {
  constructor(baseURL) {
    this.baseURL = baseURL;
    this.token = null;
  }

  // Arrow method — safe to pass as callback
  fetch = async (endpoint) => {
    const url = `${this.baseURL}${endpoint}`; // this always bound
    const response = await fetch(url, {
      headers: { Authorization: `Bearer ${this.token}` }
    });
    return response.json();
  };
}

const api = new ApiService("https://api.example.com");
// Safe: api.fetch can be passed to useEffect, setTimeout, etc.
useEffect(() => {
  api.fetch("/products").then(setProducts); // this = api (arrow field)
}, []);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Arrow functions as object methods
```javascript
const obj = {
  name: "Aditya",
  // WRONG: arrow doesn't get obj as this
  greet: () => `Hello, ${this.name}`, // this = outer scope (window/undefined)
};
obj.greet(); // "Hello, undefined"

// CORRECT: regular method
const obj2 = {
  name: "Aditya",
  greet() { return `Hello, ${this.name}`; }, // this = obj2
};
obj2.greet(); // "Hello, Aditya" ✅
```

❌ **Mistake 2:** Detaching methods from objects
```javascript
const user = { name: "Aditya", greet() { return this.name; } };

const fn = user.greet; // detached — no longer bound to user
fn(); // undefined (or crash in strict) — this is not user!

// CORRECT: bind when detaching
const boundFn = user.greet.bind(user);
boundFn(); // "Aditya" ✅
```

❌ **Mistake 3:** Using regular function in callback expecting this to persist
```javascript
class Timer {
  ticks = 0;
  start() {
    setInterval(function() {
      this.ticks++; // ❌ this = undefined/window
    }, 1000);
  }
}

// CORRECT: arrow function
class Timer {
  ticks = 0;
  start() {
    setInterval(() => {
      this.ticks++; // ✅ arrow inherits this from start()
    }, 1000);
  }
}
```

---

## 🧠 Tricky Interview Output Question
```javascript
const obj = {
  name: "Aditya",
  getName() { return this.name; },
  getArrow: () => this?.name,
};

const { getName, getArrow } = obj;

console.log(obj.getName());  // A
console.log(getName());      // B
console.log(obj.getArrow()); // C
console.log(getArrow());     // D
```
**Answer (strict mode):**
```
"Aditya"   ← A: called on obj, this = obj
undefined  ← B: detached, this = undefined (strict), no .name
undefined  ← C: arrow, this = outer scope (not obj), this?.name = undefined
undefined  ← D: same — arrow always has outer this, not obj
```

---

## ⚫ Interview Questions + Answers

**Q1: What is `this` in JavaScript and what determines its value?**
A1: `this` refers to the execution context — the object "calling" the function. Its value is determined by **how** the function is invoked: (1) method call → the owning object, (2) regular function call → undefined (strict) / global, (3) constructor (`new`) → the new instance, (4) `call`/`apply`/`bind` → explicitly set, (5) arrow function → inherits from enclosing lexical scope.

**Q2: What is the difference between call, apply, and bind?**
A2: All three explicitly set `this`. `call(thisArg, arg1, arg2)` — invokes immediately, arguments comma-separated. `apply(thisArg, [arg1, arg2])` — invokes immediately, arguments as array (useful for spreading). `bind(thisArg, arg1)` — returns a new permanently-bound function without calling it (useful for callbacks, event handlers, partial application).

**Q3: Why don't arrow functions have their own `this`?**
A3: Arrow functions were designed for callbacks — to avoid the common bug of losing `this` in nested functions. Instead of having their own `this` (determined at call time), arrows inherit `this` from the surrounding lexical scope (determined at definition time). This makes them ideal for callbacks, `setTimeout`, `forEach`, and React event handlers inside class components.

**Q4: What is the "lost this" problem and how do you fix it?**
A4: When you pass an object's method as a callback, it loses its binding to the object. `setTimeout(obj.method, 100)` — when called by setTimeout, `this` is no longer `obj`. Fix options: (1) Arrow function wrapper: `setTimeout(() => obj.method(), 100)`. (2) `.bind`: `setTimeout(obj.method.bind(obj), 100)`. (3) Arrow class fields (modern): `method = () => { ... }` — always bound to instance.

**Q5: How does `this` work in classes?**
A5: In class constructors and methods, `this` refers to the instance. Regular class methods can lose `this` if passed as callbacks. Solutions: (1) Bind in constructor: `this.method = this.method.bind(this)`. (2) Arrow class fields: `method = () => {}` — auto-bound. Modern React class components use arrow fields for event handlers. In functional components, `this` is irrelevant — hooks replace it entirely.

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [Akshay Saini — this keyword](https://www.youtube.com/results?search_query=this+keyword+javascript+akshay+saini) | All 5 rules explained |
| 📺 YouTube | [Web Dev Simplified — this](https://www.youtube.com/results?search_query=this+keyword+javascript+web+dev+simplified) | Visual call/apply/bind |
| 📝 Article | [javascript.info — Object methods this](https://javascript.info/object-methods) | Complete this guide |
| 📝 Article | [MDN — this](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/this) | All contexts explained |

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| this | Current execution context | Current execution context |
| Execution context | Object calling the function | Function call करने वाला object |
| Method call | obj.fn() → this = obj | Method call |
| Implicit binding | this set by how fn is called | Call से this तय होना |
| Explicit binding | call/apply/bind | call/apply/bind से this set करना |
| Arrow this | Inherited from outer scope | Outer scope से this inherit |
| Lost this | Method detached from object | Method का object से अलग होना |

---

## ⚡ 3-Line Summary
**English:**
1. `this` = the object calling the function — 5 rules: global, method call, constructor, explicit (.call/.apply/.bind), arrow (lexical).
2. Arrow functions have NO own `this` — they inherit from enclosing scope. Never use arrows as object methods.
3. "Lost this" bug: pass method as callback → `this` becomes undefined. Fix: arrow wrapper, `.bind()`, or arrow class fields.

**Hindi:**
1. `this` = function call करने वाला object — 5 rules: global, method call, constructor, explicit, arrow (lexical)।
2. Arrow functions का अपना `this` नहीं — outer scope से inherit। Arrow को object method कभी मत बनाओ।
3. "Lost this" bug: method को callback में pass करो → `this` undefined। Fix: arrow wrapper, `.bind()`, या arrow class fields।

---

## ➡️ Next Topic
**32. Prototypes and Prototype Chain** — JavaScript का inheritance system — `__proto__`, Object.create, और class के under the hood।
