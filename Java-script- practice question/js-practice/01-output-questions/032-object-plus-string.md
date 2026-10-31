---

# Q032. Object + String Output
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```javascript
const obj = { a: 1 };
console.log(obj + 'x');
console.log(`${obj}`);
console.log([1, 2] + 'x');
console.log({ toString() { return 'custom'; } } + '!');
```

---

## 💡 Quick Concept (2 lines only)
When an object meets `+` with a string, JS converts it to a primitive via `valueOf()` then `toString()`. Plain objects become "[object Object]".
हिंदी: object + string में object पहले primitive बनता है; साधारण object का रूप "[object Object]" होता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: ToPrimitive calls valueOf() -> returns object itself (not primitive)
// Step 2: Falls back to toString() -> "[object Object]"
// Step 3: Arrays override toString() -> join(',') -> "1,2"
// Step 4: Custom toString is used when defined

const obj = { a: 1 };                                  // plain object
console.log(obj + 'x');                                // "[object Object]x"
console.log(`${obj}`);                                 // template literal uses toString
console.log([1, 2] + 'x');                             // "1,2x"
console.log({ toString() { return 'custom'; } } + '!'); // "custom!"

// ============================================
// TEST CASES
// ============================================

const money = { valueOf() { return 100; }, toString() { return 'rupees'; } }; // both defined
console.log(money + 1);        // Expected: 101     (valueOf wins for +)
console.log(`${money}`);       // Expected: rupees  (template prefers toString)
console.log(String(money));    // Expected: rupees

// ============================================
// OUTPUT:
// ============================================
// [object Object]x
// [object Object]
// 1,2x
// custom!
// 101
// rupees
// rupees
```

---

## 🔍 Why This Works (3 lines max)
ToPrimitive tries `valueOf` first (for the default hint) and `toString` second. Template literals and `String()` use the string hint, so `toString` runs first.
हिंदी: + में पहले valueOf चलता है, जबकि template literal और String() में पहले toString चलता है।

---

## ⚡ Alternative Solution
```javascript
// Control conversion fully with Symbol.toPrimitive
const temp = {
  [Symbol.toPrimitive](hint) {          // hint: 'number' | 'string' | 'default'
    return hint === 'number' ? 36 : '36C'; // choose based on hint
  }
};
console.log(+temp);       // 36
console.log(`${temp}`);   // 36C
console.log(temp + '');   // 36C
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: logging objects via string concatenation
const user = { name: 'Aditya' };
console.log('User: ' + user);        // User: [object Object]

// ✅ Correct: stringify or log separately
console.log('User: ' + JSON.stringify(user)); // User: {"name":"Aditya"}
```

---

## 🎯 Interview Tip (1 line)
Say: "Objects go through ToPrimitive: valueOf then toString for +, toString first for strings, and Symbol.toPrimitive overrides both."

---

## 🔗 Related Questions
→ Q031 (string + number) | Q033 ([] + []) | Q034 ([] + {})
