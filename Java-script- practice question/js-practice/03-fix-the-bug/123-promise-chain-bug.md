---

# Q123. Fix Promise Chain Bug
# Category: Fix the Bug
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
The chain should print `userId=1`, then `name=Aman`. Instead the second step prints `undefined`. Fix the bug.

```javascript
// BUGGY CODE:
const getUser = () => Promise.resolve({ id: 1 });
const getName = (id) => Promise.resolve('Aman');

getUser()
  .then(user => {
    console.log('userId=' + user.id);
    getName(user.id);            // not returned
  })
  .then(name => console.log('name=' + name)); // undefined
```

---

## 💡 Quick Concept (2 lines only)
A `.then` callback must RETURN the next promise/value, otherwise the next `.then` receives `undefined` and does not wait.
हिंदी: `.then` के अंदर `return` ज़रूरी है, वरना अगला step `undefined` पाता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Two async helpers
const getUser = () => Promise.resolve({ id: 1 });          // resolves a user
const getName = (id) => Promise.resolve('Aman');           // resolves a name

// Step 2: Return the inner promise so the chain waits for it
getUser()
  .then(user => {
    console.log('userId=' + user.id); // Expected: userId=1
    return getName(user.id);          // FIX: return the promise
  })
  .then(name => console.log('name=' + name)) // Step 3: receives 'Aman'
  .catch(err => console.log('error', err));  // Step 4: one catch for whole chain

// ============================================
// TEST CASES
// ============================================

// Expected output:
// userId=1
// name=Aman
```

---

## 🔍 Why This Works (3 lines max)
Returning a promise from `.then` makes the outer chain adopt its result and wait. Forgetting `return` makes the callback resolve to `undefined` immediately.
हिंदी: return किया हुआ promise अगले `.then` को value देता है और chain उसका इंतज़ार करती है।

---

## ⚡ Alternative Solution
```javascript
// async/await avoids the forgotten-return problem
(async () => {
  const user = await getUser();   // wait for user
  const name = await getName(user.id); // wait for name
  console.log(name);              // Aman
})();
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: arrow with braces but no return
Promise.resolve(1).then(x => { x + 1; }).then(console.log); // undefined
// ✅ Correct: implicit return (no braces) or explicit return
Promise.resolve(1).then(x => x + 1).then(console.log);      // 2
```

---

## 🎯 Interview Tip (1 line)
Say: "Always return inside .then — otherwise the chain breaks and errors/values are lost."

---

## 🔗 Related Questions
→ Q011 (Promise order) | Q122 (async error handling) | Q145 (complete Promise chain) | Q207 (chain async operations)
