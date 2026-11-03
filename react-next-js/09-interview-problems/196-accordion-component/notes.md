# 196. Build Accordion Component
# हिंदी में: Accordion Component बनाना

Code: [`App.jsx`](./App.jsx) in this folder (single-open or multiple-open mode, state in a `Set`, ARIA buttons and regions).

---

## 🔵 Simple Definition (English)
An accordion is a vertical list of sections where each header can be clicked to show or hide its content. In **single** mode only one section is open at a time; in **multiple** mode any number can be open.

## 🔵 सरल परिभाषा (Hindi)
Accordion sections की खड़ी list है जिसमें हर header पर click करके उसका content दिखाया या छिपाया जाता है। **Single** mode में एक समय में सिर्फ एक section खुला रहता है; **multiple** mode में कितने भी खुले रह सकते हैं।

---

## 🔴 Problem it Solves

Pages with a lot of content (FAQs, filters, settings) become long and hard to scan. An accordion hides detail until needed. The interview challenge is to model "which panels are open" with the right state shape, support both modes with one component, avoid per-item boolean states, and keep it accessible (keyboard and screen readers).

```jsx
// PROBLEM: one boolean per item doesn't scale and can't enforce "only one open"
const [open1, setOpen1] = useState(false);
const [open2, setOpen2] = useState(false);
const [open3, setOpen3] = useState(false);       // 3 items = 3 states; 30 items = nightmare ❌
```

## 🔴 यह क्यों बना? (Hindi)
बहुत content वाले pages (FAQs, filters, settings) लंबे और स्कैन करने में कठिन हो जाते हैं। Accordion ज़रूरत तक details छिपाता है। Interview की चुनौती है "कौन से panels खुले हैं" के लिए सही state shape चुनना, एक ही component में दोनों modes देना, हर item के लिए अलग boolean से बचना, और उसे accessible रखना (keyboard और screen readers)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Props: items [{ id, title, content }], multiple (default false)
Step 2 → State: openIds = new Set()  (ids of open panels)
Step 3 → Click header → toggle(id)
Step 4 → toggle builds a NEW Set: single mode starts empty, multiple mode copies the old
Step 5 → If the id was open → delete it (close); else → add it (open)
Step 6 → Render: isOpen = openIds.has(item.id); button gets aria-expanded; panel gets hidden
Step 7 → ARIA: button id + aria-controls ↔ panel id + aria-labelledby (via useId prefix)

Interview approach: "State = Set of open ids; one toggle function; single mode is just
'start from an empty set'; real <button> elements for keyboard support."
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Props: items [{ id, title, content }], multiple (default false)
Step 2 → State: openIds = new Set()  (खुले panels की ids)
Step 3 → Header click → toggle(id)
Step 4 → toggle नया Set बनाता है: single mode में खाली से शुरू, multiple mode में पुराना copy
Step 5 → अगर id खुली थी → delete (बंद); वरना → add (खोलो)
Step 6 → Render: isOpen = openIds.has(item.id); button को aria-expanded; panel को hidden
Step 7 → ARIA: button id + aria-controls ↔ panel id + aria-labelledby (useId prefix से)

Interview approach: "State = खुली ids का Set; एक toggle function; single mode बस
'खाली set से शुरू'; keyboard support के लिए असली <button> elements।"
```

---

## 🟡 Real World Example
**Amazon / Flipkart help center FAQs, Swiggy "Order help" topics, Zomato filters panel:** "Where is my order?", "How do I get a refund?" are collapsed headings. In a filter sidebar (Brand, Price, Rating) users open several sections at once, which is multiple mode. In an FAQ, single mode keeps the page tidy.

## 🟡 Real Example Hindi mein
**Amazon / Flipkart help center FAQs, Swiggy "Order help" topics, Zomato filters panel:** "मेरा order कहाँ है?", "Refund कैसे मिलेगा?" बंद headings होते हैं। Filter sidebar (Brand, Price, Rating) में users कई sections एक साथ खोलते हैं, यानी multiple mode। FAQ में single mode page को साफ़ रखता है।

---

## 💻 Code Example — Basic

```jsx
// Simplest accordion: single open item stored as an id (or null)
import { useState } from 'react';

const ITEMS = [
  { id: 1, title: 'Track order', body: 'Go to Orders → Track.' },
  { id: 2, title: 'Refund', body: 'Refunds take 5-7 days.' },
];

export default function Accordion() {
  const [openId, setOpenId] = useState(null);                // which item is open (one at a time)
  return (
    <div>
      {ITEMS.map((it) => (
        <div key={it.id}>
          <button onClick={() => setOpenId(openId === it.id ? null : it.id)}> {/* toggle */}
            {it.title}
          </button>
          {openId === it.id && <p>{it.body}</p>}              {/* render only when open */}
        </div>
      ))}
    </div>
  );
}
```

## 💻 Code Example — Advanced

Full code: [`App.jsx`](./App.jsx). The state logic that supports both modes:

```jsx
const [openIds, setOpenIds] = useState(new Set());          // ids of open panels

const toggle = (id) =>
  setOpenIds((prev) => {
    const next = new Set(multiple ? prev : []);              // single: start empty, multiple: copy
    if (prev.has(id)) next.delete(id);                       // was open → close
    else next.add(id);                                       // was closed → open
    return next;                                             // NEW Set → React re-renders
  });

// Accessible markup per item
<h3>
  <button
    id={`${baseId}-btn-${item.id}`}
    aria-expanded={isOpen}                                   // announces expanded/collapsed
    aria-controls={`${baseId}-panel-${item.id}`}
    onClick={() => toggle(item.id)}
  >{item.title}</button>
</h3>
<div id={`${baseId}-panel-${item.id}`} role="region"
     aria-labelledby={`${baseId}-btn-${item.id}`} hidden={!isOpen}>
  <p>{item.content}</p>
</div>
```

Verified with jsdom: in single mode opening item B closes item A; with `multiple={true}` both stay open.

For smooth height animation use the CSS `grid-template-rows: 0fr → 1fr` trick or `<details>/<summary>` for a no-JS version (note: `<details name="group">` gives native single-open behaviour in modern browsers).

---

## 🟠 Next.js Connection

The accordion needs click state, so it is a Client Component. The **content** can still come from the server: a Server Component fetches the FAQ and passes it as props or `children`, so the text is part of the initial HTML (good for SEO). Because `hidden` content is still in the DOM, crawlers can read it.

```jsx
// app/help/page.jsx (Server Component)
import { Accordion } from './Accordion';                    // 'use client' file
import { getFaqs } from '@/lib/faqs';                        // hypothetical server function

export const revalidate = 3600;                              // ISR: refresh FAQs hourly

export default async function Help() {
  const faqs = await getFaqs();                              // [{ id, title, content }]
  return (
    <>
      <h1>Help Center</h1>
      <Accordion items={faqs} />                             {/* only interactivity is shipped as JS */}
    </>
  );
}
```
```jsx
// app/help/Accordion.jsx
'use client';                                                // uses useState
export { Accordion } from '@/components/Accordion';          // re-export the App.jsx implementation
```
(Re-exporting from a `'use client'` file makes that module's tree a client boundary. Simpler: put `'use client'` at the top of the component file itself.) For SEO you can also add FAQ structured data (JSON-LD) from the server.

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** One boolean state per item
✅ **Correct:** One state for the set (or id) of open items.

```jsx
// Wrong
const [a, setA] = useState(false); const [b, setB] = useState(false);          // ❌
// Right
const [openIds, setOpenIds] = useState(new Set());                              // ✅
```

❌ **Mistake 2:** Mutating the Set (`openIds.add(id); setOpenIds(openIds)`)
✅ **Correct:** Create a new Set; React compares by reference and ignores the same object.

```jsx
// Wrong: same reference → no re-render
openIds.add(id); setOpenIds(openIds);                                          // ❌
// Right
setOpenIds((prev) => { const n = new Set(prev); n.add(id); return n; });       // ✅
```

❌ **Mistake 3:** Using `<div onClick>` for headers, and unmounting panels when they hold state
✅ **Correct:** Use a real `<button>` (keyboard focus, Enter/Space, role) and ARIA attributes. If a closed panel contains a form that must keep its input, use `hidden` instead of conditional rendering.

```jsx
// Wrong: not focusable, no keyboard support, no ARIA
<div onClick={toggle}>Title</div>                                              // ❌
// Right
<button aria-expanded={isOpen} aria-controls={panelId} onClick={toggle}>Title</button> // ✅
```

---

## 🧠 Tricky Interview Question

```jsx
function Panel({ title }) {
  const [text, setText] = useState('');
  return <div><b>{title}</b><input value={text} onChange={(e) => setText(e.target.value)} /></div>;
}

function Demo() {
  const [open, setOpen] = useState(true);
  return (
    <>
      <button onClick={() => setOpen((o) => !o)}>toggle</button>
      {open && <Panel title="A" />}                  // conditional rendering
    </>
  );
}
// The user types "hello", clicks toggle twice (close, then open). What is in the input?
```
**Answer:** The input is **empty**. `{open && <Panel />}` unmounts `Panel` when `open` is false, which destroys its state. When shown again it is a brand-new instance with `text = ''`. If you render the panel always and hide it with the `hidden` attribute or CSS (`display: none`), the component stays mounted and keeps `hello`. This is why `App.jsx` uses `hidden={!isOpen}`. Trade-off: hidden panels still render (cost for heavy content); for expensive content use conditional rendering and lift the state up, or lazy-render on first open.

---

## ⚫ Interview Questions + Answers

Q1: Why store open items as a `Set` of ids and not a boolean array?
A1: Ids are stable even if items reorder or are filtered, `Set.has` is O(1), and the same shape handles both single (one id) and multiple (many ids) modes. Index-based arrays break when the list changes.

Q2: How do you support both single and multiple mode?
A2: A `multiple` prop. In `toggle`, start from a copy of the previous set when `multiple` is true, otherwise from an empty set. Then toggle the clicked id.

Q3: Which ARIA attributes are needed?
A3: On the button: `aria-expanded` (state) and `aria-controls` (panel id). On the panel: `role="region"` and `aria-labelledby` pointing to the button. Headers should be real headings containing buttons. Optional keyboard: Arrow Up/Down, Home, End to move between headers.

Q4: `hidden` vs conditional rendering: which one and why?
A4: `hidden` keeps the DOM and component state (typed input, scroll, video), allows CSS animation and SEO of the text, but renders everything up front. Conditional rendering saves work for heavy content but loses state. Choose by content weight and state needs.

Q5: How would you make it controlled?
A5: Accept `value` (open ids) and `onValueChange` props, and use internal state only when `value` is undefined. Libraries (Radix Accordion) support both. It lets parents open a section from outside, for example from a URL hash.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- There are many short sections users scan (FAQ, settings, filters)
- Vertical space is limited, especially on mobile

❌ **Avoid when:**
- Users need to compare content of many sections at once (show everything or use tabs/table)
- There are only one or two sections (just show them)
- Critical content would be hidden behind a click

---

## 📊 Visual Diagram

```
  openIds = Set { 'b' }

  ┌ How do I track my order?        [+] ┐   aria-expanded=false  panel hidden
  ├ Can I cancel an order?          [-] ┤   aria-expanded=true
  │   Yes, before the restaurant accepts│   panel visible
  ├ How do refunds work?            [+] ┘   aria-expanded=false

  click 'c' (single mode)             click 'c' (multiple mode)
  prev {b} → next = {} + c = {c}      prev {b} → next = {b} + c = {b, c}

  Re-render: whole Accordion on each toggle (small); panels use `hidden`,
  so their children keep state. Memoise heavy panel content if needed.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Accordion | Collapsible list of sections | खुलने-बंद होने वाले sections की list |
| Set | Collection of unique values | अद्वितीय values का संग्रह |
| aria-expanded | Announces open/closed state | खुला/बंद state बताता है |
| aria-controls | Links a button to the panel it controls | Button को उसके panel से जोड़ता है |
| useId | Hook for unique, SSR-safe ids | Unique, SSR-safe ids का hook |
| hidden attribute | Hides an element but keeps it mounted | Element छिपाता है पर mounted रखता है |
| Controlled component | State owned by the parent | Parent के पास state का मालिकाना |
| Immutable update | New object instead of mutation | Mutation की जगह नया object |

---

## ⚡ 3-Line Summary
**English:**
1. Keep open panels as a `Set` of ids and update it with a new `Set` on each toggle; single mode starts from an empty set.
2. Use real buttons with `aria-expanded` / `aria-controls` and `hidden` panels so state and SEO text survive.
3. In Next.js it is a Client Component fed with server-fetched content.

**Hindi:**
1. खुले panels को ids के `Set` में रखो और हर toggle पर नया `Set` बनाओ; single mode खाली set से शुरू होता है।
2. असली buttons के साथ `aria-expanded` / `aria-controls` और `hidden` panels इस्तेमाल करो ताकि state और SEO text बचे रहें।
3. Next.js में यह Client Component है जिसे server से लाया content दिया जाता है।

---

## ➡️ Next Topic
**197. Build Tabs Component** — compound components (`Tabs.List`, `Tabs.Tab`, `Tabs.Panel`) और Context के साथ, plus keyboard navigation (Arrow keys, Home, End)।
