# 187. Implement call, apply, bind
# हिंदी में: call, apply, bind बनाना — `this` को तय करने के तीन तरीके

---

## 🔵 Simple Definition (English)
`call`, `apply`, and `bind` are methods on every function that control the value of `this` inside it. `call` runs the function now with a given `this` and separate arguments, `apply` does the same with an array of arguments, and `bind` returns a new function with `this` (and optionally some arguments) fixed for later.

## 🔵 सरल परिभाषा (Hindi)
`call`, `apply` और `bind` हर function पर मिलने वाले methods हैं, जो function के अंदर `this` का मान तय करते हैं। `call` उसी समय function को दिए गए `this` और अलग-अलग arguments के साथ चलाता है, `apply` वही काम arguments की array लेकर करता है, और `bind` एक नया function लौटाता है जिसमें `this` (और कुछ arguments) पहले से तय होते हैं।

---

## 🔴 Problem it Solves
**Problem Statement:** Implement `myCall`, `myApply`, and `myBind` on `Function.prototype`. They must set `this`, pass arguments correctly, return the result, and let a bound function work with `new`.

A method like `user.greet` does not carry its owner with it. When you pass it as a callback, `this` is lost. Libraries need a way to run a function as if it were called on another object, for example to borrow `Array.prototype.slice` for an array-like `arguments` object. Express route handlers and event callbacks depend on the same idea.

## 🔴 यह क्यों बना? (Hindi)
**Problem Statement:** `Function.prototype` पर `myCall`, `myApply` और `myBind` बनाओ। ये `this` तय करें, arguments सही भेजें, result लौटाएँ, और bound function `new` के साथ भी काम करे।

`user.greet` जैसा method अपना owner साथ नहीं ले जाता। Callback के रूप में पास करने पर `this` खो जाता है। Libraries को function को किसी दूसरे object पर call करने का तरीका चाहिए, जैसे `arguments` जैसे array-like object पर `Array.prototype.slice` उधार लेना। Express route handlers और event callbacks भी इसी विचार पर चलते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → To call `fn` with a chosen `this`, attach `fn` as a temporary property on that object.
Step 2 → Call the property, so JavaScript sets `this` to that object automatically.
Step 3 → Delete the temporary property and return the result.
Step 4 → `apply` does the same, but spreads an array of arguments.
Step 5 → `bind` saves `this` and the first arguments in a closure and returns a new function.
Step 6 → If the bound function is called with `new`, ignore the saved `this` and construct the target.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → किसी `this` के साथ `fn` call करने के लिए, `fn` को उसी object पर एक अस्थायी property के रूप में लगाओ।
Step 2 → उस property को call करो, तो JavaScript अपने आप `this` को उस object पर सेट कर देता है।
Step 3 → अस्थायी property हटाओ और result लौटाओ।
Step 4 → `apply` वही करता है, पर arguments की array को spread करके।
Step 5 → `bind` `this` और पहले arguments को closure में रखता है और नया function लौटाता है।
Step 6 → अगर bound function `new` से call हो, तो सहेजे गए `this` को छोड़कर target को construct करो।

---

## 🟡 Real World Example
Zomato's order page has a `RestaurantCard` helper that formats a price with the restaurant's currency and tax rules. The helper uses `this.currency`, so the page must call it with the right `this`. A list component borrows `Array.prototype.map` with `call` to process a `NodeList` from the DOM, and a payment SDK exposes `bind` so a callback keeps its `merchant` context.

Scenario: A Swiggy invoice function `formatTotal(prefix, suffix)` reads `this.currency`. The cart object is `{ currency: "INR" }`. Calling it with `call(cart, "Total: ", " (incl. GST)")` prints the total with the cart's currency, and `bind` gives the same function to a timer without losing the cart.

## 🟡 Real Example Hindi mein
Zomato के order page पर एक `RestaurantCard` helper है जो restaurant की currency और tax नियमों से price format करता है। Helper `this.currency` पढ़ता है, इसलिए page को सही `this` से call करना पड़ता है। एक list component DOM के `NodeList` के लिए `Array.prototype.map` को `call` से उधार लेता है, और एक payment SDK `bind` देता है ताकि callback अपना `merchant` context न खोए।

उदाहरण: Swiggy का invoice function `formatTotal(prefix, suffix)` `this.currency` पढ़ता है। Cart object `{ currency: "INR" }` है। `call(cart, "Total: ", " (incl. GST)")` से cart की currency के साथ total छपता है, और `bind` से वही function timer को दिया जा सकता है बिना cart खोए।

---

## 💻 Code Example — Basic
```javascript
// Basic: the native call, apply, and bind show what our versions must reproduce
const cart = { currency: "INR", items: 3 };      // an object that has a currency

// A function that uses this.currency
function formatTotal(prefix, suffix) {
  return `${prefix}${this.currency} for ${this.items} items${suffix}`; // read this.currency and this.items
}

// call: run now, with this = cart and arguments listed one by one
console.log(formatTotal.call(cart, "Total: ", "!"));    // Expected output: Total: INR for 3 items!

// apply: run now, with this = cart and arguments given as an array
console.log(formatTotal.apply(cart, ["Sum: ", "."]));   // Expected output: Sum: INR for 3 items.

// bind: create a new function with this = cart fixed, and the first argument fixed too
const withCart = formatTotal.bind(cart, "Bill: ");      // prefix is preset to "Bill: "
console.log(withCart(" ✔"));                            // Expected output: Bill: INR for 3 items ✔
```

## 💻 Code Example — Advanced
```javascript
// Advanced: our own myCall, myApply, and myBind, added to Function.prototype

// myCall: run this function with a given this and separate arguments
Function.prototype.myCall = function (thisArg, ...args) {
  // Guard: call must be used on a function
  if (typeof this !== "function") throw new TypeError("myCall must be called on a function");
  const ctx = thisArg == null ? globalThis : Object(thisArg); // null/undefined -> global object, primitives boxed
  const key = Symbol("tempFn");                  // unique key so we never overwrite a real property
  ctx[key] = this;                               // attach the function to the context object
  try {
    return ctx[key](...args);                    // calling it as ctx[key]() makes this = ctx
  } finally {
    delete ctx[key];                             // always remove the temporary property, even if it throws
  }
};

// myApply: same as myCall, but the arguments come as an array (or array-like)
Function.prototype.myApply = function (thisArg, argsList) {
  if (typeof this !== "function") throw new TypeError("myApply must be called on a function");
  // null or undefined means no arguments; any other value is turned into an array
  const list = argsList == null ? [] : Array.from(argsList);
  return this.myCall(thisArg, ...list);          // reuse myCall with the spread array
};

// myBind: return a new function with this and leading arguments fixed
Function.prototype.myBind = function (thisArg, ...presetArgs) {
  if (typeof this !== "function") throw new TypeError("myBind must be called on a function");
  const target = this;                           // the original function
  function bound(...laterArgs) {                 // the function that bind returns
    const allArgs = [...presetArgs, ...laterArgs]; // preset arguments come first, then the new ones
    if (new.target) {                            // called with new: thisArg is ignored, as in native bind
      return new target(...allArgs);             // construct the original with the combined arguments
    }
    return target.apply(thisArg, allArgs);       // normal call: use the fixed this
  }
  bound.prototype = Object.create(target.prototype); // so bound instances pass instanceof checks
  return bound;                                  // return the new function
};

// ---- Tests: run with plain node ----
function greet(greeting, punct) {
  return `${greeting}, ${this.name}${punct}`;   // uses this.name
}
const riya = { name: "Riya" };                   // the object we borrow as this
console.log(greet.myCall(riya, "Hi", "!"));      // Expected output: Hi, Riya!
console.log(greet.myApply(riya, ["Hello", "?"])); // Expected output: Hello, Riya?
const namaste = greet.myBind(riya, "Namaste");   // preset the greeting argument
console.log(namaste("."));                       // Expected output: Namaste, Riya.

class Point {
  constructor(x, y) { this.x = x; this.y = y; }  // constructor with two fields
}
const BoundPoint = Point.myBind(null, 1);        // bound constructor with x preset to 1
const p = new BoundPoint(9);                     // new uses the target, so this is a new Point
console.log(p instanceof Point, p.x, p.y);       // Expected output: true 1 9
console.log(Math.max.myApply(null, [3, 7, 2])); // Expected output: 7

// Time:  O(a) per call, where a is the number of arguments (spread and array copy)
// Space: O(a) for the argument array, plus one temporary Symbol property during myCall
```

### Edge Cases
```javascript
// These checks use native call, apply, bind; our versions must match them
function show(label) { return `${label}:${this === undefined ? "undefined" : typeof this}`; } // reports this

// Edge 1: null or undefined thisArg falls back to the global object in sloppy mode
console.log(show.call(null, "a"));               // Expected output: a:object
// Edge 2: a primitive this is boxed in sloppy mode
console.log(show.call(42, "b"));                 // Expected output: b:object
// Edge 3: apply needs an array-like second argument, not loose values
console.log(Math.max.apply(null, [1, 9, 4]));    // Expected output: 9
// Edge 4: bind on a bound function keeps the first this (it cannot be changed again)
const first = show.bind({ id: 1 });              // first binding
const second = first.bind({ id: 2 });            // binding again does nothing to this
console.log(second("c"));                        // Expected output: c:object
```

---

## 🟠 Express.js Integration
Express calls a route handler as a plain function, so a handler that uses `this` loses its owner. In a controller class, the usual fix is `bind` when registering the route. The same pattern appears in Express's `app.use` when middleware is a method of a class.

```javascript
// Express.js: a controller class whose methods use this, registered with bind
const express = require("express");               // import Express
const app = express();                            // create the app

// A controller that keeps its data in this.products
class ProductController {
  constructor(products) {
    this.products = products;                     // store the product list on the instance
  }
  // Uses this.products, so it must be called with the right this
  list(req, res) {
    const min = Number(req.query.minPrice || 0);  // read an optional filter from the query string
    const items = this.products.filter((p) => p.price >= min); // use this.products
    res.json(items);                              // 200 OK with the filtered list
  }
}

const controller = new ProductController([
  { id: 1, name: "Biryani", price: 180 },        // sample product
  { id: 2, name: "Paneer Roll", price: 120 },    // sample product
]);

// Wrong: app.get("/api/products", controller.list) would call list with this = undefined
// Right: bind the method to the controller so this.products works inside the handler
app.get("/api/products", controller.list.bind(controller)); // fixed this for every request

// Start the server on PORT from the environment, or 3000 by default
app.listen(process.env.PORT || 3000, () => {
  console.log("Product API running");            // ready message
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Passing a method as a callback without binding it, so `this` is lost
✅ **Correct:** Bind it, or wrap it in an arrow function that calls the method on the object

```javascript
// Wrong: the method loses its owner when it is copied into a variable and called alone
const worker = { label: "kitchen", report() { return this.label; } }; // object with a method
const detached = worker.report;                  // copy the function, not the owner
console.log(detached());                         // Expected output: undefined (this is not worker)

// Right: bind it to the object, or use an arrow wrapper
const attached = worker.report.bind(worker);     // this is fixed to worker
console.log(attached());                         // Expected output: kitchen
```

❌ **Mistake 2:** Passing loose arguments to `apply`, which expects an array
✅ **Correct:** Use `call` for a list of arguments, or pass an array to `apply`

```javascript
// Wrong: apply's second argument must be an array-like, so the loose number 1 is rejected
try {
  console.log(Math.max.apply(null, 1, 2, 3));   // the call itself throws before Math.max runs
} catch (err) {
  console.log(err.constructor.name);            // Expected output: TypeError
}

// Right: call takes the arguments one by one; apply takes them as one array
console.log(Math.max.call(null, 1, 2, 3));      // Expected output: 3
console.log(Math.max.apply(null, [1, 2, 3]));   // Expected output: 3
```

❌ **Mistake 3:** Expecting `bind` to change `this` for an arrow function
✅ **Correct:** Arrow functions take `this` from where they were written, so `bind` cannot change it

```javascript
// Wrong: the arrow function ignores the bound this and keeps the outer this
const obj = { name: "outer", make() { return () => this.name; } }; // arrow captures this
const arrow = obj.make().bind({ name: "bound" });               // try to rebind it
console.log(arrow());                                           // Expected output: outer

// Right: a normal function gets the bound this
const normal = function () { return this.name; };               // regular function
console.log(normal.bind({ name: "bound" })());                  // Expected output: bound
```

---

## 🧠 Tricky Interview Question
```javascript
const obj = { name: "obj", say() { return this.name; } }; // a method using this
const say = obj.say;                                       // copy the method, lose the owner
const bound = obj.say.bind({ name: "bound" });             // bind to a new object
console.log(say());                                        // ?
console.log(bound());                                      // ?
console.log(bound.call({ name: "other" }));                // ?
```
Answer: `undefined`, `bound`, `bound`.
`say()` runs as a plain call, so `this` is the global object in a non-strict file, and `globalThis.name` is `undefined`. `bound()` uses the bound `this`. `bound.call({ name: "other" })` still prints `bound`, because a bound function ignores later `call` and `apply` attempts to change `this`. Bind always wins.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between call and apply?**
A1: Both run the function immediately with a chosen `this`. `call` takes the arguments one by one, while `apply` takes them as a single array-like value.

**Q2: Why does `myCall` attach the function to the object?**
A2: Calling `ctx[key](...args)` is the only simple way to make JavaScript set `this` to `ctx` for that call. The `Symbol` key prevents clashes, and `delete` cleans up.

**Q3: What does `bind` return, and when does it run?**
A3: It returns a new function. Nothing runs until that new function is called. The new function has `this` and some arguments fixed.

**Q4: How does a bound function behave with `new`?**
A4: `new` ignores the bound `this` and creates a new instance of the target. Our `myBind` checks `new.target` for this case, as native bind does.

**Q5: Can you change `this` of a bound function again?**
A5: No. Calling `call`, `apply`, or `bind` on a bound function cannot override the first bound `this`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You must pass a method as a callback and keep its owner (event handlers, route handlers, timers)
- You want to borrow a method from one object for another, such as `Array.prototype.slice` on `arguments`
- You want a partially applied function with some arguments fixed (`bind`)

❌ Avoid when:
- An arrow function or a closure does the job more clearly; modern code rarely needs `bind` for simple callbacks
- You are calling a method on the same object you already have; just write `obj.method()`
- Performance matters in a hot loop; `bind` creates a new function on every call, so define it once outside the loop

---

## 📊 Visual Diagram
```
  greet.myCall(riya, "Hi", "!")
        |
        v
  riya[tempKey] = greet            <-- attach the function to the context
        |
        v
  riya[tempKey]("Hi", "!")         <-- JavaScript sets this = riya
        |
        v
  delete riya[tempKey]             <-- clean up
        |
        v
  return "Hi, Riya!"

  greet.myBind(riya, "Namaste")  -->  bound(".")
                                       |
                                       v
                       greet.apply(riya, ["Namaste", "."])
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `this` | The object a function is running on | Function किस object पर चल रहा है |
| `call` | Run now with given `this` and listed arguments | अभी चलाना, `this` और arguments अलग-अलग देकर |
| `apply` | Run now with given `this` and an argument array | अभी चलाना, arguments की array देकर |
| `bind` | Return a new function with `this` fixed | `this` तय करके नया function लौटाना |
| Method borrowing | Using one object's method on another object | एक object का method दूसरे object पर इस्तेमाल करना |
| Partial application | Fixing some arguments in advance | कुछ arguments पहले से तय करना |
| `new.target` | Tells a function whether it was called with `new` | Function को बताना कि `new` से call हुआ या नहीं |

---

## ⚡ 3-Line Summary
English:
1. `call`, `apply`, and `bind` control the value of `this` inside a function.
2. `call` and `apply` run now; `apply` takes an array, and `bind` returns a new function with `this` fixed.
3. A bound `this` cannot be overridden, and arrow functions ignore `bind` entirely.

Hindi:
1. `call`, `apply` और `bind` function के अंदर `this` का मान तय करते हैं।
2. `call` और `apply` अभी चलते हैं; `apply` array लेता है, और `bind` नया function लौटाता है जिसका `this` तय होता है।
3. Bound `this` बदला नहीं जा सकता, और arrow functions पर `bind` का असर नहीं होता।

---

## ➡️ Next Topic
**188. Implement new keyword** — once you can set `this` yourself, the next problem shows exactly what `new` does: create an object, link its prototype, call the constructor, and return the result.
