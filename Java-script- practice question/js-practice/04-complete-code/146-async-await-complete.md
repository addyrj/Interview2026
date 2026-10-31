---

# Q146. Complete Async/Await Function
# Category: Complete the Code
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Fill in the blanks: fetch two values in parallel and handle errors.

```javascript
const getA = () => new Promise(r => setTimeout(() => r(1), 20));
const getB = () => new Promise(r => setTimeout(() => r(2), 20));

____ function sum() {                      // make it async
  ____ {                                   // start error handling
    const [a, b] = ____ Promise.____([getA(), getB()]); // parallel wait
    return a + b;
  } ____ (err) {                           // catch errors
    return -1;
  }
}
```

---

## 💡 Quick Concept (2 lines only)
`async` functions return promises and `await` pauses until a promise settles. Use `Promise.all` to run independent tasks in parallel.
हिंदी: `await` promise का इंतज़ार करता है; independent काम साथ चलाने के लिए `Promise.all` लगाओ।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

const getA = () => new Promise(r => setTimeout(() => r(1), 20)); // resolves 1
const getB = () => new Promise(r => setTimeout(() => r(2), 20)); // resolves 2

async function sum() {                              // blank 1: async keyword
  try {                                             // blank 2: try block
    const [a, b] = await Promise.all([getA(), getB()]); // blanks 3+4: parallel await
    return a + b;                                   // combine results
  } catch (err) {                                   // blank 5: catch rejection
    return -1;                                      // fallback value
  }
}

// ============================================
// TEST CASES
// ============================================

sum().then(console.log);                            // Expected: 3

const bad = async () => {                           // failing example
  try { await Promise.all([getA(), Promise.reject(new Error('x'))]); }
  catch (e) { return 'caught ' + e.message; }
};
bad().then(console.log);                            // Expected: caught x
```

---

## 🔍 Why This Works (3 lines max)
`Promise.all` starts both tasks together so total time is ~20ms, not 40ms. If any rejects, `await` throws and `catch` handles it.
हिंदी: `Promise.all` दोनों को साथ चलाता है और कोई fail हो तो catch चलता है।

---

## ⚡ Alternative Solution
```javascript
// Start both first, then await (also parallel)
async function sum2() {
  const pa = getA(), pb = getB();    // both started
  return (await pa) + (await pb);
}
sum2().then(console.log); // 3
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: sequential awaits for independent tasks (slower)
// const a = await getA(); const b = await getB();
// ✅ Correct: Promise.all
```

---

## 🎯 Interview Tip (1 line)
Say: "Await sequentially only when steps depend on each other; otherwise Promise.all."

---

## 🔗 Related Questions
→ Q012 (async/await order) | Q122 (async error handling) | Q202 (promises in parallel) | Q167 (async/await internals)
