# Async Challenges Q201–Q220
# Quick Revision Cheatsheet

---

## ⏱️ Event Loop Order Recap (Q011–Q017)

```javascript
// Order rule: sync → process.nextTick → microtasks (promise / queueMicrotask / await) → macrotasks (timers, I/O, setImmediate)

// Q011: sync → microtask → macrotask
console.log('1'); setTimeout(() => console.log('2'), 0);
Promise.resolve().then(() => console.log('3')); console.log('4');
// Output: 1, 4, 3, 2

// Q012: await ke pehle ka code sync hota hai
async function main() { console.log('1'); await Promise.resolve(); console.log('2'); }
console.log('3'); main(); console.log('4');
// Output: 3, 1, 4, 2

// Q013: microtask ke andar naya timer sabse last
console.log('A'); setTimeout(() => console.log('B'), 0);
Promise.resolve().then(() => { console.log('C'); setTimeout(() => console.log('D'), 0); }).then(() => console.log('E'));
setTimeout(() => console.log('F'), 0); console.log('G');
// Output: A, G, C, E, B, F, D

// Q014: nextTick promise se pehle
console.log('start'); setTimeout(() => console.log('timeout'), 0);
Promise.resolve().then(() => console.log('promise')); process.nextTick(() => console.log('nextTick')); console.log('end');
// Output: start, end, nextTick, promise, timeout

// Q015: I/O callback ke andar
fs.readFile(__filename, () => { setTimeout(() => console.log('timeout'), 0); setImmediate(() => console.log('immediate')); });
// Output: immediate, timeout

// Q016: microtask queue poori khali hoti hai (nested bhi) phir macrotask
setTimeout(() => console.log('macro 1'), 0); setTimeout(() => console.log('macro 2'), 0);
queueMicrotask(() => { console.log('micro 1'); queueMicrotask(() => console.log('micro 3')); });
queueMicrotask(() => console.log('micro 2')); console.log('sync');
// Output: sync, micro 1, micro 2, micro 3, macro 1, macro 2

// Q017: mixed
console.log('1'); setTimeout(() => console.log('2'), 0);
new Promise(res => { console.log('3'); res(); }).then(() => console.log('4'));
(async () => { console.log('5'); await null; console.log('6'); })();
process.nextTick(() => console.log('7')); console.log('8');
// Output: 1, 3, 5, 8, 7, 4, 6, 2
```

---

## 🔗 Running Tasks (Q201–Q203)

```javascript
// Q201: Sequential (ek ke baad ek)
async function runSequentially(tasks) {
  const results = [];
  for (const task of tasks) results.push(await task());
  return results;
}
// tasks = [() => p1, () => p2] → total time = sum

// Q202: Parallel (sab ek saath; order input jaisa)
const runInParallel = tasks => Promise.all(tasks.map(t => t()));
// total time = slowest task

// Q203: Concurrency limit (worker pool)
async function runWithLimit(tasks, limit) {
  const results = new Array(tasks.length);
  let next = 0;
  async function worker() {
    while (next < tasks.length) { const i = next++; results[i] = await tasks[i](); }
  }
  await Promise.all(Array.from({ length: Math.min(limit, tasks.length) }, worker));
  return results;
}
// await runWithLimit(tasks, 2) → max 2 ek saath, order preserved
```

---

## 🛡️ Retry / Timeout / Cancel (Q204–Q206)

```javascript
// Q204: Retry (total calls = retries + 1)
const sleep = ms => new Promise(r => setTimeout(r, ms));
async function retry(fn, retries = 3, delay = 100) {
  let lastError;
  for (let attempt = 0; attempt <= retries; attempt++) {
    try { return await fn(attempt); }
    catch (err) { lastError = err; if (attempt < retries) await sleep(delay); }
  }
  throw lastError;
}
// await retry(flaky, 3, 100)

// Q205: Timeout a promise (race + clearTimeout in finally)
function withTimeout(promise, ms) {
  let id;
  const timeout = new Promise((_, rej) => { id = setTimeout(() => rej(new Error(`Timeout after ${ms}ms`)), ms); });
  return Promise.race([promise, timeout]).finally(() => clearTimeout(id));
}
// await withTimeout(slowCall(), 1000) → 1s me na aaye to Error('Timeout after 1000ms')

// Q206: Cancel a promise (real request cancel nahi, sirf result ignore)
function makeCancellable(promise) {
  let cancelled = false, rejectWrapper;
  const wrapped = new Promise((resolve, reject) => {
    rejectWrapper = reject;
    promise.then(v => { if (!cancelled) resolve(v); }, e => { if (!cancelled) reject(e); });
  });
  return { promise: wrapped, cancel() { cancelled = true; rejectWrapper(new Error('Cancelled')); } };
}
// const { promise, cancel } = makeCancellable(p); cancel() → promise rejects 'Cancelled'
```

---

## 🧵 Chaining & Errors (Q207–Q209)

```javascript
// Q207: Chain dependent calls (har step pichle ka result use karta hai)
async function getUserSummary(id) {
  const user = await getUser(id);
  const posts = await getPosts(user);
  const comments = await getComments(posts[0]);
  return `${user.name} wrote "${posts[0].title}" with ${comments.length} comments`;
}
// .then version: inner promise return karo to chain flat rehti hai

// Q208: Multiple errors — allSettled se index ke saath collect
async function collect(tasks) {
  const settled = await Promise.allSettled(tasks.map(t => t()));
  const results = [], errors = [];
  settled.forEach((s, index) => s.status === 'fulfilled'
    ? results.push(s.value) : errors.push({ index, message: s.reason.message }));
  return { results, errors };
}
// → { results: [...], errors: [{ index: 1, message: '...' }] }

// Q209: Async reduce (sequential, acc await hota hai)
async function asyncReduce(array, fn, initial) {
  let acc = initial;
  for (let i = 0; i < array.length; i++) acc = await fn(acc, array[i], i, array);
  return acc;
}
// await asyncReduce([1, 2, 3], async (a, x) => a + x, 0) → 6
```

---

## 🗺️ Map / Waterfall / Fallback / Polling (Q210–Q213)

```javascript
// Q210: Async map with limit (order preserved)
async function mapLimit(array, limit, fn) {
  const results = new Array(array.length);
  let cursor = 0;
  async function worker() {
    while (cursor < array.length) { const i = cursor++; results[i] = await fn(array[i], i); }
  }
  await Promise.all(Array.from({ length: Math.min(limit, array.length) }, worker));
  return results;
}
// await mapLimit(ids, 3, fetchUser) → max 3 parallel

// Q211: Waterfall (output → next ka input)
async function waterfall(tasks, initial) {
  let value = initial;
  for (const task of tasks) value = await task(value);
  return value;
}
// await waterfall([async x => x + 1, async x => x * 2], 5) → 12

// Q212: Race with fallback (fail ya timeout → fallback)
async function fetchWithFallback(primary, fallback, ms) {
  let id;
  const timeout = new Promise((_, rej) => { id = setTimeout(() => rej(new Error('timeout')), ms); });
  try { return await Promise.race([primary(), timeout]); }
  catch (err) { return fallback(); }
  finally { clearTimeout(id); }
}
// await fetchWithFallback(api, cache, 500)

// Q213: Polling (condition poori hone tak)
const sleep3 = ms => new Promise(r => setTimeout(r, ms));
async function poll(fn, { interval = 100, maxAttempts = 5, until = Boolean } = {}) {
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    const result = await fn(attempt);
    if (until(result)) return result;
    if (attempt < maxAttempts) await sleep3(interval);
  }
  throw new Error(`Polling gave up after ${maxAttempts} attempts`);
}
// await poll(checkJob, { until: r => r.done })
```

---

## 🧠 Debounce / Memoize / Queue / Batch / Cache (Q214–Q218)

```javascript
// Q214: Debounce async (saare callers ko ek hi result milta hai)
function debounceAsync(fn, wait) {
  let timerId = null, pending = [];
  return function (...args) {
    return new Promise((resolve, reject) => {
      pending.push({ resolve, reject });
      clearTimeout(timerId);
      timerId = setTimeout(async () => {
        const callers = pending; pending = [];
        try { const r = await fn.apply(this, args); callers.forEach(c => c.resolve(r)); }
        catch (e) { callers.forEach(c => c.reject(e)); }
      }, wait);
    });
  };
}
// const s = debounceAsync(search, 200); s('a'); s('ab') → dono ko 'ab' ka result

// Q215: Memoize async (promise cache; fail pe entry hatao)
function memoizeAsync(fn) {
  const cache = new Map();
  return function (...args) {
    const key = JSON.stringify(args);
    if (cache.has(key)) return cache.get(key);
    const p = fn.apply(this, args).catch(err => { cache.delete(key); throw err; });
    cache.set(key, p);
    return p;
  };
}
// same args ki 2 parallel calls → fn sirf ek baar

// Q216: Async task queue
class AsyncQueue {
  constructor(concurrency = 1) { this.concurrency = concurrency; this.running = 0; this.queue = []; }
  add(task) {
    return new Promise((resolve, reject) => { this.queue.push({ task, resolve, reject }); this._next(); });
  }
  _next() {
    while (this.running < this.concurrency && this.queue.length) {
      const { task, resolve, reject } = this.queue.shift();
      this.running++;
      task().then(resolve, reject).finally(() => { this.running--; this._next(); });
    }
  }
}
// new AsyncQueue(2).add(() => job())

// Q217: Batch API calls (chunks me, sequential)
function chunk(array, size) {
  const out = [];
  for (let i = 0; i < array.length; i += size) out.push(array.slice(i, i + size));
  return out;
}
async function batchFetch(ids, size, fetchBatch) {
  const results = [];
  for (const group of chunk(ids, size)) results.push(...await fetchBatch(group));
  return results;
}
// await batchFetch([1,2,3,4,5], 2, api) → 3 API calls

// Q218: Cached fetcher with TTL
function createCachedFetcher(fetchFn, ttl) {
  const cache = new Map();
  async function get(url) {
    const e = cache.get(url);
    if (e && Date.now() < e.expiresAt) return e.promise;
    const promise = fetchFn(url);
    cache.set(url, { promise, expiresAt: Date.now() + ttl });
    try { return await promise; } catch (err) { cache.delete(url); throw err; }
  }
  get.clear = () => cache.clear();
  return get;
}
// const f = createCachedFetcher(fetchFn, 5000); f(url); f(url) → ek hi network call
```

---

## 🌊 Abort & Streams (Q219–Q220)

```javascript
// Q219: Abort fetch (AbortController / AbortSignal.timeout)
async function fetchJson(url, { signal } = {}) {
  try {
    const res = await fetch(url, { signal });
    return await res.json();
  } catch (err) {
    if (err.name === 'AbortError') return 'aborted';
    if (err.name === 'TimeoutError') return 'timed out';
    throw err;
  }
}
// const ac = new AbortController(); fetchJson(url, { signal: ac.signal }); ac.abort() → 'aborted'
// fetchJson(url, { signal: AbortSignal.timeout(100) }) → 'timed out'

// Q220: Stream large data (chunk boundary pe line toot sakti hai → leftover rakho)
async function summarize(stream) {
  let leftover = '', lines = 0, sum = 0, chunks = 0;
  const handle = line => { if (line === '') return; lines++; sum += Number(line); };
  for await (const chunk of stream) {
    chunks++;
    const parts = (leftover + chunk).split('\n');
    leftover = parts.pop();          // aakhri adhoori line agle chunk ke saath judegi
    parts.forEach(handle);
  }
  handle(leftover);
  return { lines, sum, chunks };
}
// await summarize(new ReadableStream({...})) → { lines, sum, chunks } (for await ReadableStream: Node 18+)
```
