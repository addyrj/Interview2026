---

# Q110. Implement New Keyword
# Category: Implement / Build
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Implement `myNew(Constructor, ...args)` that behaves like `new Constructor(...args)`.

```javascript
function Person(name) { this.name = name; }
const p = myNew(Person, 'Aditya');
p.name; // "Aditya"
```

---

## 💡 Quick Concept (2 lines only)
`new` does 4 things: create an empty object, link its prototype to `Constructor.prototype`, run the constructor with `this` = that object, return the object (unless constructor returns an object).
हिंदी: `new` नया object बनाता है, prototype जोड़ता है, constructor चलाता है और object लौटाता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: create object linked to Constructor.prototype
// Step 2: run Constructor with this = new object
// Step 3: if constructor returned an object, use it; else return our object

function myNew(Constructor, ...args) {
  const obj = Object.create(Constructor.prototype);  // empty object + prototype link
  const result = Constructor.apply(obj, args);       // run constructor with this = obj
  const isObject = result !== null &&
    (typeof result === 'object' || typeof result === 'function'); // returned an object?
  return isObject ? result : obj;                    // object return wins, else our obj
}

// ============================================
// TEST CASES
// ============================================

function Person(name, age) {
  this.name = name;                  // set property on this
  this.age = age;
}
Person.prototype.sayHi = function () { return `Hi ${this.name}`; }; // shared method

const p = myNew(Person, 'Aditya', 25);               // create instance
console.log(p.name, p.age);          // Expected: Aditya 25
console.log(p.sayHi());              // Expected: Hi Aditya
console.log(p instanceof Person);    // Expected: true

function ReturnsObject() { this.a = 1; return { b: 2 }; } // returns custom object
console.log(myNew(ReturnsObject));   // Expected: { b: 2 }

function ReturnsPrimitive() { this.a = 1; return 5; }     // primitive is ignored
console.log(myNew(ReturnsPrimitive)); // Expected: ReturnsPrimitive { a: 1 }
```

---

## 🔍 Why This Works (3 lines max)
`Object.create` sets the prototype chain so methods are inherited. `apply` fills the object via `this`. The return check copies the native rule: only object returns override.
हिंदी: Object.create से prototype जुड़ता है, apply से properties भरती हैं, और सिर्फ object return ही override करता है।

---

## ⚡ Alternative Solution
```javascript
// Using Reflect.construct (native, also handles classes)
function myNew2(Ctor, ...args) {
  return Reflect.construct(Ctor, args);   // does everything `new` does
}
class Car { constructor(n) { this.n = n; } }
console.log(myNew2(Car, 'BMW').n);        // Expected: BMW
// Note: myNew above fails for classes (they cannot be called without new)
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: always returning obj, ignoring constructor's returned object
Constructor.apply(obj, args);
return obj;

// ✅ Correct: check the constructor's return value
const result = Constructor.apply(obj, args);
return typeof result === 'object' && result !== null ? result : obj;
```

---

## 🎯 Interview Tip (1 line)
Recite the 4 steps of `new` clearly, then mention the object-return override rule.

---

## 🔗 Related Questions
→ Q111 (Object.create) | Q109 (bind) | Q024 (prototype chain output) | Q162 (explain prototype)
