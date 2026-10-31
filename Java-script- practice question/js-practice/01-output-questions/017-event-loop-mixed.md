---

# Q017. Event Loop Order (Mixed)
# Category: Output Questions
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
What will the following Node.js (CommonJS) code print?

```javascript
console.log('1');
setTimeout(() => console.log('2'), 0);
new Promise((res) => { console.log('3'); res(); }).then(() => console.log('4'));
(async () => { console.log('5'); await null; console.log('6'); })();
process.nextTick(() => console.log('7'));
console.log('8');
```

---

## 💡 Quick Concept (2 lines only)
Order: sync (including the Promise executor and async code before `await`) -> nextTick -> promise microtasks -> timers.
हिंदी: Order: sync (Promise executor और await से पहले का code) -> nextTick -> Promise microtasks -> timers।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: sync -> 1, 3 (executor is sync), 5 (before await), 8
// Step 2: nextTick -> 7, then microtasks in queue order -> 4, 6
// Step 3: timer -> 2

console.log('1');                                  // sync
setTimeout(() => console.log('2'), 0);             // macrotask
new Promise((res) => {                             // executor runs synchronously
  console.log('3');                                // sync
  res();                                           // schedules .then
}).then(() => console.log('4'));                   // microtask #1
(async () => {
  console.log('5');                                // sync part of async fn
  await null;                                      // rest becomes microtask #2
  console.log('6');                                // after await
})();
process.nextTick(() => console.log('7'));          // before promise microtasks
console.log('8');                                  // sync

// ============================================
// TEST CASES
// ============================================

// Output order:
// 1
// 3
// 5
// 8
// 7
// 4
// 6
// 2
```

---

## 🔍 Why This Works (3 lines max)
Promise executors and async functions run synchronously until the first `await`. Then Node drains nextTick, then promise jobs in FIFO order, then timers.
हिंदी: await तक async function sync चलता है; उसके बाद nextTick, microtasks, फिर timers।

---

## ⚡ Alternative Solution
```javascript
// Browser version (no nextTick): 1 3 5 8 4 6 2
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Thinking the Promise executor body is async
// ✅ Only .then callbacks are async; the executor runs immediately
```

---

## 🎯 Interview Tip (1 line)
Narrate in steps: "sync, nextTick, microtasks, then macrotasks" and mark where `await` splits a function.

---

## 🔗 Related Questions
→ Q012 (async/await order) | Q014 (nextTick) | Q016 (microtask vs macrotask) | Q163 (explain event loop)
