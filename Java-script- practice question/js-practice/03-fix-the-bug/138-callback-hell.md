---

# Q138. Fix Callback Hell Bug
# Category: Fix the Bug
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Deeply nested callbacks are hard to read and handle errors poorly. Refactor to async/await.

```javascript
// BUGGY CODE:
getUser(1, (err, user) => {
  if (err) return console.log(err);
  getPosts(user.id, (err, posts) => {
    if (err) return console.log(err);
    getComments(posts[0], (err, comments) => {
      if (err) return console.log(err);
      console.log(comments);
    });
  });
});
```

---

## 💡 Quick Concept (2 lines only)
Promisify callback APIs, then use async/await for flat, linear code with a single try/catch.
हिंदी: callbacks को promise बनाओ और async/await से सीधा, एक catch वाला code लिखो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: callback-style helpers
const getUser = (id, cb) => setTimeout(() => cb(null, { id }), 10);                 // returns user
const getPosts = (uid, cb) => setTimeout(() => cb(null, ['post-' + uid]), 10);       // returns posts
const getComments = (post, cb) => setTimeout(() => cb(null, ['c1 on ' + post]), 10); // returns comments

// Step 2: generic promisify wrapper
const promisify = (fn) => (...args) =>
  new Promise((resolve, reject) =>
    fn(...args, (err, data) => (err ? reject(err) : resolve(data)))); // settle from callback

// Step 3 (FIX): flat async/await flow
async function main() {
  try {
    const user = await promisify(getUser)(1);              // wait for user
    const posts = await promisify(getPosts)(user.id);      // then posts
    const comments = await promisify(getComments)(posts[0]); // then comments
    return comments;                                       // final result
  } catch (err) {
    return 'error: ' + err;                                // single error handler
  }
}

// ============================================
// TEST CASES
// ============================================

main().then(console.log); // Expected: [ 'c1 on post-1' ]
```

---

## 🔍 Why This Works (3 lines max)
`promisify` converts error-first callbacks into promises, and `await` flattens the pyramid. One try/catch handles errors from every step.
हिंदी: promisify callbacks को promise बनाता है और await से nesting खत्म हो जाती है।

---

## ⚡ Alternative Solution
```javascript
// Node built-in
const { promisify: p } = require('util');
p(setTimeout)(10).then(() => console.log('done')); // done
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: await inside forEach does not wait
// [1, 2].forEach(async (n) => { await work(n); });
// ✅ Correct: for...of loop
// for (const n of [1, 2]) { await work(n); }
```

---

## 🎯 Interview Tip (1 line)
Say: "Promisify error-first callbacks, then async/await — flat code, one catch, easy to parallelize with Promise.all."

---

## 🔗 Related Questions
→ Q123 (Promise chain bug) | Q146 (complete async/await) | Q201 (sequential promises) | Q207 (chain async operations)
