---

# Q033. [] + [] Output
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```javascript
console.log([] + []);
console.log(typeof ([] + []));
console.log([1] + [2]);
console.log([] + 1);
```

---

## 💡 Quick Concept (2 lines only)
Arrays are converted to strings via `toString()` (which joins elements), then `+` concatenates the strings. Empty array becomes "".
हिंदी: Array पहले string बनता है (खाली array = ""), फिर दोनों strings जुड़ जाती हैं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: [] -> valueOf returns the array (not primitive)
// Step 2: toString() -> join(',') -> "" for empty array
// Step 3: "" + "" = "" (an empty string)
// Step 4: [1] -> "1", [2] -> "2", so "12"

console.log([] + []);            // "" + "" -> empty string (prints blank line)
console.log(typeof ([] + []));   // result is a string -> "string"
console.log([1] + [2]);          // "1" + "2" -> "12"
console.log([] + 1);             // "" + 1 -> "1"

// ============================================
// TEST CASES
// ============================================

console.log([1, 2] + [3]);       // Expected: 1,23
console.log([] + null);          // Expected: null
console.log(([] + []).length);   // Expected: 0

// ============================================
// OUTPUT:
// ============================================
// (empty line)
// string
// 12
// 1
// 1,23
// null
// 0
```

---

## 🔍 Why This Works (3 lines max)
`+` converts both operands to primitives; arrays yield strings through `Array.prototype.toString`. An empty array joins to "", so the sum is an empty string, not 0 or an array.
हिंदी: + दोनों को primitive में बदलता है; array का toString join करता है, इसलिए नतीजा string आता है।

---

## ⚡ Alternative Solution
```javascript
// Merge arrays properly instead of using +
const a = [1], b = [2];          // two arrays
console.log([...a, ...b]);       // [ 1, 2 ] (spread)
console.log(a.concat(b));        // [ 1, 2 ] (concat)
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: using + to merge arrays
const merged = [1, 2] + [3, 4];
console.log(merged);               // "1,23,4" (a string!)

// ✅ Correct: use concat or spread
console.log([...[1, 2], ...[3, 4]]); // [ 1, 2, 3, 4 ]
```

---

## 🎯 Interview Tip (1 line)
Say: "Arrays stringify through join, so [] + [] is an empty string; to combine arrays I use spread or concat."

---

## 🔗 Related Questions
→ Q032 (object + string) | Q034 ([] + {}) | Q035 ({} + [])
