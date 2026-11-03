# 162. React + D3.js Basics
# हिंदी में: React + D3.js — Data Visualisation (Charts) बनाना

---

## 🔵 Simple Definition (English)
**D3.js** is a JavaScript library of data-visualisation tools: **scales** (data to pixels), **shapes** (line, arc, area generators), **axes**, and layouts. With React, the best pattern is: let **D3 do the math** and **React render the SVG**, instead of letting D3 manipulate the DOM.

## 🔵 सरल परिभाषा (Hindi)
**D3.js** data visualisation के औज़ारों की JavaScript library है: **scales** (data से pixels), **shapes** (line, arc, area generators), **axes**, और layouts। React के साथ सबसे अच्छा तरीका है: **D3 गणित करे** और **React SVG render करे**, D3 को DOM सीधे बदलने न दें।

---

## 🔴 Problem it Solves

Writing a chart by hand means calculating every x/y position, tick label and path string yourself. D3 solves that math. But D3's classic style (`d3.select('svg').append('rect')...`) directly mutates the DOM, which fights with React: React does not know about those nodes, re-renders can wipe them, and you end up with two systems controlling one element.

```jsx
// PROBLEM: D3 and React both own the same SVG
useEffect(() => {
  d3.select(ref.current).selectAll('rect').data(data).join('rect') /* ... */;  // D3 mutates DOM
}, [data]);
// React re-render, Strict Mode double effect, and conditional rendering can conflict with this.
```

## 🔴 यह क्यों बना? (Hindi)
हाथ से chart बनाने का मतलब है हर x/y position, tick label और path string खुद गिनना। D3 यह गणित सँभालता है। पर D3 की पुरानी शैली (`d3.select('svg').append('rect')...`) DOM सीधे बदलती है, जो React से टकराती है: React को उन nodes की जानकारी नहीं, re-render उन्हें मिटा सकता है, और एक element पर दो सिस्टम का कब्ज़ा हो जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Install only the D3 modules you need: npm i d3-scale d3-shape d3-array (or the full "d3")
Step 2 → Define dimensions and margins (width, height, margin { top, right, bottom, left })
Step 3 → Create SCALES: scaleLinear/scaleTime/scaleBand map data values to pixel positions
Step 4 → Create GENERATORS: line(), area(), arc() turn data into SVG path strings
Step 5 → In React JSX, render <svg>, <path d={line(data)}>, <rect>, <text> from the scale outputs
Step 6 → Draw axes yourself from scale.ticks() as <line>/<text>, or use d3-axis in a ref for quick work
Step 7 → useMemo the scales and paths so they are recomputed only when data or size change
Step 8 → Use D3 DOM manipulation only for things React cannot do well: zoom/brush/drag behaviours, via ref

Re-render behavior: React re-renders the SVG when data/size change; each datum is a React element that
React diffs. For > ~2,000 elements, switch to Canvas or aggregate the data first.
Performance impact: scales are cheap; the cost is the number of SVG nodes. Memoise computed paths.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → सिर्फ़ ज़रूरी D3 modules install करो: npm i d3-scale d3-shape d3-array (या पूरा "d3")
Step 2 → Dimensions और margins तय करो (width, height, margin { top, right, bottom, left })
Step 3 → SCALES बनाओ: scaleLinear/scaleTime/scaleBand data values को pixel positions में बदलते हैं
Step 4 → GENERATORS बनाओ: line(), area(), arc() data को SVG path strings में बदलते हैं
Step 5 → React JSX में scale के नतीजों से <svg>, <path d={line(data)}>, <rect>, <text> render करो
Step 6 → Axes scale.ticks() से खुद <line>/<text> की तरह बनाओ, या जल्दी काम के लिए d3-axis ref में चलाओ
Step 7 → Scales और paths को useMemo करो ताकि वे सिर्फ़ data या size बदलने पर दोबारा बनें
Step 8 → D3 की DOM manipulation सिर्फ़ उन चीज़ों के लिए जो React अच्छे से नहीं कर पाता: zoom/brush/drag, ref के ज़रिए

Re-render behavior: data/size बदलने पर React SVG फिर से render करता है; हर datum एक React element है
जिसे React diff करता है। ~2,000 से ज़्यादा elements हों तो Canvas पर जाओ या data aggregate करो।
Performance impact: scales सस्ते हैं; लागत SVG nodes की संख्या की है। गणना किए paths को memoise करो।
```

---

## 🟡 Real World Example
**Zerodha / Groww stock price line chart and Swiggy "orders per hour" dashboard:** The price history array `[{date, close}, ...]` goes through a time scale for the x axis and a linear scale for the y axis. A `d3.line()` generator turns it into one SVG path. React draws the path, the axis ticks and a hover tooltip. When the user picks "1M" instead of "1Y", the data array changes and React redraws the chart.

## 🟡 Real Example Hindi mein
**Zerodha / Groww stock price line chart और Swiggy "orders per hour" dashboard:** Price history array `[{date, close}, ...]` x axis के लिए time scale और y axis के लिए linear scale से गुज़रता है। `d3.line()` generator उसे एक SVG path में बदलता है। React path, axis ticks और hover tooltip draw करता है। User "1Y" की जगह "1M" चुने तो data array बदलता है और React chart फिर बनाता है।

---

## 💻 Code Example — Basic

```jsx
// Basic: bar chart. D3 for scales, React for the SVG. Needs: npm i d3
import { scaleBand, scaleLinear, max } from 'd3';        // D3 does the math only
import { createRoot } from 'react-dom/client';

const data = [                                           // orders per weekday
  { day: 'Mon', orders: 120 }, { day: 'Tue', orders: 98 }, { day: 'Wed', orders: 150 },
  { day: 'Thu', orders: 170 }, { day: 'Fri', orders: 210 },
];

function BarChart({ data, width = 400, height = 220 }) {
  const margin = { top: 10, right: 10, bottom: 30, left: 40 };       // space for axes
  const innerW = width - margin.left - margin.right;                  // drawable width
  const innerH = height - margin.top - margin.bottom;                 // drawable height

  const x = scaleBand()                                               // categories -> x positions
    .domain(data.map((d) => d.day))                                   // ['Mon', 'Tue', ...]
    .range([0, innerW])                                               // pixel range
    .padding(0.2);                                                    // gap between bars

  const y = scaleLinear()                                             // numbers -> y positions
    .domain([0, max(data, (d) => d.orders)])                          // from 0 to largest value
    .nice()                                                           // round to a clean maximum
    .range([innerH, 0]);                                              // SVG y grows downward, so flip

  return (
    <svg width={width} height={height} role="img" aria-label="Orders per weekday">
      <g transform={`translate(${margin.left},${margin.top})`}>       {/* move inside margins */}
        {y.ticks(5).map((t) => (                                       // y axis ticks from the scale
          <g key={t} transform={`translate(0,${y(t)})`}>
            <line x2={innerW} stroke="#ddd" />                         {/* grid line */}
            <text x={-6} dy="0.32em" textAnchor="end" fontSize="10">{t}</text>
          </g>
        ))}
        {data.map((d) => (                                             // one <rect> per bar
          <rect key={d.day} x={x(d.day)} y={y(d.orders)}
                width={x.bandwidth()} height={innerH - y(d.orders)} fill="#e23744" />
        ))}
        {data.map((d) => (                                             // x axis labels
          <text key={d.day} x={x(d.day) + x.bandwidth() / 2} y={innerH + 18}
                textAnchor="middle" fontSize="11">{d.day}</text>
        ))}
      </g>
    </svg>
  );
}

createRoot(document.getElementById('root')).render(<BarChart data={data} />);
```

## 💻 Code Example — Advanced

```jsx
// Advanced: responsive line chart with memoised scales, hover tooltip using bisector,
// and a D3 zoom behaviour attached through a ref (D3 only handles the gesture, React renders).
import { useMemo, useRef, useState, useEffect } from 'react';
import { scaleTime, scaleLinear, extent, line, bisector, timeFormat, select, zoom } from 'd3';

const fmt = timeFormat('%d %b');                          // date formatter, created once

// Hook: measure container width so the chart is responsive (ResizeObserver)
function useWidth() {
  const ref = useRef(null);
  const [width, setWidth] = useState(600);                // sensible default before measuring
  useEffect(() => {
    const ro = new ResizeObserver(([entry]) => setWidth(entry.contentRect.width));
    ro.observe(ref.current);
    return () => ro.disconnect();                          // cleanup
  }, []);
  return [ref, width];
}

export function PriceChart({ data, height = 260 }) {      // data: [{ date: Date, close: number }]
  const [wrapRef, width] = useWidth();
  const svgRef = useRef(null);
  const [hover, setHover] = useState(null);               // nearest datum under the mouse
  const [transform, setTransform] = useState({ k: 1, x: 0 }); // zoom state from D3 gesture

  const margin = { top: 10, right: 12, bottom: 24, left: 44 };
  const innerW = Math.max(width - margin.left - margin.right, 10);
  const innerH = height - margin.top - margin.bottom;

  // Scales and path are recomputed only when inputs change
  const { x, y, path } = useMemo(() => {
    const baseX = scaleTime().domain(extent(data, (d) => d.date)).range([0, innerW]);
    const x = baseX.copy().domain(baseX.range().map((r) => baseX.invert((r - transform.x) / transform.k)));
    const y = scaleLinear().domain(extent(data, (d) => d.close)).nice().range([innerH, 0]);
    const gen = line().x((d) => x(d.date)).y((d) => y(d.close)); // data -> "M0,10L5,8..."
    return { x, y, path: gen(data) };
  }, [data, innerW, innerH, transform]);

  // D3 zoom: only reports pan/zoom values; React still renders everything
  useEffect(() => {
    const z = zoom().scaleExtent([1, 8])
      .translateExtent([[0, 0], [innerW, innerH]]).extent([[0, 0], [innerW, innerH]])
      .on('zoom', (e) => setTransform({ k: e.transform.k, x: e.transform.x }));
    select(svgRef.current).call(z);                        // attach listeners
    return () => select(svgRef.current).on('.zoom', null); // remove listeners on cleanup
  }, [innerW, innerH]);

  const bisect = useMemo(() => bisector((d) => d.date).center, []);   // find nearest date quickly

  function onMove(e) {
    const rect = svgRef.current.getBoundingClientRect();
    const date = x.invert(e.clientX - rect.left - margin.left);       // pixel -> date
    setHover(data[bisect(data, date)]);                                // nearest point
  }

  return (
    <div ref={wrapRef} style={{ width: '100%' }}>
      <svg ref={svgRef} width={width} height={height} onMouseMove={onMove} onMouseLeave={() => setHover(null)}>
        <defs><clipPath id="clip"><rect width={innerW} height={innerH} /></clipPath></defs>
        <g transform={`translate(${margin.left},${margin.top})`}>
          {y.ticks(5).map((t) => (
            <g key={t} transform={`translate(0,${y(t)})`}>
              <line x2={innerW} stroke="#eee" /><text x={-6} dy="0.32em" textAnchor="end" fontSize="10">{t}</text>
            </g>
          ))}
          {x.ticks(6).map((t) => (
            <text key={+t} x={x(t)} y={innerH + 16} textAnchor="middle" fontSize="10">{fmt(t)}</text>
          ))}
          <g clipPath="url(#clip)">
            <path d={path} fill="none" stroke="#5367ff" strokeWidth="2" />   {/* the whole line */}
            {hover && <circle cx={x(hover.date)} cy={y(hover.close)} r="4" fill="#5367ff" />}
          </g>
        </g>
      </svg>
      {hover && <p>{fmt(hover.date)}: Rs. {hover.close.toFixed(2)}</p>}
    </div>
  );
}
```

---

## 🟠 Next.js Connection

D3 scales and generators are pure functions, so they run fine in **Server Components**: you can compute scales and paths on the server and send only an SVG, with no D3 JavaScript in the browser. Only interactive parts (tooltip, zoom) need a Client Component. Server-rendered SVG also avoids layout shift because the chart exists in the first HTML.

```jsx
// app/dashboard/StaticChart.jsx : Server Component (NO 'use client'): D3 math runs on the server
import { scaleLinear, line } from 'd3';                  // imported only on the server, not shipped to the browser

export default function StaticChart({ data, width = 500, height = 200 }) {
  const x = scaleLinear().domain([0, data.length - 1]).range([0, width]);      // index -> x
  const y = scaleLinear().domain([0, Math.max(...data)]).range([height, 0]);   // value -> y
  const d = line().x((_, i) => x(i)).y((v) => y(v))(data);                       // path string
  return (
    <svg width={width} height={height} role="img" aria-label="Weekly revenue">
      <path d={d} fill="none" stroke="#e23744" strokeWidth="2" />                {/* zero client JS */}
    </svg>
  );
}
```

```jsx
// app/dashboard/page.jsx
import StaticChart from './StaticChart';
export default async function Page() {
  const revenue = [120, 160, 140, 210, 190, 260, 300];   // fetch from DB in real life
  return <StaticChart data={revenue} />;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Letting D3 append/remove DOM nodes inside a React-rendered `<svg>`
✅ **Correct:** Use D3 for math, render elements with JSX; use D3 DOM only on a ref for behaviours (zoom, brush) that don't create React-managed nodes

```jsx
// Wrong
useEffect(() => { select(ref.current).selectAll('circle').data(data).join('circle'); }, [data]); // ❌ conflicts with React
// Right
{data.map((d) => <circle key={d.id} cx={x(d.t)} cy={y(d.v)} r="3" />)}                           // ✅
```

❌ **Mistake 2:** Forgetting that SVG's y axis points downward
✅ **Correct:** Use `.range([height, 0])` for y scales

```jsx
// Wrong: bars hang from the top and look upside-down
const y = scaleLinear().domain([0, 100]).range([0, innerH]);       // ❌
// Right
const y = scaleLinear().domain([0, 100]).range([innerH, 0]);       // ✅
```

❌ **Mistake 3:** Importing the whole `d3` bundle, or recomputing scales on every render for big data
✅ **Correct:** Import only needed modules (`d3-scale`, `d3-shape`) and `useMemo` scales and paths

```jsx
// Wrong
import * as d3 from 'd3';                                     // ❌ large bundle if unused parts are not tree-shaken
const path = line()(bigData);                                  // ❌ recomputed on every hover re-render
// Right
import { scaleLinear } from 'd3-scale';                        // ✅ small
const path = useMemo(() => line()(bigData), [bigData]);        // ✅
```

---

## 🧠 Tricky Interview Question

```jsx
function Chart({ data }) {
  const [hover, setHover] = useState(null);
  const x = scaleLinear().domain([0, 10]).range([0, 300]);
  const path = line().x((d) => x(d.t)).y((d) => d.v)(data);   // 50,000 points
  return <svg onMouseMove={(e) => setHover(e.clientX)}><path d={path} />{/* ... */}</svg>;
}
```
**Answer:** Every mouse move updates `hover`, which re-renders `Chart` and recomputes the 50,000-point path string, so hovering becomes janky. The path does not depend on `hover`, so wrap it in `useMemo(..., [data])`, or split the static line into a `React.memo` child and keep only the tooltip in the part that re-renders. With very large data, also downsample (for example, largest-triangle-three-buckets) or draw on Canvas.

---

## ⚫ Interview Questions + Answers

Q1: How do you combine D3 and React?
A1: The recommended way is "D3 for math, React for DOM": use d3-scale, d3-shape and d3-array to compute positions and path strings, then render SVG elements with JSX. For imperative behaviours (zoom, brush, drag) attach D3 to a ref in `useEffect` and push the results into React state.

Q2: What are scales in D3?
A2: Functions that map a domain (data values) to a range (pixels or colours), such as `scaleLinear`, `scaleTime`, `scaleBand` and `scaleOrdinal`. They also provide `ticks()` for axes and `invert()` for converting pixels back to data.

Q3: What does `d3.line()` return?
A3: A generator function. You configure accessors (`.x()`, `.y()`) and call it with an array of data, and it returns an SVG path string (`d` attribute). `area()` and `arc()` work the same way.

Q4: When would you choose a library such as Recharts, Visx or Nivo over raw D3?
A4: For standard charts and faster delivery, use Recharts or Nivo. Visx gives D3 primitives as React components for custom visualisations. Raw D3 gives the most control but needs the most code.

Q5: How do you make the chart responsive and performant?
A5: Measure the container with `ResizeObserver` (or `useMeasure`), derive scales from the measured width, `useMemo` heavy computations, limit elements (aggregate/downsample), and switch to Canvas for tens of thousands of marks.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- You need custom visualisations that standard chart libraries cannot make
- You want full control over scales, shapes and interactions
- You can compute charts on the server and send only SVG

❌ **Avoid when:**
- A simple bar/line/pie chart is enough (use Recharts, Chart.js, Nivo)
- The team has no D3 experience and deadlines are tight
- You have tens of thousands of points (use Canvas or WebGL)

---

## 📊 Visual Diagram

```
  data: [{date, close}, ...]
        │
        ▼
  D3 (math only)                          React (rendering)
  ┌───────────────────────────┐          ┌───────────────────────────────┐
  │ scaleTime  → x(date)      │          │ <svg>                          │
  │ scaleLinear→ y(close)     │ ───────► │   <g> ticks <line/><text/>     │
  │ line()     → "M0,10L5,8…" │          │   <path d={path}/>             │
  │ bisector   → nearest point│          │   <circle cx cy/> (hover)      │
  └───────────────────────────┘          └───────────────────────────────┘
        ▲ zoom/brush/drag (D3 events via ref) ───► setState ───► React re-renders
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Scale | Maps data values to pixels | Data को pixels में बदलने वाला function |
| Domain | Input data range | Data की इनपुट सीमा |
| Range | Output pixel range | Output pixel सीमा |
| Generator | Function that makes SVG paths | SVG path बनाने वाला function |
| Margin | Space around the chart | Chart के चारों ओर जगह |
| Ticks | Marks on an axis | Axis के निशान |
| Bisector | Finds nearest value in sorted data | क्रमबद्ध data में निकटतम मान खोजना |
| ResizeObserver | Watches element size | Element के size पर नज़र रखना |

---

## ⚡ 3-Line Summary
**English:**
1. Use D3 for scales and shape generators, and let React render the SVG elements.
2. Memoise scales and paths, flip the y range, and import only the D3 modules you need.
3. Keep D3 DOM behaviours (zoom, brush) in refs, render static charts on the server in Next.js, and use Canvas for huge data.

**Hindi:**
1. Scales और shape generators के लिए D3 इस्तेमाल करो, और SVG elements React से render कराओ।
2. Scales व paths को memoise करो, y range उलटा रखो, और सिर्फ़ ज़रूरी D3 modules import करो।
3. D3 के DOM व्यवहार (zoom, brush) refs में रखो, Next.js में static charts server पर बनाओ, और बहुत बड़े data के लिए Canvas लो।

---

## ➡️ Next Topic
**163. React Native Basics** — अब तक आपने web के लिए React सीखा; अगला कदम उसी React ज्ञान से mobile apps बनाना है। (`07-advanced` में इसके बाद 163-165 के notes पहले से मौजूद हैं।)
