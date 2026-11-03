# 44. Context API vs Props Drilling
# हिंदी में: Context API बनाम Props Drilling — कौन सा कब

---

## 🔵 Simple Definition (English)
**Props drilling** means passing data down through many components as props, even when the middle ones do not use it. **Context** lets a deep component read the data directly from a Provider above it. Neither is always better: drilling is simple and explicit, Context is convenient but implicit.

## 🔵 सरल परिभाषा (Hindi)
**Props drilling** का मतलब है data को कई components से props के रूप में नीचे भेजना, भले ही बीच के components उसे इस्तेमाल न करें। **Context** में गहरा component data सीधे ऊपर के Provider से पढ़ता है। कोई हमेशा बेहतर नहीं है: drilling सरल और साफ़ (explicit) है, Context सुविधाजनक पर छिपा हुआ (implicit) है।

---

## 🔴 Problem it Solves

Beginners reach for Context as soon as props go through two levels. Others drill props through ten components. Both extremes hurt: too much drilling makes refactoring painful (rename a prop, edit ten files), and too much Context hides data flow, makes components hard to reuse and causes wide re-renders. The comparison helps you choose the lightest tool that works. There is also a third option: **composition**, passing finished JSX as `children`, which often removes the need for both.

```jsx
// DRILLING: Page → Layout → Sidebar → UserMenu (Layout and Sidebar just forward)
<Layout user={user}>  →  <Sidebar user={user}>  →  <UserMenu user={user} />

// COMPOSITION: pass the finished element, no drilling and no Context
<Layout sidebar={<Sidebar><UserMenu user={user} /></Sidebar>} />

// CONTEXT: when truly many unrelated consumers need it
<UserContext.Provider value={user}> ... <UserMenu /> ... <Avatar /> ... </UserContext.Provider>
```

## 🔴 यह क्यों बना? (Hindi)
नए developers दो स्तर पर ही props जाते देखकर Context उठा लेते हैं। कुछ लोग दस components से props गुज़ारते हैं। दोनों अति नुकसान करती हैं: बहुत ज़्यादा drilling से refactoring कठिन हो जाती है (prop का नाम बदलो तो दस files बदलो), और बहुत ज़्यादा Context data का रास्ता छिपा देता है, components दोबारा इस्तेमाल करना मुश्किल करता है और बड़े पैमाने पर re-render कराता है। यह तुलना सबसे हल्का काम करने वाला औज़ार चुनने में मदद करती है। एक तीसरा विकल्प भी है: **composition**, यानी तैयार JSX को `children` में देना, जो अक्सर दोनों की ज़रूरत ख़त्म कर देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Count the levels between the owner of the data and the component that uses it
Step 2 → 1 to 2 levels, few consumers → pass props (clear, easy to trace, easy to test)
Step 3 → Middle components only forward it → try composition (children / slot props) first
Step 4 → Many consumers at different depths, slow-changing data → Context
Step 5 → Frequently changing or complex shared state → Redux Toolkit / Zustand / TanStack Query
Step 6 → Re-check later: if Context value changes often and many components re-render, split or move

DECISION:
  data used by 1 child ........... props
  middle layers just forward ..... composition (children)
  theme/user/locale everywhere ... Context
  big, fast-changing app state ... state library
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Data के मालिक और उसे इस्तेमाल करने वाले component के बीच कितने स्तर हैं, गिनो
Step 2 → 1 से 2 स्तर, कम consumers → props भेजो (साफ़, trace करना आसान, test करना आसान)
Step 3 → बीच के components सिर्फ़ forward करते हैं → पहले composition (children / slot props) आज़माओ
Step 4 → अलग-अलग गहराई पर कई consumers, धीरे बदलने वाला data → Context
Step 5 → बार-बार बदलने वाली या जटिल shared state → Redux Toolkit / Zustand / TanStack Query
Step 6 → बाद में फिर जाँचो: Context value बार-बार बदलती है और कई components re-render होते हैं, तो बाँटो या बदलो

निर्णय:
  data 1 child इस्तेमाल करता है ...... props
  बीच की layers सिर्फ़ forward करती हैं ... composition (children)
  theme/user/locale हर जगह ........... Context
  बड़ी, तेज़ बदलने वाली app state ....... state library
```

---

## 🟡 Real World Example
**Swiggy:** The restaurant page has `RestaurantPage → MenuSection → DishCard → AddButton`. The `AddButton` needs `restaurantId` (2 levels, passed as a prop is fine). The header, the cart bar at the bottom and the checkout all need the logged-in user and cart, in different branches of the tree, so those go in Context (or a store). The "veg only" filter needed by `MenuSection` and `DishList` only, under the same parent: props.

## 🟡 Real Example Hindi mein
**Swiggy:** Restaurant page में `RestaurantPage → MenuSection → DishCard → AddButton` है। `AddButton` को `restaurantId` चाहिए (2 स्तर, prop से भेजना ठीक है)। Header, नीचे का cart bar और checkout, जो tree की अलग शाखाओं में हैं, सबको logged-in user और cart चाहिए, इसलिए वे Context (या store) में जाते हैं। "Veg only" filter सिर्फ़ `MenuSection` और `DishList` को चाहिए, जो एक ही parent के नीचे हैं: props।

---

## 💻 Code Example — Basic

```jsx
// The same "username" problem solved three ways
import { createContext, useContext } from 'react';    // for the Context version
import { createRoot } from 'react-dom/client';        // React 18/19 root API

// ---------- 1) PROPS DRILLING ----------
function DrillPage({ user }) { return <DrillLayout user={user} />; }       // forwards only
function DrillLayout({ user }) { return <DrillHeader user={user} />; }     // forwards only
function DrillHeader({ user }) { return <p>Hello, {user}</p>; }            // finally uses it

// ---------- 2) COMPOSITION (no drilling, no Context) ----------
function ComposePage({ user }) {
  return <ComposeLayout header={<p>Hello, {user}</p>} />;  // page builds the element itself
}
function ComposeLayout({ header }) { return <div>{header}</div>; }          // layout knows nothing about user

// ---------- 3) CONTEXT ----------
const UserContext = createContext('Guest');                                  // default value
function CtxPage() {
  return <UserContext.Provider value="Aditya"><CtxLayout /></UserContext.Provider>;
}
function CtxLayout() { return <CtxHeader />; }                               // no props at all
function CtxHeader() { return <p>Hello, {useContext(UserContext)}</p>; }     // reads directly

createRoot(document.getElementById('root')).render(
  <>
    <DrillPage user="Aditya" />
    <ComposePage user="Aditya" />
    <CtxPage />
  </>
);
```

## 💻 Code Example — Advanced

```jsx
// Re-render comparison: Context re-renders consumers; props with memo let you control exactly who updates
import { createContext, useContext, useState, memo } from 'react';
import { createRoot } from 'react-dom/client';

const CartContext = createContext(0);                // cart count context

let renders = { ctxConsumer: 0, ctxBystander: 0, propsConsumer: 0, propsBystander: 0 };

// --- Context version ---
function CtxConsumer() {
  const count = useContext(CartContext);             // subscribed: re-renders on every count change
  renders.ctxConsumer++;
  return <p>Context consumer: {count}</p>;
}
const CtxBystander = memo(function CtxBystander() {  // does not read the context
  renders.ctxBystander++;                            // memo + no context → skipped on updates
  return <p>Context bystander</p>;
});

// --- Props version ---
const PropsConsumer = memo(function PropsConsumer({ count }) {
  renders.propsConsumer++;                           // re-renders only when count prop changes
  return <p>Props consumer: {count}</p>;
});
const PropsBystander = memo(function PropsBystander() {
  renders.propsBystander++;                          // never re-renders after mount
  return <p>Props bystander</p>;
});

function App() {
  const [count, setCount] = useState(0);             // cart count state
  return (
    <CartContext.Provider value={count}>
      <button onClick={() => setCount(c => c + 1)}>Add to cart</button>
      <CtxConsumer />
      <CtxBystander />
      <PropsConsumer count={count} />
      <PropsBystander />
      <pre>{JSON.stringify(renders)}</pre>          {/* shows counts as of this render */}
    </CartContext.Provider>
  );
}

createRoot(document.getElementById('root')).render(<App />);
// After 3 clicks: consumers re-rendered 4 times each, bystanders only once (initial mount)
```

---

## 🟠 Next.js Connection

In the App Router, **Server Components cannot use Context** (no `createContext` consumption, no hooks), but they can pass data as props to Client Components. This often makes props drilling less painful, because data is fetched **where it is needed** (each Server Component fetches its own data, and `fetch` calls are deduplicated by Next.js or by React's `cache`). So the "global user" often becomes `await getUser()` inside whichever Server Component needs it, instead of a Context. Use Context only for client-side state (theme toggle, cart drawer).

```jsx
// lib/user.js: request-scoped, deduplicated data access (replaces a UserContext on the server)
import { cache } from 'react';
export const getUser = cache(async () => {              // same call in one request runs once
  const res = await fetch('https://example.com/api/me', { cache: 'no-store' });
  return res.json();
});
```

```jsx
// app/components/Header.jsx (Server Component: no Context, no drilling)
import { getUser } from '@/lib/user';

export default async function Header() {
  const user = await getUser();                          // fetch where used
  return <p>Hello, {user.name}</p>;
}
// Any other Server Component can call getUser() too, without receiving it as a prop.
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using Context for everything, including a value used one level down
✅ **Correct:** Start with props, and move to composition or Context only when it hurts

```jsx
// Wrong: Context just to pass a title to a direct child
const TitleCtx = createContext('');                     // ❌ overkill
// Right
<Card title="Order" />                                  // ✅ plain prop
```

❌ **Mistake 2:** Drilling through many layers instead of using composition
✅ **Correct:** Pass the finished element so middle layers need no props

```jsx
// Wrong
<Layout user={user} cart={cart} theme={theme} />       // ❌ Layout only forwards them
// Right
<Layout header={<Header user={user} cart={cart} />} /> // ✅ Layout renders {header}
```

❌ **Mistake 3:** Context for fast-changing state, causing the whole subtree to re-render
✅ **Correct:** Use local state, or a store with selectors (Zustand, Redux Toolkit)

```jsx
// Wrong: mouse position in context → every consumer re-renders on every mouse move
<MouseCtx.Provider value={{ x, y }}>{children}</MouseCtx.Provider>   // ❌
// Right: keep x,y local to the component that needs them, or subscribe via a store selector
```

---

## 🧠 Tricky Interview Question

```jsx
const Ctx = createContext(0);

function App() {
  const [n, setN] = useState(0);
  return (
    <Ctx.Provider value={n}>
      <Parent />
      <button onClick={() => setN(n + 1)}>+</button>
    </Ctx.Provider>
  );
}
function Parent() { console.log('Parent'); return <Child />; }
function Child()  { console.log('Child', useContext(Ctx)); return null; }
```
**Answer:** On mount: `Parent`, `Child 0`. On click: `App` re-renders and creates new `<Parent />` element, so `Parent` re-renders too: `Parent`, `Child 1`. `Parent` is re-rendered because it is not memoized and its parent re-rendered, not because of the context. If you pass `<Parent />` as `children` from a component above the stateful one (the "state down, children stay" trick), `Parent` would be skipped and only `Child` would re-render, due to the context subscription.

---

## ⚫ Interview Questions + Answers

Q1: What is props drilling and is it always bad?
A1: Passing props through intermediate components that do not use them. It is not always bad. For 1 to 2 levels it is explicit and easy to trace. It becomes a problem with deep trees and many forwarded props.

Q2: When is Context better than props?
A2: When many components at different depths need the same value (theme, user, language), and the value changes rarely.

Q3: What is a good alternative to both?
A3: Component composition: pass elements via `children` or slot props, so intermediate layers do not need to know about the data. Also moving state down, closer to where it is used.

Q4: What are the downsides of Context?
A4: Implicit dependencies (components are harder to reuse and test without a Provider), all consumers re-render on any value change, and no built-in selectors. Splitting contexts and memoizing values helps.

Q5: How does Next.js App Router change this decision?
A5: Server Components fetch data where they need it (deduplicated), so there is less need for a global Context for server data. Context remains for client interactivity (theme, modals, cart state) inside `'use client'` providers.

---

## 🔷 When to Use + When Not to Use
✅ **Use props when:**
- Data goes 1 to 2 levels, or the component is a reusable, presentational piece
- You want explicit, easy-to-test data flow

✅ **Use Context when:**
- Many consumers at various depths need slow-changing data
- You build a compound component (Tabs, Accordion) sharing internal state

❌ **Avoid Context when:**
- The value changes frequently or the tree is large (re-render cost)
- A simple composition or a refactor (moving state down) removes the drilling

---

## 📊 Visual Diagram

```
 PROPS DRILLING                    COMPOSITION                    CONTEXT
 App(user)                         App(user)                      App ── Provider(user)
  └─ Layout(user)  forwards         └─ Layout(header=<Header/>)     ├─ Layout (no props)
      └─ Sidebar(user) forwards          └─ renders {header}        │    └─ Sidebar (no props)
          └─ Menu(user) USES                                         │         └─ Menu ◄─ useContext
                                    Header(user) built in App        └─ Avatar ◄─ useContext

 Re-renders: props → parent change re-renders chain (memo can cut it)
             context → every consumer re-renders when value changes
 Traceability: props = high (explicit), context = lower (implicit)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Props drilling | Forwarding props through layers | Layers से props आगे बढ़ाना |
| Context | Tree-wide value sharing | Tree में value साझा करना |
| Composition | Passing elements as children/slots | Elements को children/slots में देना |
| Explicit | Visible in code | कोड में साफ़ दिखने वाला |
| Implicit | Hidden dependency | छिपी हुई निर्भरता |
| Lifting state | Moving state to a common parent | State को साझा parent में ले जाना |
| Selector | Subscribing to a slice of state | State के एक हिस्से की subscription |

---

## ⚡ 3-Line Summary
**English:**
1. Props are explicit and best for short paths; Context is implicit and best for slow-changing, widely used data.
2. Try composition and moving state down before reaching for Context.
3. For fast-changing global state use a store; in Next.js, Server Components fetch data where needed.

**Hindi:**
1. Props साफ़ हैं और छोटे रास्तों के लिए बेहतर; Context छिपा हुआ है और धीरे बदलने वाले, कई जगह इस्तेमाल होने वाले data के लिए बेहतर।
2. Context से पहले composition और state को नीचे ले जाना आज़माओ।
3. तेज़ बदलने वाली global state के लिए store इस्तेमाल करो; Next.js में Server Components data वहीं fetch करते हैं जहाँ चाहिए।

---

## 📚 Go Deeper — External Resources
| Type | Link | Why |
|------|------|-----|
| 📝 Article | [react.dev — Passing Data Deeply with Context](https://react.dev/learn/passing-data-deeply-with-context) | Includes "Before you use context" advice |
| 📝 Article | [react.dev — Scaling Up with Reducer and Context](https://react.dev/learn/scaling-up-with-reducer-and-context) | Pattern for bigger apps |

---

## ➡️ Next Topic
**45. useReducer** (already covered) और फिर **46. useReducer vs useState** — जटिल state के लिए reducer कब बेहतर है, और Context के साथ इसका जोड़ कैसे बनता है।
