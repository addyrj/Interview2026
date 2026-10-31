---

# Q194. Build Data Fetcher Hook
# Category: Real World Problems
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Build a `useFetch(url)`-style data fetcher with `loading`, `data`, `error` states, request cancellation, and ignoring stale responses. First build the framework-free core `createFetcher`, then show the React hook that wraps it.

```javascript
const { data, loading, error } = useFetch('/api/users');
```

---

## 💡 Quick Concept (2 lines only)
State machine: idle -> loading -> success | error; cancel/ignore old requests when the URL changes or the component unmounts.
हिंदी: loading → success/error की state रखो, और URL बदलने या unmount होने पर पुराना request cancel करो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

function createFetcher(fetchFn) {
  let state = { data: null, loading: false, error: null }; // Step 1: current state
  let runId = 0;                                 // id of newest request
  const listeners = new Set();                   // subscribers (React setState etc.)

  const setState = (patch) => {
    state = { ...state, ...patch };              // Step 2: immutable update
    listeners.forEach((l) => l(state));          // notify
  };

  async function load(url) {
    const myId = ++runId;                        // Step 3: tag request
    setState({ loading: true, error: null });    // start loading
    try {
      const data = await fetchFn(url);           // call API
      if (myId === runId) setState({ data, loading: false }); // Step 4: only newest wins
    } catch (error) {
      if (myId === runId) setState({ error: error.message, loading: false }); // newest error only
    }
  }

  return {
    load,
    cancel: () => { runId++; },                  // Step 5: invalidate in-flight request (unmount)
    getState: () => state,
    subscribe: (l) => (listeners.add(l), () => listeners.delete(l)),
  };
}

// ============================================
// TEST CASES
// ============================================

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const api = async (url) => {
  await sleep(url === '/slow' ? 50 : 10);        // /slow is slower
  if (url === '/bad') throw new Error('500 Server Error');
  return `data from ${url}`;
};

const f = createFetcher(api);
f.subscribe((s) => !s.loading && console.log('settled:', JSON.stringify(s))); // log only finished states

(async () => {
  await f.load('/users');
  // Expected: settled: {"data":"data from /users","loading":false,"error":null}
  f.load('/slow');                               // older, slow request
  await f.load('/fast');                         // newer request finishes first
  await sleep(80);                               // /slow resolves later but is ignored
  console.log(f.getState().data);                // Expected: settled: {"data":"data from /fast","loading":false,"error":null}  then  data from /fast
  await f.load('/bad');
  console.log(f.getState().error);               // Expected: settled: {..."error":"500 Server Error"}  then  500 Server Error
})();
```

---

## 🔍 Why This Works (3 lines max)
The `runId` check makes out-of-order responses harmless, and `cancel()` bumping it protects after unmount. Subscribers get a fresh state object each time, so React re-renders.
हिंदी: runId से पुराने responses ignore हो जाते हैं, और हर बार नया state object बनने से React re-render करता है।

---

## ⚡ Alternative Solution
```javascript
// React hook version using AbortController (browser/React)
function useFetch(url) {
  const [state, setState] = useState({ data: null, loading: true, error: null });
  useEffect(() => {
    const controller = new AbortController();    // cancel on cleanup
    setState({ data: null, loading: true, error: null });
    fetch(url, { signal: controller.signal })
      .then((r) => r.json())
      .then((data) => setState({ data, loading: false, error: null }))
      .catch((e) => e.name !== 'AbortError' && setState({ data: null, loading: false, error: e.message }));
    return () => controller.abort();             // cleanup on url change/unmount
  }, [url]);
  return state;
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: no cleanup -> setState on unmounted component + stale data on fast url change
useEffect(() => { fetch(url).then(r => r.json()).then(setData); }, [url]);

// ✅ Correct: AbortController (or an `ignore` flag) in the cleanup function
```

---

## 🎯 Interview Tip (1 line)
Mention race conditions, AbortController cleanup, and that libraries like React Query/SWR add caching + dedupe.

---

## 🔗 Related Questions
→ Q139 (fix race condition) | Q181 (search with debounce) | Q219 (abort fetch) | Q185 (cache with TTL)
