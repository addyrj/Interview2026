---

# Q034. [] + {} Output
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```javascript
console.log([] + {});
console.log(typeof ([] + {}));
console.log([] + {} + 1);
console.log([1, 2] + {});
```

---

## 💡 Quick Concept (2 lines only)
`[]` becomes "" and `{}` becomes "[object Object]"; `+` then concatenates the two strings.
हिंदी: [] से "" और {} से "[object Object]" बनता है, दोनों जुड़कर "[object Object]" आता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: [] -> toString -> ""
// Step 2: {} -> toString -> "[object Object]"
// Step 3: "" + "[object Object]" -> "[object Object]"
// Step 4: further + 1 appends "1"

console.log([] + {});            // "" + "[object Object]"
console.log(typeof ([] + {}));   // always a string
console.log([] + {} + 1);        // "[object Object]" + 1 -> "[object Object]1"
console.log([1, 2] + {});        // "1,2" + "[object Object]"

// ============================================
// TEST CASES
// ============================================

console.log(String([] + {}).length); // Expected: 15
console.log({} + {});                // Expected: [object Object][object Object]
console.log([] + {} === '[object Object]'); // Expected: true

// ============================================
// OUTPUT:
// ============================================
// [object Object]
// string
// [object Object]1
// 1,2[object Object]
// 15
// [object Object][object Object]
// true
```

---

## 🔍 Why This Works (3 lines max)
Neither operand is a primitive, so both go through ToPrimitive and become strings. Since the result is a string concatenation, the final type is always "string".
हिंदी: दोनों operands string में बदलते हैं, इसलिए नतीजा हमेशा string होता है।

---

## ⚡ Alternative Solution
```javascript
// Explicit conversions show what happens under the hood
console.log(String([]) + String({}));  // "[object Object]"
console.log([].toString() + ({}).toString()); // "[object Object]"
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: expecting 0 or NaN or an object
// console.log([] + {}) -> people guess 0 or "[object Object]" as an object

// ✅ Correct: it is the STRING "[object Object]"
console.log(typeof ([] + {})); // string
```

---

## 🎯 Interview Tip (1 line)
Say: "Both operands are stringified: empty array gives an empty string and a plain object gives [object Object]."

---

## 🔗 Related Questions
→ Q033 ([] + []) | Q035 ({} + []) | Q032 (object + string)
