---

# Q227. Virtual Scroll DOM
# Category: DOM Questions
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Render a list of 100,000 rows in a 300px-high scroll container, but keep only the visible rows (plus a small buffer) in the DOM.

---

## 💡 Quick Concept (2 lines only)
Use a tall spacer to get the right scrollbar, then render only rows between `scrollTop / rowHeight` and the visible count, positioned with `translateY`.
हिंदी: सिर्फ़ दिखने वाली rows DOM में रखो, बाकी का सिर्फ़ height (spacer) बनाओ।

---

## ✅ Answer / Solution

```html
<div id="viewport" style="height:300px;overflow:auto;position:relative">
  <div id="spacer"></div>
  <div id="rows" style="position:absolute;top:0;left:0;right:0"></div>
</div>
```

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Set total height = count * rowHeight on spacer
// Step 2: On scroll compute start index and end index
// Step 3: Render only that slice, shift container by translateY

const TOTAL = 100000;                                    // total rows
const ROW_H = 30;                                        // fixed row height in px
const BUFFER = 5;                                        // extra rows above/below
const viewport = document.getElementById('viewport');    // scroll container
const spacer = document.getElementById('spacer');        // gives scroll height
const rows = document.getElementById('rows');            // holds visible rows

spacer.style.height = TOTAL * ROW_H + 'px';              // full virtual height

function render() {
  const scrollTop = viewport.scrollTop;                  // current scroll position
  const visible = Math.ceil(viewport.clientHeight / ROW_H); // rows that fit
  const start = Math.max(0, Math.floor(scrollTop / ROW_H) - BUFFER); // first row
  const end = Math.min(TOTAL, start + visible + BUFFER * 2);         // last row + 1
  const frag = document.createDocumentFragment();        // batch inserts
  for (let i = start; i < end; i++) {                    // only visible slice
    const div = document.createElement('div');           // row element
    div.style.height = ROW_H + 'px';                     // fixed height
    div.textContent = 'Row ' + (i + 1);                  // content
    frag.appendChild(div);                               // add to fragment
  }
  rows.replaceChildren(frag);                            // swap old rows with new
  rows.style.transform = `translateY(${start * ROW_H}px)`; // position slice
}

let ticking = false;                                     // rAF throttle flag
viewport.addEventListener('scroll', () => {              // on scroll
  if (ticking) return;                                   // already scheduled
  ticking = true;                                        // lock
  requestAnimationFrame(() => { render(); ticking = false; }); // render once per frame
});
render();                                                // initial draw

// ============================================
// TEST CASES
// ============================================

// Test 1: rows.children.length         -> Expected: about 20 (10 visible + 10 buffer), not 100000
// Test 2: viewport.scrollTop = 3000; (wait a frame) rows.firstChild.textContent
//         -> Expected: "Row 96" (3000/30 = 100, minus buffer 5 = index 95)
// Test 3: spacer.offsetHeight          -> Expected: 3000000
```

---

## 🔍 Why This Works (3 lines max)
The spacer keeps the scrollbar accurate while DOM stays at ~20 nodes. Index math from `scrollTop` picks the slice and `translateY` places it. `requestAnimationFrame` limits rendering to once per frame.
हिंदी: Spacer से scrollbar सही रहता है, और सिर्फ़ ~20 nodes होने से page fast रहता है।

---

## ⚡ Alternative Solution
```javascript
// Use CSS content-visibility for lighter "virtualization" (browser skips rendering offscreen)
// .row { content-visibility: auto; contain-intrinsic-size: 30px; }
// Simple, but nodes still exist in DOM, so use libs (react-window) for huge lists.
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: rendering all 100000 nodes -> slow load, high memory
for (let i = 0; i < 100000; i++) rows.appendChild(document.createElement('div'));

// ✅ Correct: render only the visible window (see above)
```

---

## 🎯 Interview Tip (1 line)
Say: "Windowing: total height spacer + start/end index from scrollTop + buffer; fixed row height keeps math O(1), variable heights need measured offsets."

---

## 🔗 Related Questions
→ Q226 (infinite scroll) | Q280 (virtualization concept) | Q284 (requestAnimationFrame)
