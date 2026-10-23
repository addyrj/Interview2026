# 32. Prototypes and Prototype Chain
# हिंदी में: Prototypes — JavaScript का Inheritance System, Under the Hood

---

## 🔵 Simple Definition (English)
Every JavaScript object has a hidden `[[Prototype]]` link to another object (its prototype). When you access a property, JS looks at the object first, then walks up the **prototype chain** until it finds it or reaches `null`. This is how inheritance works — `class` syntax is just syntactic sugar over this prototype system.

## 🔵 सरल परिभाषा (Hindi)
हर JavaScript object के पास एक hidden `[[Prototype]]` link होता है दूसरे object (उसका prototype) की तरफ। जब property access की जाती है, JS पहले object में देखता है, फिर **prototype chain** में ऊपर जाता है। यही JavaScript का inheritance system है — `class` syntax इसी का syntactic sugar है।

---

## 🔴 Why it Matters
```javascript
// Why can you call .toString() on a number?
(42).toString(); // "42"
// Number doesn't have toString — it's inherited from Object.prototype!

// Why does [].map() work?
// Arrays don't have map directly — they inherit from Array.prototype!

// Every object → [[Prototype]] → Object.prototype → null
```

---

## 🟢 The Chain

```
myArray → Array.prototype → Object.prototype → null

myObject → Object.prototype → null

myClass instance → MyClass.prototype → Object.prototype → null

Accessing a property:
1. Check object itself
2. Check [[Prototype]]
3. Check [[Prototype]]'s [[Prototype]]
...until null → undefined
```

---

## 🟡 Real World Example
```javascript
// What happens under the hood when you use a class:

class Animal {
  constructor(name) { this.name = name; }
  speak() { return `${this.name} makes a sound`; }
}

class Dog extends Animal {
  speak() { return `${this.name} barks!`; }
  fetch() { return `${this.name} fetches the ball!`; }
}

const dog = new Dog("Rex");

dog.speak();    // "Rex barks!" — Dog.prototype.speak
dog.fetch();    // "Rex fetches the ball!" — Dog.prototype.fetch
dog.toString(); // "[object Object]" — from Object.prototype!

// dog → Dog.prototype → Animal.prototype → Object.prototype → null
Object.getPrototypeOf(dog) === Dog.prototype; // true
```

---

## 💻 Code Example — Basic
```javascript
// ── ACCESSING PROTOTYPE ──────────────────

const obj = { name: "Aditya" };

// Access prototype:
Object.getPrototypeOf(obj); // Object.prototype
obj.__proto__;              // Object.prototype (deprecated accessor, avoid)

// Is Object.prototype the prototype of obj?
Object.getPrototypeOf(obj) === Object.prototype; // true

// ── PROTOTYPE CHAIN LOOKUP ───────────────

const parent = {
  greet() { return "Hello from parent"; },
  type: "parent",
};

const child = Object.create(parent); // child's prototype = parent
child.name = "child object";
child.type = "child"; // shadows parent.type

child.name;   // "child object" — own property
child.type;   // "child" — own property (shadows parent.type)
child.greet(); // "Hello from parent" — from prototype!

// Verify:
Object.getPrototypeOf(child) === parent; // true

// ── PROPERTY LOOKUP ORDER ────────────────

// Check if property is own vs inherited:
child.hasOwnProperty("name");  // true  — own
child.hasOwnProperty("type");  // true  — own (shadows)
child.hasOwnProperty("greet"); // false — inherited from parent!
"greet" in child;              // true  — `in` checks chain

// ── FUNCTION PROTOTYPE ───────────────────

function Person(name, age) {
  this.name = name;
  this.age = age;
}

// Add method to prototype (shared by all instances):
Person.prototype.greet = function() {
  return `Hi, I'm ${this.name}`;
};

Person.prototype.species = "Homo Sapiens";

const p1 = new Person("Aditya", 25);
const p2 = new Person("Priya", 22);

p1.greet(); // "Hi, I'm Aditya" — from Person.prototype
p2.greet(); // "Hi, I'm Priya"  — from Person.prototype

// Both share the SAME greet function (not duplicated):
p1.greet === p2.greet; // true! (same function in prototype)

// Own properties vs prototype:
p1.hasOwnProperty("name"); // true  — set in constructor
p1.hasOwnProperty("greet"); // false — in prototype

// ── NULL PROTOTYPE OBJECT ────────────────
// Object with no prototype (no toString, no hasOwnProperty):
const clean = Object.create(null);
clean.key = "value";
// clean.toString() → TypeError (no prototype!)
// Useful for: pure hash maps, no prototype pollution
```

## 💻 Code Example — Advanced
```javascript
// ── CLASS IS SYNTACTIC SUGAR ──────────────

// ES6 class:
class Vehicle {
  constructor(brand) { this.brand = brand; }
  describe() { return `${this.brand} vehicle`; }
}

class Car extends Vehicle {
  constructor(brand, model) {
    super(brand); // calls Vehicle constructor
    this.model = model;
  }
  describe() { return `${this.brand} ${this.model}`; }
}

// Equivalent prototype-based code:
function VehicleFn(brand) { this.brand = brand; }
VehicleFn.prototype.describe = function() { return `${this.brand} vehicle`; };

function CarFn(brand, model) {
  VehicleFn.call(this, brand); // super()
  this.model = model;
}
// Set up inheritance chain:
CarFn.prototype = Object.create(VehicleFn.prototype);
CarFn.prototype.constructor = CarFn; // fix constructor reference
CarFn.prototype.describe = function() { return `${this.brand} ${this.model}`; };

// Both approaches produce same prototype chain:
// car → Car.prototype → Vehicle.prototype → Object.prototype → null

// ── CHECKING PROTOTYPE CHAIN ─────────────

const car = new Car("Toyota", "Camry");

car instanceof Car;      // true
car instanceof Vehicle;  // true (in chain)
car instanceof Object;   // true (everything inherits from Object)

// More precise check:
Object.getPrototypeOf(car) === Car.prototype;     // true
Object.getPrototypeOf(Car.prototype) === Vehicle.prototype; // true

// ── PROTOTYPE POLLUTION AWARENESS ────────

// DANGEROUS: modifying Object.prototype (affects ALL objects)
Object.prototype.hack = "hacked";
const innocent = {};
console.log(innocent.hack); // "hacked"! (via prototype chain)
// Never modify built-in prototypes in production code!

// SAFE: extend custom classes/prototypes only

// ── ADDING METHODS TO BUILT-INS (USE WITH CAUTION) ──

// Array.prototype extension — RISKY in shared codebases
Array.prototype.last = function() {
  return this[this.length - 1];
};
[1, 2, 3].last(); // 3 — but may conflict with future JS additions!
// Instead: use utility functions

function last(arr) { return arr[arr.length - 1]; }
// OR: arr.at(-1) — built-in!

// ── MIXINS PATTERN ──────────────────────
// Add functionality from multiple sources (JS has no multiple inheritance)

const Serializable = {
  serialize()   { return JSON.stringify(this); },
  deserialize(str) { return JSON.parse(str); },
};

const Validatable = {
  validate() { return Object.keys(this).every(k => this[k] !== null); },
};

class UserModel {
  constructor(name, email) {
    this.name = name;
    this.email = email;
  }
}

// Mix in:
Object.assign(UserModel.prototype, Serializable, Validatable);

const u = new UserModel("Aditya", "a@example.com");
u.serialize(); // '{"name":"Aditya","email":"a@example.com"}'
u.validate();  // true
```

---

## 🟠 React/Next.js Connection
```jsx
// ── WHY THIS MATTERS IN REACT ────────────

// 1. Custom hooks follow prototypal design:
// useState, useEffect — all functions that "hang off" the React module object

// 2. Class components use prototype chain:
class MyComponent extends React.Component {
  // MyComponent.prototype → React.Component.prototype → Object.prototype
  // Methods like setState, forceUpdate come from React.Component.prototype
  render() {
    return <div>{this.state.value}</div>;
  }
}

// 3. Understanding why spread doesn't deep copy (prototype not copied):
class Order {
  constructor(id) { this.id = id; }
  getStatus() { return "pending"; }
}
const order = new Order("ORD-1");
const copy = { ...order }; // { id: "ORD-1" } — getStatus NOT copied!
// Spread copies own enumerable properties only — not prototype methods

// 4. instanceof checks in HOCs and middleware:
function withAuth(WrappedComponent) {
  return class extends React.Component {
    render() {
      const { user, ...props } = this.props;
      if (!(user instanceof AuthenticatedUser)) return <Redirect to="/login" />;
      return <WrappedComponent user={user} {...props} />;
    }
  };
}

// ── NODE.JS MIDDLEWARE PATTERN ─────────────
// Express middleware uses prototype chaining under the hood
// Your route handlers get req/res — these are instances of classes
// with methods like req.json(), res.send() from their prototypes

app.use((req, res, next) => {
  // req.body, req.headers — from IncomingMessage.prototype
  // res.json, res.send — from ServerResponse.prototype
  next();
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Modifying Object.prototype or Array.prototype
```javascript
// DANGEROUS: pollutes ALL objects
Object.prototype.myMethod = function() { return "bad"; };
// Now EVERY object has myMethod — breaks for...in loops, libraries, etc.

// CORRECT: never modify built-in prototypes
// Add to your own class prototypes only
```

❌ **Mistake 2:** Confusing `__proto__` with `prototype`
```javascript
function Foo() {}
const foo = new Foo();

// prototype: property of constructor functions
Foo.prototype; // Object — methods added here are inherited by instances

// __proto__: the actual link on INSTANCES
foo.__proto__;                   // = Foo.prototype
Object.getPrototypeOf(foo);      // preferred over __proto__

// Don't confuse: Foo.prototype !== Foo.__proto__
Foo.__proto__; // Function.prototype (Foo is itself a function!)
```

❌ **Mistake 3:** Forgetting `new` with constructor functions
```javascript
function Person(name) {
  this.name = name; // without new, 'this' is global!
}

const p = Person("Aditya"); // ❌ forgot new!
// this.name = "Aditya" set on global object (window)!
// p === undefined

const p2 = new Person("Aditya"); // ✅
// Use classes to avoid this — they throw if called without new
```

---

## 🧠 Tricky Interview Output Question
```javascript
function Animal(name) { this.name = name; }
Animal.prototype.type = "Animal";

const cat = new Animal("Tom");
cat.type = "Cat"; // own property

console.log(cat.type);                    // A
console.log(Object.getPrototypeOf(cat).type); // B
delete cat.type;
console.log(cat.type);                    // C
```
**Answer:**
```
"Cat"     ← A: own property shadows prototype
"Animal"  ← B: prototype still has "Animal"
"Animal"  ← C: own deleted, now prototype's "Animal" is visible
```

---

## ⚫ Interview Questions + Answers

**Q1: What is the prototype chain?**
A1: The prototype chain is a series of linked objects. Every JavaScript object has a hidden `[[Prototype]]` (accessible via `Object.getPrototypeOf()`). When you access a property, JavaScript looks at the object itself first, then checks `[[Prototype]]`, then its `[[Prototype]]`, continuing up the chain until `null` is reached (end of chain). This is how all objects inherit methods like `toString()`, `hasOwnProperty()`, etc. from `Object.prototype`.

**Q2: What is the difference between `prototype` and `__proto__`?**
A2: `prototype` is a property of **constructor functions** — it's the object that will become the `[[Prototype]]` of all instances created with `new`. `__proto__` (or `Object.getPrototypeOf()`) is on every **instance** — it's the actual chain link pointing to the constructor's `prototype`. `Foo.prototype` is the object; `new Foo().__proto__` points to that same object.

**Q3: How do classes relate to prototypes?**
A3: ES6 classes are syntactic sugar over the prototype system. `class Dog extends Animal {}` sets up `Dog.prototype`'s `[[Prototype]]` to `Animal.prototype`. `super()` calls the parent constructor. Methods defined in a class body go on the class's `prototype`, not on each instance — so all instances share the same method references (memory efficient). Under the hood, it's all prototype chains.

**Q4: What is the difference between `instanceof` and `typeof`?**
A4: `typeof` returns a string type — works for primitives and functions but limited (null → "object", arrays → "object"). `instanceof` checks if an object's prototype chain includes the given constructor's `prototype` — `car instanceof Vehicle` returns true if `Vehicle.prototype` is anywhere in car's chain. Use `instanceof` for class/constructor checks, `Array.isArray()` for arrays, `typeof` for primitive type checks.

**Q5: What does `Object.create(null)` do and when would you use it?**
A5: Creates an object with NO prototype (no `[[Prototype]]` chain, no `Object.prototype` methods). It has no `toString`, no `hasOwnProperty`, no `valueOf` — a truly clean slate. Use cases: (1) Pure hash maps/dictionaries with no risk of prototype pollution. (2) When iterating with `for...in` and you want no inherited properties. (3) Security-conscious code where `__proto__` attacks could be a concern.

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [Akshay Saini — Prototype](https://www.youtube.com/results?search_query=prototype+javascript+akshay+saini+namaste) | Prototype chain visualization |
| 📝 Article | [javascript.info — Prototypal inheritance](https://javascript.info/prototype-inheritance) | Complete prototype tutorial |
| 📝 Article | [MDN — Inheritance and prototype chain](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Inheritance_and_the_prototype_chain) | Full reference |
| 📖 Book | [YDKJS — this & Object Prototypes](https://github.com/getify/You-Dont-Know-JS/tree/2nd-ed/objects-classes) | Deep understanding |

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Prototype | Object that provides inherited properties | Inherited properties देने वाला object |
| Prototype chain | Chain of linked prototype objects | Linked prototype objects की chain |
| [[Prototype]] | Hidden link to prototype | Prototype की hidden link |
| `__proto__` | Instance's prototype accessor | Instance का prototype accessor |
| `.prototype` | Constructor function's prototype | Constructor function का prototype |
| instanceof | Check prototype chain membership | Prototype chain में है या नहीं |
| Own property | Property directly on object | Object पर directly property |

---

## ⚡ 3-Line Summary
**English:**
1. Every object has a `[[Prototype]]` link — property lookups walk the chain until found or `null`.
2. `class` syntax is sugar over prototypes — methods go on the class's `prototype`, shared by all instances.
3. Never modify `Object.prototype` or `Array.prototype` — it pollutes ALL objects in the codebase.

**Hindi:**
1. हर object के पास `[[Prototype]]` link होती है — property lookup chain में walk करता है।
2. `class` syntax prototypes का sugar है — methods class के `prototype` पर होते हैं, सब instances share करते हैं।
3. कभी `Object.prototype` या `Array.prototype` modify मत करो — सब objects pollute हो जाते हैं।

---

## ➡️ Next Topic
**33. Classes and OOP in JavaScript** — ES6 Classes, constructor, extends, super, static, private fields — full OOP in JS।
