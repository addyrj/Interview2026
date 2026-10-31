---

# Q181. Build Search with Debounce
# Category: Real World Problems
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build a search-box feature: call the API only after the user stops typing for `delay` ms, and ignore stale (out-of-order) responses.

```javascript
const search = createSearch(fetchResults, render, 300);
input.addEventListener('input', e => search(e.target.value));
```

---

## 💡 Quick Concept (2 lines only)
Debounce the keystrokes, then tag each request with an id so only the newest response is rendered.
हिंदी: Typing रुकने पर ही API call करो, और पुराना (stale) response ignore करो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: generic debounce helper
function debounce(fn, delay) {
  let timerId;                                   // holds pending timer
  return function (...args) {
    clearTimeout(timerId);                       // cancel previous call
    timerId = setTimeout(() => fn.apply(this, args), delay); // schedule new one
  };
}

// Step 2: search feature = debounce + stale response guard
function createSearch(fetchFn, onResult, delay) {
  let latestId = 0;                              // id of newest request
  return debounce(async (query) => {             // debounced handler
    const myId = ++latestId;                     // Step 3: tag this request
    const data = await fetchFn(query);           // call API
    if (myId !== latestId) return;               // Step 4: newer request exists -> drop
    onResult(data);                              // render only fresh data
  }, delay);
}

// ============================================
// TEST CASES
// ============================================

const sleep = (ms) => new Promise((r) => setTimeout(r, ms)); // wait helper
const fakeFetch = (q) => sleep(q === 're' ? 50 : 10).then(() => `results for ${q}`); // slow for 're'
const search = createSearch(fakeFetch, (d) => console.log(d), 20); // 20ms debounce

(async () => {
  search('r'); search('re'); search('rea');      // rapid typing
  await sleep(100);                              // Expected: results for rea
  search('re');                                  // fires after 20ms, slow API (50ms)
  await sleep(25);                               // 're' request is now in flight
  search('go');                                  // newer query
  await sleep(150);                              // Expected: results for go  ('re' dropped)
})();
```

---

## 🔍 Why This Works (3 lines max)
Debounce collapses a burst of keystrokes into one call. The `latestId` counter lets slower old responses detect they are outdated and exit silently.
हिंदी: हर request को id मिलती है — सिर्फ latest id वाला response ही screen पर दिखता है।

---

## ⚡ Alternative Solution
```javascript
// Use AbortController to cancel the old request instead of ignoring it
let controller;                                  // current controller
const run = debounce(async (q) => {
  controller?.abort();                           // cancel previous in-flight fetch
  controller = new AbortController();            // new controller
  const res = await fetch(`/api?q=${q}`, { signal: controller.signal });
  render(await res.json());                      // render fresh data
}, 300);
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: debounce created inside handler -> new timer each time, never cancels
input.onchange = (e) => debounce(callApi, 300)(e.target.value);

// ✅ Correct: create debounced function ONCE, reuse it
const debounced = debounce(callApi, 300);
input.oninput = (e) => debounced(e.target.value);
```

---

## 🎯 Interview Tip (1 line)
Mention both debounce AND race-condition handling (stale response / AbortController) — that is what separates senior answers.

---

## 🔗 Related Questions
→ Q081 (debounce) | Q219 (abort fetch) | Q232 (debounce input search) | Q308 (debounce real use case)
