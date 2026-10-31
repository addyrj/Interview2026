---

# Q289. Efficient Array Operations
# Category: Performance
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Make three common array tasks faster: (1) membership checks, (2) chained map/filter on big data, (3) removing duplicates. Compare approaches by result and complexity.

---

## 💡 Quick Concept (2 lines only)
Pick the right structure: Set/Map lookups are O(1) versus O(n) for `includes`, and one pass beats chained passes.
हिंदी: सही data structure चुनो, Set lookup O(1) है जबकि includes O(n) है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: includes (O(n) each) vs Set (O(1) each)
// Step 2: map+filter (2 passes) vs reduce (1 pass)
// Step 3: dedupe via Set

const big = Array.from({ length: 20000 }, (_, i) => i);   // 0..19999
const queries = [5, 19999, 25000];                        // lookups

// (1) Membership
const slowHits = queries.filter((q) => big.includes(q));  // scans array each time: O(n*m)
const set = new Set(big);                                 // build once: O(n)
const fastHits = queries.filter((q) => set.has(q));       // O(1) each

// (2) Chained vs single pass
const chained = big.map((x) => x * 2).filter((x) => x % 3 === 0); // 2 passes + temp array
const single = big.reduce((acc, x) => {                   // 1 pass, no temp array
  const d = x * 2;                                        // transform
  if (d % 3 === 0) acc.push(d);                           // filter
  return acc;
}, []);

// (3) Dedupe
const dupes = [3, 1, 3, 2, 1];                            // has duplicates
const unique = [...new Set(dupes)];                       // O(n), keeps first-seen order

// ============================================
// TEST CASES
// ============================================

console.log(slowHits, fastHits);                          // Expected: [ 5, 19999 ] [ 5, 19999 ]
console.log(chained.length, single.length);               // Expected: 6667 6667
console.log(unique);                                      // Expected: [ 3, 1, 2 ]
console.log(JSON.stringify(chained) === JSON.stringify(single)); // Expected: true
```

---

## 🔍 Why This Works (3 lines max)
Hash lookups avoid scanning, and a single pass avoids allocating an intermediate array. Same results, less work (timing varies by machine).
हिंदी: Hash lookup से scan बचता है और एक pass से बीच का temporary array नहीं बनता।

---

## ⚡ Alternative Solution
```javascript
// Other wins
const arr = [];                                           // build array
for (let i = 0; i < 5; i++) arr.push(i);                  // push is O(1); unshift is O(n)
console.log(arr.at(-1));                                  // Expected: 4
const total = arr.reduce((a, b) => a + b, 0);             // sum in one pass
console.log(total);                                       // Expected: 10
// Also: break early with some()/find() instead of filter()[0]
console.log(arr.some((x) => x > 2));                      // Expected: true (stops at 3)
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: nested includes/indexOf inside a loop → O(n²)
// a.filter((x) => b.includes(x))
// ✅ Correct: const s = new Set(b); a.filter((x) => s.has(x))  // O(n + m)
```

---

## 🎯 Interview Tip (1 line)
Always state Big-O before and after, and mention preferring `for` loops only in proven hot paths.

---

## 🔗 Related Questions
→ Q062 (Intersection) | Q055 (Remove duplicates) | Q278 (Lazy evaluation)
