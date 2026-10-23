# Top 50 Must-Know JS Interview Questions
# Quick Revision Cheatsheet

---

## ⚡ Output Questions (Category 1) — Must Know

```javascript
// Q001: var hoisting
console.log(a); var a = 5;
// Output: undefined (var hoisted, initialized as undefined)

// Q002: let TDZ
console.log(b); let b = 5;
// Output: ReferenceError (TDZ — not initialized)

// Q006: closure + var loop
for (var i = 0; i < 3; i++) setTimeout(() => console.log(i), 100);
// Output: 3, 3, 3 (all share same var i; fix: use let)

// Q011: Promise order
console.log(1);
setTimeout(() => console.log(2), 0);
Promise.resolve().then(() => console.log(3));
console.log(4);
// Output: 1, 4, 3, 2 (sync → microtask → macrotask)

// Q018: this binding
const obj = { name: 'A', fn: function() { console.log(this.name); } };
obj.fn();              // 'A' (method call — this = obj)
const f = obj.fn; f(); // undefined (detached — this = global/undefined)

// Q027: == coercion
0 == false    // true  (false → 0)
'' == false   // true  (both → 0)
null == undefined // true (special case)
NaN == NaN    // false (NaN ≠ anything)

// Q030: type coercion traps
1 + '2'       // '12'  (number + string = string concat)
1 - '2'       // -1    (arithmetic — string coerced to number)
[] + []       // ''    (both to '', '' + '' = '')
[] + {}       // '[object Object]'
{} + []       // 0     (interpreted as block + unary plus)

// Q038: nullish coalescing
null ?? 'default'      // 'default'
undefined ?? 'default' // 'default'
0 ?? 'default'         // 0  (0 is not null/undefined!)
'' ?? 'default'        // '' (empty string is not null/undefined!)
// Compare: || returns right if LEFT is falsy (0, '', false, null, undefined, NaN)
//          ?? returns right ONLY if left is null/undefined
```

---

## 🔨 Implement / Build (Category 2) — Must Know

```javascript
// Q051: Reverse string
const reverse = str => str.split('').reverse().join('');

// Q053: Check palindrome
const isPalin = str => { const s = str.toLowerCase(); return s === s.split('').reverse().join(''); };

// Q055: Remove duplicates
const unique = arr => [...new Set(arr)];

// Q058: Flatten array (1 level)
const flatten = arr => arr.flat();
// Flatten all levels:
const flattenAll = arr => arr.flat(Infinity);
// Manual:
const flatDeep = arr => arr.reduce((acc, val) => 
  Array.isArray(val) ? acc.concat(flatDeep(val)) : acc.concat(val), []);

// Q081: Debounce
function debounce(fn, delay) {
  let timer;
  return function(...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

// Q082: Throttle
function throttle(fn, limit) {
  let last = 0;
  return function(...args) {
    if (Date.now() - last >= limit) {
      last = Date.now();
      return fn.apply(this, args);
    }
  };
}

// Q083: Memoize
function memoize(fn) {
  const cache = new Map();
  return function(...args) {
    const key = JSON.stringify(args);
    if (cache.has(key)) return cache.get(key);
    const result = fn.apply(this, args);
    cache.set(key, result);
    return result;
  };
}

// Q084: Curry
function curry(fn) {
  return function curried(...args) {
    if (args.length >= fn.length) return fn.apply(this, args);
    return function(...more) { return curried.apply(this, args.concat(more)); };
  };
}

// Q091: Promise.all
function myPromiseAll(promises) {
  return new Promise((resolve, reject) => {
    const results = [];
    let count = 0;
    if (!promises.length) return resolve([]);
    promises.forEach((p, i) => {
      Promise.resolve(p)
        .then(val => { results[i] = val; if (++count === promises.length) resolve(results); })
        .catch(reject);
    });
  });
}

// Q099: LRU Cache (Map approach)
class LRUCache {
  constructor(cap) { this.cap = cap; this.cache = new Map(); }
  get(key) {
    if (!this.cache.has(key)) return -1;
    const val = this.cache.get(key);
    this.cache.delete(key); this.cache.set(key, val);
    return val;
  }
  put(key, val) {
    if (this.cache.has(key)) this.cache.delete(key);
    else if (this.cache.size >= this.cap) this.cache.delete(this.cache.keys().next().value);
    this.cache.set(key, val);
  }
}
```

---

## 🔧 Fix the Bug (Category 3) — Must Know

```javascript
// Q121: Closure bug in loop
// ❌ Bug:
for (var i = 0; i < 3; i++) setTimeout(() => console.log(i), 100); // 3,3,3
// ✅ Fix:
for (let i = 0; i < 3; i++) setTimeout(() => console.log(i), 100); // 0,1,2

// Q122: async error not caught
// ❌ Bug:
async function fetchData() {
  const data = await fetch('/api').json(); // .json() is also async!
}
// ✅ Fix:
const res = await fetch('/api');
const data = await res.json();

// Q124: this binding lost
// ❌ Bug:
class Timer {
  constructor() { this.count = 0; }
  start() { setInterval(function() { this.count++; }, 1000); } // this = undefined!
}
// ✅ Fix: arrow function
start() { setInterval(() => { this.count++; }, 1000); }
```

---

## 💡 Tricky Concepts (Category 5) — Must Know

```javascript
// Q161: Closure
function outer() {
  let x = 10;
  return function inner() { return x; }; // inner closes over x
}
const fn = outer();
fn(); // 10 — x still accessible even though outer() returned

// Q163: Event Loop Order
// sync → nextTick → Promise.then → setTimeout → setImmediate

// Q164: Hoisting summary
// var → hoisted + initialized as undefined
// let/const → hoisted + TDZ (not initialized, accessing throws ReferenceError)
// function declarations → fully hoisted (can call before declaration)
// function expressions → only variable hoisted, not the function

// Q165: this — 5 rules
// 1. Global: this = window (browser) or {} (Node)
// 2. Method call: obj.fn() → this = obj
// 3. Plain function: fn() → this = undefined (strict) or window
// 4. Arrow function: inherits this from enclosing scope (lexical)
// 5. new keyword: this = newly created object
// 6. call/apply/bind: this = first argument

// Q166: call vs apply vs bind
fn.call(thisArg, arg1, arg2);    // call immediately, args as list
fn.apply(thisArg, [arg1, arg2]); // call immediately, args as array
const bound = fn.bind(thisArg, arg1); // returns new function, doesn't call
```

---

## ⏱️ Async (Category 7) — Must Know

```javascript
// Q201: Sequential promises
async function sequential(ids) {
  const results = [];
  for (const id of ids) {
    results.push(await fetchById(id));
  }
  return results;
}

// Q202: Parallel promises
async function parallel(ids) {
  return Promise.all(ids.map(id => fetchById(id)));
}

// Q203: Limit concurrent promises
async function withLimit(tasks, limit) {
  const results = [];
  for (let i = 0; i < tasks.length; i += limit) {
    const batch = tasks.slice(i, i + limit);
    const batchResults = await Promise.all(batch.map(t => t()));
    results.push(...batchResults);
  }
  return results;
}

// Q205: Timeout a promise
function withTimeout(promise, ms) {
  const timeout = new Promise((_, reject) =>
    setTimeout(() => reject(new Error('Timeout!')), ms)
  );
  return Promise.race([promise, timeout]);
}
```

---

## 🎯 Interview Classics (Category 12) — Must Know

```javascript
// Q291: var vs let vs const
// var: function scope, hoisted (undefined), re-declarable, re-assignable
// let: block scope, TDZ, no re-declare, re-assignable
// const: block scope, TDZ, no re-declare, no re-assign (binding), must init

// Q292: == vs ===
// == type coercion: 0==false (true), ''==false (true), null==undefined (true)
// === no coercion: type AND value must match exactly
// NaN !== NaN always (use Number.isNaN())

// Q293: null vs undefined
// null = intentional absence of value (you set it)
// undefined = variable declared but not assigned, missing property, no return value
typeof null      // 'object' (historical bug!)
typeof undefined // 'undefined'
null == undefined  // true (both nullish)
null === undefined // false (different types)

// Q294: shallow vs deep copy
const shallow = { ...obj };  // nested objects still shared
const deep = structuredClone(obj);  // complete independent copy

// Q296: call stack vs event loop
// Call stack: LIFO, sync code runs here, one at a time
// Event loop: picks tasks from queues when stack is empty
// Microtask queue: Promise.then, queueMicrotask — higher priority
// Macrotask queue: setTimeout, setInterval, I/O — lower priority

// Q299: map vs forEach vs filter vs reduce
// map → transforms each element, returns new array (same length)
// filter → keeps elements matching condition, returns new array (shorter)
// forEach → side effects only, returns undefined
// reduce → accumulates to single value

// Q300: Promise vs async/await
// async/await = syntactic sugar over Promises
// await pauses async function (not thread)
// Use Promise.all() for parallel — don't sequential-await independent calls

// Q301: Closure use cases
// Counter factory, private data, memoize, event handlers, React hooks

// Q308: Debounce use case
// Search input (wait 300ms after user stops typing), form validation
// Implementation: clearTimeout on each call, setTimeout at end

// Q309: Throttle use case  
// Scroll handlers, resize handlers (limit to once per 200ms)
// Implementation: check if enough time has passed since last run
```

---

## 📋 Quick Reference

| Topic | Key Answer |
|-------|-----------|
| var hoisting | Hoisted + undefined |
| let/const hoisting | TDZ — ReferenceError |
| Event loop order | sync → microtask → macrotask |
| this in arrow | Lexical (outer scope) |
| this in method | Calling object |
| == vs === | == coerces types |
| null == undefined | true |
| NaN == NaN | false |
| Debounce | Wait for pause, then fire |
| Throttle | Fire periodically |
| Closure | Function + outer scope |
| Promise.all | All resolve or fail fast |
| Shallow copy | Spread / Object.assign |
| Deep copy | structuredClone() |
