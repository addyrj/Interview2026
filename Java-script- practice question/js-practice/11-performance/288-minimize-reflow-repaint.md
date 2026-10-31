---

# Q288. Minimize Reflow/Repaint
# Category: Performance
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Show layout thrashing (interleaved read/write) versus batching reads then writes. A mock element counts forced layouts so it runs in Node.

---

## 💡 Quick Concept (2 lines only)
Reading layout (offsetHeight) after a style write forces a synchronous reflow. Group all reads first, then all writes.
हिंदी: Write के तुरंत बाद read करने पर browser को reflow करना पड़ता है, इसलिए पहले सब read फिर सब write करो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Mock layout engine with a dirty flag
// Step 2: Thrash: read → write → read → write ...
// Step 3: Batch: all reads, then all writes

let layouts = 0;                                    // forced synchronous layouts
let dirty = false;                                  // styles changed since last layout?

class MockEl {
  constructor() { this._h = 10; }
  get offsetHeight() {                              // READ (like real DOM)
    if (dirty) { layouts++; dirty = false; }        // dirty + read → forced reflow
    return this._h;
  }
  setHeight(h) { this._h = h; dirty = true; }       // WRITE invalidates layout
}

const els = Array.from({ length: 100 }, () => new MockEl()); // 100 elements

// ❌ Thrashing: read then write inside the loop
els.forEach((el) => el.setHeight(el.offsetHeight + 1)); // each read after a write forces layout
const thrash = layouts;                             // record
layouts = 0; dirty = false;                         // reset

// ✅ Batched: reads first, writes after
const heights = els.map((el) => el.offsetHeight);   // all reads (1 layout max)
els.forEach((el, i) => el.setHeight(heights[i] + 1)); // all writes, no reads between

// ============================================
// TEST CASES
// ============================================

console.log(thrash);                                // Expected: 99
console.log(layouts);                               // Expected: 0 (reads happened before any dirty write)
console.log(els[0]._h);                             // Expected: 12 (incremented in both passes)
```

---

## 🔍 Why This Works (3 lines max)
The browser lazily batches style changes and only recomputes layout when you read geometry. Reads after writes force that work every iteration; grouping avoids it.
हिंदी: Browser layout को टालता रहता है, पर geometry read करते ही उसे तुरंत गणना करनी पड़ती है।

---

## ⚡ Alternative Solution
```javascript
// Browser tips (no Node demo possible):
// 1. Change a class once instead of many style props: el.classList.add('active');
// 2. Animate transform/opacity (compositor only, no layout/paint):
//    el.style.transform = 'translateX(100px)';
// 3. Use requestAnimationFrame to batch writes; avoid reading offset*/scroll*/getBoundingClientRect in loops
// 4. CSS contain / will-change for isolated subtrees
console.log('browser tips'); // Expected: browser tips
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: el.style.width = el.offsetWidth + 10 + 'px' inside a loop
// ✅ Correct: collect widths first, then assign in a second loop
```

---

## 🎯 Interview Tip (1 line)
Explain the pipeline Style → Layout (reflow) → Paint → Composite, and that transform/opacity skip the first three.

---

## 🔗 Related Questions
→ Q287 (Batch DOM updates) | Q284 (requestAnimationFrame) | Q229 (Smooth scroll)
