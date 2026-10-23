# 33. Classes and OOP in JavaScript
# हिंदी में: Classes — JavaScript में Object-Oriented Programming

---

## 🔵 Simple Definition (English)
ES6 **classes** are syntactic sugar over prototypes — they provide a clean OOP syntax for creating objects with shared behavior. Key features: `constructor`, `extends`, `super`, `static`, `get`/`set`, and private fields (`#`).

## 🔵 सरल परिभाषा (Hindi)
ES6 classes prototypes का syntactic sugar हैं — shared behavior वाले objects बनाने का clean OOP syntax। Key features: `constructor`, `extends`, `super`, `static`, `get`/`set`, और private fields (`#`)।

---

## 🟢 OOP Pillars in JavaScript
```
1. ENCAPSULATION  — Bundle data + methods, hide internals (#privateFields)
2. INHERITANCE    — Subclass extends superclass (extends + super)
3. POLYMORPHISM   — Same interface, different behavior (method overriding)
4. ABSTRACTION    — Expose only what's needed, hide implementation
```

---

## 🟡 Real World Example
```javascript
class Product {
  #stock = 0; // private
  
  constructor(id, name, price) {
    this.id = id;
    this.name = name;
    this.price = price;
  }
  
  addStock(qty) { this.#stock += qty; }
  
  get inStock() { return this.#stock > 0; }
  
  get displayPrice() { return `₹${this.price.toLocaleString("en-IN")}`; }
  
  toString() { return `${this.name} (${this.displayPrice})`; }
}

class FoodProduct extends Product {
  constructor(id, name, price, cuisine) {
    super(id, name, price);
    this.cuisine = cuisine;
  }
  
  toString() { return `${super.toString()} — ${this.cuisine}`; }
}

const pizza = new FoodProduct("P1", "Pizza", 299, "Italian");
pizza.addStock(50);
console.log(pizza.inStock);     // true
console.log(pizza.toString());  // "Pizza (₹299) — Italian"
```

---

## 💻 Code Example — Basic
```javascript
// ── BASIC CLASS ──────────────────────────

class BankAccount {
  // Class field (public):
  currency = "INR";

  // Private field (only accessible within class):
  #balance;
  #transactions = [];

  // Constructor: called when `new BankAccount(...)` is used
  constructor(owner, initialBalance = 0) {
    this.owner = owner;
    this.#balance = initialBalance;
  }

  // Instance methods:
  deposit(amount) {
    if (amount <= 0) throw new Error("Invalid amount");
    this.#balance += amount;
    this.#transactions.push({ type: "deposit", amount, date: new Date() });
    return this; // enable chaining
  }

  withdraw(amount) {
    if (amount > this.#balance) throw new Error("Insufficient funds");
    this.#balance -= amount;
    this.#transactions.push({ type: "withdraw", amount, date: new Date() });
    return this;
  }

  // Getter — accessed as property (no parens)
  get balance() { return this.#balance; }

  // Setter — validates before setting
  set balance(value) {
    if (value < 0) throw new Error("Balance can't be negative");
    this.#balance = value;
  }

  // Static method — belongs to class, not instances
  static createSavings(owner) {
    const acc = new BankAccount(owner, 0);
    acc.type = "savings";
    return acc;
  }

  getStatement() {
    return this.#transactions.map(t =>
      `${t.type}: ₹${t.amount}`
    ).join("\n");
  }
}

const acc = new BankAccount("Aditya", 1000);
acc.deposit(500).deposit(200).withdraw(300); // chaining
console.log(acc.balance); // 1400 (getter)
// acc.#balance → SyntaxError — private!

const savings = BankAccount.createSavings("Priya"); // static factory

// ── GETTERS AND SETTERS ──────────────────

class Temperature {
  #celsius;

  constructor(celsius) { this.#celsius = celsius; }

  get celsius() { return this.#celsius; }
  set celsius(value) {
    if (value < -273.15) throw new Error("Below absolute zero!");
    this.#celsius = value;
  }

  get fahrenheit() { return this.#celsius * 9/5 + 32; }
  set fahrenheit(value) { this.#celsius = (value - 32) * 5/9; }

  get kelvin() { return this.#celsius + 273.15; }
}

const temp = new Temperature(100);
console.log(temp.fahrenheit); // 212
temp.fahrenheit = 32;
console.log(temp.celsius);    // 0
```

## 💻 Code Example — Advanced
```javascript
// ── INHERITANCE ──────────────────────────

class Animal {
  constructor(name, sound) {
    this.name = name;
    this.sound = sound;
  }

  speak() { return `${this.name} says ${this.sound}`; }

  toString() { return `Animal: ${this.name}`; }
}

class Dog extends Animal {
  #tricks = [];

  constructor(name) {
    super(name, "Woof"); // MUST call super() first
    this.type = "dog";
  }

  // Override (polymorphism):
  speak() {
    return `${super.speak()}! ${this.name} is excited!`;
  }

  learn(trick) {
    this.#tricks.push(trick);
    return this;
  }

  perform() {
    return this.#tricks.length > 0
      ? `${this.name} does: ${this.#tricks.join(", ")}`
      : `${this.name} doesn't know any tricks yet`;
  }
}

class GuideDog extends Dog {
  constructor(name, owner) {
    super(name);
    this.owner = owner;
  }

  guide() { return `${this.name} guides ${this.owner}`; }
}

const rex = new Dog("Rex");
rex.learn("sit").learn("shake").learn("roll over");
rex.perform(); // "Rex does: sit, shake, roll over"
rex.speak();   // "Rex says Woof! Rex is excited!"

const buddy = new GuideDog("Buddy", "Aditya");
buddy.guide(); // "Buddy guides Aditya"

// instanceof checks:
buddy instanceof GuideDog; // true
buddy instanceof Dog;      // true
buddy instanceof Animal;   // true

// ── STATIC METHODS AND PROPERTIES ────────

class MathUtils {
  static PI = 3.14159;
  static E = 2.71828;

  static circleArea(r) { return MathUtils.PI * r * r; }
  static distance(x1, y1, x2, y2) {
    return Math.sqrt((x2-x1)**2 + (y2-y1)**2);
  }
  static clamp(value, min, max) { return Math.min(Math.max(value, min), max); }
}

MathUtils.circleArea(5); // 78.53975 (no instance needed)
MathUtils.clamp(150, 0, 100); // 100

// Factory pattern with static:
class User {
  static #count = 0; // static private

  constructor(name, email, role) {
    this.id = ++User.#count;
    this.name = name;
    this.email = email;
    this.role = role;
  }

  static createAdmin(name, email) {
    return new User(name, email, "admin");
  }

  static createGuest(name) {
    return new User(name, "guest@temp.com", "guest");
  }

  static getTotalUsers() { return User.#count; }
}

const admin = User.createAdmin("Aditya", "admin@example.com");
const guest = User.createGuest("Visitor");
User.getTotalUsers(); // 2

// ── ABSTRACT CLASS PATTERN ───────────────
// JavaScript doesn't have abstract classes — simulate with errors

class Shape {
  constructor(color = "black") { this.color = color; }

  // "Abstract" method — must be overridden
  area() { throw new Error(`${this.constructor.name} must implement area()`); }
  perimeter() { throw new Error(`${this.constructor.name} must implement perimeter()`); }

  // Concrete method using abstract ones:
  describe() {
    return `A ${this.color} ${this.constructor.name}: area=${this.area().toFixed(2)}`;
  }
}

class Circle extends Shape {
  constructor(radius, color) { super(color); this.radius = radius; }
  area() { return Math.PI * this.radius ** 2; }
  perimeter() { return 2 * Math.PI * this.radius; }
}

class Rectangle extends Shape {
  constructor(w, h, color) { super(color); this.w = w; this.h = h; }
  area() { return this.w * this.h; }
  perimeter() { return 2 * (this.w + this.h); }
}

const c = new Circle(5, "red");
const r = new Rectangle(4, 6, "blue");
c.describe(); // "A red Circle: area=78.54"
r.describe(); // "A blue Rectangle: area=24.00"
```

---

## 🟠 React/Next.js Connection
```jsx
// ── SERVICE CLASSES IN NEXT.JS ────────────

class ProductService {
  #baseURL;
  #cache = new Map();

  constructor(baseURL) {
    this.#baseURL = baseURL;
  }

  async getAll(filters = {}) {
    const key = JSON.stringify(filters);
    if (this.#cache.has(key)) return this.#cache.get(key);

    const params = new URLSearchParams(filters);
    const response = await fetch(`${this.#baseURL}/products?${params}`);
    const data = await response.json();

    this.#cache.set(key, data);
    return data;
  }

  async getById(id) {
    const response = await fetch(`${this.#baseURL}/products/${id}`);
    if (!response.ok) throw new Error(`Product ${id} not found`);
    return response.json();
  }

  static create(env = "production") {
    const baseURL = env === "production"
      ? "https://api.myapp.com"
      : "http://localhost:3001";
    return new ProductService(baseURL);
  }
}

const productService = ProductService.create(process.env.NODE_ENV);

// ── CUSTOM ERROR CLASSES ──────────────────

class AppError extends Error {
  constructor(message, statusCode = 500, code = "INTERNAL_ERROR") {
    super(message);
    this.name = this.constructor.name;
    this.statusCode = statusCode;
    this.code = code;
    Error.captureStackTrace(this, this.constructor);
  }
}

class ValidationError extends AppError {
  constructor(message, fields = {}) {
    super(message, 400, "VALIDATION_ERROR");
    this.fields = fields;
  }
}

class NotFoundError extends AppError {
  constructor(resource, id) {
    super(`${resource} with id ${id} not found`, 404, "NOT_FOUND");
    this.resource = resource;
  }
}

// Usage in API routes:
app.get("/api/products/:id", async (req, res, next) => {
  try {
    const product = await db.findById(req.params.id);
    if (!product) throw new NotFoundError("Product", req.params.id);
    res.json(product);
  } catch (error) {
    if (error instanceof AppError) {
      res.status(error.statusCode).json({ error: error.message, code: error.code });
    } else {
      next(error); // pass to global error handler
    }
  }
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting `super()` in derived constructor
```javascript
class Child extends Parent {
  constructor(value) {
    // this.value = value; // ❌ ReferenceError: Must call super before accessing 'this'
    super(); // ✅ must come first
    this.value = value;
  }
}
```

❌ **Mistake 2:** Arrow functions as class methods (can't be overridden via prototype)
```javascript
class Animal {
  speak = () => "sound"; // arrow class field — on instance, not prototype
}
class Dog extends Animal {
  speak = () => "woof";  // creates own speak, doesn't override prototype
}
// For true polymorphism, use regular methods (go on prototype):
class Animal { speak() { return "sound"; } }
class Dog extends Animal { speak() { return "woof"; } }
```

❌ **Mistake 3:** Accessing private fields from outside
```javascript
class Box {
  #secret = "private";
}
const b = new Box();
b.#secret; // ❌ SyntaxError: Private field '#secret' must be declared in an enclosing class
```

---

## 🧠 Tricky Interview Output Question
```javascript
class Counter {
  static count = 0;
  #value;

  constructor(initial = 0) {
    this.#value = initial;
    Counter.count++;
  }

  increment() { return ++this.#value; }

  static reset() { Counter.count = 0; }
}

const c1 = new Counter(5);
const c2 = new Counter(10);

c1.increment();
c1.increment();

console.log(c1.increment()); // A
console.log(Counter.count);  // B
// console.log(c1.#value);   // C
```
**Answer:**
```
8     ← A: 5 + increment + increment + increment = 8
2     ← B: two instances created (c1 and c2)
SyntaxError ← C: private field not accessible outside class
```

---

## ⚫ Interview Questions + Answers

**Q1: What are the pillars of OOP and how does JavaScript support them?**
A1: (1) **Encapsulation** — private fields (`#field`) hide state, public methods expose behavior. (2) **Inheritance** — `extends` creates subclasses, `super` calls parent. (3) **Polymorphism** — override methods in subclasses; same interface, different behavior. (4) **Abstraction** — expose what's needed, hide complexity (simulate with Error throws for abstract methods). JavaScript supports all four, though some require patterns/conventions.

**Q2: What is the difference between static and instance methods?**
A2: **Instance methods** belong to each object created by the class — `this` refers to the instance. **Static methods** belong to the class itself (not instances) — accessed via `ClassName.method()`. Use static for: factory methods (create multiple types of instances), utility functions (stateless operations on inputs), class-level state (counters, caches). You can't call static methods on instances.

**Q3: What are private class fields and how are they different from convention?**
A3: Private fields (`#field`) are a language-level feature — trying to access them outside the class throws a `SyntaxError`. Before `#`, developers used `_underscore` convention to signal "private" — but it's just a convention, the property is still accessible. `#` fields are truly private: no access, no reflection, completely hidden. They're also stored differently for security.

**Q4: What does `super` do?**
A4: In a constructor: `super()` calls the parent class's constructor — mandatory before using `this` in a derived class. In a method: `super.method()` calls the parent class's version of a method — useful for extending behavior. `super.property` accesses parent properties. Always call `super()` first in derived constructors.

**Q5: When would you use a class vs a plain object vs a function in JavaScript?**
A5: **Class**: when you need multiple instances with shared behavior and state, inheritance, private fields, or clear OOP structure (services, models, custom errors). **Plain object**: one-off objects, configuration, data transfer objects — no methods needed. **Function**: pure utilities, React functional components, transformations without state. In modern React, functional components + hooks replace most class use cases.

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [Akshay Saini — Classes](https://www.youtube.com/results?search_query=classes+javascript+akshay+saini) | ES6 classes deep dive |
| 📝 Article | [javascript.info — Classes](https://javascript.info/classes) | Complete class tutorial |
| 📝 Article | [MDN — Classes](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes) | All class features |
| 📝 Article | [javascript.info — Private class fields](https://javascript.info/private-protected-properties-methods) | Encapsulation patterns |

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| constructor | Special method to initialize instances | Instance initialize करने वाला method |
| extends | Create subclass from superclass | Subclass बनाना |
| super | Call parent constructor/method | Parent को call करना |
| static | Belongs to class, not instances | Class का, instances का नहीं |
| private (#) | Only accessible within class | सिर्फ class के अंदर accessible |
| getter/setter | Property-like access to methods | Method को property की तरह access |
| polymorphism | Same interface, different behavior | Same interface, अलग behavior |

---

## ⚡ 3-Line Summary
**English:**
1. Classes = constructor + instance methods + static methods + getters/setters + private fields (`#`).
2. Inheritance: `extends` + `super()` first in constructor — subclass gets all parent behavior + can override.
3. Use classes for services, models, custom errors; use functional patterns for React components and transformations.

**Hindi:**
1. Classes = constructor + instance methods + static methods + getters/setters + private fields (`#`)।
2. Inheritance: `extends` + constructor में पहले `super()` — subclass को parent behavior + override करने की power।
3. Services, models, custom errors के लिए classes; React components और transformations के लिए functional patterns।

---

## ➡️ Next Topic
**34. Error Handling — try/catch/finally, Custom Errors** — Errors को gracefully handle करना।
