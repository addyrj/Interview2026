---

# Q016. Microtask vs Macrotask Order
# Category: Output Questions
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
What will the following code print?

```javascript
setTimeout(() => console.log('macro 1'), 0);
setTimeout(() => console.log('macro 2'), 0);
queueMicrotask(() => {
  console.log('micro 1');
  queueMicrotask(() => console.log('micro 3'));
});
queueMicrotask(() => console.log('micro 2'));
console.log('sync');
```

---

## 💡 Quick Concept (2 lines only)
The microtask queue is drained completely, including microtasks added while draining, before the next macrotask starts.
हिंदी: Microtask queue पूरी खाली होती है (नए जुड़े microtasks समेत), उसके बाद ही अगला macrotask चलता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: sync code -> 'sync'
// Step 2: drain microtasks: micro 1, micro 2, then newly added micro 3
// Step 3: run macrotasks one by one: macro 1, macro 2

setTimeout(() => console.log('macro 1'), 0);       // macrotask
setTimeout(() => console.log('macro 2'), 0);       // macrotask
queueMicrotask(() => {                             // microtask A
  console.log('micro 1');                          // runs first among micros
  queueMicrotask(() => console.log('micro 3'));    // appended to the same queue
});
queueMicrotask(() => console.log('micro 2'));      // microtask B
console.log('sync');                               // sync

// ============================================
// TEST CASES
// ============================================

// Output order:
// sync
// micro 1
// micro 2
// micro 3
// macro 1
// macro 2
```

---

## 🔍 Why This Works (3 lines max)
The queue is FIFO: micro 2 was queued before micro 3, so it runs first. The loop only moves on when the microtask queue is empty.
हिंदी: Queue FIFO है, micro 3 बाद में जुड़ा इसलिए micro 2 के बाद चलता है।

---

## ⚡ Alternative Solution
```javascript
// Danger: endless microtasks starve macrotasks
// let n = 0; const loop = () => { if (n++ < 1e6) queueMicrotask(loop); }; loop();
// Timers wait until the microtask queue finally empties
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Thinking one microtask runs, then a timer gets a turn
// ✅ ALL microtasks run first; only then one macrotask
```

---

## 🎯 Interview Tip (1 line)
Say: "Microtasks: Promise.then, queueMicrotask, MutationObserver; macrotasks: setTimeout, setInterval, I/O, UI events."

---

## 🔗 Related Questions
→ Q011 (Promise order) | Q013 (Promise + setTimeout) | Q017 (event loop mixed) | Q163 (explain event loop)
