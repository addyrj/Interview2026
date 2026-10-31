---

# Q126. Fix Infinite Loop Bug
# Category: Fix the Bug
# Difficulty: ⭐ Easy

---

## ❓ Question
This function should sum numbers from 1 to n but never finishes. Fix it.

```javascript
// BUGGY CODE:
function sumTo(n) {
  let sum = 0;
  let i = 1;
  while (i <= n) {
    sum += i;
    // i is never updated
  }
  return sum;
}
```

---

## 💡 Quick Concept (2 lines only)
A loop ends only when its condition becomes false. If the variable in the condition never changes, the loop runs forever.
हिंदी: loop की condition वाला variable बदलना ज़रूरी है, वरना loop कभी खत्म नहीं होता।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

function sumTo(n) {
  let sum = 0;            // Step 1: accumulator
  let i = 1;              // Step 2: counter
  while (i <= n) {        // Step 3: loop while counter within limit
    sum += i;             // add current number
    i++;                  // FIX: move toward the exit condition
  }
  return sum;             // Step 4: return total
}

// ============================================
// TEST CASES
// ============================================

console.log(sumTo(5));    // Expected: 15
console.log(sumTo(1));    // Expected: 1
console.log(sumTo(0));    // Expected: 0
```

---

## 🔍 Why This Works (3 lines max)
Incrementing `i` each pass guarantees `i <= n` eventually becomes false. Always check that every loop iteration moves closer to termination.
हिंदी: `i++` से हर बार loop exit के पास पहुँचता है और अंत में रुक जाता है।

---

## ⚡ Alternative Solution
```javascript
// for loop keeps the update in the header (harder to forget)
function sumTo2(n) {
  let sum = 0;
  for (let i = 1; i <= n; i++) sum += i; // update is built in
  return sum;
}
console.log(sumTo2(5)); // 15
// Or formula: n * (n + 1) / 2
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: update moves away from the limit
// for (let i = 0; i < 5; i--) { }   // i goes negative forever
// ✅ Correct
for (let i = 0; i < 5; i++) {}
```

---

## 🎯 Interview Tip (1 line)
Say: "I check initial value, condition, and update direction — and add a guard for bad input like NaN."

---

## 🔗 Related Questions
→ Q103 (binary search) | Q104 (bubble sort) | Q153 (complete binary search)
