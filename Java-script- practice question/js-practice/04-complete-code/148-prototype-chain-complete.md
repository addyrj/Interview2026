---

# Q148. Complete Prototype Chain
# Category: Complete the Code
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Fill in the blanks to make `Student` inherit from `Person` using prototypes.

```javascript
function Person(name) { this.name = name; }
Person.prototype.hello = function () { return 'Hi ' + this.name; };

function Student(name, school) {
  Person.____(this, name);                       // reuse parent constructor
  this.school = school;
}
Student.prototype = Object.____(Person.____);    // link prototypes
Student.prototype.____ = Student;                // fix constructor
```

---

## 💡 Quick Concept (2 lines only)
Property lookup walks up the `__proto__` chain. `Object.create(Parent.prototype)` links the child to parent methods.
हिंदी: property न मिले तो JS prototype chain में ऊपर ढूँढता है; `Object.create` से chain जुड़ती है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

function Person(name) { this.name = name; }                    // Step 1: parent constructor
Person.prototype.hello = function () { return 'Hi ' + this.name; }; // shared method

function Student(name, school) {
  Person.call(this, name);                                     // blank 1: run parent init on this
  this.school = school;                                        // child property
}
Student.prototype = Object.create(Person.prototype);           // blanks 2+3: inherit methods
Student.prototype.constructor = Student;                       // blank 4: restore constructor

// ============================================
// TEST CASES
// ============================================

const s = new Student('Aman', 'DU');
console.log(s.hello());                                        // Expected: Hi Aman
console.log(s instanceof Person);                              // Expected: true
console.log(Object.getPrototypeOf(Student.prototype) === Person.prototype); // Expected: true
console.log(s.constructor === Student);                        // Expected: true
```

---

## 🔍 Why This Works (3 lines max)
`call` copies instance properties, and `Object.create` makes Student.prototype delegate to Person.prototype. Resetting `constructor` keeps it pointing to Student.
हिंदी: `call` properties लाता है और `Object.create` methods; `constructor` को वापस सेट करना ज़रूरी है।

---

## ⚡ Alternative Solution
```javascript
// Modern: setPrototypeOf
Object.setPrototypeOf(Student.prototype, Person.prototype);
console.log(new Student('x', 'y').hello()); // Hi x
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: Student.prototype = Person.prototype  (shared object, child edits affect parent)
// ✅ Correct: Object.create(Person.prototype)
```

---

## 🎯 Interview Tip (1 line)
Say: "Chain: instance -> Student.prototype -> Person.prototype -> Object.prototype -> null."

---

## 🔗 Related Questions
→ Q024 (prototype chain output) | Q111 (Object.create) | Q129 (prototype mutation) | Q162 (prototype explained)
