# Implement / Build Q051–Q120
# Quick Revision Cheatsheet (shortest correct version of each)

---

## 🔤 Strings (Q051–Q054)

```javascript
// Q051: Reverse string
const reverseString = s => [...s].reverse().join('');
// reverseString('abc') → 'cba'

// Q052: Reverse words
const reverseWords = s => s.trim().split(/\s+/).reverse().join(' ');
// reverseWords('  hello   world ') → 'world hello'

// Q053: Palindrome
function isPalindrome(str) {
  const c = str.toLowerCase().replace(/[^a-z0-9]/g, '');
  return c === [...c].reverse().join('');
}
// isPalindrome('A man, a plan, a canal: Panama') → true

// Q054: Count vowels
const countVowels = s => (s.match(/[aeiou]/gi) || []).length;
// countVowels('Hello World') → 3
```

---

## 📚 Arrays (Q055–Q070)

```javascript
// Q055: Remove duplicates
const removeDuplicates = arr => [...new Set(arr)];
// removeDuplicates([1, 2, 2, 3]) → [1, 2, 3]

// Q056: Find max
const findMax = arr => arr.length ? Math.max(...arr) : undefined;
// findMax([3, 9, 2]) → 9

// Q057: Find min
const findMin = arr => arr.length ? Math.min(...arr) : undefined;
// findMin([3, 9, 2]) → 2

// Q058: Flatten (1 level)
const flatten = arr => [].concat(...arr);
// flatten([1, [2, 3], [4]]) → [1, 2, 3, 4]

// Q059: Deep flatten
const deepFlatten = arr => arr.reduce((a, x) => a.concat(Array.isArray(x) ? deepFlatten(x) : x), []);
// deepFlatten([1, [2, [3, [4]]]]) → [1, 2, 3, 4]

// Q060: Chunk
function chunk(arr, size) {
  const out = [];
  for (let i = 0; i < arr.length; i += size) out.push(arr.slice(i, i + size));
  return out;
}
// chunk([1, 2, 3, 4, 5], 2) → [[1, 2], [3, 4], [5]]

// Q061: Zip
const zip = (a, b) => a.slice(0, Math.min(a.length, b.length)).map((x, i) => [x, b[i]]);
// zip([1, 2, 3], ['a', 'b']) → [[1, 'a'], [2, 'b']]

// Q062: Intersection
const intersection = (a, b) => { const s = new Set(b); return [...new Set(a.filter(x => s.has(x)))]; };
// intersection([1, 2, 3], [2, 3, 4]) → [2, 3]

// Q063: Difference
const difference = (a, b) => { const s = new Set(b); return a.filter(x => !s.has(x)); };
// difference([1, 2, 3], [2]) → [1, 3]

// Q064: Group by property / fn
const groupBy = (arr, k) => arr.reduce((acc, x) => {
  const g = typeof k === 'function' ? k(x) : x[k];
  (acc[g] ||= []).push(x);
  return acc;
}, {});
// groupBy([{t:'a'},{t:'b'},{t:'a'}], 't') → { a: [..2], b: [..1] }

// Q065: Sort array of objects
const sortBy = (arr, key, order = 'asc') =>
  [...arr].sort((a, b) => (a[key] < b[key] ? -1 : a[key] > b[key] ? 1 : 0) * (order === 'desc' ? -1 : 1));
// sortBy([{n:2},{n:1}], 'n') → [{n:1},{n:2}]

// Q066: Count occurrences
const countOccurrences = arr => arr.reduce((f, x) => (f[x] = (f[x] || 0) + 1, f), {});
// countOccurrences(['a', 'b', 'a']) → { a: 2, b: 1 }

// Q067: Find duplicates
function findDuplicates(arr) {
  const seen = new Set(), dupes = new Set();
  for (const x of arr) seen.has(x) ? dupes.add(x) : seen.add(x);
  return [...dupes];
}
// findDuplicates([1, 2, 2, 3, 3, 3]) → [2, 3]

// Q068: Remove falsy
const compact = arr => arr.filter(Boolean);
// compact([0, 1, '', 'a', null, NaN]) → [1, 'a']

// Q069: Unique by key
function uniqueBy(arr, fn = x => x) {
  const seen = new Set();
  return arr.filter(x => { const k = fn(x); return seen.has(k) ? false : (seen.add(k), true); });
}
// uniqueBy([{id:1},{id:1},{id:2}], o => o.id) → [{id:1},{id:2}]

// Q070: Rotate right by k
function rotate(arr, k) {
  const n = arr.length;
  if (!n) return [];
  const s = ((k % n) + n) % n;
  return [...arr.slice(n - s), ...arr.slice(0, n - s)];
}
// rotate([1, 2, 3, 4, 5], 2) → [4, 5, 1, 2, 3]
```

---

## 🗂️ Objects (Q071–Q080)

```javascript
// Q071: Deep clone (circular safe)
function deepClone(v, seen = new WeakMap()) {
  if (v === null || typeof v !== 'object') return v;
  if (v instanceof Date) return new Date(v);
  if (seen.has(v)) return seen.get(v);
  const copy = Array.isArray(v) ? [] : {};
  seen.set(v, copy);
  for (const k of Object.keys(v)) copy[k] = deepClone(v[k], seen);
  return copy;
}
// deepClone({ a: { b: 1 } }).a !== orig.a → true   (ya structuredClone)

// Q072: Deep merge
const isPlain = v => v !== null && typeof v === 'object' && !Array.isArray(v);
function deepMerge(a, b) {
  const r = { ...a };
  for (const k of Object.keys(b)) r[k] = isPlain(a[k]) && isPlain(b[k]) ? deepMerge(a[k], b[k]) : b[k];
  return r;
}
// deepMerge({ a: { x: 1 } }, { a: { y: 2 } }) → { a: { x: 1, y: 2 } }

// Q073: Flatten nested object
function flattenObject(obj, prefix = '', out = {}) {
  for (const k of Object.keys(obj)) {
    const p = prefix ? `${prefix}.${k}` : k, v = obj[k];
    if (v !== null && typeof v === 'object' && !Array.isArray(v)) flattenObject(v, p, out);
    else out[p] = v;
  }
  return out;
}
// flattenObject({ a: { b: 1, c: { d: 2 } } }) → { 'a.b': 1, 'a.c.d': 2 }

// Q074: Get value by path
function get(obj, path, def) {
  const keys = path.replace(/\[(\w+)\]/g, '.$1').split('.').filter(Boolean);
  let cur = obj;
  for (const k of keys) { if (cur == null) return def; cur = cur[k]; }
  return cur === undefined ? def : cur;
}
// get({ a: { b: [{ c: 5 }] } }, 'a.b[0].c') → 5

// Q075: Omit keys
const omit = (obj, keys) => Object.fromEntries(Object.entries(obj).filter(([k]) => !keys.includes(k)));
// omit({ a: 1, b: 2 }, ['a']) → { b: 2 }

// Q076: Pick keys
const pick = (obj, keys) => Object.fromEntries(keys.filter(k => Object.hasOwn(obj, k)).map(k => [k, obj[k]]));
// pick({ a: 1, b: 2 }, ['a']) → { a: 1 }

// Q077: Is object empty
const isEmpty = o => o == null || (typeof o === 'object' && Object.keys(o).length === 0);
// isEmpty({}) → true, isEmpty({ a: 1 }) → false

// Q078: Deep equal
function deepEqual(a, b) {
  if (a === b || (Number.isNaN(a) && Number.isNaN(b))) return true;
  if (typeof a !== 'object' || typeof b !== 'object' || !a || !b) return false;
  if (Array.isArray(a) !== Array.isArray(b)) return false;
  const ka = Object.keys(a);
  return ka.length === Object.keys(b).length && ka.every(k => Object.hasOwn(b, k) && deepEqual(a[k], b[k]));
}
// deepEqual({ a: [1, { b: 2 }] }, { a: [1, { b: 2 }] }) → true

// Q079: Count key occurrences (nested)
function countKey(obj, key) {
  if (obj === null || typeof obj !== 'object') return 0;
  let n = !Array.isArray(obj) && Object.hasOwn(obj, key) ? 1 : 0;
  for (const c of Object.values(obj)) n += countKey(c, key);
  return n;
}
// countKey({ id: 1, a: { id: 2 }, b: [{ id: 3 }] }, 'id') → 3

// Q080: Transform keys (deep)
function transformKeys(v, fn) {
  if (Array.isArray(v)) return v.map(x => transformKeys(x, fn));
  if (v === null || typeof v !== 'object') return v;
  return Object.fromEntries(Object.entries(v).map(([k, x]) => [fn(k), transformKeys(x, fn)]));
}
const toCamel = s => s.replace(/_([a-z])/g, (_, c) => c.toUpperCase());
// transformKeys({ user_name: 'A' }, toCamel) → { userName: 'A' }
```

---

## 🛠️ Function Utilities (Q081–Q090)

```javascript
// Q081: Debounce — last call ke delay baad chalta hai
function debounce(fn, delay) {
  let t;
  return function (...args) { clearTimeout(t); t = setTimeout(() => fn.apply(this, args), delay); };
}
// const d = debounce(search, 300); d('a'); d('ab');  → search sirf 'ab' ke saath, ek baar

// Q082: Throttle — limit me max ek baar
function throttle(fn, limit) {
  let last = 0;
  return function (...args) {
    const now = Date.now();
    if (now - last >= limit) { last = now; return fn.apply(this, args); }
  };
}
// const t = throttle(onScroll, 200);  → 200ms me ek baar

// Q083: Memoize
function memoize(fn) {
  const cache = new Map();
  return function (...args) {
    const k = JSON.stringify(args);
    if (!cache.has(k)) cache.set(k, fn.apply(this, args));
    return cache.get(k);
  };
}
// const fastSq = memoize(x => x * x); fastSq(4); fastSq(4) → 2nd call cache se

// Q084: Curry
function curry(fn) {
  return function curried(...args) {
    return args.length >= fn.length ? fn.apply(this, args) : (...more) => curried.apply(this, [...args, ...more]);
  };
}
// curry((a, b, c) => a + b + c)(1)(2)(3) → 6

// Q085: Compose (right → left)
const compose = (...fns) => x => fns.reduceRight((acc, f) => f(acc), x);
// compose(x => x + 1, x => x * 2)(5) → 11

// Q086: Pipe (left → right)
const pipe = (...fns) => x => fns.reduce((acc, f) => f(acc), x);
// pipe(x => x + 1, x => x * 2)(5) → 12

// Q087: Once
function once(fn) {
  let called = false, result;
  return function (...args) {
    if (!called) { called = true; result = fn.apply(this, args); }
    return result;
  };
}
// const init = once(() => 42); init(); init() → dono 42, fn ek baar chala

// Q088: Partial application
const partial = (fn, ...preset) => function (...later) { return fn.apply(this, [...preset, ...later]); };
// partial((a, b, c) => a + b + c, 1, 2)(3) → 6

// Q089: Retry
const sleep = ms => new Promise(r => setTimeout(r, ms));
async function retry(fn, retries, delay) {
  let err;
  for (let i = 0; i <= retries; i++) {
    try { return await fn(i); } catch (e) { err = e; if (i < retries) await sleep(delay); }
  }
  throw err;
}
// await retry(flakyCall, 3, 100) → success ya last error throw

// Q090: Sleep
const sleep2 = ms => new Promise(resolve => setTimeout(resolve, ms));
// await sleep2(500);  → 500ms ruk jao
```

---

## 🤝 Promise Polyfills (Q091–Q095)

```javascript
// Q091: Promise.all
function myPromiseAll(promises) {
  return new Promise((resolve, reject) => {
    if (!promises.length) return resolve([]);
    const res = new Array(promises.length);
    let done = 0;
    promises.forEach((p, i) => Promise.resolve(p).then(v => {
      res[i] = v;
      if (++done === promises.length) resolve(res);
    }, reject));
  });
}
// await myPromiseAll([1, Promise.resolve(2)]) → [1, 2]

// Q092: Promise.race
const myRace = ps => new Promise((resolve, reject) => ps.forEach(p => Promise.resolve(p).then(resolve, reject)));
// await myRace([slow, fast]) → fast ka result

// Q093: Promise.allSettled
function myAllSettled(ps) {
  return Promise.all(ps.map(p => Promise.resolve(p).then(
    value => ({ status: 'fulfilled', value }),
    reason => ({ status: 'rejected', reason })
  )));
}
// await myAllSettled([Promise.resolve(1), Promise.reject('x')]) → [{status:'fulfilled',value:1},{status:'rejected',reason:'x'}]

// Q094: Promise.any
function myAny(ps) {
  return new Promise((resolve, reject) => {
    const errors = []; let failed = 0;
    if (!ps.length) return reject(new AggregateError([], 'All promises were rejected'));
    ps.forEach((p, i) => Promise.resolve(p).then(resolve, e => {
      errors[i] = e;
      if (++failed === ps.length) reject(new AggregateError(errors, 'All promises were rejected'));
    }));
  });
}
// await myAny([Promise.reject(1), Promise.resolve(2)]) → 2

// Q095: Async queue (concurrency limit)
class AsyncQueue {
  constructor(concurrency = 1) { this.c = concurrency; this.running = 0; this.waiting = []; }
  add(task) {
    return new Promise((resolve, reject) => { this.waiting.push({ task, resolve, reject }); this.next(); });
  }
  next() {
    while (this.running < this.c && this.waiting.length) {
      const { task, resolve, reject } = this.waiting.shift();
      this.running++;
      task().then(resolve, reject).finally(() => { this.running--; this.next(); });
    }
  }
}
// const q = new AsyncQueue(2); q.add(() => fetchX());  → max 2 ek saath
```

---

## 📡 Event Patterns (Q096–Q098)

```javascript
// Q096: EventEmitter
class EventEmitter {
  constructor() { this.events = {}; }
  on(e, fn) { (this.events[e] ||= []).push(fn); return this; }
  off(e, fn) { this.events[e] = (this.events[e] || []).filter(f => f !== fn); return this; }
  emit(e, ...args) { (this.events[e] || []).slice().forEach(fn => fn.apply(this, args)); return !!this.events[e]?.length; }
  once(e, fn) { const w = (...a) => { this.off(e, w); fn.apply(this, a); }; return this.on(e, w); }
}
// em.on('hi', console.log); em.emit('hi', 1) → logs 1

// Q097: Pub/Sub
class PubSub {
  constructor() { this.topics = new Map(); }
  subscribe(topic, cb) {
    if (!this.topics.has(topic)) this.topics.set(topic, new Set());
    this.topics.get(topic).add(cb);
    return () => this.topics.get(topic)?.delete(cb);   // unsubscribe fn
  }
  publish(topic, data) { [...(this.topics.get(topic) || [])].forEach(cb => cb(data)); }
}
// const off = ps.subscribe('news', console.log); ps.publish('news', 'hi'); off();

// Q098: Observable (minimal)
class Observable {
  constructor(producer) { this.producer = producer; }
  subscribe(next) {
    let closed = false;
    const cleanup = this.producer({ next: v => { if (!closed) next(v); } });
    return { unsubscribe: () => { closed = true; if (typeof cleanup === 'function') cleanup(); } };
  }
  map(fn) { return new Observable(o => this.subscribe(v => o.next(fn(v))).unsubscribe); }
}
// new Observable(o => { o.next(1); o.next(2); }).map(x => x * 2).subscribe(console.log) → 2, 4
```

---

## 🧱 Data Structures & Sorting (Q099–Q106)

```javascript
// Q099: LRU Cache (Map insertion order)
class LRUCache {
  constructor(cap) { this.cap = cap; this.m = new Map(); }
  get(k) {
    if (!this.m.has(k)) return -1;
    const v = this.m.get(k); this.m.delete(k); this.m.set(k, v);
    return v;
  }
  put(k, v) {
    this.m.delete(k);
    if (this.m.size >= this.cap) this.m.delete(this.m.keys().next().value);
    this.m.set(k, v);
  }
}
// c = new LRUCache(2); c.put(1,1); c.put(2,2); c.get(1); c.put(3,3); c.get(2) → -1

// Q100: Stack
class Stack {
  #items = [];
  push(x) { this.#items.push(x); return this; }
  pop() { return this.#items.pop(); }
  peek() { return this.#items.at(-1); }
  isEmpty() { return this.#items.length === 0; }
  size() { return this.#items.length; }
}
// new Stack().push(1).push(2).pop() → 2

// Q101: Queue
class Queue {
  constructor() { this.items = []; }
  enqueue(x) { this.items.push(x); return this; }
  dequeue() { return this.items.shift(); }
  peek() { return this.items[0]; }
  isEmpty() { return this.items.length === 0; }
  size() { return this.items.length; }
}
// new Queue().enqueue(1).enqueue(2).dequeue() → 1

// Q102: Linked list
class Node { constructor(value) { this.value = value; this.next = null; } }
class LinkedList {
  constructor() { this.head = null; }
  append(v) {
    const n = new Node(v);
    if (!this.head) { this.head = n; return this; }
    let c = this.head; while (c.next) c = c.next;
    c.next = n; return this;
  }
  reverse() {
    let prev = null, cur = this.head;
    while (cur) { [cur.next, prev, cur] = [prev, cur, cur.next]; }
    this.head = prev; return this;
  }
  toArray() { const out = []; for (let c = this.head; c; c = c.next) out.push(c.value); return out; }
}
// new LinkedList().append(1).append(2).reverse().toArray() → [2, 1]

// Q103: Binary search (sorted array)
function binarySearch(arr, target) {
  let lo = 0, hi = arr.length - 1;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    if (arr[mid] === target) return mid;
    arr[mid] < target ? (lo = mid + 1) : (hi = mid - 1);
  }
  return -1;
}
// binarySearch([1, 3, 5, 7], 5) → 2

// Q104: Bubble sort
function bubbleSort(arr) {
  const a = [...arr];
  for (let i = 0; i < a.length - 1; i++) {
    let swapped = false;
    for (let j = 0; j < a.length - 1 - i; j++)
      if (a[j] > a[j + 1]) { [a[j], a[j + 1]] = [a[j + 1], a[j]]; swapped = true; }
    if (!swapped) break;
  }
  return a;
}
// bubbleSort([3, 1, 2]) → [1, 2, 3]

// Q105: Quick sort
function quickSort(arr) {
  if (arr.length <= 1) return arr;
  const p = arr[arr.length >> 1];
  return [...quickSort(arr.filter(x => x < p)), ...arr.filter(x => x === p), ...quickSort(arr.filter(x => x > p))];
}
// quickSort([3, 6, 1, 3]) → [1, 3, 3, 6]

// Q106: Merge sort
function mergeSort(arr) {
  if (arr.length <= 1) return arr;
  const mid = arr.length >> 1, l = mergeSort(arr.slice(0, mid)), r = mergeSort(arr.slice(mid)), out = [];
  let i = 0, j = 0;
  while (i < l.length && j < r.length) out.push(l[i] <= r[j] ? l[i++] : r[j++]);
  return [...out, ...l.slice(i), ...r.slice(j)];
}
// mergeSort([5, 2, 4, 1]) → [1, 2, 4, 5]
```

---

## 🧰 Polyfills: call / apply / bind / new / create (Q107–Q111)

```javascript
// Q107: call — function ko temporary method bana do
Function.prototype.myCall = function (ctx, ...args) {
  ctx = ctx == null ? globalThis : Object(ctx);
  const k = Symbol('fn'); ctx[k] = this;
  const r = ctx[k](...args); delete ctx[k];
  return r;
};
// greet.myCall({ name: 'A' }, 'Hi')

// Q108: apply — call jaisa, args array me
Function.prototype.myApply = function (ctx, arr) {
  ctx = ctx == null ? globalThis : Object(ctx);
  const k = Symbol('fn'); ctx[k] = this;
  const r = arr == null ? ctx[k]() : ctx[k](...arr); delete ctx[k];
  return r;
};
// greet.myApply({ name: 'A' }, ['Hi'])

// Q109: bind — new ke saath bound ctx ignore
Function.prototype.myBind = function (ctx, ...bound) {
  const fn = this;
  function b(...rest) { return fn.apply(this instanceof b ? this : ctx, [...bound, ...rest]); }
  b.prototype = Object.create(fn.prototype);
  return b;
};
// const f = greet.myBind({ name: 'A' }, 'Hi'); f('!')

// Q110: new keyword
function myNew(C, ...args) {
  const obj = Object.create(C.prototype);
  const r = C.apply(obj, args);
  return r !== null && (typeof r === 'object' || typeof r === 'function') ? r : obj;
}
// myNew(Person, 'A') → Person { name: 'A' }

// Q111: Object.create
function myCreate(proto, props) {
  function F() {}
  F.prototype = proto;
  const obj = new F();
  if (proto === null) Object.setPrototypeOf(obj, null);
  if (props) Object.defineProperties(obj, props);
  return obj;
}
// Object.getPrototypeOf(myCreate(p)) === p → true
```

---

## 🧮 Array Method Polyfills (Q112–Q117)

```javascript
// Q112: map
Array.prototype.myMap = function (cb, thisArg) {
  const r = new Array(this.length);
  for (let i = 0; i < this.length; i++) if (i in this) r[i] = cb.call(thisArg, this[i], i, this);
  return r;
};
// [1, 2, 3].myMap(x => x * 2) → [2, 4, 6]

// Q113: filter
Array.prototype.myFilter = function (cb, thisArg) {
  const r = [];
  for (let i = 0; i < this.length; i++) if (i in this && cb.call(thisArg, this[i], i, this)) r.push(this[i]);
  return r;
};
// [1, 2, 3, 4].myFilter(x => x % 2 === 0) → [2, 4]

// Q114: reduce (initialValue check = arguments.length)
Array.prototype.myReduce = function (cb, init) {
  let acc, i = 0;
  if (arguments.length >= 2) acc = init;
  else { if (!this.length) throw new TypeError('Reduce of empty array with no initial value'); acc = this[0]; i = 1; }
  for (; i < this.length; i++) if (i in this) acc = cb(acc, this[i], i, this);
  return acc;
};
// [1, 2, 3].myReduce((a, b) => a + b, 0) → 6

// Q115: forEach
Array.prototype.myForEach = function (cb, thisArg) {
  for (let i = 0; i < this.length; i++) if (i in this) cb.call(thisArg, this[i], i, this);
};
// [1, 2].myForEach(x => console.log(x)) → 1, 2 (return undefined)

// Q116: find
Array.prototype.myFind = function (cb, thisArg) {
  for (let i = 0; i < this.length; i++) if (cb.call(thisArg, this[i], i, this)) return this[i];
};
// [5, 12, 8].myFind(x => x > 10) → 12

// Q117: flat
Array.prototype.myFlat = function (depth = 1) {
  const r = [];
  for (let i = 0; i < this.length; i++) {
    if (!(i in this)) continue;
    Array.isArray(this[i]) && depth > 0 ? r.push(...this[i].myFlat(depth - 1)) : r.push(this[i]);
  }
  return r;
};
// [1, [2, [3]]].myFlat(2) → [1, 2, 3]
```

---

## 📄 JSON & Freeze (Q118–Q120)

```javascript
// Q118: JSON.stringify
function myStringify(v) {
  if (v === null) return 'null';
  if (typeof v === 'string') return `"${v.replace(/\\/g, '\\\\').replace(/"/g, '\\"')}"`;
  if (typeof v === 'number') return Number.isFinite(v) ? String(v) : 'null';
  if (typeof v === 'boolean') return String(v);
  if (v === undefined || typeof v === 'function' || typeof v === 'symbol') return undefined;
  if (typeof v.toJSON === 'function') return myStringify(v.toJSON());
  if (Array.isArray(v)) return `[${v.map(x => myStringify(x) ?? 'null').join(',')}]`;
  const pairs = [];
  for (const k of Object.keys(v)) { const s = myStringify(v[k]); if (s !== undefined) pairs.push(`"${k}":${s}`); }
  return `{${pairs.join(',')}}`;
}
// myStringify({ a: [1, undefined], b: 'x' }) → '{"a":[1,null],"b":"x"}'

// Q119: JSON.parse (recursive descent: value → object / array / string / number)
function myParse(str) {
  let i = 0;
  const fail = () => { throw new SyntaxError(`Unexpected token ${str[i] ?? 'end'} at position ${i}`); };
  const ws = () => { while (/\s/.test(str[i] ?? '')) i++; };
  function value() {
    ws();
    const c = str[i];
    if (c === '{') return object();
    if (c === '[') return array();
    if (c === '"') return string();
    for (const [w, v] of [['true', true], ['false', false], ['null', null]])
      if (str.startsWith(w, i)) { i += w.length; return v; }
    const m = /^-?\d+(\.\d+)?([eE][+-]?\d+)?/.exec(str.slice(i));
    if (!m) fail();
    i += m[0].length; return Number(m[0]);
  }
  function string() {
    i++; let out = '';
    while (str[i] !== '"') {
      if (i >= str.length) fail();
      if (str[i] === '\\') { i++; out += { n: '\n', t: '\t', r: '\r' }[str[i]] ?? str[i]; i++; }
      else out += str[i++];
    }
    i++; return out;
  }
  function array() {
    i++; const a = []; ws();
    if (str[i] === ']') { i++; return a; }
    for (;;) { a.push(value()); ws(); if (str[i] === ',') { i++; continue; } if (str[i++] === ']') return a; i--; fail(); }
  }
  function object() {
    i++; const o = {}; ws();
    if (str[i] === '}') { i++; return o; }
    for (;;) {
      ws(); if (str[i] !== '"') fail();
      const k = string(); ws();
      if (str[i++] !== ':') fail();
      o[k] = value(); ws();
      if (str[i] === ',') { i++; continue; }
      if (str[i++] === '}') return o;
      i--; fail();
    }
  }
  const r = value(); ws();
  if (i < str.length) fail();
  return r;
}
// myParse('{"a":[1,true,null]}') → { a: [1, true, null] }

// Q120: Deep freeze
function deepFreeze(obj) {
  if (obj === null || (typeof obj !== 'object' && typeof obj !== 'function') || Object.isFrozen(obj)) return obj;
  Object.freeze(obj);
  for (const k of Reflect.ownKeys(obj)) deepFreeze(obj[k]);
  return obj;
}
// const o = deepFreeze({ a: { b: 1 } }); o.a.b = 2 → ignored (strict me TypeError)
```
