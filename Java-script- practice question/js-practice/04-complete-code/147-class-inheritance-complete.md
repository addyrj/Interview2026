---

# Q147. Complete Class Inheritance
# Category: Complete the Code
# Difficulty: ⭐ Easy

---

## ❓ Question
Fill in the blanks so `Dog` inherits from `Animal` and overrides `speak`.

```javascript
class Animal {
  constructor(name) { this.name = name; }
  speak() { return this.name + ' makes a sound'; }
}

class Dog ____ Animal {                    // inherit
  constructor(name, breed) {
    ____(name);                            // call parent constructor
    this.breed = breed;
  }
  speak() {
    return ____.speak() + ' - Woof';       // reuse parent method
  }
}
```

---

## 💡 Quick Concept (2 lines only)
`extends` links child to parent. `super()` must run before using `this` in the child constructor, and `super.method()` calls the parent version.
हिंदी: `extends` से inherit करते हैं, `super()` parent constructor चलाता है और `super.method()` parent method।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

class Animal {
  constructor(name) { this.name = name; }                  // Step 1: parent state
  speak() { return this.name + ' makes a sound'; }         // parent method
}

class Dog extends Animal {                                 // blank 1: inherit
  constructor(name, breed) {
    super(name);                                           // blank 2: must come first
    this.breed = breed;                                    // child state
  }
  speak() {
    return super.speak() + ' - Woof';                      // blank 3: extend parent behavior
  }
}

// ============================================
// TEST CASES
// ============================================

const d = new Dog('Rex', 'Lab');
console.log(d.speak());                // Expected: Rex makes a sound - Woof
console.log(d instanceof Animal);      // Expected: true
console.log(d.breed);                  // Expected: Lab
```

---

## 🔍 Why This Works (3 lines max)
`extends` sets Dog.prototype's prototype to Animal.prototype. `super` refers to the parent so you can reuse and extend its logic.
हिंदी: `extends` prototype chain जोड़ता है और `super` से parent का code दोबारा use होता है।

---

## ⚡ Alternative Solution
```javascript
// Same idea with Object.create (pre-ES6)
function A(n) { this.name = n; }
function B(n) { A.call(this, n); }
B.prototype = Object.create(A.prototype);
B.prototype.constructor = B;
console.log(new B('x') instanceof A); // true
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: using this before super()
// constructor(n) { this.x = 1; super(n); }  // ReferenceError
// ✅ Correct: call super(n) first
```

---

## 🎯 Interview Tip (1 line)
Say: "Classes are syntax over prototypes; extends wires the chain and super() initialises the parent part."

---

## 🔗 Related Questions
→ Q020 (this in class) | Q148 (complete prototype chain) | Q297 (prototype vs class) | Q271 (mixin pattern)
