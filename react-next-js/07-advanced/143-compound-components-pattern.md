# 143. Compound Components Pattern
# हिंदी में: Compound Components Pattern — आपस में जुड़े Components

---

## 🔵 Simple Definition (English)
**Compound components** are a group of components that work together and share implicit state, usually through context. The caller composes them like HTML (`<Select><Select.Option/></Select>`), while the parent hides the state logic.

## 🔵 सरल परिभाषा (Hindi)
**Compound components** ऐसे components का समूह है जो साथ मिलकर काम करते हैं और state को अंदर ही अंदर (आमतौर पर context से) share करते हैं। Caller इन्हें HTML की तरह जोड़ता है (`<Select><Select.Option/></Select>`), और state का logic parent छुपाए रखता है।

---

## 🔴 Problem it Solves

A single "smart" component with many config props becomes rigid. For an accordion you end up with `items=[{title, content, icon, disabled}]`, `renderTitle`, `renderContent`, `openIconPosition`, and still cannot reorder or insert custom elements between parts.

```jsx
// PROBLEM: config-prop API is rigid and keeps growing
<Accordion
  items={[{ title: 'Delivery', content: '2 days', icon: 'truck', disabled: false }]}
  iconPosition="right"
  renderTitle={(t) => <b>{t}</b>}
/>

// SOLUTION: compound API, the caller controls structure and styling of each part
<Accordion>
  <Accordion.Item id="delivery">
    <Accordion.Header><TruckIcon /> Delivery</Accordion.Header>   {/* any markup allowed */}
    <Accordion.Panel>2 days</Accordion.Panel>
  </Accordion.Item>
</Accordion>
```

## 🔴 यह क्यों बना? (Hindi)
कई config props वाला एक "smart" component कठोर हो जाता है। Accordion के लिए `items=[{title, content, icon, disabled}]`, `renderTitle`, `openIconPosition` जैसे props बढ़ते जाते हैं, फिर भी parts का क्रम बदलना या बीच में custom element डालना संभव नहीं होता। Compound API में caller हर हिस्से की structure और styling खुद तय करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create a context that holds the shared state (open id, setter)
Step 2 → Root component owns the state with useState/useReducer and renders <Context.Provider>
Step 3 → Child parts (Item, Header, Panel) call useContext to read/update the state
Step 4 → Attach children as static properties: Accordion.Item = Item (single import)
Step 5 → Child parts throw a clear error if used outside the root (context is null)
Step 6 → The caller arranges parts freely in JSX

Alternative (older): React.Children.map + cloneElement to inject props, but it breaks with wrappers/fragments. Context is the recommended approach
Re-render: when context value changes, ALL consumers re-render; memoize the value (useMemo) and split state/actions contexts for big groups
Performance: cheap for small groups; for large lists split contexts or use per-item selectors
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → एक context बनाओ जिसमें shared state हो (open id, setter)
Step 2 → Root component useState/useReducer से state रखता है और <Context.Provider> render करता है
Step 3 → Child parts (Item, Header, Panel) useContext से state पढ़ते/बदलते हैं
Step 4 → Children को static properties की तरह जोड़ो: Accordion.Item = Item (एक ही import)
Step 5 → अगर part root के बाहर इस्तेमाल हो तो साफ error फेंको (context null है)
Step 6 → Caller JSX में parts को अपनी मर्ज़ी से सजाता है

पुराना तरीका: React.Children.map + cloneElement से props inject करना, पर wrappers/fragments के साथ टूट जाता है। Context ही सुझाया तरीका है
Re-render: context value बदलने पर सारे consumers re-render होते हैं; value को useMemo करो और बड़े groups में state/actions contexts अलग करो
Performance: छोटे groups में सस्ता; बड़ी lists में contexts बाँटो
```

---

## 🟡 Real World Example
**Swiggy FAQ / Help section and Zomato filter tabs:** The Help page has an accordion where each question expands. Product wants a "NEW" badge on one question and a link inside another. With compound components, the team just drops a `<Badge/>` inside `Accordion.Header` or a `<Link/>` inside `Accordion.Panel`, with no change to the Accordion library. Material UI, Radix UI and Headless UI use exactly this pattern for Tabs, Menus and Dialogs.

## 🟡 Real Example Hindi mein
**Swiggy FAQ / Help section और Zomato filter tabs:** Help page पर accordion है जहाँ हर सवाल खुलता है। Product एक सवाल पर "NEW" badge और दूसरे में link चाहता है। Compound components में टीम बस `Accordion.Header` के अंदर `<Badge/>` या `Accordion.Panel` के अंदर `<Link/>` रख देती है, Accordion library बदलनी नहीं पड़ती। Material UI, Radix UI और Headless UI Tabs, Menus और Dialogs के लिए यही pattern इस्तेमाल करते हैं।

---

## 💻 Code Example — Basic

```jsx
// Basic: a Toggle compound component (Toggle, Toggle.On, Toggle.Off, Toggle.Button)
import { createContext, useContext, useState } from 'react';  // context + state
import { createRoot } from 'react-dom/client';                  // root API

const ToggleContext = createContext(null);                      // shared state container

function Toggle({ children }) {                                  // root: owns the state
  const [on, setOn] = useState(false);                           // on/off value
  const toggle = () => setOn((o) => !o);                         // updater function
  return (
    <ToggleContext.Provider value={{ on, toggle }}>              {/* share with all parts */}
      {children}
    </ToggleContext.Provider>
  );
}

function useToggle() {                                           // helper hook for parts
  const ctx = useContext(ToggleContext);                         // read the nearest Toggle
  if (!ctx) throw new Error('Use Toggle parts inside <Toggle>'); // clear error for misuse
  return ctx;
}

Toggle.On = ({ children }) => (useToggle().on ? children : null);   // renders only when on
Toggle.Off = ({ children }) => (useToggle().on ? null : children);  // renders only when off
Toggle.Button = () => {                                              // the clickable part
  const { on, toggle } = useToggle();                                // read + update state
  return <button onClick={toggle}>{on ? 'Turn off' : 'Turn on'}</button>;
};

createRoot(document.getElementById('root')).render(
  <Toggle>
    <Toggle.On>Veg only: ON</Toggle.On>                {/* visible when on */}
    <Toggle.Off>Veg only: OFF</Toggle.Off>             {/* visible when off */}
    <Toggle.Button />                                   {/* flips the state */}
  </Toggle>
);
```

## 💻 Code Example — Advanced

```jsx
// Advanced: accessible Accordion with controlled/uncontrolled mode, memoized context, and ids
import { createContext, useContext, useId, useMemo, useState, useCallback } from 'react';
import { createRoot } from 'react-dom/client';

const AccordionContext = createContext(null);              // root-level shared state
const ItemContext = createContext(null);                   // per-item id, so parts know their item

function useAccordion() {
  const ctx = useContext(AccordionContext);                // read root context
  if (!ctx) throw new Error('Accordion parts must be inside <Accordion>');
  return ctx;
}

function Accordion({ value, defaultValue = null, onChange, children }) {
  const isControlled = value !== undefined;                // parent supplies `value` → controlled
  const [inner, setInner] = useState(defaultValue);        // used only when uncontrolled
  const openId = isControlled ? value : inner;             // the source of truth
  const setOpenId = useCallback((id) => {                  // stable setter
    if (!isControlled) setInner(id);                       // update own state when uncontrolled
    onChange?.(id);                                        // always notify the parent
  }, [isControlled, onChange]);
  const ctx = useMemo(() => ({ openId, setOpenId }), [openId, setOpenId]); // avoid needless re-renders
  return <AccordionContext.Provider value={ctx}><div>{children}</div></AccordionContext.Provider>;
}

function Item({ id, children }) {
  const uid = useId();                                     // unique prefix for aria ids (SSR safe)
  const itemCtx = useMemo(() => ({ id, uid }), [id, uid]); // per-item context value
  return <ItemContext.Provider value={itemCtx}><section>{children}</section></ItemContext.Provider>;
}

function Header({ children }) {
  const { openId, setOpenId } = useAccordion();            // root state
  const { id, uid } = useContext(ItemContext);             // this item's identity
  const open = openId === id;                              // is this item open?
  return (
    <h3>
      <button
        id={`${uid}-h`}                                    // id for aria-labelledby
        aria-expanded={open}                               // screen readers announce state
        aria-controls={`${uid}-p`}                         // links button to panel
        onClick={() => setOpenId(open ? null : id)}        // toggle open/close
      >
        {children}
      </button>
    </h3>
  );
}

function Panel({ children }) {
  const { openId } = useAccordion();
  const { id, uid } = useContext(ItemContext);
  if (openId !== id) return null;                          // closed panels render nothing
  return <div id={`${uid}-p`} role="region" aria-labelledby={`${uid}-h`}>{children}</div>;
}

Accordion.Item = Item;                                     // static composition API
Accordion.Header = Header;
Accordion.Panel = Panel;

function HelpPage() {
  return (
    <Accordion defaultValue="refund">                      {/* uncontrolled: refund opens first */}
      <Accordion.Item id="refund">
        <Accordion.Header>Refund policy <em>NEW</em></Accordion.Header> {/* custom markup */}
        <Accordion.Panel>Refunds are processed in 5-7 days.</Accordion.Panel>
      </Accordion.Item>
      <Accordion.Item id="delivery">
        <Accordion.Header>Delivery time</Accordion.Header>
        <Accordion.Panel>Usually 30 minutes. <a href="/track">Track order</a></Accordion.Panel>
      </Accordion.Item>
    </Accordion>
  );
}

createRoot(document.getElementById('root')).render(<HelpPage />);
```

---

## 🟠 Next.js Connection

Because compound components rely on context and state, the root and parts must be Client Components. A good pattern is to put `'use client'` in the file that defines the whole compound component, then use it from Server Components, passing server-rendered content as `children`. When using dot notation (`Accordion.Item`) from a Server Component, Next.js can fail because properties of a client module are references; prefer named exports (`AccordionItem`) when you hit this (a known limitation, version-dependent).

```jsx
// components/accordion.jsx
'use client';                                              // state + context → client
import { createContext, useContext, useState } from 'react';
const Ctx = createContext(null);
export function Accordion({ children }) {
  const [open, setOpen] = useState(null);                  // which item is open
  return <Ctx.Provider value={{ open, setOpen }}>{children}</Ctx.Provider>;
}
export function AccordionItem({ id, title, children }) {   // named export works in Server Components
  const { open, setOpen } = useContext(Ctx);
  return (
    <div>
      <button onClick={() => setOpen(open === id ? null : id)}>{title}</button>
      {open === id && <div>{children}</div>}               {/* children may be server-rendered */}
    </div>
  );
}

// app/help/page.jsx (Server Component)
import { Accordion, AccordionItem } from '@/components/accordion';
export default async function Page() {
  const faqs = await getFaqs();                            // hypothetical DB call on the server
  return (
    <Accordion>
      {faqs.map((f) => <AccordionItem key={f.id} id={f.id} title={f.q}><p>{f.a}</p></AccordionItem>)}
    </Accordion>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Relying on `React.Children.map` + `cloneElement` to pass state
✅ **Correct:** Use context, so parts can be nested anywhere (inside divs, fragments, custom wrappers)

```jsx
// Wrong: breaks when a part is wrapped in another component or <div>
{React.Children.map(children, (c) => React.cloneElement(c, { open }))}   // ❌ only direct children

// Right: parts read the state from context at any depth
const { open } = useContext(AccordionContext);                          // ✅
```

❌ **Mistake 2:** Passing a new object to the Provider every render
✅ **Correct:** Memoize the context value (`useMemo`) so consumers re-render only when needed

```jsx
// Wrong: new object identity every render → every consumer re-renders
<Ctx.Provider value={{ open, setOpen }}>        // ❌
// Right
const value = useMemo(() => ({ open, setOpen }), [open]);   // ✅
<Ctx.Provider value={value}>
```

❌ **Mistake 3:** No error when a part is used outside the root
✅ **Correct:** Throw a helpful error in the hook

```jsx
// Wrong: ctx is null → "Cannot destructure property 'open' of null" (confusing)
const { open } = useContext(Ctx);
// Right
const ctx = useContext(Ctx);
if (!ctx) throw new Error('Accordion.Header must be used inside <Accordion>'); // ✅
```

---

## 🧠 Tricky Interview Question

```jsx
function Tabs({ children }) {
  const [i, setI] = useState(0);
  return React.Children.map(children, (child, idx) =>
    React.cloneElement(child, { active: idx === i, onSelect: () => setI(idx) })
  );
}

<Tabs>
  <Tab>One</Tab>
  <Fragment>
    <Tab>Two</Tab>
    <Tab>Three</Tab>
  </Fragment>
</Tabs>
```
**Answer:** `Tabs` sees only TWO children: `<Tab>One</Tab>` and the `<Fragment>`. `React.Children.map` does not flatten fragments, so `cloneElement` adds `active`/`onSelect` props to the Fragment (which ignores them), and "Two" and "Three" never become interactive or active. Same issue arises when a Tab is wrapped in a custom component. This is why context-based compound components are preferred: each `Tab` reads state from context regardless of nesting.

---

## ⚫ Interview Questions + Answers

Q1: What are compound components?
A1: A set of components that share implicit state and are used together, like `<select>` and `<option>`. The root owns state, the parts consume it through context, and the caller controls layout.

Q2: How do you implement them?
A2: Create a context, make the root hold state and provide it, build parts that consume it with a custom hook that throws outside the root, and optionally attach parts as static properties (`Tabs.Tab`).

Q3: Context vs `cloneElement`: which is better and why?
A3: Context. `cloneElement` only reaches direct children and breaks with fragments or wrappers. Context works at any depth and does not need to inspect children.

Q4: What are the drawbacks?
A4: More code than a simple prop API, implicit coupling (parts only work inside the root), more re-renders if the context value is not memoized, and in Next.js, dot-notation usage from Server Components has limitations.

Q5: How would you make a compound component controlled and uncontrolled?
A5: Accept `value`/`onChange` for controlled mode and `defaultValue` for uncontrolled mode. If `value !== undefined`, use it as the source of truth; otherwise keep internal state and always call `onChange`.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Building reusable UI kits: tabs, accordions, menus, dialogs, selects
- Callers need flexible layout or custom markup between parts
- Parts must share state without prop drilling

❌ **Avoid when:**
- A simple component with two or three props is enough
- There is no shared state between the parts
- The API is used by a few places only (extra abstraction not worth it)

---

## 📊 Visual Diagram

```
 <Accordion>  ── owns state: openId ───────────────┐
   │              provides AccordionContext         │ (context)
   ├─ <Accordion.Item id="refund">                  │
   │     ├─ <Accordion.Header>  ◀── reads/writes ───┤
   │     └─ <Accordion.Panel>   ◀── reads ──────────┤
   └─ <Accordion.Item id="delivery">                │
         ├─ <Accordion.Header>  ◀── reads/writes ───┤
         └─ <Accordion.Panel>   ◀── reads ──────────┘

 Click Header → setOpenId → context value changes → consumers re-render → matching Panel appears
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Compound component | Parts that share implicit state | State share करने वाले जुड़े parts |
| Context | React's way to share data without props | बिना props के data share करने का तरीका |
| Implicit state | State hidden inside the root | Root के अंदर छुपी state |
| Static property | Part attached like `Tabs.Tab` | `Tabs.Tab` जैसा जुड़ा हुआ part |
| Controlled | Parent owns the value | Parent के पास value |
| Uncontrolled | Component owns its own value | Component के पास अपनी value |
| `cloneElement` | API that copies an element with new props | नए props के साथ element की copy बनाना |
| Slot | Place where the caller puts content | जहाँ caller content रखता है |

---

## ⚡ 3-Line Summary
**English:**
1. Compound components are a root plus parts that share state through context, composed freely by the caller.
2. Prefer context over `cloneElement`, memoize the provider value, and throw errors when parts are used outside the root.
3. In Next.js, put them in a `'use client'` file and prefer named exports.

**Hindi:**
1. Compound components में एक root और उसके parts context से state share करते हैं, और caller उन्हें खुलकर जोड़ता है।
2. `cloneElement` की जगह context लो, provider value memoize करो, और root के बाहर parts इस्तेमाल हों तो error फेंको।
3. Next.js में इन्हें `'use client'` file में रखो और named exports को प्राथमिकता दो।

---

## ➡️ Next Topic
**144. Controlled Components Pattern** — Component की value parent के हाथ में देना (`value` + `onChange`), ताकि parent पूरा नियंत्रण रखे।
