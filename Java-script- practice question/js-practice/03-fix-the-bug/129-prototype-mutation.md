---

# Q129. Fix Prototype Mutation Bug
# Category: Fix the Bug
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Two users share the same `skills` array because it lives on the prototype. Fix it so each user has its own.

```javascript
// BUGGY CODE:
function User(name) { this.name = name; }
User.prototype.skills = [];            // shared by every instance
User.prototype.addSkill = function (s) { this.skills.push(s); };

const a = new User('A'), b = new User('B');
a.addSkill('js');
console.log(b.skills);                 // [ 'js' ] (unexpected)
```

---

## 💡 Quick Concept (2 lines only)
Prototype properties are shared. Mutating an object/array found on the prototype changes it for ALL instances. Put per-instance data in the constructor.
हिंदी: prototype पर रखा array सबके बीच share होता है — instance data constructor में रखो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

function User(name) {
  this.name = name;                    // Step 1: own property
  this.skills = [];                    // Step 2 (FIX): each instance gets its own array
}
User.prototype.addSkill = function (s) { // Step 3: shared behavior (methods) stay on prototype
  this.skills.push(s);                 // pushes into this instance's array
};

// ============================================
// TEST CASES
// ============================================

const a = new User('A');
const b = new User('B');
a.addSkill('js');
console.log(a.skills);                 // Expected: [ 'js' ]
console.log(b.skills);                 // Expected: []
console.log(a.skills === b.skills);    // Expected: false
```

---

## 🔍 Why This Works (3 lines max)
`this.skills = []` in the constructor creates a separate array on each object, shadowing nothing on the prototype. Methods are safe to share because they hold no state.
हिंदी: constructor में बना array हर object का अपना होता है, methods ही prototype पर share होते हैं।

---

## ⚡ Alternative Solution
```javascript
// class with a field gives each instance its own array
class User2 {
  skills = [];                          // per-instance field
  addSkill(s) { this.skills.push(s); }
}
const x = new User2(), y = new User2();
x.addSkill('css');
console.log(y.skills); // []
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: modifying built-in prototypes
// Array.prototype.last = function () { return this[this.length - 1]; }; // shows up in for...in
// ✅ Correct: use a helper function
const last = (arr) => arr[arr.length - 1];
console.log(last([1, 2, 3])); // 3
```

---

## 🎯 Interview Tip (1 line)
Say: "Share methods via prototype, never mutable state; reassigning (a.x = 1) shadows, but push mutates the shared object."

---

## 🔗 Related Questions
→ Q024 (prototype chain) | Q148 (complete prototype chain) | Q162 (prototype explained) | Q297 (prototype vs class)
