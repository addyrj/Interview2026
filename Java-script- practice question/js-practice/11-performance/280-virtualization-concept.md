---

# Q280. Virtualization Concept
# Category: Performance
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Given 100,000 rows of height 30px in a 300px viewport, compute which rows to render for a given `scrollTop` (windowing logic).

---

## 💡 Quick Concept (2 lines only)
Virtualization renders only the rows visible in the viewport (plus a small buffer) and fakes the rest with padding.
हिंदी: सिर्फ screen पर दिखने वाली rows render करो, बाकी की जगह खाली padding रखो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: startIndex = floor(scrollTop / rowHeight)
// Step 2: visibleCount = ceil(viewport / rowHeight)
// Step 3: add overscan buffer and clamp to bounds

function getVisibleRange({ scrollTop, viewportHeight, rowHeight, total, overscan = 2 }) {
  const first = Math.floor(scrollTop / rowHeight);           // first row at top edge
  const visible = Math.ceil(viewportHeight / rowHeight);     // rows that fit on screen
  const start = Math.max(0, first - overscan);               // buffer above
  const end = Math.min(total - 1, first + visible + overscan); // buffer below
  return {
    start,                                                   // first row to render
    end,                                                     // last row to render
    offsetTop: start * rowHeight,                            // spacer height above
    totalHeight: total * rowHeight,                          // full scroll height
  };
}

const cfg = { viewportHeight: 300, rowHeight: 30, total: 100000 }; // config

// ============================================
// TEST CASES
// ============================================

console.log(getVisibleRange({ ...cfg, scrollTop: 0 }));
// Expected: { start: 0, end: 12, offsetTop: 0, totalHeight: 3000000 }
const r = getVisibleRange({ ...cfg, scrollTop: 3000 });      // scrolled 100 rows
console.log(r.start, r.end);                                 // Expected: 98 112
console.log(r.end - r.start + 1);                            // Expected: 15 (DOM nodes, not 100000)
console.log(getVisibleRange({ ...cfg, scrollTop: 2999999 }).end); // Expected: 99999
```

---

## 🔍 Why This Works (3 lines max)
Position math (scrollTop / rowHeight) tells which rows intersect the viewport, so DOM size stays constant (~15 nodes). A spacer of `offsetTop` plus the full height keeps the scrollbar accurate.
हिंदी: DOM में हमेशा बस थोड़े nodes रहते हैं, पर scrollbar पूरी list जैसा ही दिखता है।

---

## ⚡ Alternative Solution
```javascript
// Browser note: in React use libraries like react-window / react-virtuoso,
// or IntersectionObserver for variable heights. Pure-JS slice version:
const rows = Array.from({ length: 100000 }, (_, i) => `row ${i}`); // data
const first = Math.floor(600 / 30);                                 // scrollTop 600, rowHeight 30 -> row 20
const slice = rows.slice(first - 2, first + 10 + 2 + 1);            // overscan 2, 10 visible
console.log(slice.length, slice[0]);                                // Expected: 15 row 18
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: rendering 100,000 DOM nodes (slow layout, high memory)
// ✅ Correct: render only [start..end] and absolutely position / pad the list
```

---

## 🎯 Interview Tip (1 line)
Say virtualization cuts DOM nodes from O(N) to O(visible); mention overscan to avoid blank flashes on fast scroll.

---

## 🔗 Related Questions
→ Q227 (Virtual scroll DOM) | Q226 (Infinite scroll) | Q281 (Efficient DOM updates)
