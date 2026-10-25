# 201. Async Iterators in Node
# हिंदी में: Node में Async Iterators

---

## 🔵 Simple Definition (English)
An **async iterator** is an object that produces a sequence of values asynchronously, one at a time, each wrapped in a Promise — consumed cleanly with the `for await...of` loop. Node.js streams and many paginated-data sources implement the `Symbol.asyncIterator` protocol, letting you loop over async data sources (files, DB cursors, paginated APIs) as if they were simple arrays.

## 🔵 सरल परिभाषा (Hindi)
**Async iterator** एक object है जो values को asynchronously, एक-एक करके produce करता है, हर value एक Promise में wrapped होती है — `for await...of` loop से इसे साफ तरीके से consume किया जाता है। Node.js streams और कई paginated-data sources `Symbol.asyncIterator` protocol implement करते हैं, जिससे async data sources (files, DB cursors, paginated APIs) को simple arrays जैसे loop कर सकते हैं।

---

## 🔴 Problem it Solves
```
PROBLEM:
  Iterating over data that arrives ASYNCHRONOUSLY in chunks (a file stream,
  a paginated API, a DB cursor) with plain loops or even Promise.all is awkward:
  - Promise.all needs ALL items upfront (loads everything into memory)
  - Manual recursive callback-based pagination is painful to read
  - Regular `for...of` only works with SYNCHRONOUS iterables

ASYNC ITERATOR SOLUTION:
  `for await (const chunk of asyncSource) { ... }`
  Reads like a normal loop, but pulls ONE item at a time as it becomes
  available — great for memory efficiency (streaming) and natural pagination
```

## 🔴 यह क्यों बना? (Hindi)
```
Problem: file stream, paginated API, DB cursor जैसे async data sources को loop
करना मुश्किल था — Promise.all सब कुछ memory में load करता है
Regular for...of सिर्फ sync iterables के साथ काम करता है

Solution: for await...of से एक-एक item async रूप से pull करो
Memory-efficient streaming और natural pagination मिलती है
```

---

## 🟢 How it Works — Step by Step

Step 1 → An object implements `[Symbol.asyncIterator]()`, returning an object with a `next()` method that returns a `Promise<{value, done}>`
Step 2 → `for await (const item of asyncIterable) { ... }` repeatedly calls `next()`, `await`s the returned promise, and unwraps `{value, done}` automatically
Step 3 → The loop body runs once per yielded value; it stops when `done: true` is returned
Step 4 → Node.js Readable streams are natively async-iterable: `for await (const chunk of readableStream)`
Step 5 → You can also write your OWN async generator function (`async function* gen() { yield await fetchPage(1); yield await fetchPage(2); }`) to produce a custom async sequence, e.g., for paginated API results

## 🟢 कैसे काम करता है? (Hindi)
```
1. Object [Symbol.asyncIterator]() implement करता है, next() एक Promise<{value,done}> return करता है
2. for await...of हर बार next() call करता है, promise await करता है
3. done: true आने तक loop चलता रहता है
4. Node की Readable streams natively async-iterable हैं
5. async generator function (async function* gen()) से खुद का async sequence बना सकते हो
```

---

## 🟡 Real World Example
**Zomato restaurant data export (paginated API consumption):** When a backend job needs to process ALL restaurants from a paginated internal API (1000 restaurants, 50 per page = 20 pages), instead of manually tracking `page++` and recursively calling fetch, you write an async generator `async function* fetchAllRestaurants() { let page = 1; while (true) { const data = await fetchPage(page++); if (data.length === 0) return; yield* data; } }` — then simply `for await (const restaurant of fetchAllRestaurants()) { process(restaurant); }`. Memory stays low (one page in memory at a time) and the code reads like a simple loop over a plain array.

## 🟡 Real Example Hindi mein
**Zomato restaurant data export:** Paginated API से 1000 restaurants (20 pages) process करने के लिए async generator बनाओ — हर बार एक page fetch करो, yield करो। `for await` से simple loop जैसे consume करो। Memory कम रहता है, code साफ दिखता है।

---

## 💻 Code Example — Basic

```javascript
// basic-async-iterator.js
// Run: node basic-async-iterator.js

// An async generator function — 'async function*' combines async + generator
async function* countWithDelay(max) {
  for (let i = 1; i <= max; i++) {
    // Simulate async work before producing each value (e.g., a DB/API call)
    await new Promise((resolve) => setTimeout(resolve, 200));
    yield i;  // yields a value wrapped implicitly as {value: i, done: false}
  }
}

async function main() {
  console.log('Starting...');
  // for await...of consumes the async generator one value at a time
  for await (const num of countWithDelay(5)) {
    console.log('Got:', num);  // logs 1, 2, 3, 4, 5 — one every 200ms
  }
  console.log('Done!');
}

main();
```

## 💻 Code Example — Advanced

```javascript
// advanced-pagination-iterator.js
// Realistic pattern: async generator wrapping a paginated API,
// consumed with for-await, with error handling and early termination.

function fetchPage(pageNumber) {
  // Simulates an API call returning a page of restaurant data
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const totalPages = 3;
      if (pageNumber > totalPages) {
        return resolve({ items: [], hasMore: false });  // no more pages
      }
      const items = Array.from({ length: 2 }, (_, i) => ({
        id: `r_${pageNumber}_${i}`,
        name: `Restaurant ${pageNumber}-${i}`,
      }));
      resolve({ items, hasMore: pageNumber < totalPages });
    }, 100);
  });
}

// Async generator that transparently handles pagination for the consumer
async function* fetchAllRestaurants() {
  let page = 1;
  while (true) {
    const { items, hasMore } = await fetchPage(page);
    // yield* delegates to another iterable — yields each item individually
    yield* items;
    if (!hasMore) return;  // stop the generator — done: true on next() call
    page++;
  }
}

async function processAllRestaurants() {
  let count = 0;
  try {
    for await (const restaurant of fetchAllRestaurants()) {
      console.log('Processing:', restaurant.name);
      count++;
      if (count >= 4) {
        console.log('Stopping early after 4 items');
        break;  // for-await supports break — generator's cleanup (if any) still runs
      }
    }
  } catch (err) {
    console.error('Error during pagination:', err.message);
  }
  console.log(`Processed ${count} restaurants total`);
}

processAllRestaurants();
```

---

## 🟠 Express.js Integration

```javascript
// Streaming a large dataset to the client as NDJSON using async iteration,
// instead of loading everything into memory and sending one giant JSON array.
const express = require('express');
const app = express();

async function* fetchOrdersInBatches(userId) {
  const totalBatches = 3;
  for (let batch = 1; batch <= totalBatches; batch++) {
    // Simulate fetching a batch from a DB cursor
    await new Promise((r) => setTimeout(r, 50));
    yield { batch, orders: [{ id: `order_${batch}_1` }, { id: `order_${batch}_2` }] };
  }
}

app.get('/api/users/:id/orders/stream', async (req, res) => {
  res.set('Content-Type', 'application/x-ndjson');  // newline-delimited JSON
  try {
    // Stream each batch to the client as it's ready, instead of buffering all of them
    for await (const batch of fetchOrdersInBatches(req.params.id)) {
      res.write(JSON.stringify(batch) + '\n');  // one JSON object per line
    }
    res.end();
  } catch (err) {
    res.status(500).end(JSON.stringify({ error: err.message }));
  }
});

app.listen(3000, () => console.log('Server on port 3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `Promise.all` to eagerly fetch ALL pages before processing, defeating the memory-efficiency purpose of async iteration.
✅ Correct: Fetch pages lazily, one at a time, inside the generator — only pull the next page when the consumer asks for it.

```javascript
// Wrong — loads every page into memory upfront
const allPages = await Promise.all([fetchPage(1), fetchPage(2), fetchPage(3)]);

// Right — lazy, one page at a time
async function* fetchAll() {
  let page = 1;
  while (true) {
    const data = await fetchPage(page++);
    if (data.items.length === 0) return;
    yield* data.items;
  }
}
```

❌ Mistake 2: Forgetting that `for await...of` on a REGULAR (non-async) iterable still works but gains nothing — don't force async syntax where a plain loop suffices.
✅ Correct: Use `for await...of` specifically for genuinely async sources (streams, async generators); use plain `for...of` for synchronous arrays/iterables.

❌ Mistake 3: Not handling errors thrown inside the async generator — an unhandled rejection deep in pagination logic can silently stop processing without clear diagnostics.
✅ Correct: Wrap the `for await` loop in `try/catch` so generator errors surface clearly.

---

## 🧠 Tricky Interview Question

```javascript
async function* gen() {
  try {
    yield 1;
    yield 2;
    yield 3;
  } finally {
    console.log('cleanup ran');
  }
}

async function main() {
  for await (const val of gen()) {
    console.log(val);
    if (val === 2) break;  // early exit
  }
}
main();
```
What is logged?
Answer:
```
1
2
cleanup ran
```
**Explanation:** When a `for await...of` loop exits early via `break`, JavaScript automatically calls the generator's `.return()` method, which causes the generator function to behave as if a `return` statement executed at the current `yield` point — this triggers any pending `finally` block inside the generator BEFORE the loop fully exits. So `3` is never yielded/logged (we broke before reaching it), but `'cleanup ran'` still prints because the `finally` block runs as part of properly closing the generator — this cleanup guarantee is why generators are safe to use for resources needing teardown (like closing a DB cursor or file handle).

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between a regular iterator and an async iterator?
A1: A regular iterator's `next()` method returns `{value, done}` synchronously. An async iterator's `next()` returns a `Promise<{value, done}>` — the value/done status isn't known until that promise resolves. Regular iterables are consumed with `for...of`; async iterables need `for await...of` to properly await each `next()` call.

Q2: How do you create a custom async iterable?
A2: Either write an `async function*` (async generator function) — the easiest way, where `yield` produces each value — or manually implement `[Symbol.asyncIterator]()` on an object, returning an object with a `next()` method that returns a Promise resolving to `{value, done}`.

Q3: Why are async iterators memory-efficient for pagination compared to fetching everything upfront?
A3: Because each `next()` call only fetches/produces ONE item (or one page) at a time, on demand — the consumer processes it and then the next item is requested. Unlike `Promise.all` or loading an entire dataset into an array first, memory usage stays bounded to roughly one page/item's worth of data, regardless of how large the total dataset is.

Q4: Are Node.js Readable streams async-iterable?
A4: Yes — since Node.js 10+, `Readable` streams implement `Symbol.asyncIterator`, so you can write `for await (const chunk of readableStream) { ... }` directly instead of manually attaching `'data'`/`'end'` event listeners, making stream consumption read like simple sequential code.

Q5: What happens if you `break` out of a `for await...of` loop early?
A5: JavaScript calls the underlying async iterator's `.return()` method (if it has one), signaling the generator/iterator to clean up — any `finally` block inside an async generator still executing at a `yield` point will run before the generator is fully closed. This ensures resources (DB connections, file handles, cursors) tied to the generator are properly released even on early exit.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Consuming paginated APIs, DB cursors, or Node streams without loading everything into memory at once
- Writing a reusable, composable data-producing function (async generator) that callers can consume lazily
- Streaming large responses to clients incrementally

❌ Avoid when:
- The dataset is small and already fully in memory — a plain array with `for...of` or `.map()` is simpler
- You actually NEED all results simultaneously to compute something (e.g., sorting the whole set) — you'll have to buffer it anyway, so async iteration adds complexity without benefit

---

## 📊 Visual Diagram
```
ASYNC ITERATION FLOW
──────────────────────────────────────────
for await (const item of asyncGen()) {
  process(item)
}

   asyncGen()
      │
      ▼
  next() → Promise<{value: 1, done:false}> ──▶ await ──▶ process(1)
      │
  next() → Promise<{value: 2, done:false}> ──▶ await ──▶ process(2)
      │
  next() → Promise<{value: undefined, done:true}> ──▶ loop ends

  [break early] ──▶ .return() called ──▶ finally{} in generator runs
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Async iterator | Produces values asynchronously | Values को async रूप से produce करना |
| for await...of | Loop for consuming async iterables | Async iterables consume करने का loop |
| Async generator | async function* producing a sequence | async function* जो sequence produce करे |
| yield* | Delegates to another iterable | दूसरे iterable को delegate करना |
| Symbol.asyncIterator | Protocol for async iterables | Async iterables का protocol |

---

## ⚡ 3-Line Summary
English:
1. Async iterators produce values one at a time wrapped in Promises, consumed with `for await...of`.
2. Async generators (`async function*`) are the easiest way to build custom async sequences like paginated data fetchers.
3. They're memory-efficient for large/paginated datasets since each item is pulled lazily, on demand.

Hindi:
1. Async iterators values को एक-एक करके Promise में wrap करके produce करते हैं, `for await...of` से consume होते हैं।
2. `async function*` custom async sequences (जैसे paginated fetchers) बनाने का आसान तरीका है।
3. बड़े/paginated datasets के लिए memory-efficient हैं — हर item lazily, demand पर आता है।

---

## ➡️ Next Topic
**202. Event-Driven Pattern** — Understanding Node's EventEmitter and the broader event-driven architecture style.
