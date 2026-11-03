# 161. React + Canvas
# हिंदी में: React + Canvas — तेज़ Graphics और Animation Draw करना

---

## 🔵 Simple Definition (English)
The HTML **`<canvas>`** is a pixel surface you draw on with JavaScript (`getContext('2d')`). It is **imperative**: you tell it "draw a circle here", it does not remember objects. In React you render one `<canvas>` element, keep a `ref` to it, and run the drawing code in `useEffect`.

## 🔵 सरल परिभाषा (Hindi)
HTML **`<canvas>`** एक pixel सतह है जिस पर आप JavaScript (`getContext('2d')`) से draw करते हैं। यह **imperative** है: आप कहते हैं "यहाँ एक circle बनाओ", वह objects को याद नहीं रखता। React में आप एक `<canvas>` element render करते हैं, उसका `ref` रखते हैं, और drawing code `useEffect` में चलाते हैं।

---

## 🔴 Problem it Solves

DOM and SVG create one node per shape. A heat map with 50,000 points, a signature pad, a particle animation or a game would create thousands of DOM elements, and React would diff all of them on each update, making the page slow. Canvas draws pixels directly: one element, no per-shape node, no React diffing. The challenge: React is declarative and Canvas is imperative, so you must bridge them carefully.

```jsx
// PROBLEM: 20,000 DOM nodes for a live scatter plot
{points.map((p) => <circle key={p.id} cx={p.x} cy={p.y} r="2" />)}   // slow to create, diff and paint
```

## 🔴 यह क्यों बना? (Hindi)
DOM और SVG हर shape के लिए एक node बनाते हैं। 50,000 points का heat map, signature pad, particle animation या game हज़ारों DOM elements बना देता, और हर update पर React उन सबको diff करता, जिससे page धीमा होता। Canvas सीधे pixels draw करता है: एक element, हर shape का node नहीं, React diffing नहीं। चुनौती यह है कि React declarative है और Canvas imperative, इसलिए दोनों को सावधानी से जोड़ना पड़ता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Render <canvas ref={canvasRef} width={w} height={h} /> (React only owns this one element)
Step 2 → In useEffect, get ctx = canvasRef.current.getContext('2d')
Step 3 → Draw with ctx.fillRect, arc, lineTo, drawImage, fillText ...
Step 4 → For animation: requestAnimationFrame(loop) and cancelAnimationFrame in cleanup
Step 5 → Keep fast-changing values (positions, time) in refs, NOT in state, so React does not re-render 60 times a second
Step 6 → Re-draw when React props/state change by listing them in the effect dependencies
Step 7 → Handle high-DPI screens: scale the canvas by devicePixelRatio, keep CSS size separate
Step 8 → Canvas content is not in the DOM: add aria-label / fallback content for accessibility

Re-render behavior: React re-renders the component only when props/state change; drawing happens in
an effect or rAF loop and does NOT cause re-renders. Updating state every frame is the #1 mistake.
Performance impact: draw cost depends on pixels and shapes, not on React; batch draw calls, avoid
clearing/redrawing more than needed, and use OffscreenCanvas/workers for very heavy scenes.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → <canvas ref={canvasRef} width={w} height={h} /> render करो (React सिर्फ़ इसी एक element का मालिक है)
Step 2 → useEffect में ctx = canvasRef.current.getContext('2d') लो
Step 3 → ctx.fillRect, arc, lineTo, drawImage, fillText ... से draw करो
Step 4 → Animation के लिए: requestAnimationFrame(loop) और cleanup में cancelAnimationFrame
Step 5 → तेज़ी से बदलने वाले मान (positions, time) refs में रखो, state में नहीं, ताकि React सेकंड में 60 बार re-render न हो
Step 6 → React props/state बदलने पर दोबारा draw करने के लिए उन्हें effect dependencies में लिखो
Step 7 → High-DPI screens: canvas को devicePixelRatio से scale करो, CSS size अलग रखो
Step 8 → Canvas का content DOM में नहीं होता: accessibility के लिए aria-label / fallback content दो

Re-render behavior: React तभी re-render करता है जब props/state बदलें; drawing effect या rAF loop में होती है
और re-render नहीं कराती। हर frame state बदलना सबसे बड़ी गलती है।
Performance impact: draw की लागत pixels और shapes पर निर्भर है, React पर नहीं; draw calls batch करो,
ज़रूरत से ज़्यादा clear/redraw मत करो, बहुत भारी scene के लिए OffscreenCanvas/workers लो।
```

---

## 🟡 Real World Example
**Zerodha Kite / Groww charts and Google Maps heat layers:** A candlestick chart with thousands of candles, plus a crosshair that follows the mouse, is drawn on canvas because creating a DOM node per candle would make scrolling stutter. Other examples: Figma's canvas, Instagram's photo filter preview, Swiggy's delivery-heat map, and "sign here" boxes in digital KYC forms.

## 🟡 Real Example Hindi mein
**Zerodha Kite / Groww charts और Google Maps heat layers:** हज़ारों candles वाला candlestick chart और mouse के पीछे चलने वाला crosshair canvas पर बनाया जाता है, क्योंकि हर candle के लिए DOM node बनाने से scrolling अटकती। दूसरे उदाहरण: Figma का canvas, Instagram का photo filter preview, Swiggy का delivery-heat map, और digital KYC forms में "यहाँ sign करें" वाले boxes।

---

## 💻 Code Example — Basic

```jsx
// Basic: draw a bar chart on a canvas whenever `data` changes
import { useEffect, useRef } from 'react';
import { createRoot } from 'react-dom/client';

function BarChart({ data, width = 300, height = 150 }) {
  const canvasRef = useRef(null);                          // reference to the real <canvas> DOM node

  useEffect(() => {
    const canvas = canvasRef.current;                      // DOM node (exists after mount)
    const ctx = canvas.getContext('2d');                   // 2D drawing API
    ctx.clearRect(0, 0, width, height);                    // erase the previous drawing
    const max = Math.max(...data, 1);                      // largest value for scaling (avoid divide by 0)
    const barW = width / data.length;                      // width of each bar slot
    data.forEach((v, i) => {
      const h = (v / max) * (height - 10);                 // scaled bar height
      ctx.fillStyle = '#e23744';                           // Zomato-like red
      ctx.fillRect(i * barW + 4, height - h, barW - 8, h); // x, y, width, height
    });
  }, [data, width, height]);                               // redraw only when these change

  return <canvas ref={canvasRef} width={width} height={height} aria-label="Orders per day chart" role="img" />;
}

createRoot(document.getElementById('root')).render(<BarChart data={[12, 30, 18, 45, 27]} />);
```

## 💻 Code Example — Advanced

```jsx
// Advanced: animated particles with requestAnimationFrame, refs for fast data,
// High-DPI scaling, resize handling, pause on unmount, and a drawing (signature) pad.
import { useEffect, useRef, useState } from 'react';

// ---------- 1. Animation loop hook: no React state per frame ----------
function useAnimationFrame(callback) {
  const cbRef = useRef(callback);                          // always latest callback
  cbRef.current = callback;                                // update without restarting the loop
  useEffect(() => {
    let id;                                                // rAF id
    let last = performance.now();                          // previous timestamp
    const loop = (now) => {
      const dt = (now - last) / 1000;                      // seconds since last frame
      last = now;
      cbRef.current(dt);                                   // draw using elapsed time
      id = requestAnimationFrame(loop);                    // schedule next frame
    };
    id = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(id);                 // stop on unmount (no leaks)
  }, []);
}

// ---------- 2. Particle canvas ----------
export function Particles({ count = 80 }) {
  const canvasRef = useRef(null);
  const particles = useRef([]);                            // mutable simulation data (NOT state)
  const size = useRef({ w: 0, h: 0 });                     // CSS pixel size

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    function resize() {
      const dpr = window.devicePixelRatio || 1;            // 2 on retina screens
      const { clientWidth: w, clientHeight: h } = canvas;  // CSS size from layout
      canvas.width = w * dpr;                              // backing store size
      canvas.height = h * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);              // draw in CSS pixels, sharp on retina
      size.current = { w, h };
      if (particles.current.length === 0) {                // create particles once
        particles.current = Array.from({ length: count }, () => ({
          x: Math.random() * w, y: Math.random() * h,
          vx: (Math.random() - 0.5) * 60, vy: (Math.random() - 0.5) * 60,   // pixels per second
        }));
      }
    }
    resize();
    window.addEventListener('resize', resize);             // keep it crisp when the window changes
    return () => window.removeEventListener('resize', resize);
  }, [count]);

  useAnimationFrame((dt) => {
    const ctx = canvasRef.current?.getContext('2d');
    if (!ctx) return;
    const { w, h } = size.current;
    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = '#fc8019';                             // Swiggy orange
    for (const p of particles.current) {
      p.x = (p.x + p.vx * dt + w) % w;                     // move and wrap around the edges
      p.y = (p.y + p.vy * dt + h) % h;
      ctx.beginPath();
      ctx.arc(p.x, p.y, 2.5, 0, Math.PI * 2);              // draw a dot
      ctx.fill();
    }
  });

  return <canvas ref={canvasRef} style={{ width: '100%', height: 200, background: '#111' }} aria-hidden="true" />;
}

// ---------- 3. Signature pad using pointer events ----------
export function SignaturePad() {
  const canvasRef = useRef(null);
  const drawing = useRef(false);                           // is the pointer down? (ref: no re-render)
  const [empty, setEmpty] = useState(true);                // UI state: enable/disable the Clear button

  const pos = (e) => {
    const r = canvasRef.current.getBoundingClientRect();   // canvas position on screen
    return { x: e.clientX - r.left, y: e.clientY - r.top };// pointer inside canvas coordinates
  };

  function down(e) {
    drawing.current = true;
    const ctx = canvasRef.current.getContext('2d');
    const { x, y } = pos(e);
    ctx.beginPath(); ctx.moveTo(x, y);                     // start a new stroke
    canvasRef.current.setPointerCapture(e.pointerId);      // keep events if the pointer leaves
  }
  function move(e) {
    if (!drawing.current) return;
    const ctx = canvasRef.current.getContext('2d');
    const { x, y } = pos(e);
    ctx.lineTo(x, y); ctx.stroke();                        // extend the stroke
    if (empty) setEmpty(false);                            // state changes only once
  }
  function up() { drawing.current = false; }

  function clear() {
    const c = canvasRef.current;
    c.getContext('2d').clearRect(0, 0, c.width, c.height);
    setEmpty(true);
  }

  return (
    <div>
      <canvas
        ref={canvasRef} width={300} height={120}
        style={{ border: '1px solid #999', touchAction: 'none' }}   // touchAction none: stop page scroll while signing
        onPointerDown={down} onPointerMove={move} onPointerUp={up}
      />
      <button onClick={clear} disabled={empty}>Clear</button>
    </div>
  );
}
```

---

## 🟠 Next.js Connection

Canvas needs browser APIs, so use it only in **Client Components** (`'use client'`) and inside `useEffect` (which never runs during server rendering, so `document` and `window` are safe there). For heavy canvas libraries that touch `window` at import time, load them with `next/dynamic` and `ssr: false` (in the App Router this option must be used from a Client Component). React Three Fiber (for 3D) and react-konva are popular wrappers that follow the same rules.

```jsx
// app/reports/page.jsx : Server Component prepares data, client island draws it
import ChartClient from './ChartClient';                   // Client Component wrapper

export default async function Page() {
  const orders = [12, 30, 18, 45, 27];                     // pretend this came from the database
  return (
    <main>
      <h1>Orders this week</h1>
      <ChartClient data={orders} />                        {/* plain data crosses the boundary */}
    </main>
  );
}
```

```jsx
// app/reports/ChartClient.jsx
'use client';
import dynamic from 'next/dynamic';                        // lazy-load without server rendering

// BarChart touches the DOM; load it only in the browser and show a placeholder meanwhile
const BarChart = dynamic(() => import('@/components/BarChart'), {
  ssr: false,
  loading: () => <p>Loading chart...</p>,
});

export default function ChartClient({ data }) {
  return <BarChart data={data} />;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Storing animation values (x, y, time) in `useState` and updating them every frame
✅ **Correct:** Keep them in `useRef`; draw directly, and use state only for UI that must re-render

```jsx
// Wrong: 60 re-renders per second
const [x, setX] = useState(0);
useAnimationFrame(() => setX((v) => v + 1));      // ❌ re-renders the component every frame
// Right
const x = useRef(0);
useAnimationFrame(() => { x.current += 1; draw(x.current); });   // ✅ no re-render
```

❌ **Mistake 2:** Forgetting to cancel `requestAnimationFrame` and listeners on unmount
✅ **Correct:** Return a cleanup from `useEffect`

```jsx
// Wrong
useEffect(() => { const loop = () => { draw(); requestAnimationFrame(loop); }; loop(); }, []); // ❌ runs forever
// Right
useEffect(() => {
  let id; const loop = () => { draw(); id = requestAnimationFrame(loop); }; loop();
  return () => cancelAnimationFrame(id);                                                     // ✅
}, []);
```

❌ **Mistake 3:** Styling width/height with CSS only (the drawing looks blurry or stretched)
✅ **Correct:** Set the `width`/`height` attributes (backing store) and scale for `devicePixelRatio`

```jsx
// Wrong: canvas is 300x150 pixels stretched to 600x300 → blurry
<canvas style={{ width: 600, height: 300 }} />                    // ❌
// Right: match the backing store to the display (see resize() in Particles)       ✅
```

---

## 🧠 Tricky Interview Question

```jsx
function Box({ color }) {
  const ref = useRef(null);
  useEffect(() => {
    const ctx = ref.current.getContext('2d');
    ctx.fillStyle = color;
    ctx.fillRect(0, 0, 50, 50);
  });                                         // no dependency array
  return <canvas ref={ref} width={50} height={50} />;
}
```
**Answer:** It works but redraws after every render (no dependency array). If the parent re-renders for unrelated reasons, the same pixels are redrawn, which wastes time on bigger scenes. Also, changing `width` or `height` attributes **clears** the canvas, so a re-render that changes size erases the drawing and needs a redraw. Best practice: `[color]` as dependencies, and redraw whenever the size changes. React will not reset canvas pixels by itself when only other props change, because it does not touch pixels.

---

## ⚫ Interview Questions + Answers

Q1: Canvas vs SVG in React?
A1: SVG elements are DOM nodes, declarative, accessible and styleable, but slow with thousands of nodes. Canvas is pixel-based, imperative and fast for large or frequently changing scenes, but has no built-in element hit-testing or accessibility. Use SVG for up to a few hundred interactive shapes (charts, icons) and Canvas for heavy scenes.

Q2: Why is `useEffect` (or a ref) needed to draw on a canvas?
A2: The canvas DOM node exists only after React commits. The `ref` gives access to it, and the effect runs after commit, so `getContext` works. Drawing in the render function would be a side effect and would also fail on the server.

Q3: How do you animate without re-rendering 60 times per second?
A3: Use `requestAnimationFrame` in an effect, keep simulation data in refs, draw directly to the context, and cancel in cleanup. Use state only for rare UI changes (buttons, scores).

Q4: How do you make canvas sharp on retina screens?
A4: Set `canvas.width/height` to CSS size multiplied by `devicePixelRatio`, set CSS size to the logical size, and call `ctx.scale(dpr, dpr)` or `setTransform`.

Q5: How do you handle accessibility and events on canvas?
A5: Provide `role="img"` with `aria-label` (or fallback content inside the tag), offer a text/table alternative for data charts, make controls real buttons, and do your own hit-testing from pointer coordinates. Libraries like Konva or PixiJS provide event handling per shape.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Thousands of shapes, charts with large data, games, particle effects, image editing
- Frequent redraws (60 fps animation, real-time feeds)
- Drawing/signature tools

❌ **Avoid when:**
- Content is mostly text and UI (DOM is better for accessibility and SEO)
- You have few shapes that need CSS styling, tooltips and click handlers (SVG is simpler)
- You need the content to be searchable or selectable by the browser

---

## 📊 Visual Diagram

```
  React world (declarative)                Canvas world (imperative)
  ┌───────────────────────┐                ┌─────────────────────────────┐
  │ <BarChart data=[..]/> │                │  pixels: no objects, no DOM │
  │  state / props        │                │  ctx.fillRect(...)          │
  │        │              │                │  ctx.arc(...)               │
  │   <canvas ref=.../>   │──ref.current──►│  getContext('2d')           │
  └───────────────────────┘                └─────────────────────────────┘
        ▲ re-render only on props/state          ▲ useEffect / rAF loop draws
        │                                        │
   [data changes] ─► effect deps ─► clear + redraw      [every frame] ─► refs, NO setState
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Canvas | Pixel drawing surface | Pixels पर draw करने की सतह |
| Context (ctx) | Object with drawing methods | Drawing methods वाला object |
| Imperative | Step-by-step commands | क्रम से आदेश देना |
| requestAnimationFrame | Browser frame callback | हर frame पर चलने वाला callback |
| devicePixelRatio | Physical to CSS pixel ratio | Physical और CSS pixels का अनुपात |
| Backing store | Real pixel buffer of canvas | Canvas का असली pixel buffer |
| Hit-testing | Finding shape under pointer | Pointer के नीचे की shape ढूँढना |
| OffscreenCanvas | Canvas usable in workers | Worker में चलने वाला canvas |

---

## ⚡ 3-Line Summary
**English:**
1. Canvas draws pixels imperatively; React renders one `<canvas>` and you draw in `useEffect` using a ref.
2. Keep fast-changing animation data in refs, drive loops with `requestAnimationFrame`, and always clean up.
3. Use Canvas for heavy scenes, SVG for small interactive graphics, and `'use client'` plus `dynamic(ssr:false)` in Next.js.

**Hindi:**
1. Canvas pixels imperative रूप से draw करता है; React एक `<canvas>` render करता है और आप ref से `useEffect` में draw करते हैं।
2. तेज़ी से बदलने वाला animation data refs में रखो, loops `requestAnimationFrame` से चलाओ, और cleanup हमेशा करो।
3. भारी scenes के लिए Canvas, छोटे interactive graphics के लिए SVG, और Next.js में `'use client'` के साथ `dynamic(ssr:false)` लो।

---

## ➡️ Next Topic
**162. React + D3.js Basics** — Charts बनाने के लिए D3 की scales, axes और data math को React के साथ जोड़ना सीखेंगे, ताकि SVG या Canvas पर साफ़ data visualisation बने।
