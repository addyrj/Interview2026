# 188. Implement new keyword
# हिंदी में: `new` keyword को खुद बनाना — Object बनाना, Prototype जोड़ना और Constructor चलाना

---

## 🔵 Simple Definition (English)
The `new` keyword creates an object from a constructor function. It makes a fresh object, links that object to the constructor's `prototype`, runs the constructor with `this` set to the new object, and returns that object (unless the constructor returns another object).

## 🔵 सरल परिभाषा (Hindi)
`new` keyword constructor function से एक नया object बनाता है। यह नया object बनाता है, उसे constructor के `prototype` से जोड़ता है, constructor को `this` के साथ चलाता है, और वही object लौटाता है (जब तक constructor कोई दूसरा object न लौटाए)।

---

## 🔴 Problem it Solves
**Problem Statement:** Write `myNew(Constructor, ...args)` that behaves like `new Constructor(...args)`. It must create an object linked to `Constructor.prototype`, run the constructor with that object as `this`, and return the object. If the constructor returns an object, that object is returned instead. Arrow functions must throw because they cannot be constructed.

Without `new`, a constructor called as a plain function sets properties on the global object, which causes bugs that are hard to find. Without a shared prototype, every instance would store its own copy of every method, which wastes memory. `new` solves both by creating the object and linking it to a shared prototype in one step.

## 🔴 यह क्यों बना? (Hindi)
**Problem Statement:** `myNew(Constructor, ...args)` लिखो जो `new Constructor(...args)` जैसा व्यवहार करे। इसे नया object बनाना है, उसे `Constructor.prototype` से जोड़ना है, constructor को उसी object को `this` बनाकर चलाना है, और object लौटाना है। अगर constructor कोई object लौटाए, तो वही लौटाओ। Arrow functions पर throw करो, क्योंकि उन्हें constructor के रूप में नहीं चलाया जा सकता।

`new` के बिना constructor को सामान्य function की तरह call करने पर properties global object पर लगती हैं, जिससे अजीब bugs आते हैं। बिना shared prototype के हर instance अपने अंदर हर method की copy रखता, जो memory बर्बाद करता। `new` एक ही कदम में object बनाता है और उसे shared prototype से जोड़ता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Create an empty object whose prototype is `Constructor.prototype`.
Step 2 → Check that the constructor is a real constructor (it must have a `prototype`).
Step 3 → Run the constructor with `this` set to the new object and the given arguments.
Step 4 → If the constructor returned an object (or function), return that value.
Step 5 → Otherwise return the new object, which now has the constructor's properties.
Step 6 → Any method on `Constructor.prototype` is available through the prototype chain, not copied.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → एक खाली object बनाओ जिसका prototype `Constructor.prototype` हो।
Step 2 → जाँचो कि constructor सही है (उसमें `prototype` होना चाहिए)।
Step 3 → Constructor को नए object को `this` बनाकर और दिए गए arguments के साथ चलाओ।
Step 4 → अगर constructor ने object (या function) लौटाया, तो वही लौटाओ।
Step 5 → वरना नया object लौटाओ, जिसमें constructor की properties अब हैं।
Step 6 → `Constructor.prototype` पर लिखे methods prototype chain से मिलते हैं, copy नहीं होते।

---

## 🟡 Real World Example
Razorpay's SDK exposes `new Razorpay(options)`. Each checkout gets its own object with its own key and amount, but all of them share the same `open` and `close` methods from the prototype. Swiggy's cart uses the same idea: `new Cart(userId)` creates a separate cart for each user while the logic lives on the shared prototype.

Scenario: A Paytm wallet class is `function Wallet(owner, balance)`. Two users create wallets with `new`. Each wallet has its own `balance`, and both call the same `pay` method from `Wallet.prototype`. If you forget `new`, the balance is written onto the global object, and the wallet is `undefined`.

## 🟡 Real Example Hindi mein
Razorpay SDK `new Razorpay(options)` देता है। हर checkout का अपना object होता है, अपनी key और amount के साथ, लेकिन `open` और `close` methods prototype से सबको एक ही मिलते हैं। Swiggy की cart भी यही तरीका अपनाती है: `new Cart(userId)` हर user के लिए अलग cart बनाती है, जबकि logic shared prototype पर है।

उदाहरण: Paytm wallet का class `function Wallet(owner, balance)` है। दो users `new` से wallet बनाते हैं। हर wallet का अपना `balance` है, और दोनों `Wallet.prototype` का एक ही `pay` method इस्तेमाल करते हैं। अगर `new` भूल जाओ, तो balance global object पर लिखा जाता है और wallet `undefined` रहता है।

---

## 💻 Code Example — Basic
```javascript
// Basic: create an object, link its prototype, run the constructor, return the object
function basicNew(Ctor, ...args) {
  const obj = {};                                 // step 1: a new empty object
  Object.setPrototypeOf(obj, Ctor.prototype);     // step 2: link obj to the constructor's prototype
  Ctor.apply(obj, args);                          // step 3: run the constructor with this = obj
  return obj;                                     // step 4: return the object (this basic version ignores return overrides)
}

// A constructor and a shared method
function Car(brand) {
  this.brand = brand;                             // each car gets its own brand
}
Car.prototype.drive = function () {               // shared method, stored once on the prototype
  return `${this.brand} is driving`;             // uses this.brand of the object that calls it
};

const nexon = basicNew(Car, "Tata");              // create a car the way new would
console.log(nexon.brand);                         // Expected output: Tata
console.log(nexon.drive());                       // Expected output: Tata is driving
console.log(nexon instanceof Car);                // Expected output: true
```

## 💻 Code Example — Advanced
```javascript
// Advanced: myNew mirrors the real new operator, including the return-value rule
function myNew(Constructor, ...args) {
  // Guard: only functions can be constructors
  if (typeof Constructor !== "function") {
    throw new TypeError("myNew needs a constructor function");
  }
  // Guard: arrow functions and some built-in methods have no prototype, so they cannot be constructed
  if (Constructor.prototype === undefined) {
    throw new TypeError(`${Constructor.name || "anonymous"} is not a constructor`);
  }

  // Step 1 and 2: a new object whose prototype is Constructor.prototype (no methods copied)
  const obj = Object.create(Constructor.prototype);

  // Step 3: run the constructor with this = obj, so it can set properties
  const result = Constructor.apply(obj, args);

  // Step 4: if the constructor returned an object or function, that value wins
  const returnedObject = result !== null && (typeof result === "object" || typeof result === "function");
  return returnedObject ? result : obj;           // otherwise return the new object (primitives are ignored)
}

// ---- Tests: run with plain node ----
function Wallet(owner, balance) {
  this.owner = owner;                             // the owner belongs to this wallet
  this.balance = balance;                         // the balance belongs to this wallet
}
Wallet.prototype.pay = function (amount) {        // shared method on the prototype
  this.balance -= amount;                         // reduce this wallet's balance
  return `${this.owner} paid ${amount}, left ${this.balance}`; // describe the result
};

const aditya = myNew(Wallet, "Aditya", 1000);     // create a wallet
const riya = myNew(Wallet, "Riya", 250);          // create another wallet
console.log(aditya.pay(300));                     // Expected output: Aditya paid 300, left 700
console.log(riya.balance);                        // Expected output: 250
console.log(Object.getPrototypeOf(aditya) === Wallet.prototype); // Expected output: true
console.log(aditya.pay === riya.pay);             // Expected output: true (method is shared, not copied)

function ReturnsObject() {
  this.a = 1;                                     // set on the new object
  return { b: 2 };                                // but return a different object
}
console.log(myNew(ReturnsObject).b);              // Expected output: 2

function ReturnsPrimitive() {
  this.a = 1;                                     // set on the new object
  return 99;                                      // primitives are ignored by new
}
console.log(myNew(ReturnsPrimitive).a);           // Expected output: 1

// Time:  O(a) for the arguments, plus the constructor's own work
// Space: O(1) extra for the new object (the prototype is shared, not copied)
```

### Edge Cases
```javascript
// These checks use the real new keyword; myNew must match it
function Plain(x) { this.x = x; }                 // a simple constructor

// Edge 1: a constructor with no arguments still gets a new object
console.log(new Plain().x);                       // Expected output: undefined

// Edge 2: a returned array is an object, so it replaces the instance
function ReturnsArray() { return [1, 2]; }        // arrays are objects
console.log(new ReturnsArray().length);           // Expected output: 2

// Edge 3: returning null is not an object, so the new instance is used
function ReturnsNull() { this.ok = true; return null; } // null is a special value, not an object here
console.log(new ReturnsNull().ok);                // Expected output: true

// Edge 4: the instance keeps the constructor's name through its prototype
console.log(new Plain(1).constructor.name);       // Expected output: Plain
```

---

## 🟠 Express.js Integration
Express route handlers usually create a fresh object per request, such as a cart or a request-scoped service. Using `new` gives each request its own state, so one user's data never leaks into another request. Express itself uses `new` for `express.Router()`.

```javascript
// Express.js: a per-request Cart object created with new, plus a Router created with new
const express = require("express");               // import Express
const app = express();                            // create the app
app.use(express.json());                          // parse JSON bodies

// A constructor for a per-user cart; methods live on the prototype and are shared
function Cart(userId) {
  this.userId = userId;                           // each cart belongs to one user
  this.items = [];                                // each cart has its own item list
}
Cart.prototype.add = function (item) {            // shared method on the prototype
  this.items.push(item);                          // add to this cart's list
  return this.items.length;                       // return the new count
};
Cart.prototype.total = function () {              // shared method to compute the total
  return this.items.reduce((sum, i) => sum + i.price, 0); // sum the prices
};

// Router created with new, as Express's own docs show
const router = new express.Router();              // a Router object for the cart routes

// POST /api/cart/:userId/items: create a cart for this request and add an item
router.post("/cart/:userId/items", (req, res) => {
  const cart = new Cart(req.params.userId);       // a fresh object, linked to Cart.prototype
  const { name, price } = req.body || {};         // read the item from the body
  if (!name || typeof price !== "number") {       // validate the item
    return res.status(400).json({ error: "name and numeric price are required" }); // 400
  }
  cart.add({ name, price });                      // use the shared method
  res.status(201).json({ userId: cart.userId, count: cart.items.length, total: cart.total() }); // 201 Created
});

app.use("/api", router);                          // mount the router under /api

// Start the server on PORT from the environment, or 3000 by default
app.listen(process.env.PORT || 3000, () => {
  console.log("Cart API running");               // ready message
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting `new` when calling a constructor
✅ **Correct:** Always call a constructor with `new`, so `this` is a new object instead of the global object

```javascript
// Wrong: without new, this is the global object, so brand is written to globalThis
function Shop(brand) { this.brand = brand; }     // constructor
const result = Shop("Zara");                      // called like a normal function
console.log(result, globalThis.brand);            // Expected output: undefined Zara

// Right: with new, a fresh object is created and returned
const made = new Shop("Zara");                    // called with new
console.log(made.brand);                          // Expected output: Zara
```

❌ **Mistake 2:** Trying to construct an arrow function
✅ **Correct:** Use a normal `function` for anything you plan to construct, because arrows have no `prototype` and no own `this`

```javascript
// Wrong: arrow functions cannot be used with new
const Arrow = (name) => { this.name = name; };    // arrow function
try {
  new Arrow("Kabir");                            // throws before anything runs
} catch (err) {
  console.log(err.constructor.name);             // Expected output: TypeError
}

// Right: a normal function can be constructed
function Normal(name) { this.name = name; }      // regular function
console.log(new Normal("Kabir").name);           // Expected output: Kabir
```

---

## 🧠 Tricky Interview Question
```javascript
function Person(name) {
  this.name = name;                               // set the name on the new object
  return { name: "override" };                    // return a different object
}
function Person2(name) {
  this.name = name;                               // set the name on the new object
  return "text";                                  // return a primitive
}
console.log(new Person("Aditya").name);           // ?
console.log(new Person2("Riya").name);            // ?
console.log(Person.prototype.constructor === Person); // ?
```
Answer: `override`, `Riya`, `true`.
When a constructor returns an object, `new` returns that object, so the `this` that was set is thrown away. When it returns a primitive such as the string `"text"`, `new` ignores the return value and returns the new object. The last line is `true` because every function's default `prototype` has a `constructor` property that points back to the function.

---

## ⚫ Interview Questions + Answers

**Q1: What are the four things `new` does?**
A1: It creates a new object, links that object's prototype to `Constructor.prototype`, calls the constructor with `this` set to the new object, and returns the object unless the constructor returned an object.

**Q2: Why are methods put on `Constructor.prototype` instead of inside the constructor?**
A2: Methods on the prototype are shared by all instances. If they were inside the constructor, every instance would get a new copy of every method.

**Q3: What happens if you call a constructor without `new` in non-strict code?**
A3: `this` is the global object, so the properties are set on it. The function returns `undefined`. In strict mode `this` is `undefined`, so the assignment throws.

**Q4: Why can't an arrow function be a constructor?**
A4: Arrow functions have no `prototype` property and no `[[Construct]]` behaviour, so `new` throws a TypeError for them.

**Q5: How do you check that an object came from a constructor?**
A5: Use `instanceof`, which checks whether `Constructor.prototype` is in the object's prototype chain.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You create many objects with the same shape and shared methods (users, carts, wallets, connections)
- You want to keep per-request or per-user state separate
- You are using a library class such as `Router`, `Map`, `Date`, or an SDK client

❌ Avoid when:
- A factory function or an object literal is simpler, especially for objects with no shared methods
- You are writing modern code with `class` syntax; `class` already handles `new` for you
- You plan to rely on `this` inside callbacks without binding; the constructor's `this` does not follow the callback

---

## 📊 Visual Diagram
```
  myNew(Wallet, "Aditya", 1000)
        |
        v
  obj = Object.create(Wallet.prototype)   -->  obj --> Wallet.prototype --> Object.prototype
        |
        v
  Wallet.apply(obj, ["Aditya", 1000])     -->  obj.owner = "Aditya", obj.balance = 1000
        |
        v
  constructor returned an object?
     yes -> return that object
     no  -> return obj

  aditya.pay  ---(not on aditya)--->  Wallet.prototype.pay   (shared, found by prototype chain)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Constructor | A function called with `new` to build an object | `new` से object बनाने वाला function |
| Prototype | The object that instances inherit methods from | वह object जिससे instances methods लेते हैं |
| Prototype chain | Lookup path from an object to its prototypes | Prototypes की खोज की श्रृंखला |
| `Object.create` | Creates an object with a chosen prototype | दिए गए prototype वाला object बनाना |
| `instanceof` | Checks whether a prototype is in the chain | Prototype chain में होने की जाँच |
| Return override | A constructor returning an object replaces `this` | Constructor का object लौटाना, `this` की जगह लेना |
| `new.target` | Tells a function it was called with `new` | Function को बताना कि `new` से call हुआ |

---

## ⚡ 3-Line Summary
English:
1. `new` creates an object, links it to `Constructor.prototype`, runs the constructor with that object as `this`, and returns it.
2. Methods live on the prototype and are shared; a constructor that returns an object overrides the result.
3. Always use `new` with constructors, and use normal functions, not arrows, for anything you construct.

Hindi:
1. `new` एक object बनाता है, उसे `Constructor.prototype` से जोड़ता है, constructor को उसी को `this` बनाकर चलाता है, और उसे लौटाता है।
2. Methods prototype पर रहते हैं और shared होते हैं; constructor का object लौटाना result बदल देता है।
3. Constructors के साथ हमेशा `new` लगाओ, और जिन्हें construct करना है वहाँ arrow नहीं, normal function लिखो।

---

## ➡️ Next Topic
**189. Implement Object.create** — `new` builds an object from a constructor; the next problem builds one directly from any prototype you choose, which is the cleaner way to explain prototype inheritance.
