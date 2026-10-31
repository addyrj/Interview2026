---

# Q284. RequestAnimationFrame
# Category: Performance
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Use `requestAnimationFrame` to coalesce many rapid updates into one render per frame. (Node has no rAF, so we polyfill it with a 16ms timer.)

---

## 💡 Quick Concept (2 lines only)
`requestAnimationFrame` runs your callback right before the next repaint (~60fps), so visual updates sync with the screen.
हिंदी: rAF आपका code अगले repaint से ठीक पहले चलाता है, इसलिए animation smooth रहती है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Polyfill rAF for Node (browser has it built in)
// Step 2: Schedule at most one render per frame
// Step 3: Latest value wins

const raf = globalThis.requestAnimationFrame || ((cb) => setTimeout(() => cb(Date.now()), 16)); // ~60fps

let pending = false;                         // is a frame already scheduled?
let latest = null;                           // most recent value
let renders = 0;                             // how many renders happened

function scheduleRender(value) {
  latest = value;                            // always keep newest value
  if (pending) return;                       // already scheduled → coalesce
  pending = true;                            // mark scheduled
  raf(() => {                                // run once, next frame
    pending = false;                         // allow next schedule
    renders++;                               // count render
    console.log('render', latest);           // draw using latest value
  });
}

// ============================================
// TEST CASES
// ============================================

for (let i = 1; i <= 100; i++) scheduleRender(i); // 100 rapid updates (e.g. mousemove)
setTimeout(() => {                           // check after a frame passed
  console.log(renders);                      // Expected: 1
}, 50);
// Expected console order:
// render 100
// 1
```

---

## 🔍 Why This Works (3 lines max)
Only the first call schedules a frame; later calls just overwrite `latest`. The single callback renders the final state, avoiding 99 wasted renders.
हिंदी: पहली call frame schedule करती है, बाकी सिर्फ latest value बदलती हैं, render एक ही बार होता है।

---

## ⚡ Alternative Solution
```javascript
// Browser animation loop with timestamps (run in a browser console/page)
// let x = 0;
// function step(ts) {
//   x += 2;                               // move
//   box.style.transform = `translateX(${x}px)`; // GPU-friendly property
//   if (x < 300) requestAnimationFrame(step);   // schedule next frame
// }
// requestAnimationFrame(step);
console.log('browser-only demo, see comments'); // Expected: browser-only demo, see comments
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: setInterval(draw, 16) — not synced to repaint, runs in background tabs
// ✅ Correct: requestAnimationFrame(draw); cancel with cancelAnimationFrame(id)
```

---

## 🎯 Interview Tip (1 line)
Mention rAF pauses in background tabs (saves battery) and animate `transform`/`opacity` to avoid layout.

---

## 🔗 Related Questions
→ Q082 (Throttle) | Q288 (Reflow/repaint) | Q287 (Batch DOM updates)
