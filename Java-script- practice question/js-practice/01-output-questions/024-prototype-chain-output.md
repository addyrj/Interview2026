---

# Q024. Prototype Chain Output
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```javascript
function Animal() {}
Animal.prototype.speak = function () { return 'sound'; };
function Dog() {}
Dog.prototype = Object.create(Animal.prototype);
Dog.prototype.constructor = Dog;
const d = new Dog();
console.log(d.speak());
console.log(d.hasOwnProperty('speak'));
console.log(Object.getPrototypeOf(d) === Dog.prototype);
console.log(Object.getPrototypeOf(Object.prototype));
```

---

## 💡 Quick Concept (2 lines only)
Property lookup walks up the chain: object -> its prototype -> ... -> `Object.prototype` -> `null`.
हिंदी: Property खोजते समय JS chain में ऊपर जाता है: object -> prototype -> Object.prototype -> null।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: d.speak not on d -> not on Dog.prototype -> found on Animal.prototype
// Step 2: hasOwnProperty checks only d itself -> false
// Step 3: d's prototype is Dog.prototype; chain ends at null

function Animal() {}                               // base constructor
Animal.prototype.speak = function () {             // shared method
  return 'sound';
};
function Dog() {}                                  // child constructor
Dog.prototype = Object.create(Animal.prototype);   // link chain
Dog.prototype.constructor = Dog;                   // restore constructor
const d = new Dog();                               // instance

// ============================================
// TEST CASES
// ============================================

console.log(d.speak());                                    // Expected: sound
console.log(d.hasOwnProperty('speak'));                    // Expected: false
console.log(Object.getPrototypeOf(d) === Dog.prototype);   // Expected: true
console.log(Object.getPrototypeOf(Object.prototype));      // Expected: null
```

---

## 🔍 Why This Works (3 lines max)
`new Dog()` sets d's hidden prototype to `Dog.prototype`, which itself inherits from `Animal.prototype`. `speak` is found two links up, but it is not d's own property.
हिंदी: speak दो level ऊपर Animal.prototype में मिलता है, d की अपनी property नहीं है।

---

## ⚡ Alternative Solution
```javascript
// Same chain with ES6 classes
class A { speak() { return 'sound'; } }            // base class
class D extends A {}                               // inherits via prototype
console.log(new D().speak());                      // Expected: sound
console.log(Object.getPrototypeOf(D.prototype) === A.prototype); // Expected: true
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Dog.prototype = Animal.prototype;  // shares one object, edits leak to parent
// ✅ Dog.prototype = Object.create(Animal.prototype);
```

---

## 🎯 Interview Tip (1 line)
Say: "Every object has an internal [[Prototype]]; lookups walk the chain until null, and classes are sugar over this."

---

## 🔗 Related Questions
→ Q025 (instanceof) | Q111 (implement Object.create) | Q129 (prototype mutation bug) | Q162 (explain prototype)
