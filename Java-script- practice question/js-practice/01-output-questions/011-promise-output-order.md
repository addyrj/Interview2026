---

# Q011. Promise Output Order
# Category: Output Questions
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
What will the following code print, and in what order?

```javascript
console.log('1');

setTimeout(() => console.log('2'), 0);

Promise.resolve().then(() => console.log('3'));

console.log('4');
```

---

## 💡 Quick Concept (2 lines only)
Synchronous code runs first, then microtasks (Promises), then macrotasks (setTimeout) — even if setTimeout delay is 0.
हिंदी: Sync → Microtasks (Promise) → Macrotasks (setTimeout) — यही event loop का order है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

console.log('1');             // Step 1: sync → prints immediately

setTimeout(() => {
  console.log('2');           // Step 4: macrotask queue (fires after microtasks)
}, 0);

Promise.resolve().then(() => {
  console.log('3');           // Step 3: microtask queue (runs before macrotasks)
});

console.log('4');             // Step 2: sync → prints immediately

// ============================================
// OUTPUT ORDER:
// ============================================

// 1   ← sync
// 4   ← sync
// 3   ← microtask (Promise.then)
// 2   ← macrotask (setTimeout)
```

---

## 🔍 Why This Works (3 lines max)
Call stack runs all synchronous code first (1, 4). When stack is empty, JS drains the microtask queue (Promise callbacks) completely before moving to macrotask queue (setTimeout). setTimeout(0) doesn't mean "run now" — it means "run after current microtasks."
हिंदी: Sync code → microtask queue (Promise) → macrotask queue (setTimeout) — यही exact order है।

---

## ⚡ Alternative Solution
```javascript
// More complex example:
console.log('start');

setTimeout(() => console.log('timeout 1'), 0);
setTimeout(() => console.log('timeout 2'), 0);

Promise.resolve()
  .then(() => {
    console.log('promise 1');
    return Promise.resolve();
  })
  .then(() => console.log('promise 2'));

console.log('end');

// Output:
// start
// end
// promise 1
// promise 2
// timeout 1
// timeout 2

// KEY: ALL microtasks drain before ANY macrotask runs
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: thinking setTimeout(0) runs before Promise
setTimeout(() => console.log('A'), 0);
Promise.resolve().then(() => console.log('B'));

// Wrong output: A, B
// ✅ Correct output: B, A
// Microtask (Promise) ALWAYS runs before macrotask (setTimeout)
```

---

## 🎯 Interview Tip (1 line)
Say: "Event loop priority: Synchronous → Microtasks (Promise/queueMicrotask) → Macrotasks (setTimeout/setInterval) — ALL microtasks drain before any macrotask."

---

## 🔗 Related Questions
→ Q012 (async/await order) | Q013 (Promise + setTimeout) | Q016 (microtask vs macrotask) | Q163 (event loop explained)
