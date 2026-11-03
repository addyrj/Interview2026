# 26. canvas Tag Basics
# हिंदी में: canvas Tag — JavaScript से Pixels Draw करना

---

## 🔵 Simple Definition (English)
`<canvas>` is a blank rectangular bitmap area. You draw on it with JavaScript (shapes, text, images, animation) using the **2D context** (`getContext('2d')`) or WebGL. It is pixel-based: once drawn, the browser does not remember individual shapes.

## 🔵 सरल परिभाषा (Hindi)
`<canvas>` एक खाली rectangular bitmap area है। आप JavaScript से इस पर shapes, text, images और animation draw करते हैं (**2D context** `getContext('2d')` या WebGL से)। ये pixel-based है: एक बार draw होने के बाद browser को अलग-अलग shapes याद नहीं रहतीं।

---

## 🔴 Problem it Solves
```
BEFORE canvas (pre-2010):
  - Charts, games, image editors needed Flash/Silverlight plugins or server-side images.
  - Plugins: insecure, no mobile support, not part of the web standard.
  - Thousands of DOM nodes for particles/graphs = very slow.

WITH canvas:
  - Native, plugin-free pixel drawing at 60fps.
  - ONE DOM element, any number of drawn shapes -> fast for heavy graphics.
```

## 🔴 यह क्यों बना? (Hindi)
```
canvas से पहले:
  - Charts, games, image editor के लिए Flash/Silverlight plugin या server-side images चाहिए थीं।
  - Plugins insecure थे, mobile पर नहीं चलते थे।
  - हज़ारों DOM nodes (particles/graph) बहुत slow होते हैं।

canvas के साथ:
  - Plugin के बिना native pixel drawing, 60fps तक।
  - सिर्फ एक DOM element, चाहे कितनी भी shapes हों -> heavy graphics के लिए तेज़।
```

---

## 🟢 How it Works — Step by Step

```
1. Add <canvas id="c" width="400" height="200"></canvas>
2. JS: const ctx = canvas.getContext('2d');   // the drawing "pen"
3. Set state:   ctx.fillStyle = 'tomato';  ctx.lineWidth = 3;
4. Draw:        ctx.fillRect(x, y, w, h);  ctx.arc(...); ctx.fillText(...)
5. Paths:       ctx.beginPath(); ctx.moveTo(); ctx.lineTo(); ctx.stroke()/fill()
6. Animate:     requestAnimationFrame(loop) -> clear -> redraw -> repeat

COORDINATES: origin (0,0) is TOP-LEFT. x goes right, y goes DOWN.

TWO SIZES (very common interview trap):
  width/height ATTRIBUTES  -> the drawing buffer resolution (pixels)
  CSS width/height         -> how big it is displayed (scales the bitmap -> blurry)

HIGH-DPI (Retina) FIX:
  canvas.width  = cssWidth  * devicePixelRatio;
  canvas.height = cssHeight * devicePixelRatio;
  ctx.scale(devicePixelRatio, devicePixelRatio);

IMMEDIATE MODE: canvas = bitmap. To "move" a circle you clear and redraw everything.
(SVG = retained mode: shapes stay as DOM elements. See topic 27.)

ACCESSIBILITY: canvas is opaque to screen readers -> add fallback content inside the tag
and aria-label/role="img".
```

## 🟢 कैसे काम करता है? (Hindi)

```
1. <canvas id="c" width="400" height="200"></canvas> लिखें।
2. JS: const ctx = canvas.getContext('2d');   // ये आपकी "कलम" है
3. Style set करें: ctx.fillStyle = 'tomato'
4. Draw करें: fillRect, arc, fillText, drawImage
5. Path: beginPath -> moveTo -> lineTo -> stroke/fill
6. Animation: requestAnimationFrame में हर frame clear -> redraw

Coordinates: (0,0) ऊपर-बाएँ कोने में है, y नीचे की तरफ बढ़ता है।

दो sizes (interview trap):
  width/height ATTRIBUTE = drawing की असली resolution
  CSS width/height = display size (अलग हुआ तो image blurry/stretched)

Canvas एक bitmap है: circle हिलाना है तो पूरा canvas साफ करके दोबारा बनाना पड़ता है।
Screen readers canvas नहीं पढ़ पाते, इसलिए fallback text और aria-label दें।
```

---

## 🟡 Real World Example
**Google Maps (older versions) and Figma-style tools** use canvas/WebGL for smooth rendering of many shapes. **Instagram / Photoshop-like web editors** apply filters by reading pixels with `getImageData`. **Zomato / Swiggy dashboards (restaurant analytics)** often use Chart.js or ECharts, which draw on canvas. **Browser games** (Slither.io, 2048 variants) are canvas loops. **Image compression before upload:** draw the photo on a canvas and call `canvas.toBlob()` to resize it client-side.

## 🟡 Real Example Hindi mein
**Google Maps और Figma जैसे tools** बहुत सारी shapes smooth दिखाने के लिए canvas/WebGL use करते हैं। **Instagram / web photo editors** `getImageData` से pixels पढ़कर filter लगाते हैं। **Zomato / Swiggy के restaurant analytics dashboards** में Chart.js / ECharts canvas पर graph बनाते हैं। **Browser games** canvas loops हैं। **Upload से पहले image compress:** photo को canvas पर draw करके `canvas.toBlob()` से छोटा बनाना।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Canvas Basics</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <h1>Canvas Basics</h1>

  <!-- Static drawing. Content inside the tag = fallback for old browsers / screen readers -->
  <canvas id="shapes" width="400" height="200" role="img"
          aria-label="A red rectangle, a blue circle and a green line">
    Your browser does not support canvas.
  </canvas>

  <!-- Animated bouncing ball -->
  <canvas id="ball" width="400" height="200" role="img"
          aria-label="Animated bouncing ball"></canvas>

  <script>
    // ───────── 1. STATIC SHAPES ─────────
    const c1 = document.getElementById('shapes');
    const ctx1 = c1.getContext('2d');       // get the 2D drawing context

    ctx1.fillStyle = '#e53935';             // red fill
    ctx1.fillRect(20, 20, 100, 60);         // x, y, width, height

    ctx1.beginPath();                       // start a new path
    ctx1.arc(220, 60, 40, 0, Math.PI * 2);  // x, y, radius, startAngle, endAngle
    ctx1.fillStyle = '#1e88e5';
    ctx1.fill();                            // fill the circle

    ctx1.beginPath();
    ctx1.moveTo(20, 150);                   // pen goes here
    ctx1.lineTo(380, 150);                  // line to here
    ctx1.lineWidth = 4;
    ctx1.strokeStyle = '#43a047';
    ctx1.stroke();                          // actually draw the line

    ctx1.font = '20px sans-serif';
    ctx1.fillStyle = '#222';
    ctx1.fillText('Hello Canvas', 20, 185); // text baseline at y=185

    // ───────── 2. ANIMATION LOOP ─────────
    const c2 = document.getElementById('ball');
    const ctx2 = c2.getContext('2d');
    let x = 50, y = 50, dx = 3, dy = 2;     // position and velocity
    const r = 15;

    function loop() {
      ctx2.clearRect(0, 0, c2.width, c2.height);   // 1. erase old frame

      x += dx; y += dy;                             // 2. update state
      if (x + r > c2.width  || x - r < 0) dx = -dx; // bounce off walls
      if (y + r > c2.height || y - r < 0) dy = -dy;

      ctx2.beginPath();                             // 3. draw new frame
      ctx2.arc(x, y, r, 0, Math.PI * 2);
      ctx2.fillStyle = '#fb8c00';
      ctx2.fill();

      requestAnimationFrame(loop);                  // 4. ask browser for next frame
    }
    loop();
  </script>
</body>
</html>
```

```css
/* style.css */
*, *::before, *::after { box-sizing: border-box; }
body { font-family: system-ui, sans-serif; padding: 20px; background: #f6f7f9; }

/* Canvas is inline by default (gap under it). Make it block + give a visible border. */
canvas {
  display: block;
  margin: 0 0 20px;
  background: #fff;
  border: 1px solid #ccc;
  border-radius: 8px;
  /* CAUTION: setting CSS width here different from the width attribute scales the bitmap */
  max-width: 100%;   /* shrinks display only; keep aspect ratio with height:auto */
  height: auto;
}
```

---

## 🟠 React/Next.js Connection

```jsx
"use client"; // Next.js App Router: canvas needs the browser, so a Client Component
import { useRef, useEffect } from "react";

export default function Ball() {
  const ref = useRef(null);

  useEffect(() => {
    const canvas = ref.current;
    const ctx = canvas.getContext("2d");
    let x = 50, dx = 3, id;

    const loop = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      x += dx;
      if (x > canvas.width - 15 || x < 15) dx = -dx;
      ctx.beginPath();
      ctx.arc(x, 100, 15, 0, Math.PI * 2);
      ctx.fill();
      id = requestAnimationFrame(loop);
    };
    loop();

    return () => cancelAnimationFrame(id); // CLEANUP: stop loop on unmount
  }, []);

  // Tailwind: border + rounded. width/height attrs set the real resolution.
  return <canvas ref={ref} width={400} height={200} className="rounded border" />;
}
```
Use `useRef` (not `document.getElementById`). Never store animation state in `useState` per frame: it re-renders React 60 times per second. Libraries: `react-chartjs-2`, `react-konva`, `@react-three/fiber` (WebGL).

---

## ⚫ Interview Questions + Answers

Q1: What is canvas and how is it different from SVG?
A1: Canvas is a pixel bitmap drawn imperatively with JS (immediate mode); the browser keeps no shape objects. SVG is vector XML in the DOM (retained mode): each shape is an element you can style with CSS and attach events to. Canvas wins for thousands of moving objects; SVG wins for crisp scaling, few elements and accessibility.

Q2: Why is my canvas drawing blurry?
A2: CSS size differs from the width/height attributes so the bitmap is stretched, or it is on a Retina screen. Fix by setting the attribute size to `cssSize * devicePixelRatio` and calling `ctx.scale(dpr, dpr)`.

Q3: How do you animate on canvas?
A3: Use `requestAnimationFrame`: clear with `clearRect`, update positions, redraw. Do not use `setInterval`; rAF syncs with the display refresh and pauses in background tabs.

Q4: How do you make canvas accessible?
A4: It is just pixels, so give `role="img"` + `aria-label`, put fallback content inside the tag, and provide an equivalent data table or text for charts.

Q5: How do you detect a click on a shape in canvas?
A5: Canvas has no shape objects. Listen for `click` on the canvas, compute coordinates with `getBoundingClientRect()`, and do your own hit-testing (math, or `ctx.isPointInPath`).

---

## 🔷 Common Mistakes to Avoid
❌ Mistake 1: Sizing canvas only with CSS (`canvas { width: 600px; height: 300px }`), giving a stretched 300x150 bitmap.
✅ Correct way: Set `width` and `height` attributes (or via JS) for the real resolution.

❌ Mistake 2: Forgetting `beginPath()`, so old paths redraw and styles leak.
✅ Correct way: Call `ctx.beginPath()` before each new shape.

❌ Mistake 3: Running `getContext` before the element exists (script in head).
✅ Correct way: Put script at end of body, use `defer`, or `useEffect` in React.

❌ Mistake 4: Not cancelling `requestAnimationFrame` in React cleanup (memory leak, double loops).
✅ Correct way: `return () => cancelAnimationFrame(id)`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| canvas | Bitmap drawing surface | JS से draw होने वाला bitmap area |
| Context (2d) | Object with drawing methods | Drawing का "pen" object |
| Immediate mode | Draw and forget, redraw to change | Draw करो और भूल जाओ |
| requestAnimationFrame | Sync callback with screen refresh | Screen refresh के साथ animation loop |
| devicePixelRatio | Physical pixels per CSS pixel | Retina screen का scale factor |
| WebGL | GPU 3D context for canvas | GPU वाला 3D drawing |
| clearRect | Erases an area | Area साफ करना |
| Path | Series of points forming a shape | Points से बनी shape की रेखा |

---

## ⚡ 3-Line Summary
English: `<canvas>` is a pixel surface you draw on with JavaScript, great for games, charts and image editing.
Attribute width/height is the real resolution; CSS size only scales it (handle `devicePixelRatio`).
It is immediate mode and opaque to screen readers, so add `aria-label`, fallback text and manual hit-testing.

Hindi: `<canvas>` एक pixel surface है जिस पर JavaScript से draw करते हैं, games, charts और image editing के लिए बढ़िया।
Attribute वाली width/height असली resolution है; CSS size सिर्फ scale करती है (`devicePixelRatio` संभालें)।
ये immediate mode है और screen readers को नहीं दिखता, इसलिए `aria-label`, fallback text और manual hit-testing चाहिए।

---

## ➡️ Next Topic
**27. SVG in HTML** — canvas pixels बनाता है; SVG vector shapes बनाता है जो DOM में रहती हैं, CSS से style होती हैं और हर size पर sharp रहती हैं।

---
