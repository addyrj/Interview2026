# 197. Build Tabs Component
# हिंदी में: Tabs Component बनाना

Code: [`App.jsx`](./App.jsx) in this folder (compound components with Context, roving tabindex, Arrow/Home/End keyboard navigation, ARIA roles).

---

## 🔵 Simple Definition (English)
Tabs show one panel of content at a time, selected by a row of tab buttons. A well-built Tabs component uses **compound components** (`Tabs`, `Tabs.List`, `Tabs.Tab`, `Tabs.Panel`) that share the active tab through Context, and follows the WAI-ARIA tab pattern.

## 🔵 सरल परिभाषा (Hindi)
Tabs एक समय में content का एक panel दिखाते हैं, जिसे tab buttons की पंक्ति से चुना जाता है। अच्छा Tabs component **compound components** (`Tabs`, `Tabs.List`, `Tabs.Tab`, `Tabs.Panel`) इस्तेमाल करता है जो active tab को Context से share करते हैं, और WAI-ARIA tab pattern का पालन करता है।

---

## 🔴 Problem it Solves

A simple tabs component takes arrays of labels and contents as props, which becomes rigid: you cannot add an icon, a badge or a custom wrapper to one tab without new props. Passing `activeTab` and `setActiveTab` to every part by hand is tedious (prop drilling). Also, many versions ignore keyboard users: arrow keys do nothing and every tab is a Tab stop. The compound pattern gives callers full layout freedom while the parts stay connected.

```jsx
// PROBLEM: rigid config API and manual wiring
<Tabs labels={['Menu', 'Reviews']} contents={[<Menu />, <Reviews />]} />   // can't customise one tab ❌

// Manual wiring of state to each part
<TabButton active={tab} set={setTab} />  <Panel active={tab} />           // repeated everywhere ❌
```

## 🔴 यह क्यों बना? (Hindi)
सरल Tabs component labels और contents के arrays props में लेता है, जो कठोर हो जाता है: किसी एक tab में icon, badge या custom wrapper जोड़ने के लिए नए props चाहिए। हर हिस्से को `activeTab` और `setActiveTab` हाथ से भेजना थकाऊ है (prop drilling)। कई versions keyboard users को भी अनदेखा करते हैं: arrow keys कुछ नहीं करते और हर tab एक Tab stop बन जाता है। Compound pattern callers को पूरी layout आज़ादी देता है और हिस्से आपस में जुड़े रहते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → <Tabs defaultValue="menu"> owns state: active
Step 2 → It provides { active, setActive, baseId } through TabsContext
Step 3 → <Tabs.Tab value="x"> reads the context: selected = active === value; click → setActive
Step 4 → <Tabs.Panel value="x"> reads the context and renders only if active === value
Step 5 → ARIA: role=tablist / tab / tabpanel; aria-selected; aria-controls ↔ aria-labelledby
Step 6 → Roving tabindex: selected tab tabIndex=0, others -1 (Tab key enters the list once)
Step 7 → Keyboard: ArrowRight/Left move focus (wrapping), Home/End jump, and select the tab

Interview approach: "Compound components + Context, ARIA roles, roving tabindex, arrow keys."
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → <Tabs defaultValue="menu"> state का मालिक है: active
Step 2 → वह TabsContext से { active, setActive, baseId } देता है
Step 3 → <Tabs.Tab value="x"> context पढ़ता है: selected = active === value; click → setActive
Step 4 → <Tabs.Panel value="x"> context पढ़कर तभी render होता है जब active === value
Step 5 → ARIA: role=tablist / tab / tabpanel; aria-selected; aria-controls ↔ aria-labelledby
Step 6 → Roving tabindex: चुने tab का tabIndex=0, बाकी -1 (Tab key list में एक बार ही घुसती है)
Step 7 → Keyboard: ArrowRight/Left focus घुमाते हैं (wrap), Home/End कूदते हैं, और tab चुन लेते हैं

Interview approach: "Compound components + Context, ARIA roles, roving tabindex, arrow keys।"
```

---

## 🟡 Real World Example
**Zomato restaurant page (Order Online / Dining / Reviews / Photos), Amazon product page (Description / Reviews / Q&A), Swiggy account page:** each tab swaps the main content without leaving the page. Zomato's tab bar may include icons and counts like "Reviews (2.3k)", which is easy with compound components because the caller composes each tab freely.

## 🟡 Real Example Hindi mein
**Zomato restaurant page (Order Online / Dining / Reviews / Photos), Amazon product page (Description / Reviews / Q&A), Swiggy account page:** हर tab page छोड़े बिना मुख्य content बदलता है। Zomato की tab bar में icons और "Reviews (2.3k)" जैसी counts हो सकती हैं, जो compound components में आसान है क्योंकि caller हर tab को खुद compose करता है।

---

## 💻 Code Example — Basic

```jsx
// Basic tabs with a single state value (no context, no keyboard extras)
import { useState } from 'react';

export default function SimpleTabs() {
  const [tab, setTab] = useState('menu');                    // active tab id
  return (
    <div>
      <div role="tablist">
        {['menu', 'reviews'].map((t) => (
          <button
            key={t} role="tab" aria-selected={tab === t}      // accessibility state
            onClick={() => setTab(t)}                         // switch tab
            style={{ fontWeight: tab === t ? 'bold' : 'normal' }}
          >{t}</button>
        ))}
      </div>
      {tab === 'menu' && <p>Biryani, Dosa</p>}                {/* only the active panel */}
      {tab === 'reviews' && <p>4.5 stars</p>}
    </div>
  );
}
```

## 💻 Code Example — Advanced

Full code: [`App.jsx`](./App.jsx). Important parts:

```jsx
// Shared state through context (compound components)
const TabsContext = createContext(null);
function Tabs({ defaultValue, children }) {
  const [active, setActive] = useState(defaultValue);
  const baseId = useId();                                    // unique, SSR-safe id prefix
  return <TabsContext.Provider value={{ active, setActive, baseId }}>{children}</TabsContext.Provider>;
}

// Keyboard navigation inside the tablist
const onKeyDown = (e) => {
  const tabs = [...ref.current.querySelectorAll('[role="tab"]')];
  const i = tabs.indexOf(document.activeElement);
  if (i === -1) return;
  let next = null;
  if (e.key === 'ArrowRight') next = tabs[(i + 1) % tabs.length];            // wrap forward
  if (e.key === 'ArrowLeft') next = tabs[(i - 1 + tabs.length) % tabs.length]; // wrap backward
  if (e.key === 'Home') next = tabs[0];
  if (e.key === 'End') next = tabs[tabs.length - 1];
  if (next) { e.preventDefault(); next.focus(); next.click(); }               // focus and select
};

// Roving tabindex on each tab: <button tabIndex={selected ? 0 : -1} ... />

// Attach sub-components for a nice API
Tabs.List = TabList; Tabs.Tab = Tab; Tabs.Panel = TabPanel;
```

Verified with jsdom: default panel shows "Biryani"; focusing the Reviews tab and pressing ArrowRight selects the Info tab and shows "Open 10am to 11pm".

Production note: the `Tab` and `TabPanel` call `useContext` without a guard. Add `if (!ctx) throw new Error('Tab must be used inside <Tabs>')` for clearer errors, and memoise the context value (`useMemo`) if `Tabs` re-renders often.

---

## 🟠 Next.js Connection

For tabs that should be **linkable and SEO-friendly**, keep the active tab in the URL (`?tab=reviews` or nested routes) so refresh, back button and sharing work. Server Components can then render only the active tab's content.

```jsx
// app/restaurant/[id]/page.jsx (Server Component) : tab stored in the URL
import Link from 'next/link';
import Menu from './Menu';
import Reviews from './Reviews';

export default async function Page({ params, searchParams }) {
  const { id } = await params;                               // Next.js 15: Promise
  const { tab = 'menu' } = await searchParams;               // Next.js 15: Promise
  return (
    <>
      <nav role="tablist">
        {['menu', 'reviews'].map((t) => (
          <Link key={t} role="tab" aria-selected={tab === t}
                href={`/restaurant/${id}?tab=${t}`} scroll={false}>{t}</Link>
        ))}
      </nav>
      {tab === 'menu' ? <Menu id={id} /> : <Reviews id={id} />}  {/* fetched on the server */}
    </>
  );
}
```
Alternatives: nested route segments with a shared `layout.jsx` (each tab is its own URL), or parallel routes (topic 182). Use the client-state `App.jsx` version for tiny UI-only tabs where the URL does not matter. In Next.js 14, `params` and `searchParams` are plain objects (version-dependent).

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Putting every tab in the Tab key order
✅ **Correct:** Use roving tabindex: only the selected tab has `tabIndex=0`; arrow keys move between tabs.

```jsx
// Wrong: 10 tabs = 10 Tab presses to get past them
<button role="tab">...</button>                                   // ❌ all tabbable
// Right
<button role="tab" tabIndex={selected ? 0 : -1}>...</button>      // ✅
```

❌ **Mistake 2:** Defining sub-components inside the parent, or passing a new context value object without need
✅ **Correct:** Define `Tab`, `TabList`, `TabPanel` at module level so they are not remounted each render; memoise the context value if the provider re-renders often.

```jsx
// Wrong: Tab is a new component type each render → state lost, DOM recreated
function Tabs() { function Tab() { /* ... */ } return <Tab />; }       // ❌
// Right
function Tab() { /* ... */ }                                           // ✅ module level
function Tabs() { return <Tab />; }
```

❌ **Mistake 3:** Forgetting the ARIA links and unmounting expensive or stateful panels unintentionally
✅ **Correct:** `aria-controls` ↔ `aria-labelledby` with ids from `useId`; decide deliberately between rendering only the active panel (cheap, state lost) and rendering all with `hidden` (state kept).

```jsx
// Wrong: ids typed by hand collide when two Tabs are on one page
<button id="tab-menu" /> <div id="panel-menu" />                       // ❌
// Right
const baseId = useId(); <button id={`${baseId}-tab-${value}`} />       // ✅ unique per instance
```

---

## 🧠 Tricky Interview Question

```jsx
function Tabs({ children }) {
  const [active, setActive] = useState('a');
  const ctx = { active, setActive };                  // new object every render
  console.log('Tabs render');
  return <Ctx.Provider value={ctx}>{children}</Ctx.Provider>;
}
const Panel = React.memo(function Panel({ id }) {
  const { active } = useContext(Ctx);
  console.log('Panel render', id);
  return active === id ? <p>{id}</p> : null;
});
// <Tabs><Panel id="a" /><Panel id="b" /></Tabs>
// Something re-renders Tabs' PARENT with no state change in Tabs. What logs?
```
**Answer:** `Tabs render`, then `Panel render a` and `Panel render b`. Normally `React.memo` would skip each `Panel`, because its props (`id`) did not change. But `Panel` consumes the context, and `Tabs` creates a **new `ctx` object on every render**, so React sees a changed Provider value and re-renders every consumer, even though `active` is the same. `memo` cannot block context updates. Fix: `const ctx = useMemo(() => ({ active, setActive }), [active])`. Lesson: memoise context values (`setActive` from `useState` is already stable).

---

## ⚫ Interview Questions + Answers

Q1: What are compound components?
A1: A set of components designed to work together and share implicit state, usually through Context, such as `Tabs`, `Tabs.Tab` and `Tabs.Panel`. The caller composes the structure declaratively and the parts stay connected without passing props manually.

Q2: What is roving tabindex?
A2: A keyboard pattern where only one item in a group (the selected tab) has `tabIndex=0` and the others have `-1`. Tab moves focus into and out of the group in one stop, and arrow keys move focus within. It keeps long tab lists usable by keyboard.

Q3: Which ARIA roles does a tabs widget need?
A3: `role="tablist"` on the container, `role="tab"` on each trigger with `aria-selected` and `aria-controls`, and `role="tabpanel"` on each panel with `aria-labelledby`. Only the active panel is displayed (others hidden or unmounted).

Q4: Should the active tab live in state or in the URL?
A4: Use local state for small UI-only toggles. Use the URL (search param or route segment) when users should be able to share, bookmark, reload or use the back button for a tab, and when each tab's content should be indexable. In Next.js the URL approach also lets Server Components fetch only the active tab's data.

Q5: How does a controlled `Tabs` differ?
A5: It takes `value` and `onValueChange` props, so the parent owns the active tab (for example syncing with the URL). Support both with an internal state fallback when `value` is not provided, as Radix UI does.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Content is split into parallel views of the same subject (details, reviews, photos)
- Users switch between views often and only need one at a time

❌ **Avoid when:**
- Steps must be completed in order (use a stepper/wizard)
- Users must compare content across views (show side by side)
- There are many tabs that do not fit on small screens (use a select/menu)

---

## 📊 Visual Diagram

```
  <Tabs defaultValue="menu">                  ← state: active  (Context Provider)
    <Tabs.List>  role=tablist  onKeyDown ──── Arrow/Home/End
      <Tabs.Tab value="menu">     ← tabIndex 0, aria-selected=true
      <Tabs.Tab value="reviews">  ← tabIndex -1
      <Tabs.Tab value="info">     ← tabIndex -1
    </Tabs.List>
    <Tabs.Panel value="menu">      ← rendered (active)
    <Tabs.Panel value="reviews">   ← null
    <Tabs.Panel value="info">      ← null

  Click "reviews" → setActive('reviews') → Provider value changes
     → all Tab + Panel consumers re-render → menu panel unmounts, reviews mounts

  Re-render cost: only context consumers; keep Panel content light or lazy.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Compound components | Components sharing hidden state | छिपी state share करने वाले components |
| Context | React's way to share data without props | बिना props के data share करने का तरीका |
| Roving tabindex | Only the active item is tabbable | सिर्फ active item Tab से पहुँचने लायक |
| tablist / tab / tabpanel | ARIA roles of the tab pattern | Tab pattern के ARIA roles |
| aria-selected | Marks the selected tab | चुने हुए tab को दर्शाता है |
| useId | Unique id hook | Unique id वाला hook |
| Controlled | Parent owns the value | Parent के पास value |
| Deep link | URL that opens a specific tab | किसी खास tab को खोलने वाला URL |

---

## ⚡ 3-Line Summary
**English:**
1. Build Tabs as compound components that share `active` and `setActive` through Context, with `useId` for ARIA links.
2. Support keyboard users with roving tabindex and Arrow/Home/End keys, and follow the tablist / tab / tabpanel roles.
3. In Next.js keep the active tab in the URL when it must be shareable, and memoise the context value.

**Hindi:**
1. Tabs को compound components की तरह बनाओ जो `active` और `setActive` Context से share करें, ARIA links के लिए `useId` के साथ।
2. Roving tabindex और Arrow/Home/End keys से keyboard users को support करो, और tablist / tab / tabpanel roles मानो।
3. Next.js में जब tab shareable होना चाहिए तो active tab URL में रखो, और context value को memoise करो।

---

## ➡️ Next Topic
**198. Build Pagination Component** — page numbers, ellipsis ("1 ... 4 5 6 ... 20") की गणना, Prev/Next buttons और client-side बनाम server-side pagination।
