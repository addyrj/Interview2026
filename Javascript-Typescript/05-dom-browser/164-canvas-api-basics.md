# 164. Canvas API Basics
# हिंदी में: Canvas API की बुनियादी बातें

---

## 🔵 Simple Definition (English)
The Canvas API gives you a `<canvas>` element, a rectangle of pixels that JavaScript draws on with `getContext("2d")`. You draw shapes, text, and images by calling methods like `fillRect`, `arc`, and `drawImage`. Once something is drawn, the canvas keeps only pixels, not objects, so you redraw the whole scene when it changes.

## 🔵 सरल परिभाषा (Hindi)
Canvas API एक `<canvas>` element देता है, जो pixels का एक आयत है और जिस पर JavaScript `getContext("2d")` से drawing करता है। `fillRect`, `arc` और `drawImage` जैसे methods से shapes, text और images बनते हैं। एक बार कुछ draw हो जाए तो canvas में सिर्फ़ pixels बचते हैं, objects नहीं, इसलिए बदलाव पर पूरा दृश्य दोबारा बनाना पड़ता है।

---

## 🔴 Problem it Solves
Before canvas, a web page could show shapes only through DOM elements, such as `<div>` boxes, SVG nodes, or CSS. Thousands of DOM nodes make the browser slow when you animate a chart, a map, or a game. A canvas is a single element with no per-shape DOM overhead, so it handles many moving items at a smooth frame rate. Image editing, signature pads, and charts in apps like Zerodha's trading views or Google Maps-style tiles need that speed.

## 🔴 यह क्यों बना? (Hindi)
Canvas से पहले web page पर shapes सिर्फ़ DOM elements से दिखते थे, जैसे `<div>` boxes, SVG nodes या CSS। Chart, map या game को animate करते समय हज़ारों DOM nodes browser को धीमा कर देते थे। Canvas एक ही element है, जिसमें हर shape का अलग DOM overhead नहीं होता, इसलिए बहुत-सी चलती चीज़ें भी smooth frame rate पर चलती हैं। Image editing, signature pad और charts (जैसे trading screens में) को यही speed चाहिए।

---

## 🟢 How it Works — Step by Step

Step 1 → Put `<canvas id="c" width="400" height="200">` in the HTML. The `width` and `height` attributes set the pixel grid.
Step 2 → Call `canvas.getContext("2d")` to get the drawing context `ctx`.
Step 3 → Set styles (`fillStyle`, `strokeStyle`, `lineWidth`, `font`) and call drawing methods (`fillRect`, `beginPath` + `arc` + `fill`).
Step 4 → The canvas stores only pixels. Moving a shape means clearing the area (`clearRect`) and drawing again.
Step 5 → For animation, call `requestAnimationFrame(loop)`, which runs your draw code before each screen refresh.
Step 6 → Coordinates start at (0, 0) in the top-left corner, and y grows downward.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → HTML में `<canvas id="c" width="400" height="200">` रखें। `width` और `height` attributes pixel grid तय करते हैं।
Step 2 → `canvas.getContext("2d")` से drawing context `ctx` लें।
Step 3 → Styles (`fillStyle`, `strokeStyle`, `lineWidth`, `font`) सेट करें और drawing methods (`fillRect`, `beginPath` + `arc` + `fill`) चलाएँ।
Step 4 → Canvas में सिर्फ़ pixels रहते हैं। कोई चीज़ हिलानी हो तो area को `clearRect` से साफ़ करें और फिर दोबारा बनाएँ।
Step 5 → Animation के लिए `requestAnimationFrame(loop)` लें, जो हर screen refresh से पहले आपका draw code चलाता है।
Step 6 → Coordinates ऊपर-बाईं ओर (0, 0) से शुरू होते हैं, और y नीचे की ओर बढ़ता है।

---

## 🟡 Real World Example
A delivery app's heat map of order density, or a trading app's price chart, can draw thousands of points on one canvas. The app redraws the chart in each frame when a new price arrives. A signature pad on a payment screen, such as a courier's delivery proof, uses canvas pointer events to draw the customer's signature and then sends it to the server as an image. A photo editor like the ones used by e-commerce sellers to crop product images uses `drawImage` on a canvas and exports the result.

## 🟡 Real Example Hindi mein
Delivery app का order density heat map, या trading app का price chart, एक ही canvas पर हज़ारों points बना सकता है। नया price आने पर app हर frame में chart दोबारा बनाता है। Payment screen पर courier का signature pad (delivery proof के लिए) canvas के pointer events से signature बनाता है और उसे image के रूप में server पर भेजता है। E-commerce sellers के लिए product photos crop करने वाला editor canvas पर `drawImage` चलाता है और नतीजा export करता है।

---

## 💻 Code Example — Basic
Browser-only. Save as `canvas-basic.html` and open it in a browser. Node.js has no canvas, so this runs only in the browser.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">                                       <!-- text encoding -->
  <title>Canvas Basics</title>
</head>
<body>
  <canvas id="c" width="400" height="200" style="border:1px solid #999"></canvas> <!-- drawing surface -->

  <script>
    const canvas = document.getElementById("c");               // find the canvas element
    const ctx = canvas.getContext("2d");                       // 2D drawing context (the "brush")

    ctx.fillStyle = "#f4a261";                                 // fill colour for the next shapes
    ctx.fillRect(20, 20, 120, 80);                             // filled rectangle: x, y, width, height

    ctx.strokeStyle = "#2a9d8f";                               // outline colour (teal)
    ctx.lineWidth = 6;                                         // outline thickness in pixels
    ctx.strokeRect(160, 20, 120, 80);                          // outlined rectangle, no fill

    ctx.beginPath();                                           // start a new path for the circle
    ctx.arc(320, 140, 40, 0, Math.PI * 2);                     // circle: centre x, y, radius, start, end (radians)
    ctx.fillStyle = "#e76f51";                                 // new fill colour for the circle
    ctx.fill();                                                // fill the circle path

    ctx.font = "20px sans-serif";                              // font for text
    ctx.fillStyle = "#264653";                                 // text colour
    ctx.fillText("Dosa", 30, 150);                             // text at x=30, baseline y=150

    ctx.clearRect(60, 40, 40, 30);                             // erase a small box inside the rectangle
  </script>
</body>
</html>
```

## 💻 Code Example — Advanced
Browser-only sketchpad. Save as `canvas-advanced.html`. It handles high-DPI screens, pointer input, a redraw loop with `requestAnimationFrame`, and redrawing after a window resize. The coordinate helper `toCanvasPoint` has no DOM code, so Node can test it.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">                                       <!-- text encoding -->
  <meta name="viewport" content="width=device-width, initial-scale=1"> <!-- phone width -->
  <title>Canvas Sketchpad</title>
  <style>
    body { font-family: sans-serif; margin: 16px; }            /* page spacing */
    canvas { display: block; width: 100%; max-width: 600px; height: 300px; border: 1px solid #888; touch-action: none; } /* CSS size, no scroll on touch */
  </style>
</head>
<body>
  <canvas id="pad"></canvas>                                   <!-- the drawing surface -->
  <p><button id="clear">Clear</button> <span id="info"></span></p> <!-- clear button and stroke counter -->

  <script>
    // ---- Pure helper: no DOM here, so Node can test it ----
    function toCanvasPoint(clientX, clientY, rect) {          // converts viewport coordinates to canvas CSS coordinates
      return { x: clientX - rect.left, y: clientY - rect.top }; // subtract the canvas's position on the page
    }

    // ---- DOM part (browser only) ----
    const canvas = document.getElementById("pad");             // the drawing surface
    const ctx = canvas.getContext("2d");                       // 2D context
    const info = document.getElementById("info");              // counter text
    const dpr = window.devicePixelRatio || 1;                  // screen density: 2 on many phones

    let strokes = [];                                          // every finished or running stroke
    let current = null;                                        // the stroke being drawn right now
    let dirty = true;                                          // true when the screen must be redrawn

    function sizeCanvas() {                                    // matches the bitmap to the CSS size
      const rect = canvas.getBoundingClientRect();              // size on the screen in CSS pixels
      canvas.width = Math.round(rect.width * dpr);              // bitmap width in device pixels
      canvas.height = Math.round(rect.height * dpr);            // bitmap height in device pixels
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);                   // draw in CSS pixels, scaled to device pixels
      ctx.lineCap = "round";                                     // round ends for smooth lines
      ctx.lineJoin = "round";                                    // round corners between segments
      ctx.lineWidth = 3;                                         // stroke thickness in CSS pixels
      ctx.strokeStyle = "#264653";                               // stroke colour
      dirty = true;                                              // resizing clears the bitmap, so redraw
    }

    function redraw() {                                        // paints every stroke from scratch
      ctx.clearRect(0, 0, canvas.clientWidth, canvas.clientHeight); // clear in CSS pixels
      for (const s of strokes) {                               // each stroke is a list of points
        if (s.length < 2) continue;                            // one point draws nothing
        ctx.beginPath();                                       // a new path for each stroke
        ctx.moveTo(s[0].x, s[0].y);                            // start at the first point
        for (const p of s.slice(1)) ctx.lineTo(p.x, p.y);      // add each following point
        ctx.stroke();                                          // paint the path
      }
      info.textContent = `${strokes.length} stroke(s)`;        // update the counter
    }

    function loop() {                                          // runs before every screen refresh
      if (dirty) {                                             // only redraw when something changed
        dirty = false;                                         // mark as clean
        redraw();                                              // paint the whole scene
      }
      requestAnimationFrame(loop);                             // schedule the next frame
    }

    canvas.addEventListener("pointerdown", (e) => {            // finger or mouse pressed
      current = [toCanvasPoint(e.clientX, e.clientY, canvas.getBoundingClientRect())]; // first point
      strokes.push(current);                                   // store the stroke
      canvas.setPointerCapture(e.pointerId);                   // keep receiving moves outside the canvas
      dirty = true;                                            // schedule a redraw
    });

    canvas.addEventListener("pointermove", (e) => {            // finger or mouse moved
      if (!current) return;                                    // only while drawing
      current.push(toCanvasPoint(e.clientX, e.clientY, canvas.getBoundingClientRect())); // add point
      dirty = true;                                            // schedule a redraw
    });

    const stopStroke = () => { current = null; };              // end the current stroke
    canvas.addEventListener("pointerup", stopStroke);          // finger lifted
    canvas.addEventListener("pointercancel", stopStroke);      // system took over the touch

    document.getElementById("clear").addEventListener("click", () => {
      strokes = [];                                            // forget all strokes
      dirty = true;                                            // redraw the empty canvas
    });

    window.addEventListener("resize", sizeCanvas);             // resize clears the bitmap
    sizeCanvas();                                              // set up once at the start
    requestAnimationFrame(loop);                               // start the redraw loop
  </script>
</body>
</html>
```

---

## 🟠 Express.js Integration
Canvas runs in the browser, but the server often needs the result. A common flow is `canvas.toDataURL("image/png")`, which turns the drawing into a Base64 string. Express receives that string, checks it, decodes it with `Buffer`, and saves the PNG file. The example below runs with Node, so you can test it without a browser.

```javascript
// server.js — npm install express; run: node server.js
const express = require("express");                          // web framework
const fs = require("fs/promises");                           // promise-based file system API
const path = require("path");                                // path helper

const app = express();                                       // create the app
app.use(express.json({ limit: "2mb" }));                     // accept JSON bodies up to 2 MB (drawings are large)

const UPLOAD_DIR = path.join(__dirname, "uploads");          // folder for saved signatures

app.post("/api/signature", async (req, res) => {             // route receives the canvas image
  const { dataUrl, orderId } = req.body || {};               // read fields from the JSON body
  const prefix = "data:image/png;base64,";                   // what toDataURL("image/png") produces
  if (typeof dataUrl !== "string" || !dataUrl.startsWith(prefix) || !orderId) {
    return res.status(400).json({ error: "dataUrl (PNG) and orderId are required" }); // bad input
  }
  try {
    const base64 = dataUrl.slice(prefix.length);              // remove the prefix, keep the Base64 part
    const bytes = Buffer.from(base64, "base64");              // decode into binary data
    await fs.mkdir(UPLOAD_DIR, { recursive: true });          // make the folder if it does not exist
    const safeId = String(orderId).replace(/[^a-zA-Z0-9_-]/g, ""); // strip unsafe characters from the name
    const file = path.join(UPLOAD_DIR, `sig-${safeId}.png`);  // target file path
    await fs.writeFile(file, bytes);                          // save the PNG to disk
    res.status(201).json({ saved: path.basename(file), bytes: bytes.length }); // created
  } catch (err) {                                             // disk or decode failure
    console.error("signature save failed:", err.message);     // log on the server
    res.status(500).json({ error: "could not save signature" }); // generic message to the client
  }
});

app.listen(3000, () => console.log("http://localhost:3000")); // start the server
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting `devicePixelRatio`, so the drawing looks blurry on phones
✅ Correct: Set the bitmap size to CSS size times the device pixel ratio, and scale the context once.

```javascript
// Wrong — 300 x 150 bitmap stretched by CSS to 600 x 300 on a 2x screen, so it is blurry
canvas.width = 300;
canvas.height = 150;

// Right — bitmap matches the real device pixels
const r = canvas.getBoundingClientRect();
canvas.width = Math.round(r.width * dpr);
canvas.height = Math.round(r.height * dpr);
ctx.setTransform(dpr, 0, 0, dpr, 0, 0);                    // keep drawing in CSS pixels
```

❌ **Mistake 2:** Forgetting `beginPath()`, so old lines are drawn again
✅ Correct: Each new shape or stroke needs its own path. Without `beginPath()`, `stroke()` repaints everything in the current path.

```javascript
// Wrong — every frame adds a new line to the same path, so older lines repaint
function drawWrong(points) {
  for (const p of points) ctx.lineTo(p.x, p.y);            // path keeps growing
  ctx.stroke();                                            // old segments are drawn again
}

// Right — start a new path for each frame or stroke
function drawRight(points) {
  ctx.beginPath();                                         // empty path first
  ctx.moveTo(points[0].x, points[0].y);                    // start at the first point
  for (const p of points.slice(1)) ctx.lineTo(p.x, p.y);   // add the rest
  ctx.stroke();                                            // paint only this path
}
```

❌ **Mistake 3:** Skipping `clearRect`, so animated shapes leave trails
✅ Correct: The canvas never forgets pixels. Clear the area before drawing the next frame.

```javascript
// Wrong — each frame paints on top of the last one, so the ball leaves a trail
function frameWrong() {
  ctx.fillStyle = "red";
  ctx.arc(x, y, 10, 0, Math.PI * 2);                       // path only, see Mistake 2 too
  ctx.fill();
}

// Right — clear the whole canvas, then draw
function frameRight() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);        // erase the old frame
  ctx.fillStyle = "red";                                   // colour for the ball
  ctx.beginPath();                                         // new path for this frame
  ctx.arc(x, y, 10, 0, Math.PI * 2);                       // ball at its new position
  ctx.fill();                                              // paint it
}
let x = 0, y = 0;                                          // placeholder position
```

---

## 🧠 Tricky Interview Question
Run this in a browser page that has `<canvas id="c" width="200" height="100"></canvas>`. Paste the script into the DevTools console or place it inside a `<script>` tag.

```javascript
const c = document.getElementById("c");                    // the canvas element
const ctx = c.getContext("2d");                            // its 2D context
ctx.fillStyle = "red";                                     // set the fill colour to red
ctx.fillRect(0, 0, 50, 50);                                // paint a red square
c.width = 200;                                             // assigning width (even the same value)
console.log(ctx.fillStyle);                                // what colour is the context now?
console.log(ctx.getImageData(0, 0, 1, 1).data);            // what is the pixel at the top-left corner?
```

Answer: The output is:
```
#000000
Uint8ClampedArray(4) [0, 0, 0, 0]
```
Explanation: Assigning `canvas.width` (or `height`) resets the whole canvas. It clears the bitmap and sets every context property back to its default. `fillStyle` goes back to black (`#000000`), and the red square is gone, so the pixel at (0, 0) is fully transparent, `[0, 0, 0, 0]`. This trap is common in resize code. If you resize the canvas, you must redraw it afterwards, which is why the advanced example sets `dirty = true` inside `sizeCanvas()`.

---

## ⚫ Interview Questions + Answers

Q1: What does `getContext("2d")` return?
A1: A `CanvasRenderingContext2D` object with methods like `fillRect`, `arc`, `drawImage`, and properties like `fillStyle`. It is the object you draw through. The canvas itself only holds the pixel buffer.

Q2: What is the difference between the `width` attribute and CSS `width`?
A2: The `width` attribute (or `canvas.width`) sets the bitmap's pixel count. CSS `width` sets how big the element appears on the page. If they differ, the browser stretches or shrinks the bitmap, which causes blur. Set both, and multiply the bitmap by `devicePixelRatio`.

Q3: Why does a canvas not keep shapes as objects?
A3: It is an immediate-mode API. Once a shape is drawn, only its pixels remain. To move or delete a shape, you redraw the scene from your own data. This is why the sketchpad keeps the `strokes` array.

Q4: Why use `requestAnimationFrame` instead of `setInterval` for animation?
A4: `requestAnimationFrame` runs before each screen refresh, and the browser pauses it in background tabs. `setInterval` runs at a fixed time and can draw out of step with the screen, which causes stutter.

Q5: How do you export a canvas to the server?
A5: Call `canvas.toDataURL("image/png")` for a Base64 string, or `canvas.toBlob()` for a Blob. Send it with `fetch`, then decode and save it on the server, as in the Express example.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You draw many items, such as thousands of chart points, particles, or map tiles, where DOM nodes would be slow
- You need pixel-level work: image editing, filters, signature pads, or games
- You need a fast animation loop with `requestAnimationFrame`

❌ Avoid when:
- The UI is text and buttons; normal HTML and CSS are easier to make accessible and to style
- You need each shape to be a clickable object with its own events; SVG or the DOM handles that more naturally
- You need text that search engines or screen readers must read; canvas text is not in the DOM

---

## 📊 Visual Diagram
```
 HTML page
 ┌──────────────────────────────────────────────┐
 │ <canvas id="c" width="400" height="200">     │
 │   bitmap: 400 x 200 pixels (no DOM children) │
 └──────────────────────┬───────────────────────┘
                        │ getContext("2d")
                        ▼
              ctx (CanvasRenderingContext2D)
              fillStyle, lineWidth, font, transform
                        │
          ┌─────────────┼──────────────┐
          ▼             ▼              ▼
     fillRect()    arc() + fill()  drawImage()
          │             │              │
          └─────────────┴──────────────┘
                        │ writes pixels only
                        ▼
         screen shows the bitmap (no object memory)

 Animation loop:
   requestAnimationFrame ─► clearRect ─► draw scene ─► repeat next frame
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| canvas | Element holding a pixel bitmap for drawing | Pixels का bitmap रखने वाला element |
| 2D context | Object used to draw (`getContext("2d")`) | Drawing करने का object |
| Bitmap | Grid of pixels inside the canvas | Canvas के अंदर pixels का grid |
| fillRect / strokeRect | Draw a filled or outlined rectangle | भरा या खाली आयत बनाना |
| Path | Sequence of lines and curves before `fill` or `stroke` | `fill` या `stroke` से पहले lines और curves का क्रम |
| clearRect | Erases an area to transparent | किसी area को transparent करना |
| devicePixelRatio | Device pixels per CSS pixel | हर CSS pixel के लिए device pixels |
| requestAnimationFrame | Runs code before each screen refresh | हर screen refresh से पहले code चलाना |
| toDataURL | Exports the canvas as a Base64 image string | Canvas को Base64 image string में बदलना |

---

## ⚡ 3-Line Summary
**English:**
1. Canvas is a pixel bitmap that you draw on through a 2D context, with no DOM node per shape.
2. The bitmap keeps only pixels, so clear and redraw the scene each frame, and set the size with `devicePixelRatio`.
3. Use canvas for many moving or pixel-heavy items, and use DOM or SVG when each shape must be a clickable element.

**Hindi:**
1. Canvas pixels का bitmap है, जिस पर 2D context से drawing होती है, और हर shape का DOM node नहीं होता।
2. Bitmap में सिर्फ़ pixels रहते हैं, इसलिए हर frame में साफ़ करके दोबारा बनाएँ, और size `devicePixelRatio` से तय करें।
3. बहुत सारी चलती या pixel-भारी चीज़ों के लिए canvas चुनें, और हर shape clickable होना चाहिए तो DOM या SVG चुनें।

---

## ➡️ Next Topic
**165. Drag and Drop API** — अब सीखेंगे कि browser में elements को mouse या touch से कैसे खींचकर छोड़ा जाता है, और फ़ाइलें page पर कैसे drop होती हैं।
