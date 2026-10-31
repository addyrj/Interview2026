---

# Q122. Fix Async/Await Error Handling
# Category: Fix the Bug
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
`loadUser` should return `null` when the fetch fails, but the program crashes with an unhandled rejection. Find and fix the bug.

```javascript
// BUGGY CODE:
function fakeFetch(id) {
  return Promise.reject(new Error('Network down'));
}

async function loadUser(id) {
  try {
    return fakeFetch(id);   // returned without await
  } catch (err) {
    return null;
  }
}

loadUser(1).then(console.log);
```

---

## 💡 Quick Concept (2 lines only)
`return promise` inside try does NOT catch its rejection — the function exits before the promise settles. Use `return await promise` so catch can see the error.
हिंदी: try के अंदर `await` के बिना promise return करने पर catch काम नहीं करता — `return await` लगाओ।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Simulate a failing request
function fakeFetch(id) {
  return id === 1 ? Promise.reject(new Error('Network down')) : Promise.resolve({ id }); // fail only for id 1
}

// Step 2: await INSIDE try so rejection is thrown inside try
async function loadUser(id) {
  try {
    return await fakeFetch(id); // FIX: await makes the error catchable here
  } catch (err) {
    return null;                // Step 3: fallback value on error
  }
}

// ============================================
// TEST CASES
// ============================================

loadUser(1).then(r => console.log(r)); // Expected: null
loadUser(2).then(r => console.log(r)); // Expected: { id: 2 }
```

---

## 🔍 Why This Works (3 lines max)
Without `await`, the async function returns the promise and leaves the try block immediately, so catch never runs. With `return await`, the rejection becomes a thrown error inside try and catch handles it.
हिंदी: `await` से rejection try के अंदर throw होता है, इसलिए catch उसे पकड़ लेता है।

---

## ⚡ Alternative Solution
```javascript
// Use .catch() on the promise directly
const loadUser2 = (id) => fakeFetch(id).catch(() => null); // no try/catch needed
loadUser2(1).then(r => console.log(r)); // null
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: try/catch around a promise that is not awaited
try { fakeFetch(1); } catch (e) { console.log('never runs'); }

// ✅ Correct: await it
(async () => { try { await fakeFetch(1); } catch (e) { console.log('caught'); } })();
```

---

## 🎯 Interview Tip (1 line)
Say: "try/catch only catches rejections of promises that are awaited inside the try block — `return await` is the fix."

---

## 🔗 Related Questions
→ Q012 (async/await order) | Q123 (Promise chain bug) | Q146 (complete async/await) | Q300 (Promise vs async/await)
