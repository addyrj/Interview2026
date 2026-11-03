---

# D151. Asteroid Collision
# Category: DSA — Stack & Queue
# Difficulty: ⭐⭐ Medium | LeetCode #735 | Asked: Amazon, Google, Microsoft, Uber

---

## ❓ Problem
Each integer is an asteroid: absolute value = size, sign = direction (positive right, negative left). All move at the same speed. When two meet, the smaller explodes; equal sizes both explode. Return the state after all collisions.

```
Input:  [5,10,-5]
Output: [5,10]
```

---

## 💡 Quick Concept (2 lines only)
Use a stack. A collision happens only when the stack top moves right (positive) and the incoming asteroid moves left (negative). Pop smaller tops while the incoming one wins.
हिंदी: Top positive और नया negative हो तभी टकराव — छोटा वाला हटता है, बराबर हों तो दोनों।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Brute force — simulate rounds until nothing collides, O(n^2)
// ============================================

function asteroidCollisionBrute(arr) {
  let a = [...arr];                                  // working copy
  let changed = true;
  while (changed) {
    changed = false;
    for (let i = 0; i < a.length - 1; i++) {
      if (a[i] > 0 && a[i + 1] < 0) {                // right-mover meets left-mover
        const x = a[i], y = -a[i + 1];
        if (x > y) a.splice(i + 1, 1);               // right one survives
        else if (x < y) a.splice(i, 1);              // left one survives
        else a.splice(i, 2);                         // both explode
        changed = true;
        break;                                       // restart scan
      }
    }
  }
  return a;
}

// ============================================
// APPROACH 2: Stack — O(n) time, O(n) space ✅ PREFERRED
// ============================================

function asteroidCollision(asteroids) {
  const stack = [];                                  // survivors so far

  for (const ast of asteroids) {
    let alive = true;                                // does `ast` survive?
    // collision only if top goes right and ast goes left
    while (alive && ast < 0 && stack.length && stack[stack.length - 1] > 0) {
      const top = stack[stack.length - 1];
      if (top < -ast) {
        stack.pop();                                 // top is smaller -> explodes, keep checking
      } else if (top === -ast) {
        stack.pop();                                 // both explode
        alive = false;
      } else {
        alive = false;                               // ast is smaller -> explodes
      }
    }
    if (alive) stack.push(ast);                      // survivor joins the stack
  }
  return stack;
}

// ============================================
// TEST CASES
// ============================================

console.log(asteroidCollision([5,10,-5]));           // [5,10]
console.log(asteroidCollision([8,-8]));              // []
console.log(asteroidCollision([10,2,-5]));           // [10]
console.log(asteroidCollision([-2,-1,1,2]));         // [-2,-1,1,2]
console.log(asteroidCollision([1,-2,-2,-2]));        // [-2,-2,-2]
console.log(asteroidCollisionBrute([10,2,-5]));      // [10]
```

---

## 🔍 Why It Works
```
[10,2,-5]
10  push      [10]
2   push      [10,2]
-5  top 2 < 5 pop  [10]
    top 10 > 5 -> -5 explodes
result [10]
```
हिंदी: Negative के बाएँ तरफ सिर्फ positive top से ही टकराव हो सकता है, बाकी सब safe हैं।

---

## 📊 Complexity
```
Brute force: Time O(n^2) | Space O(n)
Stack:       Time O(n)   | Space O(n)
```

---

## ⚡ Variations
```
- Return number of surviving asteroids
- Different speeds -> needs event simulation (heap by collision time)
- Car Fleet (#853) — similar monotonic stack idea
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: colliding when top is negative and ast is positive (they move apart!)
// ❌ Wrong: not looping — one incoming asteroid may destroy many on the stack
// ❌ Wrong: forgetting equal sizes remove both
```

---

## 🎯 Interview Tip
Say: "Collision only for (positive top, negative incoming). I loop while the incoming one keeps winning." State the three outcomes explicitly.

---

## 🔗 Related Problems
→ D143 (Daily Temperatures) | D149 (Remove Adjacent Duplicates) | D010 (Valid Parentheses)
