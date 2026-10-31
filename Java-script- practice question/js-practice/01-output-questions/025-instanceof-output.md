---

# Q025. instanceof Output
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```javascript
class A {}
class B extends A {}
const b = new B();
console.log(b instanceof B, b instanceof A, b instanceof Object);
console.log('str' instanceof String, new String('s') instanceof String);
console.log(Object.create(null) instanceof Object);
```

---

## 💡 Quick Concept (2 lines only)
`x instanceof C` is true if `C.prototype` appears anywhere in x's prototype chain; primitives are never instances.
हिंदी: x instanceof C तब true है जब C.prototype, x की prototype chain में कहीं भी हो; primitives कभी instance नहीं होते।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: chain of b: B.prototype -> A.prototype -> Object.prototype
// Step 2: primitive 'str' has no chain -> false; wrapper object -> true
// Step 3: Object.create(null) has no chain at all -> false

class A {}                                         // base class
class B extends A {}                               // child class
const b = new B();                                 // instance

// ============================================
// TEST CASES
// ============================================

console.log(b instanceof B, b instanceof A, b instanceof Object); // Expected: true true true
console.log('str' instanceof String);              // Expected: false
console.log(new String('s') instanceof String);    // Expected: true
console.log(Object.create(null) instanceof Object); // Expected: false
console.log([] instanceof Array, [] instanceof Object); // Expected: true true
```

---

## 🔍 Why This Works (3 lines max)
instanceof walks the left side's prototype chain looking for the right side's `.prototype`. A null-prototype object has no chain, and primitives are not objects.
हिंदी: instanceof chain में ढूँढता है; null-prototype object या primitive के पास chain नहीं होती, इसलिए false।

---

## ⚡ Alternative Solution
```javascript
// Safer type checks
console.log(typeof 'str');                         // Expected: string
console.log(Array.isArray([]));                    // Expected: true
console.log(Object.prototype.toString.call(null)); // Expected: [object Null]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ if (value instanceof Array) across iframes/realms -> can be false
// ✅ Array.isArray(value) works everywhere
```

---

## 🎯 Interview Tip (1 line)
Say: "instanceof checks the prototype chain, fails for primitives and across realms; use Array.isArray / typeof where suitable."

---

## 🔗 Related Questions
→ Q024 (prototype chain) | Q026 (typeof tricky) | Q162 (explain prototype) | Q180 (typeof vs instanceof)
