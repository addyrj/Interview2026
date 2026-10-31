---

# Q045. Symbol Output
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```javascript
const s1 = Symbol('id');
const s2 = Symbol('id');
const obj = { [s1]: 1, name: 'A' };
console.log(s1 === s2);
console.log(Object.keys(obj));
console.log(JSON.stringify(obj));
console.log(Symbol.for('k') === Symbol.for('k'));
```

---

## 💡 Quick Concept (2 lines only)
Every `Symbol()` is unique, even with the same description. Symbol keys are hidden from `Object.keys`, `for...in` and JSON.
हिंदी: हर Symbol() अनोखा होता है और Symbol keys, Object.keys व JSON में नहीं दिखतीं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: two Symbol('id') calls make two different symbols -> false
// Step 2: Object.keys ignores symbol keys -> ['name']
// Step 3: JSON.stringify skips symbol keys
// Step 4: Symbol.for uses a global registry -> same symbol -> true

const s1 = Symbol('id');                       // unique symbol
const s2 = Symbol('id');                       // another unique symbol
const obj = { [s1]: 1, name: 'A' };            // symbol as computed key
console.log(s1 === s2);                        // false
console.log(Object.keys(obj));                 // [ 'name' ]
console.log(JSON.stringify(obj));              // {"name":"A"}
console.log(Symbol.for('k') === Symbol.for('k')); // true (global registry)

// ============================================
// TEST CASES
// ============================================

console.log(Object.getOwnPropertySymbols(obj).length); // Expected: 1
console.log(obj[s1]);                                  // Expected: 1
console.log(s1.toString());                            // Expected: Symbol(id)
console.log(s1.description);                           // Expected: id
try {
  console.log(s1 + '');                                // implicit string conversion
} catch (e) {
  console.log(e.name);                                 // Expected: TypeError
}

// ============================================
// OUTPUT:
// ============================================
// false
// [ 'name' ]
// {"name":"A"}
// true
// 1
// 1
// Symbol(id)
// id
// TypeError
```

---

## 🔍 Why This Works (3 lines max)
Symbols are unique primitives whose description is only a label. Because they are skipped by normal enumeration, they suit hidden or collision-free property keys. `Symbol.for` shares symbols through a registry.
हिंदी: Symbol unique primitive है; enumeration में नहीं आता, इसलिए hidden keys के लिए सही है।

---

## ⚡ Alternative Solution
```javascript
// Well-known symbol: make an object iterable
const range = {
  *[Symbol.iterator]() { yield 1; yield 2; } // custom iteration
};
console.log([...range]); // [ 1, 2 ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: using Symbol() twice expecting the same key
const a = { [Symbol('x')]: 1 };
console.log(a[Symbol('x')]);   // undefined

// ✅ Correct: use Symbol.for or keep a reference
const k = Symbol.for('x');
const b = { [k]: 1 };
console.log(b[Symbol.for('x')]); // 1
```

---

## 🎯 Interview Tip (1 line)
Say: "Symbols are unique, non-enumerable keys useful to avoid property collisions and to hook into protocols like Symbol.iterator."

---

## 🔗 Related Questions
→ Q044 (generator) | Q171 (Symbol use case) | Q248 (Symbol use cases)
