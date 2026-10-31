---

# Q035. {} + [] Output
# Category: Output Questions
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
What will the following code print? (Think about expression vs statement position.)

```javascript
console.log({} + []);
console.log(({}) + []);
const x = {} + [];
console.log(x);
console.log(eval('{} + []'));
```

---

## 💡 Quick Concept (2 lines only)
In expression position, `{}` is an object so the result is "[object Object]". At the start of a statement (like REPL), `{}` is an empty block and `+[]` becomes 0.
हिंदी: Expression में {} object है ("[object Object]"), पर statement की शुरुआत में {} खाली block बन जाता है और +[] = 0।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: inside console.log(...) {} is an object literal (expression)
// Step 2: {} -> "[object Object]", [] -> "" -> concatenated
// Step 3: eval('{} + []') parses {} as a block, leaving +[] -> 0

console.log({} + []);            // expression -> "[object Object]"
console.log(({}) + []);          // parentheses force expression -> same
const x = {} + [];               // right side of = is an expression
console.log(x);                  // "[object Object]"
console.log(eval('{} + []'));    // statement start: block + (+[]) -> 0

// ============================================
// TEST CASES
// ============================================

console.log(+[]);                // Expected: 0   (unary plus: "" -> 0)
console.log(typeof ({} + []));   // Expected: string
console.log(eval('({}) + []'));  // Expected: [object Object]

// ============================================
// OUTPUT:
// ============================================
// [object Object]
// [object Object]
// [object Object]
// 0
// 0
// string
// [object Object]
```

---

## 🔍 Why This Works (3 lines max)
The parser decides by position: at statement start `{` opens a block, elsewhere it starts an object literal. Unary `+[]` converts "" to 0, which is why the REPL shows 0.
हिंदी: Parser position देखता है; statement की शुरुआत में { block होता है, इसलिए REPL में 0 दिखता है।

---

## ⚡ Alternative Solution
```javascript
// Wrap in parentheses to avoid ambiguity everywhere
const result = ({}) + [];        // always object + array
console.log(result);             // [object Object]
console.log(String({}) + String([])); // same, explicit
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: believing {} + [] is always 0
// (true only in a REPL/statement start)

// ✅ Correct: inside console.log or assignment it is a string
console.log({} + []); // [object Object]
```

---

## 🎯 Interview Tip (1 line)
Say: "It depends on parsing context: statement-start braces are a block (result 0), expression braces are an object (result [object Object])."

---

## 🔗 Related Questions
→ Q033 ([] + []) | Q034 ([] + {}) | Q032 (object + string)
