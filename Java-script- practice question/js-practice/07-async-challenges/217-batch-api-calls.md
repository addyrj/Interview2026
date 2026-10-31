---

# Q217. Batch API Calls
# Category: Async Challenges
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
You have 10 ids and an API that accepts at most 4 ids per request. Split the ids into batches, call the API once per batch (batches in order), and return one flat result array in the original order.

```javascript
await batchFetch([1,2,3,4,5,6,7,8,9,10], 4, fetchUsersByIds);
```

---

## 💡 Quick Concept (2 lines only)
Chunk the input, call the API per chunk, then flatten. Run chunks sequentially to be gentle on the server, or with `Promise.all` for speed.
हिंदी: Ids को chunks में बाँटो, हर chunk पर एक API call करो, फिर results को flat कर दो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: split ids into chunks of `size`
// Step 2: call the batch API for each chunk (sequentially)
// Step 3: flatten into a single ordered array

function chunk(array, size) {
  const chunks = [];                                  // result chunks
  for (let i = 0; i < array.length; i += size) {      // jump by `size`
    chunks.push(array.slice(i, i + size));            // take one chunk
  }
  return chunks;
}

async function batchFetch(ids, size, fetchBatch) {
  const results = [];                                 // flat output
  for (const group of chunk(ids, size)) {             // one request per chunk
    const data = await fetchBatch(group);             // wait for this batch
    results.push(...data);                            // append in order
  }
  return results;
}

// ============================================
// TEST CASES
// ============================================

let requests = 0;                                     // number of API calls made
const fetchUsersByIds = async ids => {
  requests++;                                         // count the request
  console.log(`request ${requests}:`, ids);           // show the batch
  await new Promise(r => setTimeout(r, 10));          // fake latency
  return ids.map(id => ({ id }));                     // fake users
};

(async () => {
  const users = await batchFetch([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 4, fetchUsersByIds);
  // Expected logs:
  // request 1: [ 1, 2, 3, 4 ]
  // request 2: [ 5, 6, 7, 8 ]
  // request 3: [ 9, 10 ]
  console.log(users.length, users[9]);                // Expected: 10 { id: 10 }
  console.log('requests:', requests);                 // Expected: requests: 3

  console.log(await batchFetch([], 4, fetchUsersByIds)); // Expected: []
})();
```

---

## 🔍 Why This Works (3 lines max)
`slice` makes consistent chunks (the last one may be smaller). Sequential awaiting keeps order and limits load; 10 ids become 3 requests instead of 10.
हिंदी: 10 ids के लिए 10 की जगह सिर्फ 3 requests लगती हैं, और order बना रहता है।

---

## ⚡ Alternative Solution (if exists)
```javascript
// Parallel batches (faster; order preserved by Promise.all)
async function batchFetchParallel(ids, size, fetchBatch) {
  const groups = chunk(ids, size);                    // reuse chunk()
  const responses = await Promise.all(groups.map(fetchBatch)); // all batches at once
  return responses.flat();                            // flatten one level
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: one request per id (N+1 problem) — slow, may hit rate limits
await Promise.all(ids.map(id => fetchUser(id)));

// ✅ Correct: batch ids so requests = ceil(N / size)
```

---

## 🎯 Interview Tip (1 line)
Mention DataLoader-style batching: collect ids during one tick, then send one request.

---

## 🔗 Related Questions
→ Q060 (chunk array) | Q210 (async map with limit) | Q184 (request queue) | Q186 (rate limiter)
