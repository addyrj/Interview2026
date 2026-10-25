# 196. this Output Questions
# हिंदी में: `this` के Output Questions — Call Site, Arrow Functions, bind और Class Methods

---

## 🔵 Simple Definition (English)
`this` is a value that a function receives when it runs, and it points to the object the function was called on. The value depends on how the function is called, not where it is written. Arrow functions are the exception: they take `this` from the code around them. Interviews use `this` to test whether you can predict the value from the call site.

## 🔵 सरल परिभाषा (Hindi)
`this` एक value है जो function को चलते समय मिलती है, और वह उस object की तरफ इशारा करती है जिस पर function call हुआ। यह value इस बात पर निर्भर करती है कि function कैसे call हुआ, न कि वह कहाँ लिखा है। Arrow functions अपवाद हैं: वे अपना `this` अपने आसपास के code से लेते हैं। Interview में `this` इसलिए पूछा जाता है ताकि देखा जाए कि आप call के तरीके से value पहचान सकते हैं या नहीं।

---

## 🔴 Problem it Solves
**Problem Statement:** Predict the value of `this` for each call: a plain function call, a method call, a method passed as a callback, an arrow function, a `bind`-ed function, a constructor call, and a `setTimeout` callback. Then fix the cases where `this` is lost.

Before arrow functions and `bind` were common, callbacks lost their object and printed `undefined`. Developers wrote `var self = this` everywhere. Even today, passing `controller.show` into a router or `obj.method` into `setTimeout` loses `this` if you do not bind it.

## 🔴 यह क्यों बना? (Hindi)
**Problem Statement:** हर call पर `this` की value बताओ: सादा function call, method call, callback के रूप में पास किया गया method, arrow function, `bind` किया गया function, constructor call, और `setTimeout` callback। फिर उन जगहों को ठीक करो जहाँ `this` खो जाता है।

Arrow functions और `bind` आम होने से पहले callbacks अपना object खो देते थे और `undefined` छापते थे। Developers हर जगह `var self = this` लिखते थे। आज भी controller का method router को देने पर या `obj.method` को `setTimeout` में देने पर `this` खो जाता है, अगर bind न करें।

---

## 🟢 How it Works — Step by Step

Step 1 → `new` call: `this` is the new empty object that the constructor will fill.
Step 2 → Explicit call: `fn.call(obj)`, `fn.apply(obj)`, or `fn.bind(obj)` sets `this` to `obj`.
Step 3 → Method call: `obj.fn()` sets `this` to `obj`, the object left of the dot.
Step 4 → Plain call: `fn()` sets `this` to `undefined` in strict mode, and to `globalThis` in sloppy mode.
Step 5 → Arrow function: `this` is taken from the surrounding scope when the arrow is created, and it never changes.
Step 6 → Priority, highest first: `new` > bound function > explicit call/apply > method call > default.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → `new` call: `this` वह नया खाली object है जिसे constructor भरेगा।
Step 2 → साफ़ call: `fn.call(obj)`, `fn.apply(obj)`, या `fn.bind(obj)` से `this` `obj` बनता है।
Step 3 → Method call: `obj.fn()` में `this` वह object है जो dot के बाईं तरफ है।
Step 4 → सादा call: `fn()` में strict mode में `this` `undefined` होता है, और sloppy mode में `globalThis`।
Step 5 → Arrow function: `this` उस समय के आसपास के scope से लिया जाता है जब arrow बना, और वह कभी नहीं बदलता।
Step 6 → प्राथमिकता, ऊपर से नीचे: `new` > bound function > call/apply > method call > default।

---

## 🟡 Real World Example
Zomato's cart code keeps a `Cart` object with `items` and a `total()` method. A button's click handler calls `cart.total` as a callback, and the total shows `NaN` because `this` is the button, not the cart. Developers fix it with an arrow function or `bind`. A Paytm dashboard uses a `ReportService` class whose methods are passed to an Express router, and it uses `bind` in the constructor so each method keeps the service.

Scenario: A Flipkart product card has `addToCart()` in a class. The class is rendered inside a list, and the click handler passes `this.addToCart` directly. On click, `this.items` is `undefined`, and the error says "Cannot read properties of undefined". The fix is `bind` in the constructor.

## 🟡 Real Example Hindi mein
Zomato के cart code में `Cart` object है जिसमें `items` और `total()` method है। Button का click handler `cart.total` को callback की तरह call करता है, और total `NaN` दिखता है क्योंकि `this` cart नहीं, button है। Developers arrow function या `bind` से ठीक करते हैं। Paytm के dashboard में `ReportService` class के methods Express router को दिए जाते हैं, और constructor में `bind` होता है ताकि हर method अपना service याद रखे।

उदाहरण: Flipkart के product card में class का `addToCart()` है। Click handler सीधे `this.addToCart` पास करता है। Click पर `this.items` `undefined` होता है, और error आता है "Cannot read properties of undefined"। Constructor में `bind` करने से ठीक हो जाता है।

---

## 💻 Code Example — Basic
```javascript
// Run with: node file.js  (a normal .js file, CommonJS)

// 1. Sloppy-mode plain call: this is globalThis
function whoAmI() {
  return this === globalThis ? "global" : "other";  // compare this with the global object
}
console.log(whoAmI());                              // Expected output: global

// 2. Strict-mode plain call: this is undefined
function strictWho() {
  "use strict";                                     // turns on strict mode for this function only
  return this;                                      // nothing was passed on the left of the call
}
console.log(strictWho());                           // Expected output: undefined

// 3. Method call: this is the object on the left of the dot
const user = {
  name: "Riya",                                     // data stored on the object
  greet() { return `hi ${this.name}`; },            // this = the object that calls greet
};
console.log(user.greet());                          // Expected output: hi Riya
const loose = user.greet;                           // copy the function out; the object is not attached
console.log(loose());                               // Expected output: hi undefined (this = globalThis)

// 4. Arrow functions take this from the surrounding code
const shop = {
  name: "Chai Point",                               // data
  arrow: () => Object.keys(this).length,            // this = module.exports at file level (empty object)
  regular() { return this.name; },                  // method: this = shop
  nested() {
    const inner = () => this.name;                  // arrow inside a method: this = the method's this
    return inner();                                 // called as a plain function, but arrow ignores that
  },
};
console.log(shop.arrow());                          // Expected output: 0
console.log(shop.nested());                         // Expected output: Chai Point

// 5. call, apply, bind: set this explicitly
function intro(greeting, punct) {
  return `${greeting}, I am ${this.name}${punct}`;  // uses this and two arguments
}
const person = { name: "Aman" };                    // object to borrow the function
console.log(intro.call(person, "Hello", "!"));      // Expected output: Hello, I am Aman!
console.log(intro.apply(person, ["Namaste", "."])); // Expected output: Namaste, I am Aman.
const bound = intro.bind(person, "Hi");             // this and the first argument are fixed
console.log(bound("?"));                            // Expected output: Hi, I am Aman?
const again = bound.bind({ name: "Other" });        // binding a bound function again does nothing new
console.log(again("!"));                            // Expected output: Hi, I am Aman!

// 6. new: this is a brand-new object
class Counter {
  constructor() { this.count = 0; }                 // new creates the object and sets this to it
  inc() { this.count++; return this.count; }        // method uses this to reach the object's count
}
const c = new Counter();                            // this = the new object
console.log(c.inc(), c.inc());                      // Expected output: 1 2
const inc = c.inc;                                  // extract the method (class bodies are strict)
try {
  inc();                                            // plain call: this is undefined in strict code
} catch (e) {
  console.log(e.constructor.name, e.message);       // Expected output: TypeError Cannot read properties of undefined (reading 'count')
}
```

## 💻 Code Example — Advanced
```javascript
// myBind: a small version of Function.prototype.bind; it fixes this and some leading arguments
function myBind(fn, ctx, ...preset) {
  function bound(...later) {                        // the function we return
    if (new.target) {                               // true when the bound function is called with new
      return new fn(...preset, ...later);           // new ignores ctx, just like the native bind
    }
    return fn.apply(ctx, [...preset, ...later]);    // normal call: force this and join the arguments
  }
  return bound;                                     // hand back the bound function
}

// A constructor function to test new with a bound function
function Point(x, y) { this.x = x; this.y = y; }    // sets x and y on the new object
const BoundPoint = myBind(Point, { ignored: true }, 1); // preset x = 1; ctx is ignored for new
const p = new BoundPoint(5);                        // same as new Point(1, 5)
console.log(p.x, p.y, p instanceof Point);          // Expected output: 1 5 true

// A normal function with a forced this
const addTo = myBind(function (k) { return this.base + k; }, { base: 10 }); // this is always {base: 10}
console.log(addTo(5));                              // Expected output: 15

// bindAll: fix this on chosen methods of an instance so the methods can be passed as callbacks
function bindAll(obj, ...names) {
  for (const name of names) {                       // each method name to fix
    obj[name] = obj[name].bind(obj);                // store a bound copy on the object itself
  }
  return obj;                                       // same object, now safe to pass its methods around
}
class Timer {
  constructor() { this.ticks = 0; }                 // state on the instance
  tick() { this.ticks++; return this.ticks; }       // this must be the timer
}
const t = bindAll(new Timer(), "tick");             // fix tick once, at setup time
const cb = t.tick;                                  // extracted, but still bound to t
console.log(cb(), cb());                            // Expected output: 1 2

// setTimeout: in Node, this inside a regular callback is the Timeout object, not globalThis
setTimeout(function () {
  console.log(this === globalThis, this.constructor.name); // Expected output: false Timeout
}, 0);

// Time:  O(1) to read this; bind creates one new function object
// Space: O(1) per bound function; bindAll stores one extra function per method
```

### Edge Cases
```javascript
// Edge 1: a regular function inside a method loses this (sloppy mode: globalThis)
const team = {
  name: "Dev",                                      // the name we want
  members: ["A", "B"],                              // list to map over
  broken() {
    return this.members.map(function (m) { return `${m} of ${this.name}`; }); // this is globalThis here
  },
};
console.log(team.broken());                         // Expected output: [ 'A of undefined', 'B of undefined' ]

// Edge 2: an arrow function inside the method keeps the method's this
const fixed = {
  name: "Dev",
  members: ["A", "B"],
  works() {
    return this.members.map((m) => `${m} of ${this.name}`); // arrow: this = fixed
  },
};
console.log(fixed.works());                         // Expected output: [ 'A of Dev', 'B of Dev' ]

// Edge 3: arrow functions cannot be used with new
const Arrow = () => {};                             // arrow has no this of its own and no [[Construct]]
try {
  new Arrow();                                      // try to construct
} catch (e) {
  console.log(e.message);                           // Expected output: Arrow is not a constructor
}
```

---

## 🟠 Express.js Integration
In Express, a controller method passed directly to a route loses `this`. Express calls the handler as a plain function, so `this.repo` is `undefined` inside `show`. Use `bind`, or wrap the call in an arrow function.

```javascript
// Express.js: controller methods need their this when Express calls them
const express = require("express");               // web framework (install with: npm i express)
const app = express();                            // create the app

// A fake repository; real code would query a database
const repo = { find: async (id) => ({ id, title: "Chai Mug" }) }; // returns a product

class ProductController {
  constructor(repository) { this.repo = repository; } // store the dependency on this
  async show(req, res) {                          // uses this.repo, so this must be the controller
    const product = await this.repo.find(req.params.id); // read the product by id
    res.json(product);                            // send it as JSON
  }
}

const controller = new ProductController(repo);   // one controller object for the app
app.get("/products/:id", controller.show.bind(controller)); // Right: bind keeps this = controller
// Wrong: app.get("/products/:id", controller.show); // Express calls show with this undefined

app.listen(3000, () => console.log("Products API on 3000")); // start the server
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Passing a method as a plain callback
✅ Correct: the callee decides `this`. Bind the method, or pass an arrow function that calls it.

```javascript
// Wrong: the method is copied out, so this is no longer the timer object
const timer = { label: "T", start() { return this.label; } };
const fn = timer.start;                             // copy the function only
console.log(fn());                                  // Expected output: undefined

// Right: bind keeps this on the timer object
const fixed = timer.start.bind(timer);              // this is fixed to timer
console.log(fixed());                               // Expected output: T
```

❌ **Mistake 2:** Using an arrow function as an object method
✅ Correct: an arrow function does not get its own `this`, so `this` is the file's top-level `this` (an empty `module.exports` in CommonJS). Use a method shorthand instead.

```javascript
// Wrong: this.items looks at module.exports, not at cart
const cart = { items: 3, count: () => this.items }; // arrow function as a method
console.log(cart.count());                          // Expected output: undefined

// Right: a method shorthand gets this from the call
const cart2 = { items: 3, count() { return this.items; } }; // method shorthand
console.log(cart2.count());                         // Expected output: 3
```

---

## 🧠 Tricky Interview Question
```javascript
var name = "global";                                // in a CommonJS file this stays inside the module
const user = {
  name: "Riya",
  show() { return this.name; },                     // method
  showArrow: () => this.name,                       // arrow: this is the file's top-level this
};
const show = user.show;                             // copy the method out
console.log(user.show(), show(), user.showArrow()); // what is printed?
```
Answer:
```
Riya undefined undefined
```
`user.show()` is a method call, so `this` is `user` and the answer is "Riya". `show()` is a plain call in sloppy mode, so `this` is `globalThis`. A top-level `var` in a CommonJS module is not a property of `globalThis`, so `globalThis.name` is `undefined`. `showArrow` is an arrow function, so its `this` is the top-level `this` of the module (`module.exports`), which has no `name`. The three traps are the method call, the detached call, and the arrow function.

---

## ⚫ Interview Questions + Answers

**Q1: What decides the value of `this` in a normal function?**
A1: How the function is called, not where it is written. Each call site decides: `new`, `call`/`apply`/`bind`, a method call with a dot, or a plain call.

**Q2: Why does an arrow function ignore `call` and `apply`?**
A2: Arrow functions do not have their own `this`. They capture `this` from the scope where they are created, so `call` and `apply` cannot change it.

**Q3: What happens to `this` when a method is passed to `setTimeout` or to `map`?**
A3: The method is called without an object on the left. In sloppy mode `this` becomes `globalThis`, and in strict or class code it becomes `undefined`. Use `bind`, or pass an arrow function.

**Q4: Does calling `bind` twice change `this` again?**
A4: No. The first `bind` fixes `this`, and later binds cannot change it, although they can add more leading arguments. `new` is the only way to override a bound `this`.

**Q5: Why does `new` on an arrow function throw?**
A5: Arrow functions have no `[[Construct]]` internal method, so they cannot be called with `new`. Use a normal function or a class.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You pass a method to a callback, router, or timer, and you need the object's data
- You want an arrow function for a callback that should share the outer `this`
- You need a fixed `this` for a helper that is called from many places

❌ Avoid when:
- You write `this` inside a plain callback; use an arrow function or a stored reference
- You use arrow functions as object methods that need their own `this`
- You bind everything in every class; bind only the methods that are passed around

---

## 📊 Visual Diagram
```
How this is decided (highest priority at the top)

  new Fn()              -> this = new empty object
  fn.bind(obj)()        -> this = obj   (fixed forever)
  fn.call(obj) / apply  -> this = obj
  obj.fn()              -> this = obj   (object left of the dot)
  fn()  sloppy          -> this = globalThis
  fn()  strict / class  -> this = undefined
  () => {}              -> this = this of the surrounding scope (never changes)

Lost this example:
  const fn = obj.method;   // only the function is copied
  fn();                    // this is globalThis or undefined
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| this | The object a function runs against | Function किस object पर चल रहा है |
| Call site | The place where a function is called | Function जिस जगह call होता है |
| Implicit binding | `this` is the object left of the dot | Dot के बाईं तरफ का object |
| Explicit binding | `call`, `apply`, `bind` set `this` | `call`, `apply`, `bind` से तय `this` |
| Lexical this | Arrow function takes `this` from its scope | Arrow का `this` बाहर के scope से |
| bind | Returns a function with `this` fixed | `this` को तय करने वाला नया function |
| Strict mode | Plain call gives `this` = undefined | Plain call पर `this` undefined |

---

## ⚡ 3-Line Summary
English:
1. `this` depends on the call site: `new`, explicit binding, the object left of the dot, or a plain call.
2. Arrow functions take `this` from the surrounding scope and ignore `call` and `apply`.
3. When a method is passed as a callback, bind it or wrap it in an arrow function.

Hindi:
1. `this` call के तरीके पर निर्भर करता है: `new`, explicit binding, dot के बाईं तरफ का object, या plain call।
2. Arrow functions `this` बाहर के scope से लेते हैं और `call` व `apply` को नज़रअंदाज़ करते हैं।
3. जब method callback में जाए, तो उसे bind करो या arrow function में लपेटो।

---

## ➡️ Next Topic
**197. Prototype Output Questions** — `this` decides which object a method runs on, and the prototype chain decides where a method is found in the first place. The next topic predicts property lookups along the prototype chain.
