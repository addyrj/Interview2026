---

# Q297. prototype vs class
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Is an ES6 `class` different from prototype-based constructor functions? Show both styles, prove they share the same mechanism, and list the real differences.

---

## 💡 Quick Concept (2 lines only)
`class` is syntax sugar over constructor functions + `prototype`; methods live on `Class.prototype` and are shared by all instances.
हिंदी: `class` असल में prototype का सुंदर syntax है; methods prototype पर रहते हैं और सब instances share करते हैं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: old style — constructor function + methods on prototype
// Step 2: new style — class with constructor + methods
// Step 3: compare: both create prototype links; class adds safety rules

// --- Prototype style ---
function PersonProto(name) { this.name = name; }          // constructor function
PersonProto.prototype.greet = function () {               // shared method on prototype
  return 'Hi, ' + this.name;                              // uses instance data
};

// --- Class style ---
class Person {
  constructor(name) { this.name = name; }                 // same as constructor function
  greet() { return 'Hi, ' + this.name; }                  // goes on Person.prototype
}

// Inheritance with class
class Student extends Person {
  constructor(name, school) { super(name); this.school = school; } // call parent constructor
  info() { return this.name + ' @ ' + this.school; }      // child method
}

// ============================================
// TEST CASES
// ============================================

const p1 = new PersonProto('Asha');                       // prototype-style instance
const p2 = new Person('Ravi');                            // class-style instance
const p3 = new Person('Meera');                           // another class instance

console.log(p1.greet());                                  // Expected: Hi, Asha
console.log(p2.greet());                                  // Expected: Hi, Ravi
console.log(typeof Person);                               // Expected: function
console.log(Object.getPrototypeOf(p2) === Person.prototype); // Expected: true
console.log(p2.greet === p3.greet);                       // Expected: true (shared method)
console.log(new Student('Neha', 'DPS').info());           // Expected: Neha @ DPS
console.log(Object.getPrototypeOf(Student.prototype) === Person.prototype); // Expected: true

try { Person('x'); } catch (e) { console.log(e instanceof TypeError); } // Expected: true (needs new)
console.log(PersonProto('x') === undefined);              // Expected: true (no error, but leaks this)
```

---

## 🔍 Why This Works (3 lines max)
Both styles set `instance.__proto__ = Constructor.prototype`, so lookups walk the same chain. `class` adds guard rails: must use `new`, body is strict mode, not hoisted like functions, and methods are non-enumerable.
हिंदी: दोनों में chain same है; class सिर्फ़ safe और साफ़ syntax देता है (`new` ज़रूरी, strict mode)।

---

## ⚡ Alternative Solution
```javascript
// Object.create — pure prototype inheritance without constructors
const animal = { speak() { return this.name + ' makes a sound'; } }; // prototype object
const dog = Object.create(animal);   // dog's prototype is animal
dog.name = 'Rex';                    // own property
console.log(dog.speak());            // Rex makes a sound
console.log(Object.getPrototypeOf(dog) === animal); // true
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: defining methods inside constructor — copy per instance (wasteful)
function Bad(n) { this.n = n; this.hi = function () { return this.n; }; }
console.log(new Bad(1).hi === new Bad(1).hi); // false — two different functions

// ✅ Correct: put methods on prototype / class body — shared
class Good { constructor(n) { this.n = n; } hi() { return this.n; } }
console.log(new Good(1).hi === new Good(1).hi); // true
```

---

## 🎯 Interview Tip (1 line)
Say: "Class is syntactic sugar over prototypes — same chain underneath, plus `new` enforcement, strict mode and cleaner `extends/super`."

---

## 🔗 Related Questions
→ Q024 (prototype chain) | Q110 (implement new) | Q147 (class inheritance) | Q162 (explain prototype)
