# 51. useId Hook
# हिंदी में: useId Hook — SSR-safe Unique IDs बनाना

---

## 🔵 Simple Definition (English)
**`useId`** is a React 18+ hook that generates a stable, unique ID string. The same ID is produced on the server and on the client, so it is safe for server rendering and hydration. It is meant for linking things like `<label htmlFor>` and `aria-describedby`.

## 🔵 सरल परिभाषा (Hindi)
**`useId`** React 18+ का hook है जो एक stable और unique ID string बनाता है। Server और client दोनों पर एक ही ID बनती है, इसलिए SSR और hydration में सुरक्षित है। इसका इस्तेमाल `<label htmlFor>` और `aria-describedby` जैसे links के लिए होता है।

---

## 🔴 Problem it Solves

Form inputs need a unique `id` so that a `<label>` can point to them. Developers used to write `id="email"`, but a reusable component used twice on a page then produces duplicate IDs, which breaks accessibility (clicking the label focuses the wrong field). The next idea was `Math.random()` or a global counter, but that gives different values on the server and in the browser, so React shows a **hydration mismatch** warning.

```jsx
// PROBLEM 1: hard-coded id → duplicates when the component is used twice
function Field() { return <><label htmlFor="email">Email</label><input id="email" /></>; }

// PROBLEM 2: random id → server HTML id != client id → hydration mismatch
function Field2() {
  const id = 'f-' + Math.random();              // different on server and client
  return <><label htmlFor={id}>Email</label><input id={id} /></>;
}

// SOLUTION: useId gives the same id on the server and client, unique per instance
```

## 🔴 यह क्यों बना? (Hindi)
Form input को unique `id` चाहिए ताकि `<label>` उससे जुड़ सके। `id="email"` लिखने पर component दो बार इस्तेमाल करते ही duplicate IDs बनती हैं और accessibility टूट जाती है (label पर click करने से गलत field focus होता है)। `Math.random()` या global counter से server और browser पर अलग values आती हैं, इसलिए React **hydration mismatch** का warning देता है। `useId` दोनों जगह एक जैसी और हर instance के लिए अलग ID देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Call const id = useId() at the top level of your component
Step 2 → React builds the id from the component's position in the tree (not from a random number)
Step 3 → Server renders HTML with that id (e.g. ":r1:" in React 18, "«r1»" in newer React 19.x)
Step 4 → Client hydrates the same tree, computes the same position-based id → no mismatch
Step 5 → Use the id for htmlFor / id / aria-* attributes; append suffixes for several related ids
Step 6 → Each component instance gets its own unique id, even when reused many times

KEY: the exact format of the id string is an implementation detail (version-dependent). Never parse it.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Component के top level पर const id = useId() call करो
Step 2 → React ID को component की tree में position से बनाता है (random number से नहीं)
Step 3 → Server उसी id के साथ HTML बनाता है (React 18 में जैसे ":r1:", नए React 19.x में "«r1»")
Step 4 → Client उसी tree को hydrate करता है, वही position-based id बनती है → mismatch नहीं
Step 5 → id को htmlFor / id / aria-* में इस्तेमाल करो; कई related ids के लिए suffix जोड़ो
Step 6 → Component कितनी भी बार use हो, हर instance की अपनी unique id होती है

KEY: id string का format implementation detail है (version-dependent)। उसे कभी parse मत करो।
```

---

## 🟡 Real World Example
**Swiggy checkout form:** The "Add address" form is a reusable `TextField` component. The checkout page shows it for "Flat number", "Landmark" and "Pincode", and the page is server-rendered for fast first paint. Each `TextField` calls `useId()`, so each label is tied to its own input, screen readers read the correct label, and React hydrates the page without mismatch warnings.

## 🟡 Real Example Hindi mein
**Swiggy checkout form:** "Add address" form में reusable `TextField` component है। Checkout page पर यह "Flat number", "Landmark" और "Pincode" के लिए तीन बार दिखता है, और page तेज़ first paint के लिए server-rendered है। हर `TextField` में `useId()` है, इसलिए हर label अपने input से जुड़ा रहता है, screen reader सही label पढ़ता है और hydration में कोई mismatch warning नहीं आती।

---

## 💻 Code Example — Basic

```jsx
// Basic useId: a reusable labelled input
import { useId } from 'react';                          // hook available in React 18+
import { createRoot } from 'react-dom/client';          // React 18/19 root API

function TextField({ label }) {                          // reusable field component
  const id = useId();                                    // unique, SSR-safe id for this instance
  return (
    <div>
      <label htmlFor={id}>{label}</label>                {/* label points to the input */}
      <input id={id} type="text" />                      {/* same id → clicking label focuses input */}
    </div>
  );
}

function App() {
  return (
    <form>
      <TextField label="Flat number" />                  {/* instance 1 → own id */}
      <TextField label="Landmark" />                     {/* instance 2 → different id */}
      <TextField label="Pincode" />                      {/* instance 3 → different id */}
    </form>
  );
}

createRoot(document.getElementById('root')).render(<App />); // mount the app
```

## 💻 Code Example — Advanced

```jsx
// Advanced: one useId, several derived ids + accessible error/hint text
import { useId, useState } from 'react';                 // hooks
import { createRoot } from 'react-dom/client';           // root API

function PhoneField({ label, hint }) {
  const baseId = useId();                                // ONE call per component, then derive more ids
  const inputId = `${baseId}-input`;                     // id for the input element
  const hintId = `${baseId}-hint`;                       // id for helper text
  const errorId = `${baseId}-error`;                     // id for the error message
  const [value, setValue] = useState('');                // controlled input value
  const isInvalid = value.length > 0 && !/^[6-9]\d{9}$/.test(value); // simple Indian mobile check

  return (
    <div>
      <label htmlFor={inputId}>{label}</label>           {/* clickable label */}
      <input
        id={inputId}                                     // target of the label
        value={value}                                    // controlled value
        onChange={(e) => setValue(e.target.value)}       // update state on typing
        aria-invalid={isInvalid}                         // tells assistive tech the state
        aria-describedby={isInvalid ? `${hintId} ${errorId}` : hintId} // links hint (+ error)
      />
      <small id={hintId}>{hint}</small>                  {/* always linked as description */}
      {isInvalid && (
        <p id={errorId} role="alert">Enter a valid 10-digit mobile number</p> // announced on appear
      )}
    </div>
  );
}

function App() {
  return (
    <div>
      <PhoneField label="Mobile" hint="We send the OTP here" />           {/* instance A */}
      <PhoneField label="Alternate mobile" hint="Used if the first fails" /> {/* instance B */}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
```

Re-render behavior: `useId` returns the **same string on every re-render** of that component instance, so typing in the input re-renders `PhoneField` but all ids stay unchanged. The hook itself costs almost nothing, so there is no performance concern.

---

## 🟠 Next.js Connection

`useId` was built for SSR, so it works directly in Next.js. It can be used in Server Components too (no `'use client'` needed for the hook itself), but the component that has state (`useState`) must be a Client Component. Ids stay consistent between the server HTML and client hydration.

```jsx
// app/components/SearchBox.jsx
'use client';                                            // uses state, so it is a Client Component
import { useId, useState } from 'react';                 // hooks

export default function SearchBox() {
  const id = useId();                                    // same id in server HTML and in the browser
  const [q, setQ] = useState('');                        // search text state
  return (
    <div>
      <label htmlFor={id}>Search restaurants</label>     {/* linked label */}
      <input id={id} value={q} onChange={(e) => setQ(e.target.value)} /> {/* controlled input */}
    </div>
  );
}
```

```jsx
// app/page.jsx (Server Component) → can render two SearchBox instances safely
import SearchBox from './components/SearchBox';          // each instance gets a different id
export default function Page() {
  return <><SearchBox /><SearchBox /></>;                // no duplicate ids, no hydration warning
}
```

Note: `useId` ids are not valid CSS selectors or `querySelector` targets in all versions because they contain `:` (React 18) or other special characters (version-dependent). Prefer attribute linking, not `document.querySelector('#' + id)`.

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `useId` to generate keys for list items
✅ **Correct:** Use a stable id from your data (`item.id`) for `key`

```jsx
// Wrong: useId cannot be called inside a loop/map and is not meant for keys
{items.map((item) => {
  const id = useId();                                    // ❌ breaks the Rules of Hooks
  return <li key={id}>{item.name}</li>;
})}

// Right: key comes from the data
{items.map((item) => <li key={item.id}>{item.name}</li>)} // ✅ stable key from the database id
```

❌ **Mistake 2:** Using `Math.random()` / `Date.now()` for ids in an SSR app
✅ **Correct:** Use `useId`

```jsx
// Wrong: different value on the server and the client → hydration mismatch
const id = 'field-' + Math.random();                     // ❌ not deterministic

// Right
const id = useId();                                      // ✅ deterministic across server/client
```

❌ **Mistake 3:** Calling `useId` once and reusing the same id for several elements
✅ **Correct:** Call once per component, then add suffixes

```jsx
// Wrong: label and hint both use the same id → duplicate ids on the page
<input id={id} /> <small id={id}>hint</small>            // ❌ two elements, one id

// Right: derive different ids from the base
<input id={`${id}-input`} /> <small id={`${id}-hint`}>hint</small> // ✅ unique per element
```

---

## 🧠 Tricky Interview Question

```jsx
import { useId } from 'react';
import { createRoot } from 'react-dom/client';

function Item({ text }) {
  const id = useId();                                    // each instance gets an id
  return <li data-id={id}>{text}</li>;
}

function App() {
  return (
    <ul>
      <Item text="A" />
      <Item text="B" />
    </ul>
  );
}

createRoot(document.getElementById('root')).render(<App />);
```
**Answer:** The two `<li>` elements get **different** ids (for example `:r0:` and `:r1:` in React 18; exact format is version-dependent). `useId` is tied to the component instance's position in the tree, not to the component function. If you re-render, the ids stay the same for the lifetime of each instance. A remounted instance (for example after its `key` changes) is a new instance and gets a new id.

---

## ⚫ Interview Questions + Answers

Q1: What is `useId` used for?
A1: Generating a unique, stable id string for accessibility attributes such as `htmlFor`, `aria-describedby` and `aria-labelledby`. It guarantees uniqueness per component instance and the same value on server and client.

Q2: Why not use `Math.random()` or a counter?
A2: Random values differ between server render and client hydration, causing hydration mismatches. A module-level counter breaks when the same component renders in different orders or concurrently. `useId` derives the id from the tree position, so it is deterministic.

Q3: Can I use `useId` for list keys?
A3: No. Hooks cannot be called inside loops, and keys must come from your data so React can track items between renders. Use the item's database id.

Q4: How do I make several ids from one `useId`?
A4: Call the hook once and append suffixes: `${id}-input`, `${id}-hint`, `${id}-error`. This keeps them unique and related.

Q5: Does `useId` cause re-renders or have a performance cost?
A5: No. It returns the same string for the lifetime of the instance and does not trigger renders. The cost is negligible.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- You build reusable form fields that link `label`, `input`, hint and error text
- Your app is server-rendered (Next.js, Remix) and needs hydration-safe ids
- You need ids for ARIA attributes such as `aria-controls` or `aria-labelledby`

❌ **Avoid when:**
- You need list `key` values (use data ids)
- You need an id for database records or analytics (use real data ids or `crypto.randomUUID()` in event handlers)
- You need a CSS selector id (the characters in the generated id may not be selector-friendly)

---

## 📊 Visual Diagram

```
 Server render                          Client hydration
 ─────────────                          ────────────────
 <TextField/>  position A → id ":r0:"   <TextField/> position A → id ":r0:"   ✅ match
 <TextField/>  position B → id ":r1:"   <TextField/> position B → id ":r1:"   ✅ match

 With Math.random():
 server → "f-0.31"   client → "f-0.87"                                        ❌ mismatch

 One useId, many ids:
   baseId = useId()
     ├── baseId + "-input"  → <input>
     ├── baseId + "-hint"   → <small>
     └── baseId + "-error"  → <p role="alert">
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| useId | Hook that returns a stable unique id | Stable unique id देने वाला hook |
| Hydration | Attaching React to server HTML | Server HTML से React को जोड़ना |
| Hydration mismatch | Server and client output differ | Server और client का output अलग होना |
| htmlFor | Label attribute pointing to an input id | Label को input से जोड़ने वाला attribute |
| aria-describedby | Links an element to its description | Element को उसके description से जोड़ना |
| SSR | Rendering HTML on the server | Server पर HTML बनाना |
| Deterministic | Same input gives same output | हर बार एक जैसा नतीजा |
| Accessibility (a11y) | Making UI usable for everyone | UI को सबके लिए usable बनाना |

---

## ⚡ 3-Line Summary
**English:**
1. `useId` returns a unique id that is identical on the server and the client.
2. Use it for `htmlFor` and ARIA links; derive extra ids with suffixes from one call.
3. Do not use it for list keys or CSS selectors.

**Hindi:**
1. `useId` ऐसी unique id देता है जो server और client पर एक जैसी होती है।
2. इसे `htmlFor` और ARIA links के लिए इस्तेमाल करो; एक call से suffix जोड़कर और ids बनाओ।
3. इसे list keys या CSS selectors के लिए इस्तेमाल मत करो।

---

## ➡️ Next Topic
**52. useTransition Hook** — Heavy state updates को "low priority" mark करके UI को responsive रखना। `useId` के बाद यह React 18 का सबसे ज़रूरी concurrent feature है।
