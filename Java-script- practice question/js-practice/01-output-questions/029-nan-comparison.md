---

# Q029. NaN Comparison Output
# Category: Output Questions
# Difficulty: ⭐ Easy

---

## ❓ Question
What will the following code print?

```javascript
console.log(NaN === NaN);
console.log(NaN == NaN);
console.log(Number.isNaN(NaN));
console.log(isNaN('hello'));
console.log(Number.isNaN('hello'));
```

---

## 💡 Quick Concept (2 lines only)
NaN is the only value not equal to itself. Global `isNaN` coerces to number first; `Number.isNaN` does not.
हिंदी: NaN अपने आप के बराबर भी नहीं होता; Number.isNaN बिना coercion के सही check करता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: NaN === NaN is false (IEEE 754 rule)
// Step 2: NaN == NaN is also false
// Step 3: Number.isNaN(NaN) -> true (strict check)
// Step 4: isNaN('hello') coerces 'hello' to NaN -> true
// Step 5: Number.isNaN('hello') -> false (a string is not NaN)

console.log(NaN === NaN);             // false: NaN never equals itself
console.log(NaN == NaN);              // false: same for loose equality
console.log(Number.isNaN(NaN));       // true: real NaN
console.log(isNaN('hello'));          // true: coerces string to NaN
console.log(Number.isNaN('hello'));   // false: no coercion

// ============================================
// TEST CASES
// ============================================

console.log(Object.is(NaN, NaN));     // Expected: true
console.log([NaN].includes(NaN));     // Expected: true  (SameValueZero)
console.log([NaN].indexOf(NaN));      // Expected: -1    (uses ===)
console.log(0 / 0);                   // Expected: NaN

// ============================================
// OUTPUT:
// ============================================
// false
// false
// true
// true
// false
// true
// true
// -1
// NaN
```

---

## 🔍 Why This Works (3 lines max)
IEEE 754 defines NaN as unordered, so any comparison with it is false. `Object.is` and `includes` use different equality algorithms that treat NaN as equal to NaN.
हिंदी: IEEE rule के कारण NaN कभी equal नहीं होता; Object.is और includes इसे equal मानते हैं।

---

## ⚡ Alternative Solution
```javascript
// Self-inequality trick: only NaN is not equal to itself
const isNaNValue = (v) => v !== v; // true only for NaN
console.log(isNaNValue(NaN));      // true
console.log(isNaNValue(5));        // false
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: comparing with NaN directly
const x = Number('abc');
console.log(x === NaN);        // false (always!)

// ✅ Correct: use Number.isNaN
console.log(Number.isNaN(x));  // true
```

---

## 🎯 Interview Tip (1 line)
Say: "NaN !== NaN, so I use Number.isNaN or Object.is, and avoid global isNaN because it coerces."

---

## 🔗 Related Questions
→ Q028 (null == undefined) | Q030 (type coercion) | Q047 (Set output)
