---

# Q031. String + Number Output
# Category: Output Questions
# Difficulty: ⭐ Easy

---

## ❓ Question
What will the following code print?

```javascript
console.log('5' + 3);
console.log('5' - 3);
console.log(1 + 2 + '3');
console.log('1' + 2 + 3);
console.log('5' * '2');
```

---

## 💡 Quick Concept (2 lines only)
`+` concatenates if either side is a string; `-`, `*`, `/` always convert operands to numbers. Evaluation is left to right.
हिंदी: + में string हो तो जुड़ता है, जबकि - * / हमेशा number में बदलकर गणना करते हैं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: '5' + 3 -> string involved, concatenate -> '53'
// Step 2: '5' - 3 -> minus forces numbers -> 2
// Step 3: 1 + 2 + '3' -> (1+2)=3 first, then '3'+'3' -> '33'
// Step 4: '1' + 2 + 3 -> '12' then '123'
// Step 5: '5' * '2' -> both converted -> 10

console.log('5' + 3);        // concatenation -> "53"
console.log('5' - 3);        // numeric subtraction -> 2
console.log(1 + 2 + '3');    // left to right: 3 + '3' -> "33"
console.log('1' + 2 + 3);    // left to right: '12' + 3 -> "123"
console.log('5' * '2');      // numeric multiplication -> 10

// ============================================
// TEST CASES
// ============================================

console.log(+'5' + 3);       // Expected: 8   (unary + converts to number)
console.log('5' + - '2');    // Expected: 5-2  (unary minus makes -2, then concat)
console.log('b' + 'a' + +'a' + 'a'); // Expected: baNaNa

// ============================================
// OUTPUT:
// ============================================
// 53
// 2
// 33
// 123
// 10
// 8
// 5-2
// baNaNa
```

---

## 🔍 Why This Works (3 lines max)
The `+` operator calls ToPrimitive and, if any operand is a string, does string concatenation. Other arithmetic operators always use ToNumber. Order of evaluation matters: `1 + 2 + '3'` adds first.
हिंदी: + पर string दिखे तो concat, बाकी operators number बनाते हैं और गणना बाएँ से दाएँ होती है।

---

## ⚡ Alternative Solution
```javascript
// Avoid surprises with explicit conversion
const a = '5';                 // string input (e.g. from a form)
console.log(Number(a) + 3);    // 8  (explicit conversion)
console.log(parseInt(a, 10) + 3); // 8 (parse with radix)
console.log(`${a}${3}`);       // "53" (explicit concatenation)
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: adding input values directly
const price = '10';             // from input field
console.log(price + 5);         // "105"

// ✅ Correct: convert first
console.log(Number(price) + 5); // 15
```

---

## 🎯 Interview Tip (1 line)
Say: "+ prefers strings, other math operators prefer numbers; I always convert explicitly with Number()."

---

## 🔗 Related Questions
→ Q030 (type coercion) | Q032 (object + string) | Q033 ([] + [])
