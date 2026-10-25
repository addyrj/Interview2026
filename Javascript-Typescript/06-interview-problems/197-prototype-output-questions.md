# 197. Prototype Output Questions
# हिंदी में: Prototype के Output Questions — Prototype Chain, Shadowing, Object.create और Prototype Pollution

---

## 🔵 Simple Definition (English)
Every JavaScript object has a hidden link to another object called its prototype. When you read a property that the object does not have, JavaScript follows this link, and then the link of that object, until it finds the property or reaches `null`. This chain of links is the prototype chain. Interviews test whether you can tell own properties from inherited ones and predict what changes when a prototype changes.

## 🔵 सरल परिभाषा (Hindi)
हर JavaScript object के पास एक छिपा हुआ link होता है, जिसे उसका prototype कहते हैं। जब हम ऐसा property पढ़ते हैं जो object के पास नहीं है, तो JavaScript इस link को फॉलो करता है, फिर उस object का link, जब तक property मिल न जाए या `null` न आ जाए। इन links की श्रृंखला को prototype chain कहते हैं। Interview में देखा जाता है कि आप अपने properties और inherited properties में फ़र्क कर सकते हैं या नहीं, और prototype बदलने पर क्या बदलता है, यह बता सकते हैं।

---

## 🔴 Problem it Solves
**Problem Statement:** Predict the output of property reads, writes, and prototype changes. Explain `__proto__` vs `prototype`, shadowing, `Object.create(null)`, and `instanceof`. Then write helpers that walk the chain and merge untrusted data safely.

Without prototypes, every object would need its own copy of every method. A class with 10,000 instances would store 10,000 copies of the same `sound()` function. Prototypes let all instances share one copy, and they are also the reason for bugs such as `for...in` loops that include inherited keys and prototype pollution attacks.

## 🔴 यह क्यों बना? (Hindi)
**Problem Statement:** Property reads, writes और prototype बदलने के output बताओ। `__proto__` बनाम `prototype`, shadowing, `Object.create(null)` और `instanceof` समझाओ। फिर chain में खोजने वाले helpers और untrusted data को सुरक्षित merge करने वाला function लिखो।

Prototypes के बिना हर object में हर method की अपनी copy होती। 10,000 instances वाली class में एक ही `sound()` function 10,000 बार रखा जाता। Prototypes सब instances को एक ही copy साझा करने देते हैं। लेकिन यही वजह से कुछ bugs भी आते हैं, जैसे `for...in` loop में inherited keys आना, और prototype pollution हमला।

---

## 🟢 How it Works — Step by Step

Step 1 → `obj.prop` checks `obj` itself first (own property).
Step 2 → If not found, it checks `Object.getPrototypeOf(obj)`, then the next one up.
Step 3 → The search stops when a property is found, or when the chain reaches `null`, which gives `undefined`.
Step 4 → `obj.prop = value` creates an own property on `obj`, unless an inherited read-only property blocks it.
Step 5 → `new Fn()` sets the new object's prototype to `Fn.prototype` at creation time.
Step 6 → Changing `Fn.prototype` later affects only objects created after the change, plus existing objects that read through the shared object.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → `obj.prop` पहले `obj` खुद चेक करता है (own property)।
Step 2 → न मिले तो `Object.getPrototypeOf(obj)` चेक करता है, फिर उससे ऊपर वाला।
Step 3 → Property मिलते ही खोज रुकती है, या chain `null` पर पहुँचे तो `undefined` मिलता है।
Step 4 → `obj.prop = value` `obj` पर own property बनाता है, जब तक कोई inherited read-only property रोके नहीं।
Step 5 → `new Fn()` नए object का prototype बनते समय `Fn.prototype` पर सेट करता है।
Step 6 → `Fn.prototype` बाद में बदलने से सिर्फ बाद में बने objects पर असर होता है, और पुराने objects पर वही जो shared object से पढ़ते हैं।

---

## 🟡 Real World Example
Zomato's delivery rider classes share a `Vehicle` base with `speedLimit`. Each rider's object stores only its own `name` and `location`. The shared `speedLimit` is found on the prototype, which saves memory across thousands of riders. A Razorpay config loader merges a merchant's JSON settings into defaults, and it must not let a crafted key like `__proto__` change every object in the server.

Scenario: A Paytm settings page loads user preferences from a JSON API. An attacker sends `"__proto__": {"isAdmin": true}`. A naive merge writes `isAdmin` onto `Object.prototype`, so every object in the process now looks like an admin. A guard that skips the key stops the attack.

## 🟡 Real Example Hindi mein
Zomato के delivery rider classes में एक `Vehicle` base है जिसमें `speedLimit` है। हर rider का object सिर्फ अपना `name` और `location` रखता है। साझा `speedLimit` prototype पर मिलता है, जिससे हज़ारों riders में memory बचती है। Razorpay का config loader merchant की JSON settings को defaults में merge करता है, और उसे `__proto__` जैसी key से server के हर object को नहीं बदलने देना चाहिए।

उदाहरण: Paytm की settings page API से user preferences लेती है। Attacker भेजता है `"__proto__": {"isAdmin": true}`। Naive merge `isAdmin` को `Object.prototype` पर लिख देता है, तो process के हर object को लगता है वह admin है। ऐसी key को skip करने वाला guard हमला रोक देता है।

---

## 💻 Code Example — Basic
```javascript
// Run with: node file.js

// 1. Lookup walks up the chain; writes create own properties
const animal = { breathes: true, sound: "generic" }; // parent object
const dog = Object.create(animal);                  // dog's prototype is animal; dog has no own properties yet
dog.sound = "woof";                                 // creates an own property on dog (shadows animal.sound)
console.log(dog.sound, dog.breathes);               // Expected output: woof true
console.log(Object.keys(dog));                      // Expected output: [ 'sound' ] (own keys only)
console.log("breathes" in dog, Object.hasOwn(dog, "breathes")); // Expected output: true false

// 2. __proto__ vs prototype: prototype is on functions, __proto__ is on instances
function Car(brand) { this.brand = brand; }        // constructor function
Car.prototype.wheels = 4;                           // shared property stored on Car.prototype
const car = new Car("Tata");                        // new links car's prototype to Car.prototype
console.log(car.wheels, car.brand);                 // Expected output: 4 Tata
console.log(Object.getPrototypeOf(car) === Car.prototype); // Expected output: true
console.log(car.__proto__ === Car.prototype);       // Expected output: true (__proto__ is an accessor for the link)
console.log(Object.getPrototypeOf(Car.prototype) === Object.prototype); // Expected output: true
console.log(Car.__proto__ === Function.prototype);  // Expected output: true (functions are objects too)

// 3. Prototype changes are seen by all instances that share it
function Animal() {}                                // empty constructor
Animal.prototype.sound = "generic";                 // shared value
const a = new Animal();                             // a shares Animal.prototype
const b = new Animal();                             // b shares Animal.prototype too
b.sound = "meow";                                   // own property on b only
Animal.prototype.sound = "changed";                 // change the shared value
console.log(a.sound, b.sound);                      // Expected output: changed meow

// 4. Classes are the same prototype system with nicer syntax
class Vehicle { start() { return "vehicle starts"; } } // method goes on Vehicle.prototype
class Bike extends Vehicle { ride() { return "bike rides"; } } // Bike.prototype links to Vehicle.prototype
const bike = new Bike();                            // bike -> Bike.prototype -> Vehicle.prototype -> Object.prototype
console.log(bike.ride(), bike.start());             // Expected output: bike rides vehicle starts
console.log(bike.constructor.name, bike instanceof Vehicle); // Expected output: Bike true
console.log(Object.getPrototypeOf(Bike) === Vehicle); // Expected output: true (the class itself is linked too)

// 5. Object.create(null) has no prototype at all
const dict = Object.create(null);                   // no Object.prototype in the chain
dict.toString = "not a method";                     // plain data; nothing inherited to clash with
console.log("toString" in dict, typeof dict.hasOwnProperty); // Expected output: true undefined
console.log("toString" in {});                      // Expected output: true (inherited from Object.prototype)
```

## 💻 Code Example — Advanced
```javascript
// chainOf: list the constructor names along the prototype chain of an object, from the parent upward
function chainOf(obj) {
  const names = [];                                 // one label per object in the chain
  let current = Object.getPrototypeOf(obj);         // start one step above obj
  while (current !== null) {                        // stop after the last object (Object.prototype's parent is null)
    names.push(Object.hasOwn(current, "constructor") ? current.constructor.name : "anonymous");
    current = Object.getPrototypeOf(current);       // move one level up
  }
  return names;                                     // labels from nearest to farthest
}

class Base {}                                       // simple classes to test the chain
class Child extends Base {}
console.log(chainOf(new Child()));                  // Expected output: [ 'Child', 'Base', 'Object' ]

// Keys that can reach or replace prototypes; a merge must never write to them
const UNSAFE_KEYS = new Set(["__proto__", "constructor", "prototype"]);

// safeMerge: deep-merge plain data into target, skipping keys that could change prototypes
function safeMerge(target, source) {
  for (const key of Object.keys(source)) {         // only own keys of the source, as strings
    if (UNSAFE_KEYS.has(key)) continue;             // skip the dangerous keys completely
    const value = source[key];                      // the value to copy
    if (value !== null && typeof value === "object" && !Array.isArray(value)) { // a nested object
      const existing = Object.hasOwn(target, key) ? target[key] : {}; // reuse our own object or start fresh
      target[key] = safeMerge(existing, value);     // merge into it recursively
    } else {
      target[key] = value;                          // plain value: copy it as is
    }
  }
  return target;                                    // return the merged target
}

// An attacker-style payload: JSON.parse makes "__proto__" an ordinary own key
const payload = JSON.parse('{"user":{"name":"Asha"},"__proto__":{"isAdmin":true}}');
const config = safeMerge({ theme: "dark" }, payload); // merge into safe defaults
console.log(JSON.stringify(config));                // Expected output: {"theme":"dark","user":{"name":"Asha"}}
console.log({}.isAdmin);                            // Expected output: undefined (nothing was polluted)

// Time:  O(d) to walk a chain of depth d; safeMerge is O(size of source)
// Space: O(depth) for the recursion in safeMerge
```

### Edge Cases
```javascript
// Edge 1: assigning to an inherited read-only property is silently ignored in sloppy mode
const parent = Object.defineProperty({}, "id", { value: 1, writable: false }); // read-only on parent
const child = Object.create(parent);               // child inherits id
child.id = 99;                                      // blocked by the inherited read-only property
console.log(child.id, Object.hasOwn(child, "id")); // Expected output: 1 false

// Edge 2: the top of the chain is Object.prototype, whose prototype is null
console.log(Object.getPrototypeOf(Object.prototype)); // Expected output: null

// Edge 3: a function's own prototype object has a constructor that points back to the function
function Tool() {}                                  // constructor
console.log(Tool.prototype.constructor === Tool, Object.keys(Tool.prototype).length); // Expected output: true 0
```

---

## 🟠 Express.js Integration
Express builds its `req` and `res` objects on top of its own prototypes. Adding a helper to `app.response` makes it available on every response, because every `res` inherits from that shared object. This is the same prototype-chain idea, used in a real framework.

```javascript
// Express.js: add a helper method to every response through the prototype chain
const express = require("express");                 // web framework (install with: npm i express)
const app = express();                              // create the app

// app.response is an object whose prototype is Express's response prototype (res).
// Any method added here is found by lookup on every res object.
app.response.sendOk = function (data) {             // this = the res object that called sendOk
  return this.status(200).json({ ok: true, data }); // reuse the built-in res.status and res.json
};

app.get("/health", (req, res) => {                  // every route can now use res.sendOk
  res.sendOk({ uptime: process.uptime() > 0 });     // found on the prototype chain, not copied per request
});

app.listen(3000, () => console.log("Health API on 3000")); // start the server
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Looping with `for...in` and forgetting inherited keys
✅ Correct: `for...in` visits inherited enumerable properties too. Check `Object.hasOwn` or use `Object.keys` for own keys only.

```javascript
// Wrong: the inherited "shared" key is printed as well
const base = { shared: 1 };                         // parent property
const obj = Object.create(base);                    // obj inherits shared
obj.own = 2;                                        // obj's own property
for (const k in obj) console.log(k);                // Expected output: own, then shared

// Right: keep only own keys
for (const k in obj) {
  if (Object.hasOwn(obj, k)) console.log(k);        // Expected output: own
}
```

❌ **Mistake 2:** A naive deep merge that follows `__proto__`
✅ Correct: `target["__proto__"]` returns `Object.prototype`, not an empty object. Writing into it changes every object in the program. Skip the dangerous keys.

```javascript
// Wrong: the naive merge writes into Object.prototype through the "__proto__" key
function naiveMerge(target, source) {
  for (const key of Object.keys(source)) {          // includes the "__proto__" key from JSON
    if (typeof source[key] === "object" && source[key] !== null) {
      naiveMerge(target[key] ?? (target[key] = {}), source[key]); // target.__proto__ is Object.prototype
    } else {
      target[key] = source[key];                    // plain copy
    }
  }
  return target;
}
naiveMerge({}, JSON.parse('{"__proto__":{"isAdmin":true}}')); // attacker payload
console.log({}.isAdmin);                            // Expected output: true (every object is now polluted)
```

```javascript
// Right: skip the dangerous keys, so the payload cannot reach Object.prototype
const UNSAFE = new Set(["__proto__", "constructor", "prototype"]); // keys that can change prototypes
function safeMerge(target, source) {
  for (const key of Object.keys(source)) {          // own keys only
    if (UNSAFE.has(key)) continue;                  // skip the dangerous keys
    const v = source[key];                          // value to copy
    target[key] = v !== null && typeof v === "object" ? safeMerge({}, v) : v; // recurse or copy
  }
  return target;
}
safeMerge({}, JSON.parse('{"__proto__":{"isAdmin":true}}')); // payload is skipped
console.log({}.isAdmin);                            // Expected output: undefined
```

---

## 🧠 Tricky Interview Question
```javascript
function Animal() {}                               // constructor
Animal.prototype.sound = "generic";                // shared value on the first prototype object
const a = new Animal();                            // a links to the first prototype
const b = new Animal();                            // b links to the first prototype too

Animal.prototype = { sound: "changed" };           // replace the whole prototype object
const c = new Animal();                            // c links to the NEW prototype

console.log(a.sound, b.sound, c.sound);            // what is printed?
console.log(a.constructor === Animal, c.constructor === Animal); // and this?
```
Answer:
```
generic generic changed
true false
```
`new` reads `Animal.prototype` once, at the moment the object is created. `a` and `b` keep the old prototype, which still has `sound` and a `constructor` that points to `Animal`. The new object literal `{ sound: "changed" }` has no `constructor` of its own, so `c.constructor` climbs one step to `Object.prototype` and returns `Object`. Replacing `prototype` breaks `constructor` links and affects only future objects.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between `__proto__` and `prototype`?**
A1: `prototype` is a property of functions. It is the object that new instances will link to. `__proto__` (or `Object.getPrototypeOf`) is the link on an instance, pointing to the object it inherits from.

**Q2: What happens when you assign to a property that exists on the prototype?**
A2: An own property is created on the object, which hides the prototype's value. The prototype is not changed. The exception is an inherited read-only property, which blocks the assignment.

**Q3: What is the difference between `in` and `hasOwnProperty`?**
A3: `in` checks the whole chain, so it returns true for inherited properties. `Object.hasOwn(obj, key)` checks only the object's own properties.

**Q4: Why does `Object.create(null)` exist?**
A4: It creates an object with no prototype, so there are no inherited keys such as `toString` or `hasOwnProperty`. It is useful as a clean dictionary, but its methods must be called with `Object.prototype.hasOwnProperty.call` or `Object.hasOwn`.

**Q5: What is prototype pollution?**
A5: It is when untrusted input writes to a key such as `__proto__`, `constructor`, or `prototype` during a merge, and that write reaches `Object.prototype`. Every object in the program then has the injected property. Defend by skipping those keys and by validating input.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Many objects share the same methods, so the methods live on one prototype
- You build a class hierarchy and want instances to inherit behavior
- You use `Object.create(null)` for a pure dictionary with user-defined keys

❌ Avoid when:
- You loop with `for...in` over objects without checking `Object.hasOwn`
- You merge untrusted JSON into objects without skipping the dangerous keys
- You replace `prototype` of a function after instances already exist; it confuses `constructor` and `instanceof`

---

## 📊 Visual Diagram
```
dog (own: sound = "woof")
  |  [[Prototype]]
  v
animal (own: breathes = true, sound = "generic")
  |  [[Prototype]]
  v
Object.prototype (own: toString, hasOwnProperty, ...)
  |  [[Prototype]]
  v
null

dog.sound     -> found on dog           -> "woof"
dog.breathes  -> not on dog, found on animal -> true
dog.toString  -> not on dog or animal, found on Object.prototype
dog.missing   -> reaches null             -> undefined
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Prototype | The object an instance inherits from | वह object जिससे instance inherit करता है |
| Prototype chain | The list of links searched for a property | Property खोजने वाली links की श्रृंखला |
| Own property | Stored on the object itself | Object पर खुद रखी property |
| Shadowing | Own property hides the same name on the prototype | अपनी property से prototype की property छिपना |
| Object.create | Creates an object with a chosen prototype | चुने हुए prototype वाला नया object |
| instanceof | Checks if a constructor's prototype is in the chain | Chain में constructor का prototype है या नहीं |
| Prototype pollution | Untrusted input changes Object.prototype | Input से Object.prototype बदल जाना |

---

## ⚡ 3-Line Summary
English:
1. Property reads walk the prototype chain until they find the key or reach `null`.
2. Writes create own properties and shadow inherited ones; `for...in` also visits inherited keys.
3. Never merge untrusted keys like `__proto__` blindly; skip them to prevent prototype pollution.

Hindi:
1. Property पढ़ते समय prototype chain तब तक खोजी जाती है जब तक key न मिले या `null` न आए।
2. Write अपनी property बनाता है और inherited को छिपाता है; `for...in` inherited keys भी दिखाता है।
3. `__proto__` जैसी untrusted keys को बिना जाँचे merge मत करो; उन्हें skip करो ताकि prototype pollution न हो।

---

## ➡️ Next Topic
**198. Tricky Coercion Questions** — prototypes decide where a method is found, and coercion decides how values turn into numbers and strings. The next topic predicts results like `[] + {}` and `[] == ![]`.
