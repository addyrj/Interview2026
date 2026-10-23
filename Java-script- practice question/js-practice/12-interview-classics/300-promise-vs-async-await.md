---

# Q300. Promise vs async/await
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What is the difference between Promises and async/await? Show the same code in both styles. When would you prefer one over the other?

---

## 💡 Quick Concept (2 lines only)
async/await is syntactic sugar over Promises — same mechanism, different syntax. await pauses execution of the async function until the Promise resolves, making async code look synchronous.
हिंदी: async/await Promises का syntactic sugar है — same mechanism, async code synchronous जैसा दिखता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION — Same logic, two styles
// ============================================

// SCENARIO: Fetch user, then fetch their orders

// ─── PROMISE CHAIN STYLE ──────────────────────────────────────
function getUserOrdersPromise(userId) {
  return fetchUser(userId)
    .then(user => {
      console.log('User:', user.name);
      return fetchOrders(user.id);  // return next promise
    })
    .then(orders => {
      console.log('Orders:', orders.length);
      return orders;
    })
    .catch(error => {
      console.error('Error:', error.message);
      throw error;  // re-throw to propagate
    });
}

// ─── ASYNC/AWAIT STYLE ──────────────────────────────────────
async function getUserOrdersAsync(userId) {
  try {
    const user = await fetchUser(userId);    // pauses here until resolved
    console.log('User:', user.name);
    
    const orders = await fetchOrders(user.id);  // pauses here
    console.log('Orders:', orders.length);
    
    return orders;  // auto-wrapped in Promise.resolve()
  } catch (error) {
    console.error('Error:', error.message);
    throw error;
  }
}

// ─── PARALLEL vs SEQUENTIAL ──────────────────────────────────

// WRONG: sequential when parallel is possible
async function sequential() {
  const user = await fetchUser(1);    // waits for user
  const posts = await fetchPosts(1);  // THEN fetches posts — unnecessarily slow!
  return { user, posts };
}

// CORRECT: parallel with Promise.all
async function parallel() {
  const [user, posts] = await Promise.all([  // both start simultaneously
    fetchUser(1),
    fetchPosts(1)
  ]);
  return { user, posts };
}

// ============================================
// TEST CASES
// ============================================

// Mock functions:
const fetchUser = (id) => new Promise(resolve =>
  setTimeout(() => resolve({ id, name: 'Arjun' }), 100)
);
const fetchOrders = (id) => new Promise(resolve =>
  setTimeout(() => resolve([{ item: 'Phone' }, { item: 'Laptop' }]), 100)
);
const fetchPosts = (id) => new Promise(resolve =>
  setTimeout(() => resolve([{ title: 'Hello' }]), 100)
);

// Both styles produce same result:
getUserOrdersPromise(1).then(orders => console.log(orders));
// Expected: [{item:'Phone'},{item:'Laptop'}]

getUserOrdersAsync(1).then(orders => console.log(orders));
// Expected: [{item:'Phone'},{item:'Laptop'}]
```

---

## 🔍 Why This Works (3 lines max)
`async` functions always return a Promise. `await` pauses execution of the async function (not the whole thread) and resumes when the Promise settles. Under the hood, async/await is generator-based Promise chaining.
हिंदी: `async` function हमेशा Promise return करता है; `await` function को pause करता है — thread नहीं रुकती।

---

## ⚡ Alternative Solution
```javascript
// When to use Promises (not async/await):

// 1. Multiple async operations that don't depend on each other:
Promise.all([fetchA(), fetchB(), fetchC()])
  .then(([a, b, c]) => handleAll(a, b, c));

// 2. Promise chaining with array of unknown length:
const ids = [1, 2, 3, 4, 5];
ids.reduce(
  (chain, id) => chain.then(() => processItem(id)),
  Promise.resolve()
);  // Sequential with reduce — hard to do with await

// 3. When using .finally():
fetchData()
  .finally(() => hideLoader())  // always runs
  .then(handleData)
  .catch(handleError);

// ASYNC/AWAIT ADVANTAGES:
// ✅ Easier try/catch error handling
// ✅ Better debugger stepping
// ✅ Conditional logic reads naturally
// ✅ Loop with await: for...of loop

async function processAll(ids) {
  for (const id of ids) {
    await processItem(id);  // sequential with loop — easy to read
  }
}

// Note: forEach doesn't work with await!
ids.forEach(async id => {
  await processItem(id);  // ❌ forEach doesn't wait — all start simultaneously
});
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: sequential awaits when parallel is possible
async function getData() {
  const a = await fetchA();  // 200ms
  const b = await fetchB();  // 200ms (starts AFTER a finishes)
  // Total: 400ms
}

// ✅ Correct: parallel
async function getData() {
  const [a, b] = await Promise.all([fetchA(), fetchB()]);
  // Total: 200ms (both run simultaneously)
}

// ❌ Wrong: forgetting await — returns Promise, not value
async function getUser() {
  const result = fetchUser(1);  // forgot await — result is a Promise!
  console.log(result.name);     // undefined — Promise doesn't have .name
}

// ❌ Wrong: using await outside async function
const data = await fetchData();  // SyntaxError (outside async context)
// Top-level await only works in ES modules
```

---

## 🎯 Interview Tip (1 line)
Say: "async/await is Promise under the hood — use async/await for readability; use Promise.all() for parallelism; avoid sequential awaits when calls are independent."

---

## 🔗 Related Questions
→ Q011 (Promise output) | Q012 (async/await output) | Q091 (Promise.all) | Q167 (async/await internals) | Q201 (sequential promises)
