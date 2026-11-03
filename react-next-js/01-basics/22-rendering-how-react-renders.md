# 22. Rendering — How React Renders
# हिंदी में: Rendering — React स्क्रीन कैसे बनाता है

---

## 🔵 Simple Definition (English)
**Rendering** is React calling your component functions to find out what the UI should look like. It has three steps: **trigger** (initial mount or a state change), **render** (call components, build a description of the UI), and **commit** (apply the needed changes to the real DOM). Rendering is not the same as updating the screen.

## 🔵 सरल परिभाषा (Hindi)
**Rendering** का मतलब है React का आपके component functions को call करके पता लगाना कि UI कैसा दिखना चाहिए। इसके तीन steps हैं: **trigger** (पहली बार mount या state change), **render** (components call करके UI का description बनाना), और **commit** (असली DOM में ज़रूरी बदलाव लागू करना)। Rendering का मतलब screen update होना नहीं है।

---

## 🔴 Problem it Solves

Directly editing the DOM is slow and error-prone. React needs a way to take your data, calculate the UI, and touch the real DOM as little as possible. If every state change rebuilt the whole page, the app would be slow and would lose input focus and scroll position.

Many developers also have wrong ideas: "render = DOM update" (false: a render can produce no DOM change), or "a component re-renders only when its props change" (false: it re-renders whenever its parent re-renders). Understanding the three phases explains performance, effects and StrictMode behavior.

## 🔴 यह क्यों बना? (Hindi)
सीधे DOM को बदलना धीमा और error वाला है। React को ऐसा तरीका चाहिए था जो आपके data से UI निकाले और असली DOM को कम से कम छुए। अगर हर state change पर पूरा page दोबारा बनता, तो app धीमा होता और input focus व scroll position खो जाते।

कई developers के गलत विचार भी होते हैं: "render = DOM update" (गलत: render से DOM में कोई बदलाव न भी हो सकता है), या "component तभी re-render होता है जब props बदलें" (गलत: parent re-render होने पर भी होता है)। तीनों phases समझने से performance, effects और StrictMode का व्यवहार समझ आता है।

---

## 🟢 How it Works — Step by Step

```
TRIGGER
Step 1 → Initial render:  createRoot(el).render(<App />)
         Re-render:       a setState call (or a context change, or the parent rendering)

RENDER PHASE (pure calculation, no DOM touch, can be paused/restarted in concurrent mode)
Step 2 → React calls your component function: App()
Step 3 → It returns JSX = a tree of plain objects (React elements)
Step 4 → React calls child components found in that tree, recursively
Step 5 → React diffs the new tree against the previous tree (reconciliation)
         same type + same key → reuse and update; different type → remount

COMMIT PHASE (synchronous, touches the DOM)
Step 6 → React applies only the minimal DOM changes
Step 7 → Runs ref attachment and layout effects (useLayoutEffect)
Step 8 → Browser paints the screen
Step 9 → useEffect callbacks run after paint

RULE: render must be pure (same props/state in → same JSX out, no side effects)
```

## 🟢 कैसे काम करता है? (Hindi)
```
TRIGGER
Step 1 → पहली बार:   createRoot(el).render(<App />)
         दोबारा:      setState call (या context change, या parent का render)

RENDER PHASE (शुद्ध गणना, DOM नहीं छूता, concurrent mode में रोका/फिर शुरू किया जा सकता है)
Step 2 → React आपका component function call करता है: App()
Step 3 → वह JSX लौटाता है = साधारण objects (React elements) का tree
Step 4 → React उस tree में मिले child components को recursively call करता है
Step 5 → React नए tree की पुराने tree से तुलना करता है (reconciliation)
         same type + same key → reuse और update; अलग type → remount

COMMIT PHASE (synchronous, DOM को छूता है)
Step 6 → React सिर्फ ज़रूरी न्यूनतम DOM changes लागू करता है
Step 7 → refs attach करता है और layout effects (useLayoutEffect) चलाता है
Step 8 → Browser screen paint करता है
Step 9 → paint के बाद useEffect callbacks चलते हैं

नियम: render pure होना चाहिए (same props/state → same JSX, कोई side effect नहीं)
```

---

## 🟡 Real World Example
**Zomato search:** You type "pi" in the search box. The `SearchPage` state `query` changes (trigger). React calls `SearchPage`, which calls the `ResultsList` and each `RestaurantCard` (render). React compares the old list with the new list: most cards are the same, a few are removed, and the DOM gets only those removals (commit). The input is not recreated, so you do not lose focus while typing. If `SearchPage` has a heavy header component, that header also re-renders on every keystroke unless you restructure or memoize, which is a classic performance issue.

## 🟡 Real Example Hindi mein
**Zomato search:** आप search box में "pi" लिखते हैं। `SearchPage` की state `query` बदलती है (trigger)। React `SearchPage` को call करता है, जो `ResultsList` और हर `RestaurantCard` को call करता है (render)। React पुरानी और नई list की तुलना करता है: ज़्यादातर cards वही हैं, कुछ हटे हैं, और DOM में सिर्फ वही हटाना होता है (commit)। Input दोबारा नहीं बनता, इसलिए typing के समय focus नहीं जाता। अगर `SearchPage` में भारी header component है, तो वह भी हर keystroke पर re-render होगा जब तक आप structure न बदलें या memoize न करें। यह एक classic performance समस्या है।

---

## 💻 Code Example — Basic

```jsx
// Basic: watch renders with console.log and see who re-renders
import { useState } from 'react';                    // state hook
import { createRoot } from 'react-dom/client';       // React 18/19 root API

function Child() {
  console.log('Child rendered');                     // runs every time React calls Child
  return <p>I am a child</p>;                        // no props, still re-renders with the parent
}

function Parent() {
  const [count, setCount] = useState(0);             // state change triggers a re-render
  console.log('Parent rendered, count =', count);    // render phase log
  return (
    <div>
      <button onClick={() => setCount(count + 1)}>Clicked {count}</button> {/* trigger */}
      <Child />                                      {/* re-renders on every Parent render */}
    </div>
  );
}

// First mount logs:  Parent rendered, count = 0  →  Child rendered
// Each click logs:   Parent rendered, count = N  →  Child rendered   (Child had no props change!)
createRoot(document.getElementById('root')).render(<Parent />);
```

## 💻 Code Example — Advanced

```jsx
// Advanced: three ways to stop needless re-renders, and a render counter to prove it
import { memo, useState, useRef } from 'react';      // memo + state + ref
import { createRoot } from 'react-dom/client';       // React 18/19 root API

// Tiny helper: counts how many times a component rendered (ref changes do NOT cause renders)
function useRenderCount(name) {
  const count = useRef(0);                           // survives renders, does not trigger them
  count.current += 1;                                // increment during render (OK for a debug counter)
  console.log(`${name} render #${count.current}`);   // visible in the console
  return count.current;                              // also show it in the UI
}

// 1) Heavy list: wrapped in memo → skips render when props are shallow-equal
const RestaurantList = memo(function RestaurantList({ restaurants }) {
  const n = useRenderCount('RestaurantList');        // log render count
  return (
    <ul>
      <li><i>list renders: {n}</i></li>
      {restaurants.map((r) => <li key={r}>{r}</li>)}
    </ul>
  );
});

// 2) "children as props": the element is created by the PARENT of Counter, not by Counter
function Counter({ children }) {
  const [n, setN] = useState(0);                     // state lives here
  useRenderCount('Counter');                         // Counter renders on every click
  // children is the SAME element object each time → React skips re-rendering it
  return <button onClick={() => setN(n + 1)}>Clicked {n} {children}</button>;
}

const RESTAURANTS = ['Biryani Blues', 'Green Bowl'];  // module level → same reference every render

function SearchPage() {
  const [query, setQuery] = useState('');            // typing triggers renders of SearchPage
  useRenderCount('SearchPage');                      // log every SearchPage render

  return (
    <div>
      <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search" /> {/* trigger */}
      <RestaurantList restaurants={RESTAURANTS} />   {/* props unchanged → memo skips it */}
      <Counter><b>(static child)</b></Counter>       {/* b element is created here, not inside Counter */}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<SearchPage />);
```

---

## 🟠 Next.js Connection
Next.js adds a **server render** before the browser render. In the App Router, Server Components are rendered on the server (at request time or build time) into a special payload (the RSC payload) plus HTML. The browser then **hydrates** only the Client Components: React attaches event handlers to the already existing HTML. Server Components never re-render in the browser, so they cost no client JavaScript.

```jsx
// app/page.jsx (Server Component): renders once on the server, never re-renders in the browser
export default async function Home() {
  console.log('Home rendered');                      // appears in the SERVER terminal, not the browser
  const res = await fetch('https://api.example.com/trending', { cache: 'no-store' }); // fresh per request
  const items = await res.json();                    // data is ready before HTML is sent
  return (
    <main>
      <h1>Trending</h1>
      <ul>{items.map((i) => <li key={i.id}>{i.name}</li>)}</ul>
    </main>
  );
}
```

```jsx
// app/LikeButton.jsx (Client Component): renders on the server for first HTML, then hydrates and re-renders in the browser
'use client';
import { useState } from 'react';

export default function LikeButton() {
  const [liked, setLiked] = useState(false);         // first HTML always shows liked=false
  console.log('LikeButton rendered');                // prints on server (first HTML) AND in browser
  return <button onClick={() => setLiked(!liked)}>{liked ? '♥' : '♡'}</button>;
}
```

Hydration mismatch warning: the first client render must produce the same output as the server HTML (do not use `Date.now()` or `Math.random()` directly in render).

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Doing side effects inside render
✅ **Correct:** Put side effects in event handlers or `useEffect`

```jsx
// Wrong: runs on every render (and twice in StrictMode), mutates outside values
function Bad() {
  document.title = 'Hello';                          // ❌ side effect during render
  localStorage.setItem('visits', Date.now());        // ❌ also not available on the server
  return <p>Hi</p>;
}

// Right
function Good() {
  useEffect(() => { document.title = 'Hello'; }, []);// ✅ after commit
  return <p>Hi</p>;
}
```

❌ **Mistake 2:** Thinking a re-render means the DOM was rebuilt
✅ **Correct:** Render is calculation; commit changes only the differences

```jsx
// A component can re-render 100 times, and the DOM only changes
// where the output differs. Do not "optimize" with memo before you measure
// that renders are actually expensive.
```

❌ **Mistake 3:** Creating new objects/functions in render and passing them to a `memo` child
✅ **Correct:** Keep references stable with `useMemo` / `useCallback`, or move them out

```jsx
// Wrong: new object every render → memo child always re-renders
<RestaurantList options={{ sort: 'rating' }} />      // ❌ new {} each time

// Right
const OPTIONS = { sort: 'rating' };                  // ✅ module level, stable reference
<RestaurantList options={OPTIONS} />
```

---

## 🧠 Tricky Interview Question

```jsx
import { useState } from 'react';

function Expensive() {
  console.log('Expensive');
  return <p>heavy</p>;
}

function Counter({ children }) {
  const [n, setN] = useState(0);
  return <button onClick={() => setN(n + 1)}>{n}{children}</button>;
}

function App() {
  console.log('App');
  return <Counter><Expensive /></Counter>;
}
// Mount once, then click the button 3 times (no StrictMode). What is logged?
```
**Answer:** Only `App` and `Expensive` on the initial mount; **nothing** during the clicks. The `<Expensive />` element is created inside `App`. When `Counter` re-renders from its own state, `App` does not run, so React receives the exact same element object (`children`) as before. React skips a subtree when the element is identical (same reference) and nothing inside needs updating. This "state down / content as children" pattern avoids re-renders without `memo`.

---

## ⚫ Interview Questions + Answers

Q1: What are the phases of rendering in React?
A1: Trigger (mount or state update), render (call components and build the element tree, diff against the previous one), and commit (apply changes to the DOM, run layout effects, then the browser paints and `useEffect` runs). The render phase must be pure; the commit phase is where side effects belong.

Q2: When does a component re-render?
A2: When its own state changes, when its parent re-renders (even with the same props, unless memoized), or when a context it reads changes. A prop change alone is not the reason; the parent render is.

Q3: Does re-rendering mean the DOM updates?
A3: No. React re-calls the component and compares the result with the previous output. Only the differences are written to the DOM. If nothing differs, the DOM is not touched.

Q4: What is reconciliation?
A4: The diffing process that compares the previous and the next element trees. Elements with the same type and key at the same position are updated in place; a different type or key destroys the old subtree and creates a new one. Lists need stable keys for this to work well.

Q5: What changed in React 18 about rendering?
A5: Automatic batching (all updates batched, also in promises and timeouts), concurrent rendering (the render phase can be interrupted by urgent updates, enabled by features like `useTransition`), and `createRoot` as the entry point. In dev with StrictMode the components render twice to catch impure code.

---

## 🔷 When to Use + When Not to Use
✅ **Optimize rendering (memo, splitting state, children pattern) when:**
- A profiler shows a slow component re-rendering often (big lists, charts)
- State changes very frequently (typing, scrolling, drag) above heavy children
- The expensive child receives the same props most of the time

❌ **Avoid premature optimization when:**
- Renders are cheap; extra `memo` and `useCallback` add complexity and memory
- You have not measured with React DevTools Profiler
- Props are new objects each time anyway (memo would never skip)

---

## 📊 Visual Diagram

```
  TRIGGER ──► RENDER (pure) ──────────────► COMMIT ──────────► AFTER PAINT
  setState    call App()                    DOM mutations        useEffect
  / mount     call children                 refs attached
              build element tree            useLayoutEffect
              diff old vs new tree          browser paints

  Parent re-renders:
        App ──► Parent ──► Child       (all re-run, unless memo/same element)
                  ▲
               setState

  Same-element bail-out:
        App (not re-run) ── passes <Expensive/> element ──► Counter (state)
        Counter re-renders; its children prop is the SAME object → Expensive skipped
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Render | Calling a component to get its JSX | Component को call करके JSX पाना |
| Commit | Applying changes to the real DOM | असली DOM में बदलाव लागू करना |
| Reconciliation | Diffing old and new element trees | पुराने और नए tree की तुलना |
| Re-render | Calling the component again after a trigger | Trigger के बाद component फिर चलाना |
| Pure render | Same inputs → same output, no side effects | समान input → समान output, कोई side effect नहीं |
| Hydration | Attaching React to server-made HTML | Server के HTML में React जोड़ना |
| Batching | Grouping updates into a single render | Updates को एक render में जोड़ना |
| Bail-out | React skipping work because nothing changed | कुछ न बदलने पर React का काम छोड़ देना |

---

## ⚡ 3-Line Summary
**English:**
1. Rendering = trigger, render (call components, diff), commit (update DOM); render must be pure.
2. A component re-renders on its own state change, its parent's render, or a context change, and the DOM changes only where output differs.
3. Optimize with state colocation, the children pattern and `memo` after measuring; in Next.js, Server Components render only on the server.

**Hindi:**
1. Rendering = trigger, render (components call और diff), commit (DOM update); render हमेशा pure होना चाहिए।
2. Component अपनी state बदलने, parent के render या context बदलने पर re-render होता है, और DOM सिर्फ वहाँ बदलता है जहाँ output अलग हो।
3. पहले measure करो, फिर state को पास रखकर, children pattern और `memo` से optimize करो; Next.js में Server Components सिर्फ server पर render होते हैं।

---

## ➡️ Next Topic
**25. Why key Prop is Important** — Rendering में हमने देखा कि React पुराने और नए tree की तुलना करता है। Lists में यह तुलना `key` के भरोसे चलती है। गलत key से state गलत item से जुड़ जाती है, इसलिए इसे अगला पढ़ें।
