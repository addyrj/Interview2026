---

# Q026. typeof Output (Tricky)
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```javascript
console.log(typeof null);
console.log(typeof NaN);
console.log(typeof []);
console.log(typeof function () {});
console.log(typeof undeclaredVar);
```

---

## 💡 Quick Concept (2 lines only)
`typeof` returns a string; it has historic quirks (`null` is "object", arrays are "object") and never throws for undeclared variables.
हिंदी: typeof हमेशा string देता है; null और array दोनों "object" निकलते हैं और undeclared variable पर error नहीं आता।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: typeof null is a legacy bug -> "object"
// Step 2: NaN is a special Number value -> "number"
// Step 3: arrays are objects; functions get their own "function" label
// Step 4: typeof on an undeclared variable is safe -> "undefined"

console.log(typeof null);            // null is a known JS bug, reports "object"
console.log(typeof NaN);             // NaN is of Number type
console.log(typeof []);              // arrays are objects
console.log(typeof function () {});  // functions are callable objects, label "function"
console.log(typeof undeclaredVar);   // no ReferenceError with typeof

// ============================================
// TEST CASES
// ============================================

console.log(typeof typeof 1);        // Expected: string   (typeof returns a string)
console.log(typeof 10n);             // Expected: bigint
console.log(typeof Symbol());        // Expected: symbol
console.log(typeof new String('a')); // Expected: object   (wrapper object, not primitive)

// ============================================
// OUTPUT:
// ============================================
// object
// number
// object
// function
// undefined
// string
// bigint
// symbol
// object
```

---

## 🔍 Why This Works (3 lines max)
`typeof null` returns "object" because of an original JS implementation bug that was never fixed. Arrays have no special label, so use `Array.isArray`. `typeof` is the only operator that does not throw on undeclared names.
हिंदी: null का "object" एक पुराना bug है, array check के लिए Array.isArray use करो।

---

## ⚡ Alternative Solution
```javascript
// Reliable type check using Object.prototype.toString
const typeOf = (v) => Object.prototype.toString.call(v).slice(8, -1).toLowerCase(); // extract type name
console.log(typeOf(null));  // null
console.log(typeOf([]));    // array
console.log(typeOf(new Date())); // date
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: checking object with typeof only
const val = null;
console.log(typeof val === 'object'); // true (but null is not an object!)

// ✅ Correct: exclude null explicitly
console.log(typeof val === 'object' && val !== null); // false
```

---

## 🎯 Interview Tip (1 line)
Say: "typeof null is 'object' due to a legacy bug, so I check null separately and use Array.isArray for arrays."

---

## 🔗 Related Questions
→ Q025 (instanceof) | Q028 (null == undefined) | Q180 (typeof vs instanceof)
