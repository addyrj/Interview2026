---

# Q236. Canvas Drawing
# Category: DOM Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build a simple freehand drawing pad on `<canvas>`: draw while the pointer is down, support a clear button, and make lines crisp on high-DPI screens.

---

## 💡 Quick Concept (2 lines only)
Get the 2D context, track pointer down/move/up, and draw with `beginPath`, `moveTo`, `lineTo`, `stroke`.
हिंदी: 2D context लो, pointer down पर draw शुरू करो, move पर `lineTo` + `stroke` से line खींचो।

---

## ✅ Answer / Solution

```html
<canvas id="pad" style="width:400px;height:250px;border:1px solid #333;touch-action:none"></canvas>
<button id="clear">Clear</button>
```

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Size canvas by devicePixelRatio for sharp lines
// Step 2: pointerdown starts path, pointermove draws, pointerup stops
// Step 3: Clear with clearRect

const canvas = document.getElementById('pad');          // canvas element
const ctx = canvas.getContext('2d');                     // 2D drawing context
const dpr = window.devicePixelRatio || 1;                // screen pixel density
canvas.width = 400 * dpr;                                // real pixel width
canvas.height = 250 * dpr;                               // real pixel height
ctx.scale(dpr, dpr);                                     // keep CSS units in drawing
ctx.lineWidth = 3;                                       // brush size
ctx.lineCap = 'round';                                   // smooth line ends
ctx.strokeStyle = '#2a6df4';                             // brush color

let drawing = false;                                     // is pointer down

function pos(e) {
  const r = canvas.getBoundingClientRect();              // canvas position on page
  return { x: e.clientX - r.left, y: e.clientY - r.top }; // coords inside canvas
}

canvas.addEventListener('pointerdown', (e) => {          // start drawing
  drawing = true;                                        // flag on
  canvas.setPointerCapture(e.pointerId);                 // keep events outside canvas too
  const { x, y } = pos(e);                               // current point
  ctx.beginPath();                                       // new path
  ctx.moveTo(x, y);                                      // start point
});

canvas.addEventListener('pointermove', (e) => {          // moving
  if (!drawing) return;                                  // only when pressed
  const { x, y } = pos(e);                               // current point
  ctx.lineTo(x, y);                                      // line to point
  ctx.stroke();                                          // render line
});

['pointerup', 'pointercancel'].forEach((t) => {          // end events
  canvas.addEventListener(t, () => { drawing = false; }); // stop drawing
});

document.getElementById('clear').addEventListener('click', () => { // clear button
  ctx.clearRect(0, 0, canvas.width, canvas.height);      // wipe the whole canvas
});

// ============================================
// TEST CASES
// ============================================

// Test 1: drag mouse on canvas   -> Expected: blue line follows pointer
// Test 2: release and move       -> Expected: nothing drawn
// Test 3: click Clear            -> Expected: canvas blank; ctx.getImageData(0,0,1,1).data // [0,0,0,0]
// Test 4: canvas.toDataURL().startsWith('data:image/png') // Expected: true (export as image)
```

---

## 🔍 Why This Works (3 lines max)
Canvas is immediate-mode: each `stroke()` paints pixels, nothing is stored as objects. Pointer events unify mouse and touch, and scaling by `devicePixelRatio` avoids blurry lines. `touch-action:none` stops scrolling while drawing.
हिंदी: Canvas पर pixels सीधे बनते हैं; pointer events mouse और touch दोनों सँभालते हैं।

---

## ⚡ Alternative Solution
```javascript
// Draw shapes quickly
ctx.fillStyle = 'tomato';                                // fill color
ctx.fillRect(10, 10, 80, 50);                            // rectangle
ctx.beginPath();                                         // new path
ctx.arc(150, 40, 25, 0, Math.PI * 2);                    // circle
ctx.fill();                                              // paint circle
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: sizing canvas with CSS only -> drawing is stretched/blurry
// canvas { width: 400px; height: 250px }  (internal bitmap stays 300x150)

// ✅ Correct: set canvas.width/height attributes (times devicePixelRatio) too
```

---

## 🎯 Interview Tip (1 line)
Say: "Canvas has bitmap size vs CSS size, use pointer events + getBoundingClientRect for coordinates, and requestAnimationFrame for animations."

---

## 🔗 Related Questions
→ Q225 (drag and drop) | Q284 (requestAnimationFrame) | Q240 (web worker basics)
