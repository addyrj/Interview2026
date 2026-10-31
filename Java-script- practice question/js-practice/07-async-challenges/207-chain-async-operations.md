---

# Q207. Chain Async Operations
# Category: Async Challenges
# Difficulty: ⭐ Easy

---

## ❓ Question
Three async calls depend on each other: `getUser(id)` -> `getPosts(user)` -> `getComments(post)`. Chain them so each uses the previous result, and return a final summary.

```javascript
getUserSummary(1).then(console.log);
```

---

## 💡 Quick Concept (2 lines only)
Dependent calls must be chained: `.then()` returning a promise, or `await` one after another. Each step receives the previous step's output.
हिंदी: जब अगला call पिछले के result पर निर्भर हो, तब `.then` chain या `await` का क्रम इस्तेमाल करो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: getUser -> returns user
// Step 2: getPosts(user) -> returns posts
// Step 3: getComments(first post) -> returns comments, then build summary

const sleep = (ms, v) => new Promise(r => setTimeout(() => r(v), ms)); // fake latency

const getUser = id => sleep(30, { id, name: 'Aditya' });              // fake user API
const getPosts = user => sleep(30, [{ id: 10, userId: user.id, title: 'Hello' }]); // fake posts API
const getComments = post => sleep(30, ['Nice!', 'Great post']);       // fake comments API

// Version A: async/await (reads top to bottom)
async function getUserSummary(id) {
  const user = await getUser(id);                     // wait for user
  const posts = await getPosts(user);                 // uses user
  const comments = await getComments(posts[0]);       // uses first post
  return `${user.name} wrote "${posts[0].title}" with ${comments.length} comments`; // summary
}

// Version B: .then chain (return the inner promise to keep chaining flat)
function getUserSummaryThen(id) {
  let user, posts;                                    // keep earlier values in scope
  return getUser(id)
    .then(u => { user = u; return getPosts(u); })     // returning promise flattens chain
    .then(p => { posts = p; return getComments(p[0]); })
    .then(c => `${user.name} wrote "${posts[0].title}" with ${c.length} comments`);
}

// ============================================
// TEST CASES
// ============================================

(async () => {
  console.log(await getUserSummary(1));               // Expected: Aditya wrote "Hello" with 2 comments
  console.log(await getUserSummaryThen(1));           // Expected: Aditya wrote "Hello" with 2 comments
})();
// Console order:
// Aditya wrote "Hello" with 2 comments
// Aditya wrote "Hello" with 2 comments
```

---

## 🔍 Why This Works (3 lines max)
Returning a promise from `.then` makes the next `.then` wait for it. `await` does the same thing with synchronous-looking code, so values from earlier steps stay in scope.
हिंदी: `.then` में promise return करने से chain अगले step का इंतज़ार करती है।

---

## ⚡ Alternative Solution (if exists)
```javascript
// Fire independent calls in parallel inside a chain
async function profile(id) {
  const user = await getUser(id);                     // must be first
  const [posts, friends] = await Promise.all([        // these two do NOT depend on each other
    getPosts(user),
    sleep(30, ['Ravi'])
  ]);
  return { user, posts, friends };
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: nested .then (callback hell) / forgetting to return
getUser(1).then(u => { getPosts(u); }).then(p => console.log(p)); // p is undefined!

// ✅ Correct: return the promise
getUser(1).then(u => getPosts(u)).then(p => console.log(p));
```

---

## 🎯 Interview Tip (1 line)
Say: "Chain only dependent calls; run independent ones with Promise.all to save time."

---

## 🔗 Related Questions
→ Q201 (sequential) | Q211 (waterfall) | Q123 (fix promise chain bug) | Q138 (callback hell)
