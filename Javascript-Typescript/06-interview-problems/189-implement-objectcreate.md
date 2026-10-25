# 189. Implement Object.create
# हिंदी में: Object.create बनाना — किसी भी prototype से सीधे नया object बनाना

---

## 🔵 Simple Definition (English)
`Object.create(proto)` returns a new empty object whose prototype is `proto`. The new object does not copy `proto`'s properties; it looks them up through the prototype chain. Passing `null` creates an object with no prototype at all.

## 🔵 सरल परिभाषा (Hindi)
`Object.create(proto)` एक नया खाली object लौटाता है जिसका prototype `proto` होता है। यह `proto` की properties को copy नहीं करता, बल्कि prototype chain से उन्हें खोजता है। `null` देने पर object का कोई prototype नहीं होता।

---

## 🔴 Problem it Solves
**Problem Statement:** Implement `myObjectCreate(proto, propertiesObject)`. It must accept an object or `null` as `proto`, reject any other type, return an object linked to `proto`, and optionally define own properties with descriptors, as the built-in does.

Before `Object.create`, the only way to set a prototype was a constructor function with a `prototype` property, or the non-standard `__proto__`. `Object.create` lets you inherit from a plain object directly, which is simpler and avoids the `new` ceremony. It is also the safe way to build dictionaries with no inherited keys like `toString`.

## 🔴 यह क्यों बना? (Hindi)
**Problem Statement:** `myObjectCreate(proto, propertiesObject)` लिखो। इसे `proto` के रूप में object या `null` स्वीकार करना है, बाकी types पर error देना है, `proto` से जुड़ा object लौटाना है, और चाहें तो built-in की तरह descriptors से own properties बनानी हैं।

`Object.create` से पहले prototype तय करने का एक ही तरीका था: constructor function जिसमें `prototype` हो, या गैर-मानक `__proto__`। `Object.create` सीधे plain object से inherit करने देता है, जो सरल है और `new` का झंझट नहीं। Dictionary बनाने के लिए भी यह सुरक्षित है, क्योंकि उसमें `toString` जैसी inherited keys नहीं होतीं।

---

## 🟢 How it Works — Step by Step

Step 1 → Check `proto`. It must be an object, a function, or `null`.
Step 2 → Create a temporary constructor `F` with an empty body.
Step 3 → Set `F.prototype = proto`, so `new F()` will link to `proto`.
Step 4 → Call `new F()` to get the object. If `proto` is `null`, fix its prototype to `null` (because `new` would otherwise use `Object.prototype`).
Step 5 → If a properties object was given, define each property with `Object.defineProperties`.
Step 6 → Return the new object. Its properties are looked up through `proto` when they are not its own.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → `proto` जाँचो। यह object, function या `null` होना चाहिए।
Step 2 → एक अस्थायी constructor `F` बनाओ जिसका body खाली हो।
Step 3 → `F.prototype = proto` सेट करो, ताकि `new F()` `proto` से जुड़ जाए।
Step 4 → `new F()` से object लो। अगर `proto` `null` है, तो उसका prototype `null` करो (क्योंकि `new` वरना `Object.prototype` लगा देता)।
Step 5 → अगर properties object दिया गया है, तो `Object.defineProperties` से हर property बनाओ।
Step 6 → नया object लौटाओ। जो properties उसकी अपनी नहीं हैं, वे `proto` से chain में खोजी जाती हैं।

---

## 🟡 Real World Example
Flipkart's catalogue has a base `ProductTemplate` object with shared defaults such as `currency` and `taxRate`. Each product listing is created with `Object.create(ProductTemplate)` and overrides only the fields it needs. A listing that does not set `taxRate` still reads the default from the template, so one change to the template updates every listing that inherits it.

Scenario: A Razorpay merchant config has defaults `{ currency: "INR", retries: 3 }`. A premium merchant is `Object.create(defaults)` with only `retries: 5` set. Reading `currency` gives `"INR"` through the chain, and `retries` gives `5` from its own property.

## 🟡 Real Example Hindi mein
Flipkart की catalogue में एक base `ProductTemplate` object है जिसमें `currency` और `taxRate` जैसे shared defaults हैं। हर product listing `Object.create(ProductTemplate)` से बनती है और सिर्फ़ वही fields बदलती है जो चाहिए। जो listing `taxRate` नहीं बदलती, वह template से default पढ़ती है, इसलिए template में एक बदलाव सब पर लागू होता है।

उदाहरण: Razorpay merchant config के defaults हैं `{ currency: "INR", retries: 3 }`। Premium merchant `Object.create(defaults)` से बनता है और सिर्फ़ `retries: 5` सेट होता है। `currency` पढ़ने पर chain से `"INR"` मिलता है, और `retries` अपनी property से `5` देता है।

---

## 💻 Code Example — Basic
```javascript
// Basic: use a throwaway constructor whose prototype is set to the object we want to inherit from
function basicObjectCreate(proto) {
  function F() {}                                 // an empty constructor, used only for its prototype slot
  F.prototype = proto;                            // point the prototype at the parent object
  return new F();                                 // new F() creates an object whose prototype is proto
}

const animal = {                                  // a parent object with a shared method
  breathe() {
    return `${this.name} breathes`;               // this is the child that calls the method
  },
};

const dog = basicObjectCreate(animal);            // a child that inherits from animal
dog.name = "Tommy";                               // set its own property
console.log(dog.breathe());                       // Expected output: Tommy breathes
console.log(Object.getPrototypeOf(dog) === animal); // Expected output: true
console.log(Object.hasOwn(dog, "breathe"));       // Expected output: false (inherited, not copied)
```

## 💻 Code Example — Advanced
```javascript
// Advanced: myObjectCreate with type checks, null prototypes, and property descriptors
function myObjectCreate(proto, propertiesObject) {
  // Guard: proto must be an object, a function, or null; anything else is a TypeError
  if (proto !== null && typeof proto !== "object" && typeof proto !== "function") {
    throw new TypeError("Object prototype may only be an Object or null");
  }

  function F() {}                                 // empty constructor used only for its prototype slot
  F.prototype = proto;                            // link the prototype we want
  const obj = new F();                            // new F() creates an object linked to proto

  // Special case: new F() with proto null would fall back to Object.prototype, so fix it
  if (proto === null) {
    Object.setPrototypeOf(obj, null);             // the object now has no prototype at all
  }

  // Optional second argument: define own properties with descriptors, like the built-in
  if (propertiesObject !== undefined) {
    Object.defineProperties(obj, propertiesObject); // each key becomes an own property
  }

  return obj;                                     // the new object
}

// ---- Tests: run with plain node ----
const shape = { area() { return this.w * this.h; } }; // parent with a method
const box = myObjectCreate(shape);                // child inherits area
box.w = 3;                                        // own property
box.h = 4;                                        // own property
console.log(box.area());                          // Expected output: 12
console.log(Object.getPrototypeOf(box) === shape); // Expected output: true

const bare = myObjectCreate(null);                // an object with no prototype
console.log(Object.getPrototypeOf(bare));         // Expected output: null
console.log(typeof bare.toString);                // Expected output: undefined (no inherited methods)

const withProps = myObjectCreate({}, {            // second argument: property descriptors
  id: { value: 7, enumerable: true },             // visible in Object.keys
  secret: { value: "x" },                         // not enumerable by default
});
console.log(withProps.id, Object.keys(withProps).join(",")); // Expected output: 7 id
console.log(Object.hasOwn(withProps, "secret"), withProps.secret); // Expected output: true x

try {
  myObjectCreate(42);                             // a number is not a valid prototype
} catch (err) {
  console.log(err.name);                          // Expected output: TypeError
}

// Time:  O(p) to define p properties; O(1) to link the prototype
// Space: O(1) extra for the new object, plus the properties you define
```

### Edge Cases
```javascript
// These checks use the native Object.create; myObjectCreate must match them

// Edge 1: a function can be a prototype too
const fnProto = function () { return "from function"; }; // a function object used as a prototype
const fnChild = Object.create(fnProto);            // an plain object (not callable) that inherits from it
console.log(typeof fnChild.call, typeof fnChild);  // Expected output: function object (call comes down the chain)

// Edge 2: Object.keys ignores inherited properties
const parent = { inherited: 1 };                         // parent with one property
const child = Object.create(parent);                     // child with no own properties
console.log(Object.keys(child).length);                  // Expected output: 0

// Edge 3: reading an inherited property works, but writing creates an own property
child.inherited = 2;                                     // write on the child
console.log(parent.inherited, child.inherited);          // Expected output: 1 2

// Edge 4: passing a primitive throws
try {
  Object.create("text");                                 // a string is not a valid prototype
} catch (err) {
  console.log(err.name);                                 // Expected output: TypeError
}
```

---

## 🟠 Express.js Integration
Express itself uses prototype inheritance for `req` and `res`: its init middleware links each request object to the app's `request` and `response` prototypes. You can use the same idea with `Object.create` to build a per-request context that inherits app-wide settings, so each request can override only what it needs.

```javascript
// Express.js: a per-request context created with Object.create from app-wide defaults
const express = require("express");               // import Express
const app = express();                            // create the app

// App-wide defaults shared by every request (never copied, always inherited)
const appDefaults = {
  currency: "INR",                                // default currency
  pageSize: 10,                                   // default page size
  describe() {                                    // shared method
    return `${this.currency} / page ${this.pageSize}`; // uses the current request's values
  },
};

// Middleware: create a context that inherits from appDefaults for this request only
app.use((req, res, next) => {
  req.ctx = Object.create(appDefaults);           // linked to the defaults; no copies made
  req.ctx.pageSize = Number(req.query.pageSize) || appDefaults.pageSize; // override just this field
  next();                                         // continue to the route
});

// GET /api/prices: uses the inherited currency and the overridden page size
app.get("/api/prices", (req, res) => {
  res.json({
    currency: req.ctx.currency,                   // inherited from appDefaults
    pageSize: req.ctx.pageSize,                   // own property, set by the middleware
    summary: req.ctx.describe(),                  // shared method from the prototype
  });                                             // 200 OK
});

// Start the server on PORT from the environment, or 3000 by default
app.listen(process.env.PORT || 3000, () => {
  console.log("Price API running");              // ready message
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Expecting `Object.create` to copy the parent's properties
✅ **Correct:** The child only links to the parent; use spread or `Object.assign` if you want a real copy

```javascript
// Wrong: the child has no own keys, so a copy-based check finds nothing
const parent = { a: 1, b: 2 };                    // parent with two properties
const linked = Object.create(parent);             // linked, not copied
console.log(Object.keys(linked).length);          // Expected output: 0

// Right: a real copy with own keys
const copied = { ...parent };                     // spread copies the own properties
console.log(Object.keys(copied).join(","));       // Expected output: a,b
```

❌ **Mistake 2:** Storing mutable state on the prototype, so every child shares it
✅ **Correct:** Put per-instance state on the child, and keep only shared methods on the prototype

```javascript
// Wrong: both children read the same array from the parent, so pushes leak across them
const base = { tags: [] };                        // shared array on the prototype
const a = Object.create(base);                    // child A
const b = Object.create(base);                    // child B
a.tags.push("hot");                               // A pushes into the shared array
console.log(b.tags.length);                       // Expected output: 1 (B sees A's change)

// Right: each child gets its own array
const fixedBase = {};                             // no shared array here
const c = Object.create(fixedBase);               // child C
const d = Object.create(fixedBase);               // child D
c.tags = [];                                      // own array for C
d.tags = [];                                      // own array for D
c.tags.push("hot");                               // only C changes
console.log(d.tags.length);                       // Expected output: 0
```

---

## 🧠 Tricky Interview Question
```javascript
const base = { greet() { return "hi"; } };       // parent with a method
const child = Object.create(base);               // child inherits greet
console.log(child.greet === base.greet);         // ?
console.log(Object.keys(child).length);          // ?
child.greet = () => "bye";                       // create an own property that shadows greet
console.log(base.greet());                       // ?
console.log(child.greet());                      // ?
delete child.greet;                              // remove the own property
console.log(child.greet());                      // ?
```
Answer: `true`, `0`, `hi`, `bye`, `hi`.
The child does not copy `greet`, so both point to the same function (`true`), and it has no own keys (`0`). Assigning `child.greet` creates an own property that shadows the inherited one. The parent is unchanged (`hi`), the child uses its own function (`bye`). Deleting the own property reveals the inherited method again (`hi`).

---

## ⚫ Interview Questions + Answers

**Q1: What does `Object.create(null)` produce?**
A1: An object with no prototype. It has no `toString`, `hasOwnProperty`, or other inherited methods, which makes it a clean dictionary.

**Q2: How is `Object.create` different from `new`?**
A2: `Object.create` takes any prototype directly and does not run a constructor. `new` runs a constructor function and links to its `prototype` property.

**Q3: Does reading an inherited property copy it?**
A3: No. Reads walk up the prototype chain. Writes always create an own property on the child (unless a setter or a non-writable inherited property blocks it).

**Q4: Why does the basic version use a temporary function?**
A4: `new F()` links the new object to `F.prototype`, so setting `F.prototype = proto` is the classic way to create an object linked to any chosen prototype.

**Q5: Why does the advanced version call `Object.setPrototypeOf(obj, null)` when `proto` is null?**
A5: Because `F.prototype` set to `null` makes `new F()` fall back to `Object.prototype`. Setting the prototype to `null` afterwards gives the object no prototype at all.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want inheritance from a plain object without classes or constructors
- You need dictionaries with no inherited keys (`Object.create(null)`)
- You want many objects to share defaults and override only a few fields

❌ Avoid when:
- You need many instances with shared methods and a clear type; `class` or a constructor reads better
- You want a copy, not a link; use spread or `structuredClone`
- Prototype chains become deep and hard to debug; flat objects with explicit fields are easier to maintain

---

## 📊 Visual Diagram
```
  dog (own: name = "Tommy")
    |  [[Prototype]]
    v
  animal (own: breathe)
    |  [[Prototype]]
    v
  Object.prototype (toString, hasOwnProperty, ...)
    |  [[Prototype]]
    v
  null

  dog.breathe()  -> not own -> found on animal
  dog.toString() -> not own, not on animal -> found on Object.prototype

  Object.create(null):  obj --> null   (no toString at all)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Prototype | The object that another object inherits from | वह object जिससे दूसरा object inherit करता है |
| `[[Prototype]]` | The internal link from an object to its prototype | Object से उसके prototype तक की internal link |
| Prototype chain | The path of lookups up through prototypes | Prototypes में ऊपर तक खोज का रास्ता |
| Own property | A property stored directly on the object | Object पर सीधे रखी property |
| Shadowing | A child property hides a parent property with the same name | Child की property से parent की property छिप जाना |
| Property descriptor | Settings for a property such as value, enumerable, writable | Property की सेटिंग्स, जैसे value और enumerable |
| Dictionary object | An object used as a key-value map | Key-value map के रूप में इस्तेमाल होने वाला object |

---

## ⚡ 3-Line Summary
English:
1. `Object.create(proto)` returns a new object linked to `proto`, without copying its properties.
2. Reads go up the prototype chain; writes create own properties and can shadow inherited ones.
3. Use `Object.create(null)` for clean dictionaries, and keep mutable state off shared prototypes.

Hindi:
1. `Object.create(proto)` एक नया object लौटाता है जो `proto` से जुड़ा है, उसकी properties copy किए बिना।
2. Reads prototype chain में ऊपर जाते हैं; writes अपनी property बनाते हैं और inherited को छिपा सकते हैं।
3. साफ़ dictionary के लिए `Object.create(null)` लो, और mutable state को shared prototype पर मत रखो।

---

## ➡️ Next Topic
**190. Implement Array.map, filter, reduce** — you now know how objects inherit behaviour; the next problem rebuilds the three most-used array methods, which are the building blocks of data transformation in Node APIs.
