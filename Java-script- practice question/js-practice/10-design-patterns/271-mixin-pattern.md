---

# Q271. Mixin Pattern
# Category: Design Patterns
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Add reusable behaviors (`canFly`, `canSwim`) to different classes using mixins, since JS has no multiple inheritance.

---

## 💡 Quick Concept (2 lines only)
A mixin copies or composes reusable methods into a class without using inheritance.
हिंदी: Mixin से कई जगह से methods लेकर एक class में जोड़ सकते हैं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Write behaviors as functions that extend a base class
// Step 2: Apply them in a chain
// Step 3: Or copy methods onto a prototype with Object.assign

const CanFly = (Base) => class extends Base {   // subclass factory
  fly() { return `${this.name} flies`; }        // new behavior
};

const CanSwim = (Base) => class extends Base {  // another subclass factory
  swim() { return `${this.name} swims`; }       // new behavior
};

class Animal {
  constructor(name) { this.name = name; }       // base class
}

class Duck extends CanSwim(CanFly(Animal)) {}   // compose both mixins
class Fish extends CanSwim(Animal) {}           // only swimming

// Object.assign style (copy methods)
const Walker = { walk() { return `${this.name} walks`; } }; // plain object mixin
Object.assign(Duck.prototype, Walker);          // copy onto prototype

// ============================================
// TEST CASES
// ============================================

const d = new Duck('Donald');                   // duck instance
console.log(d.fly());                           // Expected: Donald flies
console.log(d.swim());                          // Expected: Donald swims
console.log(d.walk());                          // Expected: Donald walks
console.log(typeof new Fish('Nemo').fly);       // Expected: undefined
console.log(d instanceof Animal);               // Expected: true
```

---

## 🔍 Why This Works (3 lines max)
Each mixin is a function returning a subclass, so they stack into a prototype chain. Object.assign simply copies methods onto the prototype.
हिंदी: हर mixin एक नई subclass बनाता है, इसलिए इन्हें एक के ऊपर एक लगाया जा सकता है।

---

## ⚡ Alternative Solution
```javascript
// Composition over inheritance with plain functions
const flyer = (o) => ({ ...o, fly: () => `${o.name} flies` }); // add method to object
console.log(flyer({ name: 'Bat' }).fly());                      // Expected: Bat flies
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: Object.assign(Class, mixin) — methods land on the constructor, not instances
// ✅ Correct: Object.assign(Class.prototype, mixin)
```

---

## 🎯 Interview Tip (1 line)
Say: "Prefer composition; mixins risk name clashes and hidden dependencies on `this`."

---

## 🔗 Related Questions
→ Q147 (Class inheritance) | Q024 (Prototype chain) | Q265 (Decorator)
