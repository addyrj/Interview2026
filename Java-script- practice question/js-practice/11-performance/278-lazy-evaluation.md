---

# Q278. Lazy Evaluation
# Category: Performance
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Get the first 3 even squares from an infinite sequence without computing the whole list, using generators.

---

## 💡 Quick Concept (2 lines only)
Lazy evaluation computes values only when needed; generators let you process infinite or huge sequences on demand.
हिंदी: Lazy evaluation में value तभी बनती है जब जरूरत हो, पूरी list पहले से नहीं बनती।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Infinite generator of naturals
// Step 2: Lazy map / filter / take helpers
// Step 3: Pull only what you need

function* naturals() {
  let n = 1;                                   // start
  while (true) yield n++;                      // infinite stream
}

function* map(it, fn) { for (const x of it) yield fn(x); }          // lazy map
function* filter(it, fn) { for (const x of it) if (fn(x)) yield x; } // lazy filter
function* take(it, n) {
  if (n <= 0) return;                          // nothing requested
  let i = 0;                                   // counter
  for (const x of it) {
    yield x;                                   // pass value
    if (++i >= n) return;                      // stop pulling after n items
  }
}

let calls = 0;                                 // count how many squares computed
const result = [...take(
  filter(map(naturals(), (x) => { calls++; return x * x; }), (x) => x % 2 === 0), // squares, keep evens
  3                                            // first 3 only
)];

// ============================================
// TEST CASES
// ============================================

console.log(result);                           // Expected: [ 4, 16, 36 ]
console.log(calls);                            // Expected: 6 (only up to n=6, not infinite)

const eager = Array.from({ length: 1000 }, (_, i) => i).map((x) => x * x); // eager builds all 1000
console.log(eager.length);                     // Expected: 1000
```

---

## 🔍 Why This Works (3 lines max)
Each generator pauses at `yield`, so work happens only when the consumer asks for the next value. `take` stops the pipeline early.
हिंदी: Generator हर yield पर रुक जाता है, इसलिए बाकी values की गणना होती ही नहीं।

---

## ⚡ Alternative Solution
```javascript
// Lazy property with getter caching
const obj = {
  get expensive() {                            // runs on first access only
    console.log('computing');                  // visible side effect
    Object.defineProperty(this, 'expensive', { value: 42 }); // replace getter with value
    return 42;
  },
};
console.log(obj.expensive, obj.expensive);     // Expected: computing  then  42 42
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: [...naturals()] — spreading an infinite generator hangs/crashes
// ✅ Correct: limit with take() first, then spread
```

---

## 🎯 Interview Tip (1 line)
Mention lazy loading, short-circuit `&&`, and that array chains (map→filter) are eager and allocate intermediates.

---

## 🔗 Related Questions
→ Q169 (Generators) | Q253 (Generator examples) | Q289 (Efficient arrays)
