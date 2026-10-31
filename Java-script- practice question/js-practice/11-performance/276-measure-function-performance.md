---

# Q276. Measure Function Performance
# Category: Performance
# Difficulty: ⭐ Easy

---

## ❓ Question
Write a `measure(fn, runs)` helper that runs a function many times and reports average time using `performance.now()`.

---

## 💡 Quick Concept (2 lines only)
Use `performance.now()` (high-resolution, monotonic) instead of `Date.now()`, and average over many runs to reduce noise.
हिंदी: सही timing के लिए performance.now() use करो और कई बार चलाकर average निकालो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Warm up so JIT compiles the function
// Step 2: Time N runs with performance.now()
// Step 3: Return average per run

function measure(fn, runs = 1000) {
  for (let i = 0; i < 10; i++) fn();           // warm-up runs (not timed)
  const start = performance.now();             // high-res start (ms, fractional)
  for (let i = 0; i < runs; i++) fn();         // timed runs
  const total = performance.now() - start;     // total elapsed ms
  return { total, avg: total / runs };         // average per call
}

const slow = () => { let s = 0; for (let i = 0; i < 1e5; i++) s += i; return s; }; // heavy loop
const fast = () => 1 + 1;                      // trivial work

// ============================================
// TEST CASES
// ============================================

const a = measure(slow, 100);                  // measure slow
const b = measure(fast, 100);                  // measure fast
console.log(typeof a.avg);                     // Expected: number
console.log(a.avg > b.avg);                    // Expected: true (slow takes longer)
console.log(`slow avg: ${a.avg.toFixed(4)} ms`); // Expected: varies by machine
console.log(performance.now() > 0);            // Expected: true
```

---

## 🔍 Why This Works (3 lines max)
`performance.now()` has sub-millisecond precision and never goes backwards. Warm-up avoids measuring cold JIT, and averaging smooths out noise.
हिंदी: Warm-up से JIT गर्म हो जाता है और average से random उतार-चढ़ाव कम हो जाता है।

---

## ⚡ Alternative Solution
```javascript
// Built-in console.time / performance.mark+measure
console.time('loop');                          // start labelled timer
for (let i = 0; i < 1e6; i++);                 // work
console.timeEnd('loop');                       // prints e.g. "loop: 1.2ms" (varies)

performance.mark('a');                         // mark start
for (let i = 0; i < 1e6; i++);                 // work
performance.mark('b');                         // mark end
console.log(performance.measure('m', 'a', 'b').duration > 0); // Expected: true
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: single run with Date.now() (1ms resolution, cold start, noisy)
// const t = Date.now(); fn(); console.log(Date.now() - t);

// ✅ Correct: warm-up + many runs + performance.now()
```

---

## 🎯 Interview Tip (1 line)
Say: "Micro-benchmarks lie — profile in DevTools/real workload, and beware dead-code elimination."

---

## 🔗 Related Questions
→ Q277 (Memoization) | Q083 (Memoize) | Q289 (Efficient arrays)
