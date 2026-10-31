---

# Q013. Promise + setTimeout Order
# Category: Output Questions
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
What will the following code print, and in what order?

```javascript
console.log('A');
setTimeout(() => console.log('B'), 0);
Promise.resolve()
  .then(() => {
    console.log('C');
    setTimeout(() => console.log('D'), 0);
  })
  .then(() => console.log('E'));
setTimeout(() => console.log('F'), 0);
console.log('G');
```

---

## 💡 Quick Concept (2 lines only)
Sync first, then all microtasks (including chained `.then`), then macrotasks in the order they were queued.
हिंदी: पहले sync, फिर सारे microtasks (chained .then समेत), फिर macrotasks queue के order में।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: sync -> A, G
// Step 2: microtasks -> C (queues timer D), then E
// Step 3: macrotasks in queue order -> B, F, D

console.log('A');                                 // sync
setTimeout(() => console.log('B'), 0);            // macrotask #1
Promise.resolve()                                 // resolved promise
  .then(() => {
    console.log('C');                             // microtask
    setTimeout(() => console.log('D'), 0);        // macrotask #3 (queued late)
  })
  .then(() => console.log('E'));                  // next microtask
setTimeout(() => console.log('F'), 0);            // macrotask #2
console.log('G');                                 // sync

// ============================================
// TEST CASES
// ============================================

// Output order:
// A
// G
// C
// E
// B
// F
// D
```

---

## 🔍 Why This Works (3 lines max)
Microtasks (C, E) drain fully before any timer. D is created inside a microtask, so it lands in the timer queue after B and F.
हिंदी: D बाद में queue हुआ इसलिए B और F के बाद चलता है।

---

## ⚡ Alternative Solution
```javascript
// Simplest form of the same rule
setTimeout(() => console.log('timer'), 0);        // macrotask
Promise.resolve().then(() => console.log('micro')); // microtask
// Expected: micro, timer
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Thinking a timer created inside a .then runs before older timers
// ✅ Timers run in the order they were added to the queue (B, F, then D)
```

---

## 🎯 Interview Tip (1 line)
Say: "Drain all microtasks, then run ONE macrotask, then drain microtasks again."

---

## 🔗 Related Questions
→ Q011 (Promise order) | Q016 (microtask vs macrotask) | Q017 (event loop mixed) | Q163 (explain event loop)
