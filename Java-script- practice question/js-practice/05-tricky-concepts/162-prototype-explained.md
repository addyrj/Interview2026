---

# Q162. Explain Prototype with Example
# Category: Tricky Concepts
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Explain the prototype and prototype chain in JavaScript. Show how objects inherit properties and methods, and how lookup works.

---

## 💡 Quick Concept (2 lines only)
Every object has a hidden link (`[[Prototype]]`) to another object. If a property is not found on the object, JS walks up this chain until it finds it or reaches `null`.
हिंदी: Prototype = object का पीछे वाला link — property खुद में न मिले तो JS chain में ऊपर ढूँढता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Constructor function holds own data
// Step 2: Shared methods go on Constructor.prototype
// Step 3: Lookup walks the chain: obj -> prototype -> Object.prototype -> null

function Person(name) {            // constructor function
  this.name = name;                // own property (per instance)
}

Person.prototype.greet = function () {   // shared method (one copy only)
  return `Hi, I am ${this.name}`;        // uses this to read own data
};

function Student(name, course) {   // child constructor
  Person.call(this, name);         // reuse parent constructor for own props
  this.course = course;            // own property of student
}

Student.prototype = Object.create(Person.prototype); // link chain: Student -> Person
Student.prototype.constructor = Student;             // fix constructor pointer

Student.prototype.study = function () {  // method only for students
  return `${this.name} studies ${this.course}`; // uses inherited name
};

const s = new Student('Aditya', 'JS');   // create instance

// ============================================
// TEST CASES
// ============================================

console.log(s.study());                              // Expected: Aditya studies JS
console.log(s.greet());                              // Expected: Hi, I am Aditya
console.log(s.hasOwnProperty('greet'));              // Expected: false
console.log(Object.getPrototypeOf(s) === Student.prototype); // Expected: true
console.log(s.__proto__.__proto__ === Person.prototype);     // Expected: true
console.log(s instanceof Person);                    // Expected: true
console.log(Object.getPrototypeOf(Object.prototype)); // Expected: null
```

---

## 🔍 Why This Works (3 lines max)
`new` creates an object whose `[[Prototype]]` is `Constructor.prototype`. Property lookup checks own keys first, then climbs the chain. Methods on the prototype are shared, saving memory.
हिंदी: `new` object को prototype से जोड़ता है, और methods सब instances में share होते हैं।

---

## ⚡ Alternative Solution
```javascript
// Modern way: class is syntax sugar over prototypes
class Animal {                       // parent class
  constructor(name) { this.name = name; }   // own property
  speak() { return `${this.name} makes a sound`; } // goes on Animal.prototype
}
class Dog extends Animal {           // sets up prototype chain automatically
  speak() { return `${this.name} barks`; }  // overrides parent method
}
const d = new Dog('Rex');            // create instance
console.log(d.speak());              // Expected: Rex barks
console.log(typeof Animal);          // Expected: function
console.log(Object.getPrototypeOf(Dog) === Animal); // Expected: true
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Methods inside constructor -> new copy for every instance (wastes memory)
function Bad(n) { this.n = n; this.show = function () { return this.n; }; }
console.log(new Bad(1).show === new Bad(1).show); // false

// ✅ Put methods on prototype -> shared
function Good(n) { this.n = n; }
Good.prototype.show = function () { return this.n; };
console.log(new Good(1).show === new Good(1).show); // true
```

---

## 🎯 Interview Tip (1 line)
Say: "`__proto__` is the actual link of an object; `prototype` is a property of functions used as the link for instances created via `new`; class is just sugar."

---

## 🔗 Related Questions
→ Q024 (prototype chain output) | Q111 (Object.create) | Q129 (prototype mutation bug) | Q297 (prototype vs class)
