# 14. break + continue
# हिंदी में: break और continue — Loop Control Keywords

---

## 🔵 Simple Definition (English)
`break` **exits** the loop immediately. `continue` **skips** the current iteration and moves to the next. Both only affect the **innermost** loop (unless used with labels).

## 🔵 सरल परिभाषा (Hindi)
`break` loop को तुरंत बंद करता है। `continue` current iteration skip करके अगले पर चला जाता है। दोनों सिर्फ सबसे अंदर वाले loop को affect करते हैं (labels के बिना)।

---

## 🔴 Problem it Solves
Without `break`: you'd have to loop through everything even after finding what you need — wasteful.
Without `continue`: you'd need extra nesting to skip items — messier code.

---

## 🟢 How it Works

```
break:
  for (let i = 0; i < 10; i++) {
    if (i === 5) break;   ← exits loop when i = 5
    console.log(i);        → prints 0, 1, 2, 3, 4
  }
  // code here runs after break

continue:
  for (let i = 0; i < 10; i++) {
    if (i % 2 === 0) continue;  ← skip even numbers
    console.log(i);               → prints 1, 3, 5, 7, 9
  }
```

---

## 🟡 Real World Example
```javascript
// Search: stop when found
const users = [
  { id: 1, name: "Aditya" },
  { id: 2, name: "Rajan" },
  { id: 3, name: "Kumar" },
];

let found = null;
for (const user of users) {
  if (user.id === 2) {
    found = user;
    break; // no need to check remaining users
  }
}

// Filter: skip invalid items
const orders = [
  { id: 1, status: "valid", amount: 299 },
  { id: 2, status: "cancelled", amount: 0 },
  { id: 3, status: "valid", amount: 599 },
];

let revenue = 0;
for (const order of orders) {
  if (order.status === "cancelled") continue; // skip cancelled
  revenue += order.amount;
}
console.log(revenue); // 898
```

---

## 💻 Code Example — Basic
```javascript
// ── BREAK ────────────────────────────
// Find first number divisible by 7
for (let i = 1; i <= 100; i++) {
  if (i % 7 === 0) {
    console.log(`First multiple of 7: ${i}`); // 7
    break; // stop searching
  }
}

// Break in while:
let input = "";
while (true) {               // infinite loop
  input = getNextInput();    // imaginary function
  if (input === "quit") break; // exit on "quit"
  processInput(input);
}

// ── CONTINUE ─────────────────────────
// Print only odd numbers
for (let i = 1; i <= 10; i++) {
  if (i % 2 === 0) continue; // skip even
  console.log(i); // 1, 3, 5, 7, 9
}

// Skip null/undefined in array
const data = [1, null, 3, undefined, 5, null, 7];
const clean = [];
for (const val of data) {
  if (val == null) continue; // skip null AND undefined
  clean.push(val);
}
console.log(clean); // [1, 3, 5, 7]
```

## 💻 Code Example — Advanced
```javascript
// ── BREAK IN NESTED LOOPS ─────────────
// Find position of value in 2D array
const matrix = [
  [1, 2, 3],
  [4, 5, 6],
  [7, 8, 9],
];
const target = 5;
let foundRow = -1, foundCol = -1;

outer:                             // label the outer loop
for (let row = 0; row < matrix.length; row++) {
  for (let col = 0; col < matrix[row].length; col++) {
    if (matrix[row][col] === target) {
      foundRow = row;
      foundCol = col;
      break outer; // breaks OUTER loop, not just inner
    }
  }
}
console.log(`Found at [${foundRow}][${foundCol}]`); // [1][1]

// Without label (less clean):
let found = false;
for (let row = 0; row < matrix.length && !found; row++) {
  for (let col = 0; col < matrix[row].length; col++) {
    if (matrix[row][col] === target) {
      foundRow = row;
      foundCol = col;
      found = true;
      break;
    }
  }
}

// ── BREAK IN SWITCH INSIDE LOOP ──────
// switch break only exits switch, not the loop!
for (const item of items) {
  switch (item.type) {
    case "stop":
      console.log("Found stop signal");
      break; // breaks switch ONLY, loop continues!
    case "skip":
      continue; // WAIT — this is actually OUTSIDE switch, works on loop!
  }
  processItem(item);
}
// Note: continue works on the loop when inside a switch that's inside a loop

// ── USING ARRAY METHODS vs break/continue ──

// break equivalent: Array.find(), Array.findIndex()
const firstEven = numbers.find(n => n % 2 === 0); // stops at first match

// continue equivalent: Array.filter()
const onlyValid = items.filter(item => item.status !== "cancelled");

// break equivalent in every/some:
const hasInvalid = items.some(item => item.price < 0); // stops at first true
const allValid = items.every(item => item.price > 0);  // stops at first false
```

---

## 🟠 React/Next.js Connection
```jsx
// In React, use array methods instead of loops (more functional)
// But in data processing hooks, break/continue matter:

function useDataProcessor(rawData) {
  const processed = useMemo(() => {
    const result = [];

    for (const item of rawData) {
      // continue — skip invalid
      if (!item.id || !item.name) continue;

      // break — stop after 50 items (virtual list)
      if (result.length >= 50) break;

      result.push(transformItem(item));
    }

    return result;
  }, [rawData]);

  return processed;
}

// API route: process until error
export async function POST(req) {
  const items = await req.json();
  const results = [];

  for (const item of items) {
    if (!isValid(item)) continue; // skip invalid

    try {
      const result = await processItem(item);
      results.push(result);
    } catch (error) {
      if (error.isFatal) break; // stop everything on fatal error
      results.push({ id: item.id, error: error.message });
    }
  }

  return Response.json({ results });
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** `break` inside `switch` inside a loop (only breaks switch)
```javascript
for (const item of items) {
  switch (item.status) {
    case "done":
      break; // breaks switch ONLY — loop continues!
  }
  console.log("Still running"); // this still runs for "done" items
}

// CORRECT: use a flag or restructure
for (const item of items) {
  if (item.status === "done") break; // breaks the for loop
}
```

❌ **Mistake 2:** Modifying array while iterating
```javascript
const arr = [1, 2, 3, 4, 5];

// WRONG: modifying arr while looping over it
for (let i = 0; i < arr.length; i++) {
  if (arr[i] % 2 === 0) arr.splice(i, 1); // changes indices!
}

// CORRECT: iterate over copy, or use filter
const odds = arr.filter(n => n % 2 !== 0);
```

❌ **Mistake 3:** Forgetting `break` in `switch` within a loop causes fall-through
```javascript
// Already covered in topic 11 — but worth repeating:
// Always add break to switch cases to prevent accidental fall-through
```

---

## 🧠 Tricky Interview Output Question
```javascript
outer: for (let i = 0; i < 3; i++) {
  for (let j = 0; j < 3; j++) {
    if (j === 1) continue outer; // ← what does this do?
    console.log(`${i},${j}`);
  }
}
```
**Answer:**
```
0,0
1,0
2,0
```
**Why:** `continue outer` skips to the next iteration of the **outer** loop (incrementing `i`), not the inner. So when `j === 1`, we jump to `i+1` — `j` never reaches 2.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between break and continue?**
A1: `break` exits the loop entirely — no more iterations run. `continue` skips the rest of the current iteration and moves to the next one (the loop itself keeps going). `break` is for "found what I need, stop." `continue` is for "this item doesn't qualify, skip it."

**Q2: Can you use break/continue with forEach?**
A2: No. `break` and `continue` only work in `for`, `while`, `do-while`, `for-in`, and `for-of` loops. Inside `forEach`, using `break` throws a SyntaxError. Use `for-of` if you need `break`. Use `Array.some()` as a `break` equivalent (returns true to stop), or `Array.every()` (returns false to stop).

**Q3: What are labeled loops and when do you use them?**
A3: A label is an identifier before a loop (`outer: for...`). `break label` exits to the labeled loop, and `continue label` skips to the next iteration of the labeled loop. They're used in nested loops when you need to break out of or skip to the outer loop. Rarely needed — often indicates the code could be restructured.

**Q4: What happens when you use break inside a switch that's inside a for loop?**
A4: The `break` only exits the `switch`, not the `for` loop. The for loop continues. To exit the for loop from inside a switch, use a labeled `break` (`break outerLoop`) or restructure to use `if` instead of `switch`.

**Q5: What is the functional equivalent of break and continue?**
A5: `Array.find()` or `Array.findIndex()` stop at the first match (like break). `Array.some()` stops at first true. `Array.every()` stops at first false. `Array.filter()` is the functional equivalent of continue — keeping only items that pass the condition. These are preferred in functional programming style.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| break | Exit loop immediately | Loop तुरंत बंद करना |
| continue | Skip current iteration | Current iteration skip |
| Label | Name for a loop (`outer:`) | Loop का नाम |
| Labeled break | Exit a specific outer loop | Specific loop से exit |
| Labeled continue | Skip to specific outer loop's next | Specific outer loop का next iteration |
| fall-through | Switch case without break | Switch में break नहीं |

---

## ⚡ 3-Line Summary
**English:**
1. `break` exits the loop immediately; `continue` skips the current iteration and moves to the next.
2. Both only affect the innermost loop — use labels (`outer: for`) to break/continue from nested loops.
3. Prefer functional alternatives: `find()`, `some()`, `filter()` instead of break/continue for cleaner code.

**Hindi:**
1. `break` loop तुरंत बंद करता है; `continue` current iteration skip करके अगले पर जाता है।
2. दोनों सिर्फ innermost loop को affect करते हैं — nested loops के लिए labels use करो।
3. Clean code के लिए `find()`, `some()`, `filter()` prefer करो।

---

## ➡️ Next Topic
**15. Functions — Declaration vs Expression** — Function declaration, function expression, और इनके बीच के important differences जैसे hoisting।
