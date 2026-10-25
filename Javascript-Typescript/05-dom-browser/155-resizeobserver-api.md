# 155. ResizeObserver API
# हिंदी में: ResizeObserver API

---

## 🔵 Simple Definition (English)
`ResizeObserver` tells you when the size of an element changes, whether the window was resized or the element itself was changed by CSS, content, or code. You give it a callback, and it receives the new sizes of every observed element. It is the correct tool for "redraw when my box changes size".

## 🔵 सरल परिभाषा (Hindi)
`ResizeObserver` बताता है कि किसी element का size कब बदला, चाहे window resize हुई हो, या CSS, content या code से element खुद बदला हो। इसे एक callback दिया जाता है, और उसे हर observed element का नया size मिलता है। "मेरा box size बदले तो फिर से draw करो" के लिए यही सही tool है।

---

## 🔴 Problem it Solves
Before this API, developers listened to `window.resize` to redraw charts. That missed changes that were not caused by the window: a sidebar that opened, a flex layout that changed, or a card that grew because its text got longer. Developers also read `offsetWidth` in loops, which forced layout and caused slowdowns. `ResizeObserver` reports the exact size of the specific element, only when it changes, and after layout is done.

## 🔴 यह क्यों बना? (Hindi)
इस API से पहले developers charts को फिर से बनाने के लिए `window.resize` सुनते थे। यह उन बदलावों को नहीं पकड़ता था जो window से नहीं हुए थे: जैसे sidebar खुलना, flex layout बदलना, या text लंबा होने से card बड़ा होना। Developers loops में `offsetWidth` पढ़ते थे, जिससे layout बार-बार निकलता और धीमापन आता। `ResizeObserver` उस element का सही size देता है, सिर्फ तब जब वह बदले, और layout पूरा होने के बाद।

---

## 🟢 How it Works — Step by Step

Step 1 → Create an observer: `new ResizeObserver(callback)`.
Step 2 → Call `observer.observe(element)`. The callback runs once soon after, with the element's starting size.
Step 3 → Whenever the element's size changes (for any reason), the browser calculates the new size after layout.
Step 4 → The callback receives an array of entries. Each entry has `contentRect` and `borderBoxSize`, among others.
Step 5 → The callback runs before the next paint, so changes you make inside it can be drawn in the same frame.
Step 6 → If your callback changes an observed element's size, the browser may skip some entries and log a loop warning. Defer such work with `requestAnimationFrame`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Observer बनाएँ: `new ResizeObserver(callback)`।
Step 2 → `observer.observe(element)` करें। Callback जल्द ही एक बार शुरुआती size के साथ चलता है।
Step 3 → Element का size किसी भी कारण से बदले, browser layout के बाद नया size निकालता है।
Step 4 → Callback को entries का array मिलता है। हर entry में `contentRect`, `borderBoxSize` आदि होते हैं।
Step 5 → Callback अगले paint से पहले चलता है, इसलिए उसके अंदर किए बदलाव उसी frame में दिख सकते हैं।
Step 6 → अगर callback किसी observed element का size बदल दे, तो browser कुछ entries छोड़ सकता है और loop warning देता है। ऐसे काम को `requestAnimationFrame` में टालें।

---

## 🟡 Real World Example
On a restaurant partner dashboard, the sales chart sits in a panel that changes width when the admin opens the left sidebar. A `ResizeObserver` on the chart's container redraws the chart at the new width, which a `window.resize` listener would miss. Flipkart-style product cards use the same idea: when a long product title makes the card taller, the layout reflows, and a `ResizeObserver` updates the image height. Canvas charts also use it with `devicePixelContentBoxSize` to draw sharp on high-DPI screens.

## 🟡 Real Example Hindi mein
Restaurant partner dashboard पर sales chart एक panel में रहता है, जिसकी चौड़ाई तब बदलती है जब admin बाएँ sidebar को खोलता है। Chart के container पर लगा `ResizeObserver` नई चौड़ाई पर chart फिर से बनाता है, जिसे `window.resize` listener नहीं पकड़ता। Flipkart जैसे product cards में भी यही होता है: लंबा product title card की ऊँचाई बढ़ाए तो layout बदलता है और `ResizeObserver` image की ऊँचाई अपडेट करता है। High-DPI screens पर canvas charts `devicePixelContentBoxSize` से तेज़ (sharp) चित्र बनाते हैं।

---

## 💻 Code Example — Basic
Save as `resize-observer-basic.html` and open it in a browser. Drag the bottom-right corner of the box to resize it, and watch the Console.

```html
<!DOCTYPE html>                                      <!-- HTML5 document -->
<html lang="en">                                     <!-- English page -->
<head>
  <meta charset="UTF-8">                             <!-- UTF-8 encoding -->
  <title>ResizeObserver Basic</title>               <!-- tab title -->
  <style>
    #panel { width: 300px; height: 120px; padding: 10px; background: #cde;
             border: 2px solid #357; resize: both; overflow: auto; } /* resize: both lets the user drag the corner */
  </style>
</head>
<body>
  <div id="panel">Drag the bottom-right corner to resize me.</div> <!-- the element we observe -->

  <script>
    const panel = document.getElementById("panel");  // the element to watch
    const ro = new ResizeObserver((entries) => {     // callback gets one entry per observed element
      for (const entry of entries) {                 // check each entry (here just one)
        const { width, height } = entry.contentRect; // size of the content area (no padding, no border)
        console.log(`content size: ${Math.round(width)} x ${Math.round(height)}`); // print it
      }
    });
    ro.observe(panel);                               // start watching the panel
    window.addEventListener("pagehide", () => ro.disconnect(), { once: true }); // stop on page leave
  </script>
</body>
</html>
```

## 💻 Code Example — Advanced
Save as `resize-observer-advanced.html`. It draws a canvas bar chart that stays sharp at any size and any device pixel ratio. It uses `devicePixelContentBoxSize` when available, falls back to `contentRect`, defers the redraw with `requestAnimationFrame` to avoid the loop warning, and disconnects cleanly.

```html
<!DOCTYPE html>                                      <!-- HTML5 document -->
<html lang="en">                                     <!-- English page -->
<head>
  <meta charset="UTF-8">                             <!-- UTF-8 encoding -->
  <title>Responsive canvas chart</title>            <!-- tab title -->
  <style>
    #wrap { width: 60%; min-width: 240px; height: 260px; resize: horizontal; overflow: hidden; } /* resizable box */
    canvas { display: block; width: 100%; height: 100%; }  /* canvas fills the wrapper via CSS */
  </style>
</head>
<body>
  <div id="wrap"><canvas id="chart"></canvas></div> <!-- the wrapper is what we observe -->

  <script>
    const wrap = document.getElementById("wrap");   // the element whose size we watch
    const canvas = document.getElementById("chart"); // the canvas we draw on
    const ctx = canvas.getContext("2d");            // 2D drawing context
    const data = [12, 45, 30, 60, 22];              // sample values to draw as bars
    let frame = null;                               // id of a queued animation frame, or null

    function draw(cssW, cssH, dpr) {                // draw at the real pixel size for this screen
      canvas.width = Math.round(cssW * dpr);        // backing store width in device pixels
      canvas.height = Math.round(cssH * dpr);       // backing store height in device pixels
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);       // scale so drawing code uses CSS pixels
      ctx.clearRect(0, 0, cssW, cssH);              // erase the previous frame
      const max = Math.max(...data);                // biggest value, used to scale the bars
      const barW = cssW / data.length;              // width of each bar slot
      data.forEach((v, i) => {                      // draw each bar
        const h = (v / max) * (cssH - 20);          // bar height, leaving room at the top
        ctx.fillStyle = "#357";                     // bar colour
        ctx.fillRect(i * barW + 6, cssH - h, barW - 12, h); // x, y, width, height of the bar
      });
    }

    const ro = new ResizeObserver((entries) => {    // runs before the next paint after a size change
      const entry = entries[0];                     // only one element is observed
      // Prefer the exact device-pixel size; fall back to CSS size times the device pixel ratio
      const box = entry.devicePixelContentBoxSize?.[0]; // optional chaining: may be undefined
      const dpr = window.devicePixelRatio || 1;     // screen density, e.g. 2 on retina
      const cssW = entry.contentRect.width;         // CSS width of the content area
      const cssH = entry.contentRect.height;        // CSS height of the content area
      if (box && box.inlineSize > 0) {              // exact device pixel size is available
        if (frame) cancelAnimationFrame(frame);     // drop any queued frame; keep only the latest
        frame = requestAnimationFrame(() => {       // defer the drawing to avoid the loop warning
          frame = null;                             // the queued frame has now run
          draw(box.inlineSize / dpr, box.blockSize / dpr, dpr); // draw using the exact size
        });
      } else if (cssW > 0 && cssH > 0) {            // fallback path for older browsers
        if (frame) cancelAnimationFrame(frame);     // same deferral as above
        frame = requestAnimationFrame(() => {       // defer the drawing
          frame = null;                             // reset the frame id
          draw(cssW, cssH, dpr);                    // draw using the CSS size
        });
      }
    });

    if ("ResizeObserver" in window) {               // feature check before using the API
      ro.observe(wrap);                             // start watching the wrapper
    } else {                                        // very old browser: fall back to window resize
      window.addEventListener("resize", () => draw(wrap.clientWidth, wrap.clientHeight, window.devicePixelRatio || 1));
    }

    window.addEventListener("pagehide", () => {     // page is leaving
      ro.disconnect();                              // stop observing
      if (frame) cancelAnimationFrame(frame);       // cancel any queued drawing
    }, { once: true });                             // run this cleanup once
  </script>
</body>
</html>
```

---

## 🟠 Express.js Integration
`ResizeObserver` runs only in the browser. The closest real usage is a chart that asks the server for an image sized to its container. The browser reports its width on resize, and the server returns an SVG drawn at that width. Clamping the width on the server stops clients from requesting huge images.

```javascript
// server.js — npm install express ; run: node server.js
const express = require("express");               // web framework
const app = express();                            // create the app
app.use(express.static("public"));                // serve public/index.html (with the observer)

// Returns a bar chart as SVG, sized to the width the browser asks for
app.get("/api/chart.svg", (req, res) => {         // handle GET /api/chart.svg?width=480
  const width = Math.min(1200, Math.max(120, parseInt(req.query.width, 10) || 480)); // clamp 120..1200
  const height = 200;                             // fixed chart height in pixels
  const values = [12, 45, 30, 60, 22];            // sample data (a real app reads it from a database)
  const max = Math.max(...values);                // largest value, used for scaling
  const barW = width / values.length;             // width of each bar slot
  const bars = values.map((v, i) => {             // build one <rect> per value
    const h = (v / max) * (height - 20);          // bar height in pixels
    return `<rect x="${i * barW + 6}" y="${height - h}" width="${barW - 12}" height="${h}" fill="#357"/>`;
  }).join("");                                    // join the rectangles into one string
  res.type("image/svg+xml");                      // tell the browser this is SVG
  res.set("Cache-Control", "public, max-age=60"); // let browsers cache it for 60 seconds
  res.send(`<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}">${bars}</svg>`);
});

app.listen(3000, () => console.log("http://localhost:3000")); // start the server
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Changing the observed element's size inside the callback, which causes the "ResizeObserver loop" error
✅ Correct: Defer the change with `requestAnimationFrame`, so it happens in the next frame and does not change the size while the callback is still running.

```javascript
// Wrong — resizing the observed box inside the callback can trigger another resize in the same frame
const ro1 = new ResizeObserver((entries) => {
  const box = entries[0].target;                // the observed element
  box.style.height = box.offsetWidth + "px";    // changes its own size: loop warning
});
ro1.observe(document.getElementById("card"));  // card is observed

// Right — defer the change to the next frame
const ro2 = new ResizeObserver((entries) => {
  const box = entries[0].target;                // the observed element
  requestAnimationFrame(() => {                 // run in the next frame, after the callback
    box.style.height = box.offsetWidth + "px";  // safe: no loop in the same frame
  });
});
ro2.observe(document.getElementById("card"));  // card is observed
```

❌ **Mistake 2:** Using `contentRect` for the full box size, which leaves out padding and border
✅ Correct: `contentRect` is the content area only. Use `borderBoxSize` when you need the full size of the element including padding and border.

```javascript
// Wrong — with padding 10px on each side, this reports 20px less than the real box
const ro3 = new ResizeObserver((entries) => {
  const fullWidth = entries[0].contentRect.width; // content area only: padding excluded
});

// Right — borderBoxSize gives the full width including padding and border
const ro4 = new ResizeObserver((entries) => {
  const fullWidth = entries[0].borderBoxSize[0].inlineSize; // includes padding and border
});
```

❌ **Mistake 3:** Using `window.resize` to redraw a component that changes size for other reasons
✅ Correct: Observe the component's own element with `ResizeObserver`, which catches all size changes.

```javascript
// Wrong — misses the case where the sidebar opens and the chart panel shrinks
window.addEventListener("resize", () => drawChart(panel.clientWidth)); // window size unchanged, panel changed

// Right — the observer fires whenever the panel itself changes size
new ResizeObserver(() => drawChart(panel.clientWidth)).observe(panel); // catches every panel change
function drawChart(w) {}                        // placeholder drawing function
const panel = document.createElement("div");    // placeholder element
```

---

## 🧠 Tricky Interview Question
What is printed? The element has `width: 200px`, `padding: 10px`, and the default `box-sizing: content-box`.

```html
<div id="card" style="width: 200px; padding: 10px;">Hi</div> <!-- content-box by default -->
<script>
  const ro = new ResizeObserver((entries) => {      // the callback
    const e = entries[0];                           // the single entry for the card
    console.log("contentRect width:", e.contentRect.width);        // content area only
    console.log("borderBox width:", e.borderBoxSize[0].inlineSize); // full box with padding
  });
  ro.observe(document.getElementById("card"));      // observe the card
</script>
```

Answer: The output is:
```
contentRect width: 200
borderBox width: 220
```
Explanation: The callback runs once right after `observe()`, with the element's starting size. `contentRect` describes the content area, which is the 200px set by `width`, so padding is not included. `borderBoxSize` is the full box, which is 200px content plus 10px padding on each side, giving 220px. Many developers assume `contentRect` is the full size, which is why Mistake 2 matters.

---

## ⚫ Interview Questions + Answers

Q1: When does a `ResizeObserver` callback run?
A1: Once right after `observe()` with the starting size, and again whenever the observed element's size changes. It runs after layout and before the next paint.

Q2: Why does a `window.resize` listener miss some changes?
A2: `window.resize` fires only when the browser window changes size. A sidebar opening, a flex layout change, or text growing a card does not change the window, so the listener never fires.

Q3: What is the "ResizeObserver loop" error?
A3: It appears when a callback changes the size of an observed element in a way that causes another resize in the same frame. The browser skips those notifications and logs a warning. The fix is to defer the change with `requestAnimationFrame`.

Q4: What is the difference between `contentRect` and `borderBoxSize`?
A4: `contentRect` covers only the content area, without padding and border. `borderBoxSize` covers the full box including padding and border. There is also `contentBoxSize`, which matches `contentRect` but is given as an array with `inlineSize` and `blockSize`.

Q5: How do you stop observing?
A5: Call `observer.unobserve(element)` to stop one element, or `observer.disconnect()` to stop all elements of that observer. Use `disconnect()` when the whole component is removed.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You draw charts, canvases, or maps that must match their container's size
- A component's layout changes because of a sidebar, tab, or text, not only the window
- You need exact device-pixel sizes for sharp drawing (`devicePixelContentBoxSize`)

❌ Avoid when:
- You only need to know whether an element is visible; use `IntersectionObserver` (topic 153)
- You only need to know the window size; `window.innerWidth` and `resize` are enough
- You change the observed element's own size in the callback without `requestAnimationFrame`, which causes the loop error

---

## 📊 Visual Diagram
```
  Layout pass                      ResizeObserver step              Paint
 ───────────────────────────────────────────────────────────────────────────►
 CSS / content / window change ──► browser computes new sizes ──► callback(entries)
                                                                     │
                                       ┌─────────────────────────────┤
                                       │ change sizes here?          │
                                       ▼                             │
                             requestAnimationFrame(redraw)           │
                                       │                             │
                                       ▼ next frame                  ▼
                                 redraw with new size          paint shows result

 Element box:  ┌────────── border-box (borderBoxSize) ──────────┐
               │ border                                          │
               │  ┌──────── content-box (contentRect) ────────┐   │
               │  │  text, canvas, children                    │   │
               │  └───────────────────────────────────────────┘   │
               └─────────────────────────────────────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ResizeObserver | Browser API that reports element size changes | Element का size बदलने की खबर देने वाला API |
| `contentRect` | Content area size, without padding and border | Padding और border के बिना content का size |
| `borderBoxSize` | Full box size with padding and border | Padding और border सहित पूरा size |
| `contentBoxSize` | Content size as an array (`inlineSize`, `blockSize`) | Content का size, array के रूप में |
| `devicePixelContentBoxSize` | Content size in device pixels | Device pixels में content का size |
| Resize loop | Callback changes size, causing another notification | Callback से size बदलकर फिर नई notification आना |
| `requestAnimationFrame` | Runs code before the next paint | अगले paint से पहले code चलाना |
| `unobserve` / `disconnect` | Stop observing one / all elements | एक या सारे elements को देखना बंद करना |

---

## ⚡ 3-Line Summary
**English:**
1. `ResizeObserver` reports the size of an element whenever it changes, for any reason, not only window resizes.
2. Use `contentRect` for the content area and `borderBoxSize` for the full box, and redraw inside `requestAnimationFrame` to avoid the loop error.
3. Use `disconnect()` when the component is removed, and prefer it over `window.resize` for component-level layouts.

**Hindi:**
1. `ResizeObserver` किसी element का size बदलने पर हर कारण से खबर देता है, सिर्फ window resize पर नहीं।
2. Content area के लिए `contentRect` और पूरे box के लिए `borderBoxSize` इस्तेमाल करें, और loop error से बचने के लिए redraw `requestAnimationFrame` में करें।
3. Component हटने पर `disconnect()` करें, और component-level layout के लिए `window.resize` से बेहतर यही है।

---

## ➡️ Next Topic
**156. Event Delegation** — अगला topic बताता है कि बहुत सारे elements पर अलग-अलग listeners लगाने की जगह एक parent पर listener कैसे लगाएँ।
