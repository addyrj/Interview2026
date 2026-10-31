---

# Q127. Fix Async State Update Bug
# Category: Fix the Bug
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Three async increments run in parallel but the counter ends at 1 instead of 3 (lost update). Fix it.

```javascript
// BUGGY CODE:
let counter = 0;
const wait = (ms) => new Promise(r => setTimeout(r, ms));

async function increment() {
  const current = counter;   // read old value
  await wait(10);            // others run meanwhile
  counter = current + 1;     // writes stale value
}

Promise.all([increment(), increment(), increment()]).then(() => console.log(counter)); // 1
```

---

## 💡 Quick Concept (2 lines only)
Reading state before an `await` and writing after it uses a stale value. Read-modify-write must happen with no `await` in between.
हिंदी: `await` से पहले पढ़ी value बाद में पुरानी हो जाती है — update बिना await के बीच में करो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

let counter = 0;                                   // shared state
const wait = (ms) => new Promise(r => setTimeout(r, ms)); // helper delay

async function increment() {
  await wait(10);                                  // Step 1: do async work first
  counter = counter + 1;                           // Step 2 (FIX): read + write together, fresh value
}

// ============================================
// TEST CASES
// ============================================

Promise.all([increment(), increment(), increment()]).then(() => {
  console.log(counter);                            // Expected: 3
});
```

---

## 🔍 Why This Works (3 lines max)
JS is single-threaded, so code between two awaits never gets interrupted. Reading and writing in the same synchronous step removes the stale snapshot.
हिंदी: पढ़ना और लिखना एक ही sync step में करो, तो stale value की समस्या नहीं आती।

---

## ⚡ Alternative Solution
```javascript
// Functional-update style (like React setState(prev => prev + 1))
let state = 0;
const update = (fn) => { state = fn(state); };     // always uses latest state
update(prev => prev + 1);
update(prev => prev + 1);
console.log(state); // 2
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: React-style stale closure
// setCount(count + 1); setCount(count + 1);   // ends +1
// ✅ Correct
// setCount(c => c + 1); setCount(c => c + 1); // ends +2
```

---

## 🎯 Interview Tip (1 line)
Say: "Never hold a snapshot across an await; use functional updates or do the read-modify-write synchronously."

---

## 🔗 Related Questions
→ Q012 (async/await order) | Q139 (race condition) | Q146 (complete async/await)
