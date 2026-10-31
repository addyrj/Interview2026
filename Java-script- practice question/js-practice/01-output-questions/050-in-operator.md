---

# Q050. in Operator Output
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```javascript
const obj = { a: undefined };
console.log('a' in obj);
console.log('toString' in obj);
console.log(obj.hasOwnProperty('toString'));
console.log(2 in [10, 20, 30]);
console.log('length' in []);
```

---

## 💡 Quick Concept (2 lines only)
`in` checks whether a key exists on the object or anywhere in its prototype chain, even if the value is undefined. For arrays it checks indexes, not values.
हिंदी: in operator key की मौजूदगी (prototype chain समेत) देखता है, value की नहीं; array में यह index देखता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: 'a' exists (value undefined doesn't matter) -> true
// Step 2: 'toString' is inherited from Object.prototype -> true
// Step 3: hasOwnProperty only checks own keys -> false
// Step 4: index 2 exists in a 3-item array -> true
// Step 5: arrays have an own 'length' property -> true

const obj = { a: undefined };                  // key exists, value undefined
console.log('a' in obj);                       // true
console.log('toString' in obj);                // true (inherited)
console.log(obj.hasOwnProperty('toString'));   // false (not own)
console.log(2 in [10, 20, 30]);                // true (index 2)
console.log('length' in []);                   // true

// ============================================
// TEST CASES
// ============================================

console.log(10 in [10, 20, 30]);               // Expected: false (checks index, not value)
console.log(Object.hasOwn(obj, 'a'));          // Expected: true
console.log('b' in obj, obj.b !== undefined);  // Expected: false false
const holes = [1, , 3];                        // sparse array
console.log(1 in holes);                       // Expected: false (hole)
try {
  console.log('x' in 'text');                  // right side must be an object
} catch (e) {
  console.log(e.name);                         // Expected: TypeError
}

// ============================================
// OUTPUT:
// ============================================
// true
// true
// false
// true
// true
// false
// true
// false false
// false
// TypeError
```

---

## 🔍 Why This Works (3 lines max)
`in` walks the prototype chain and tests key existence, not value. `hasOwnProperty` / `Object.hasOwn` restrict the check to own properties. Right operand must be an object.
हिंदी: in prototype chain में key खोजता है; सिर्फ अपनी property के लिए Object.hasOwn use करो।

---

## ⚡ Alternative Solution
```javascript
// Modern own-property check (safer than obj.hasOwnProperty)
const o = Object.create({ inherited: 1 }); // prototype has 'inherited'
o.own = 2;                                 // own property
console.log(Object.hasOwn(o, 'own'));       // true
console.log(Object.hasOwn(o, 'inherited')); // false
console.log('inherited' in o);              // true
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: checking existence by truthiness
const cfg = { debug: false };
if (cfg.debug) console.log('exists');   // not printed, though key exists

// ✅ Correct: use `in` or Object.hasOwn
console.log('debug' in cfg);            // true
```

---

## 🎯 Interview Tip (1 line)
Say: "`in` includes inherited keys while Object.hasOwn is own-only; neither cares whether the value is undefined."

---

## 🔗 Related Questions
→ Q049 (delete operator) | Q024 (prototype chain) | Q039 (optional chaining)
