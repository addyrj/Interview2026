---

# Q180. Explain typeof vs instanceof
# Category: Tricky Concepts
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What is the difference between `typeof` and `instanceof`? List the quirks and show a reliable way to detect types.

---

## 💡 Quick Concept (2 lines only)
`typeof` returns a string describing a primitive/function type (with quirks like `typeof null === 'object'`). `instanceof` checks whether a constructor's `prototype` appears in the object's prototype chain.
हिंदी: typeof primitive का type string देता है, instanceof देखता है कि object किसी class की chain में है या नहीं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: typeof for primitives and functions
// Step 2: instanceof for objects / class instances
// Step 3: Object.prototype.toString for reliable detection

// typeof results
console.log(typeof 42);                        // number
console.log(typeof 'hi');                      // string
console.log(typeof undefined);                 // undefined
console.log(typeof null);                      // object (historic bug)
console.log(typeof [], typeof {});             // object object
console.log(typeof function () {});            // function
console.log(typeof Symbol(), typeof 10n);      // symbol bigint
console.log(typeof undeclaredVar);             // undefined (no ReferenceError)

// instanceof results
class Animal {}                                // base class
class Dog extends Animal {}                    // derived class
const d = new Dog();                           // instance
console.log(d instanceof Dog);                 // true
console.log(d instanceof Animal);              // true (chain)
console.log(d instanceof Object);              // true
console.log([] instanceof Array);              // true
console.log('str' instanceof String);          // false (primitive)
console.log(new String('s') instanceof String); // true (wrapper object)
console.log(null instanceof Object);           // false

// Reliable detection
const type = v => Object.prototype.toString.call(v).slice(8, -1); // extract tag
console.log(type([]), type(null), type(new Date()), type(/x/)); // Array Null Date RegExp
console.log(Array.isArray([]));                // true

// ============================================
// TEST CASES
// ============================================
// Expected output:
// number
// string
// undefined
// object
// object object
// function
// symbol bigint
// undefined
// true
// true
// true
// true
// false
// true
// false
// Array Null Date RegExp
// true
```

---

## 🔍 Why This Works (3 lines max)
`typeof` reads the internal type tag of a value, while `instanceof` walks the prototype chain looking for `Constructor.prototype`. Primitives have no chain, so `instanceof` is false for them.
हिंदी: typeof value का tag पढ़ता है, instanceof prototype chain में चलकर ढूँढता है; primitives की chain नहीं होती।

---

## ⚡ Alternative Solution
```javascript
// Customise instanceof with Symbol.hasInstance
class Even { static [Symbol.hasInstance](n) { return n % 2 === 0; } } // custom check
console.log(4 instanceof Even, 3 instanceof Even); // Expected: true false
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Using typeof to detect null or arrays
const v = null;
console.log(typeof v === 'object'); // true (but it's null!)

// ✅ Check null explicitly, use Array.isArray
console.log(v !== null && typeof v === 'object'); // false
```

---

## 🎯 Interview Tip (1 line)
Say: "typeof for primitives (beware null and array), instanceof for prototype chain (fails across iframes), Array.isArray and toString for reliability."

---

## 🔗 Related Questions
→ Q025 (instanceof output) | Q026 (typeof tricky) | Q024 (prototype chain) | Q162 (prototype explained)
