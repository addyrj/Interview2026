---

# Q041. Rest Parameter Output
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```javascript
function sum(first, ...rest) {
  console.log(first, rest, rest.length);
}
sum(1, 2, 3, 4);
sum(1);
sum();
```

---

## 💡 Quick Concept (2 lines only)
Rest (`...name`) gathers the remaining arguments into a real array; it must be the last parameter. With no extra args it is an empty array.
हिंदी: Rest बचे हुए सारे arguments को एक असली array में जमा करता है और हमेशा आखिरी parameter होता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: first takes the first argument
// Step 2: ...rest collects everything after it into an array
// Step 3: if nothing remains, rest is [] (never undefined)

function sum(first, ...rest) {              // rest must be last
  console.log(first, rest, rest.length);    // show all three
}
sum(1, 2, 3, 4);  // 1 [ 2, 3, 4 ] 3
sum(1);           // 1 [] 0
sum();            // undefined [] 0

// ============================================
// TEST CASES
// ============================================

const total = (...nums) => nums.reduce((a, b) => a + b, 0); // sum any count
console.log(total(1, 2, 3));            // Expected: 6
console.log(total());                   // Expected: 0
console.log(sum.length);                // Expected: 1 (rest is not counted)
const [head, ...tail] = [10, 20, 30];   // rest in destructuring
console.log(head, tail);                // Expected: 10 [ 20, 30 ]

// ============================================
// OUTPUT:
// ============================================
// 1 [ 2, 3, 4 ] 3
// 1 [] 0
// undefined [] 0
// 6
// 0
// 1
// 10 [ 20, 30 ]
```

---

## 🔍 Why This Works (3 lines max)
Rest builds a genuine Array, so map/reduce work directly, unlike the old `arguments` object. It does not count toward `function.length`.
हिंदी: Rest असली Array देता है, इसलिए map/reduce सीधे चलते हैं, जो arguments object में नहीं होता।

---

## ⚡ Alternative Solution
```javascript
// Old way: arguments object (array-like, not a real array)
function oldSum() {
  const args = Array.from(arguments);       // convert to array
  return args.reduce((a, b) => a + b, 0);   // add all
}
console.log(oldSum(1, 2, 3)); // 6
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: rest not last -> SyntaxError
// function bad(...rest, last) {}

// ✅ Correct: rest always at the end
function good(first, ...rest) { return rest; } // valid
console.log(good(1, 2, 3)); // [ 2, 3 ]
```

---

## 🎯 Interview Tip (1 line)
Say: "Rest collects arguments into a real array and must be last; spread does the opposite by expanding."

---

## 🔗 Related Questions
→ Q040 (spread) | Q042 (destructuring) | Q179 (spread vs rest)
