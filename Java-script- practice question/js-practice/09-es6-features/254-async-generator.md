---

# Q254. Async Generator
# Category: ES6+ Features
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Write an async generator that simulates paginated API fetching and consume it with `for await...of`. Also make an async iterable object.

---

## 💡 Quick Concept (2 lines only)
`async function*` yields values asynchronously; consume it with `for await...of`, which awaits each `next()`.
हिंदी: Async generator हर value await करके देता है और `for await...of` से पढ़ते हैं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Fake async page fetcher
// Step 2: Async generator that yields one page at a time
// Step 3: Consume with for await...of (with early break)

const sleep = ms => new Promise(r => setTimeout(r, ms)); // delay helper

// Step 1: simulate API returning 3 items per page
async function fetchPage(page) {
  await sleep(10);                               // pretend network latency
  return page <= 3 ? [`item${page}a`, `item${page}b`] : []; // empty page = end
}

// Step 2: async generator
async function* pages() {
  let page = 1;                                  // start page
  while (true) {
    const items = await fetchPage(page++);       // wait for next page
    if (items.length === 0) return;              // finished
    yield items;                                 // hand page to consumer
  }
}

// Step 3: consume
(async () => {
  for await (const items of pages()) {           // awaits each page
    console.log(items);                          // Expected: [ 'item1a', 'item1b' ] then page 2, then page 3
  }

  // Early break stops fetching more pages
  for await (const items of pages()) {
    console.log('first only:', items.length);    // Expected: first only: 2
    break;                                       // generator is closed
  }

  // ============================================
  // TEST CASES
  // ============================================

  const all = [];                                // collect everything
  for await (const items of pages()) all.push(...items); // flatten
  console.log(all.length);                       // Expected: 6

  const custom = {                               // async iterable object
    async *[Symbol.asyncIterator]() { yield 'x'; yield 'y'; },
  };
  for await (const v of custom) console.log(v);  // Expected: x then y
  console.log(typeof pages()[Symbol.asyncIterator]); // Expected: function
})();
```

---

## 🔍 Why This Works (3 lines max)
Each `yield` inside an async generator returns a promise-wrapped result, and `for await` waits for it before the next loop iteration. Pages load only when the consumer asks, and `break` stops further fetching.
हिंदी: Consumer जब मांगता है तभी अगला page आता है, और `break` करने पर fetching रुक जाती है।

---

## ⚡ Alternative Solution
```javascript
// Manual iteration without for await
(async () => {
  const it = pages();                            // iterator
  const first = await it.next();                 // await next() yourself
  console.log(first.value, first.done);          // Expected: [ 'item1a', 'item1b' ] false
})();
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: plain for...of on an async generator
// for (const x of pages()) {}   // TypeError: pages(...) is not iterable

// ✅ Correct: for await...of (inside an async function)
(async () => { for await (const x of pages()) { break; } console.log('ok'); })(); // Expected: ok
```

---

## 🎯 Interview Tip (1 line)
Say: "Async generators are ideal for streaming and pagination — pull-based, lazy, with built-in backpressure."

---

## 🔗 Related Questions
→ Q253 (generators) | Q220 (stream large data) | Q182 (infinite scroll) | Q213 (polling)
