---

# Q014. process.nextTick Order
# Category: Output Questions
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
What will the following Node.js (CommonJS) code print?

```javascript
console.log('start');
setTimeout(() => console.log('timeout'), 0);
Promise.resolve().then(() => console.log('promise'));
process.nextTick(() => console.log('nextTick'));
console.log('end');
```

---

## 💡 Quick Concept (2 lines only)
In Node, the `process.nextTick` queue runs before the Promise microtask queue, and both run before timers.
हिंदी: Node में nextTick queue, Promise microtasks से भी पहले चलती है, और दोनों timers से पहले।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: sync -> start, end
// Step 2: nextTick queue -> nextTick
// Step 3: promise microtasks -> promise, then timers -> timeout

console.log('start');                              // sync
setTimeout(() => console.log('timeout'), 0);       // macrotask (timers phase)
Promise.resolve().then(() => console.log('promise')); // microtask
process.nextTick(() => console.log('nextTick'));   // runs before promises
console.log('end');                                // sync

// ============================================
// TEST CASES
// ============================================

// Output order:
// start
// end
// nextTick
// promise
// timeout
```

---

## 🔍 Why This Works (3 lines max)
After the current operation, Node empties the nextTick queue first, then the promise microtask queue, then moves to the event loop phases. (In ES modules the order of nextTick vs promise flips at top level.)
हिंदी: Order है: sync, nextTick, Promise, फिर timers।

---

## ⚡ Alternative Solution
```javascript
// queueMicrotask behaves like a Promise.then
process.nextTick(() => console.log('tick'));       // first
queueMicrotask(() => console.log('micro'));        // second
// Expected: tick, micro
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Believing nextTick is "next event loop tick"
// ✅ It runs right after the current operation, BEFORE promises; recursive nextTick can starve I/O
```

---

## 🎯 Interview Tip (1 line)
Say: "nextTick has higher priority than promise microtasks, and overusing it can starve the event loop."

---

## 🔗 Related Questions
→ Q011 (Promise order) | Q015 (setImmediate) | Q016 (microtask vs macrotask) | Q017 (event loop mixed)
