---

# Q210. Async Map with Limit
# Category: Async Challenges
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Implement `mapLimit(array, limit, asyncFn)` — like `Promise.all(array.map(fn))` but with at most `limit` calls in flight. Results must be in input order. If any call rejects, reject the whole thing.

```javascript
await mapLimit([1, 2, 3, 4, 5], 2, async n => n * 2); // [2, 4, 6, 8, 10]
```

---

## 💡 Quick Concept (2 lines only)
Spawn `limit` workers sharing a cursor; each worker maps the next item and stores the result at its index.
हिंदी: `limit` workers एक साझा index से items उठाते हैं और result सही position पर रखते हैं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: allocate results array and shared cursor
// Step 2: worker loops: take index, await fn, store result
// Step 3: run `limit` workers; any rejection propagates via Promise.all

async function mapLimit(array, limit, fn) {
  const results = new Array(array.length);            // output keeps input order
  let cursor = 0;                                     // next index to process

  async function worker() {
    while (cursor < array.length) {                   // while work remains
      const i = cursor++;                             // claim an index
      results[i] = await fn(array[i], i);             // map and store at same index
    }
  }

  const count = Math.min(limit, array.length);        // no idle workers
  await Promise.all(Array.from({ length: count }, worker)); // wait for all workers
  return results;                                     // ordered results
}

// ============================================
// TEST CASES
// ============================================

let active = 0, peak = 0;                             // concurrency tracking
const slowDouble = async n => {
  active++; peak = Math.max(peak, active);            // record peak concurrency
  await new Promise(r => setTimeout(r, 50 - n * 5));  // bigger n finishes faster
  active--;
  return n * 2;                                       // mapped value
};

(async () => {
  const out = await mapLimit([1, 2, 3, 4, 5, 6], 3, slowDouble);
  console.log(out);                                   // Expected: [ 2, 4, 6, 8, 10, 12 ]
  console.log('peak:', peak);                         // Expected: peak: 3

  console.log(await mapLimit([], 3, slowDouble));     // Expected: []

  try {
    await mapLimit([1, 2, 3], 2, async n => {
      if (n === 2) throw new Error('bad item');       // item 2 fails
      return n;
    });
  } catch (e) {
    console.log(e.message);                           // Expected: bad item
  }
})();
```

---

## 🔍 Why This Works (3 lines max)
Workers pull items on demand, so concurrency never exceeds `limit` while slots are refilled instantly. Writing to `results[i]` guarantees output order regardless of finish order.
हिंदी: Index पर लिखने से output का क्रम input जैसा रहता है, चाहे कोई भी task पहले खत्म हो।

---

## ⚡ Alternative Solution (if exists)
```javascript
// Chunked version (simpler, but slower: waits for slowest in each chunk)
async function mapChunked(array, size, fn) {
  const out = [];
  for (let i = 0; i < array.length; i += size) {
    const chunk = array.slice(i, i + size);           // next batch
    out.push(...await Promise.all(chunk.map(fn)));    // run batch in parallel
  }
  return out;
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: results.push() in completion order -> scrambled output
results.push(await fn(item));

// ✅ Correct: write to results[i]
results[i] = await fn(array[i], i);
```

---

## 🎯 Interview Tip (1 line)
Mention real uses: uploading files, hitting rate-limited APIs, DB bulk inserts — and libraries like `p-limit`.

---

## 🔗 Related Questions
→ Q203 (limit concurrent) | Q217 (batch API calls) | Q112 (implement map) | Q216 (queue tasks)
