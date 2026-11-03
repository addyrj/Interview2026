# 144. Controlled Components Pattern
# हिंदी में: Controlled Components Pattern — Value Parent के हाथ में

---

## 🔵 Simple Definition (English)
A **controlled component** gets its current value from props and reports changes through a callback (`value` + `onChange`), so the parent owns the state. An **uncontrolled** one keeps its own state (or the DOM does) and exposes only a `defaultValue`.

## 🔵 सरल परिभाषा (Hindi)
**Controlled component** अपनी मौजूदा value props से लेता है और बदलाव callback (`value` + `onChange`) से बताता है, यानी state parent के पास रहती है। **Uncontrolled** component अपनी state खुद (या DOM) रखता है और सिर्फ `defaultValue` लेता है।

---

## 🔴 Problem it Solves

When a reusable component (a quantity stepper, a search box, a rating) hides its state inside, the parent cannot reset it, validate it, sync it with another widget or save it. You end up with hacks like `key` resets or refs to read the value.

```jsx
// PROBLEM: internal state, parent has no control
function Stepper() {
  const [qty, setQty] = useState(1);                   // parent can't read, reset or limit this
  return <button onClick={() => setQty(qty + 1)}>{qty}</button>;
}
// Cart total needs qty, "Clear cart" must reset qty → impossible without hacks

// SOLUTION: controlled, parent owns the value
function Stepper({ value, onChange }) {
  return <button onClick={() => onChange(value + 1)}>{value}</button>;  // pure view of props
}
```

## 🔴 यह क्यों बना? (Hindi)
जब reusable component (quantity stepper, search box, rating) अपनी state अंदर छुपा लेता है, तो parent उसे reset, validate, किसी दूसरे widget से sync या save नहीं कर सकता। फिर `key` reset या refs से value पढ़ने जैसे hacks करने पड़ते हैं। Controlled pattern में value parent के पास रहती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Parent holds state: const [qty, setQty] = useState(1)
Step 2 → Parent passes value={qty} and onChange={setQty} to the child
Step 3 → Child renders ONLY what the value says (no own copy of the state)
Step 4 → User acts → child calls onChange(newValue) (it never sets the value itself)
Step 5 → Parent updates its state (it may also reject or transform the change: clamp, validate)
Step 6 → Parent re-renders, passes the new value, child shows it

For inputs: <input value={text} onChange=...> is controlled; <input defaultValue="x" ref=...> is uncontrolled
Rule: switching between controlled and uncontrolled for the same instance causes a React warning (value goes from undefined to defined)
Re-render: every keystroke re-renders the parent and the controlled child; memoize heavy siblings or use deferred values
Performance: fine for most forms; for very large forms consider uncontrolled + refs or libraries like react-hook-form
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Parent state रखता है: const [qty, setQty] = useState(1)
Step 2 → Parent child को value={qty} और onChange={setQty} देता है
Step 3 → Child सिर्फ वही दिखाता है जो value कहती है (अपनी state की कॉपी नहीं)
Step 4 → User कुछ करता है → child onChange(newValue) बुलाता है (खुद value नहीं बदलता)
Step 5 → Parent अपनी state update करता है (बदलाव को reject या बदल भी सकता है: clamp, validate)
Step 6 → Parent re-render होकर नई value देता है, child उसे दिखाता है

Inputs के लिए: <input value={text} onChange=...> controlled है; <input defaultValue="x" ref=...> uncontrolled है
नियम: एक ही instance में controlled से uncontrolled (या उल्टा) बदलने पर React warning देता है
Re-render: हर keystroke पर parent और controlled child re-render होते हैं; भारी siblings को memoize करो
Performance: ज़्यादातर forms के लिए ठीक; बहुत बड़े forms में uncontrolled + refs या react-hook-form
```

---

## 🟡 Real World Example
**Amazon cart quantity and Flipkart filters:** The cart page has a quantity dropdown per item, a "Subtotal" at the top, and a "Save for later" action. Because quantity is owned by the cart state (parent), changing one item updates the subtotal instantly, "Save for later" removes it, and the max quantity limit (for example 10) can be enforced in one place. On Flipkart, the price slider and the "Clear all filters" button also work because the filter state lives in the parent.

## 🟡 Real Example Hindi mein
**Amazon cart quantity और Flipkart filters:** Cart page पर हर item के लिए quantity dropdown, ऊपर "Subtotal" और "Save for later" होता है। Quantity cart की state (parent) में है, इसलिए एक item बदलते ही subtotal तुरंत बदलता है, "Save for later" उसे हटा देता है और max limit (जैसे 10) एक ही जगह लागू हो जाती है। Flipkart पर price slider और "Clear all filters" भी इसी वजह से काम करते हैं कि filter state parent में है।

---

## 💻 Code Example — Basic

```jsx
// Basic: controlled input and controlled stepper
import { useState } from 'react';                               // state hook
import { createRoot } from 'react-dom/client';                  // root API

function Stepper({ value, onChange, min = 1, max = 10 }) {      // fully controlled child
  return (
    <div>
      <button onClick={() => onChange(Math.max(min, value - 1))}>-</button> {/* ask parent to decrease */}
      <span>{value}</span>                                      {/* show what the parent says */}
      <button onClick={() => onChange(Math.min(max, value + 1))}>+</button> {/* ask parent to increase */}
    </div>
  );
}

function CartRow() {
  const [qty, setQty] = useState(1);                            // parent owns the quantity
  const [coupon, setCoupon] = useState('');                     // controlled text input
  return (
    <div>
      <Stepper value={qty} onChange={setQty} />                 {/* controlled child */}
      <input
        value={coupon}                                          // value always comes from state
        onChange={(e) => setCoupon(e.target.value.toUpperCase())} // parent can transform input
        placeholder="Coupon"
      />
      <p>Total: Rs {qty * 199}</p>                              {/* derived from parent state */}
      <button onClick={() => { setQty(1); setCoupon(''); }}>Reset</button> {/* parent resets both */}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<CartRow />);
```

## 💻 Code Example — Advanced

```jsx
// Advanced: a hook that makes ANY component work in both controlled and uncontrolled mode
import { useState, useCallback, useRef, useEffect } from 'react';
import { createRoot } from 'react-dom/client';

// useControllableState: used by libraries like Radix UI (simplified)
function useControllableState({ value, defaultValue, onChange }) {
  const isControlled = value !== undefined;                     // parent passed value → controlled
  const [inner, setInner] = useState(defaultValue);             // internal state (used if uncontrolled)
  const current = isControlled ? value : inner;                 // single source of truth
  const wasControlled = useRef(isControlled);                   // remember the first mode

  useEffect(() => {                                             // warn about mode switching (dev help)
    if (wasControlled.current !== isControlled) {
      console.warn('Component switched between controlled and uncontrolled mode.');
    }
  }, [isControlled]);

  const setValue = useCallback((next) => {                      // stable setter for children
    const resolved = typeof next === 'function' ? next(current) : next; // support updater functions
    if (!isControlled) setInner(resolved);                      // update own state only if uncontrolled
    onChange?.(resolved);                                       // always tell the parent
  }, [isControlled, current, onChange]);

  return [current, setValue];
}

// A reusable star rating that works either way
function Rating({ value, defaultValue = 0, onChange, max = 5 }) {
  const [rating, setRating] = useControllableState({ value, defaultValue, onChange });
  return (
    <div role="radiogroup" aria-label="Rating">
      {Array.from({ length: max }, (_, i) => i + 1).map((n) => (
        <button
          key={n}
          role="radio"
          aria-checked={rating === n}                           // accessible state
          onClick={() => setRating(n)}                          // works in both modes
        >
          {n <= rating ? '★' : '☆'}
        </button>
      ))}
    </div>
  );
}

function Demo() {
  const [stars, setStars] = useState(3);                        // parent state for controlled usage
  return (
    <div>
      <Rating defaultValue={2} />                               {/* uncontrolled: manages itself */}
      <Rating value={stars} onChange={setStars} />              {/* controlled: parent owns the value */}
      <button onClick={() => setStars(0)}>Clear rating</button> {/* only possible because it is controlled */}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<Demo />);
```

---

## 🟠 Next.js Connection

Controlled inputs need state, so they live in Client Components. A good Next.js pattern: keep the form simple with uncontrolled inputs and a Server Action (`<form action={...}>`) that reads `FormData`, and use controlled inputs only where live UI is needed (live validation, character counts, search-as-you-type). For shareable filters, make the URL the controlled state using `useSearchParams` (value comes from the URL, `onChange` updates it).

```jsx
// app/search/SearchBox.jsx
'use client';                                                   // uses hooks → Client Component
import { useRouter, useSearchParams } from 'next/navigation';   // App Router hooks
import { useState } from 'react';

export default function SearchBox() {
  const router = useRouter();                                   // to update the URL
  const params = useSearchParams();                             // current query string
  const [q, setQ] = useState(params.get('q') ?? '');            // controlled input, initialised from URL
  return (
    <form onSubmit={(e) => { e.preventDefault(); router.push(`/search?q=${encodeURIComponent(q)}`); }}>
      <input value={q} onChange={(e) => setQ(e.target.value)} /> {/* controlled */}
      <button>Search</button>
    </form>
  );
}

// Uncontrolled + Server Action alternative (no client JS needed for the input)
// app/contact/page.jsx
export default function Page() {
  async function send(formData) {                              // Server Action
    'use server';
    console.log(formData.get('email'));                        // read the value on the server
  }
  return <form action={send}><input name="email" defaultValue="" /><button>Send</button></form>;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** `value` without `onChange` (input becomes read-only)
✅ **Correct:** Always pair `value` with `onChange`, or use `defaultValue` for uncontrolled

```jsx
// Wrong: user cannot type, React warns
<input value={name} />                                   // ❌
// Right
<input value={name} onChange={(e) => setName(e.target.value)} />   // ✅
<input defaultValue="Aditya" />                          // ✅ uncontrolled
```

❌ **Mistake 2:** Copying a prop into state (`useState(props.value)`), so it goes stale
✅ **Correct:** Use the prop directly, or reset with a `key`

```jsx
// Wrong: when parent changes `value`, the child still shows the old copy
function Field({ value }) { const [v, setV] = useState(value); /* ❌ stale */ }

// Right: derive from props
function Field({ value, onChange }) { return <input value={value} onChange={(e) => onChange(e.target.value)} />; }
// Or restart state for a different entity: <Field key={user.id} initial={user.name} />
```

❌ **Mistake 3:** Starting with `undefined` and later setting a value (uncontrolled to controlled)
✅ **Correct:** Always initialize with a defined value such as `''`

```jsx
// Wrong
const [email, setEmail] = useState();                    // ❌ undefined → warning when it becomes a string
<input value={email} onChange={(e) => setEmail(e.target.value)} />
// Right
const [email, setEmail] = useState('');                  // ✅
```

---

## 🧠 Tricky Interview Question

```jsx
function App() {
  const [text, setText] = useState('');
  return (
    <input
      value={text}
      onChange={(e) => {
        if (e.target.value.length <= 3) setText(e.target.value);  // ignore longer values
      }}
    />
  );
}
```
**Answer:** The user can type at most 3 characters. When they type a 4th, the handler does not update state, React re-renders (or reconciles) with `value` still equal to the old 3-char string, and React restores the DOM input to that value, so the extra character vanishes immediately. This is the main power of controlled components: the state, not the DOM, decides what the input shows. With an uncontrolled input you could not block the character this way (you would need `maxLength`).

---

## ⚫ Interview Questions + Answers

Q1: What is a controlled component?
A1: A component whose value is controlled by React state through props (`value` and `onChange`). The DOM element always shows what the state says, so React is the single source of truth.

Q2: Controlled vs uncontrolled: how do you choose?
A2: Controlled for live validation, formatting, dependent fields, resetting and syncing. Uncontrolled (`defaultValue` + `ref` or `FormData`) for simple forms, file inputs (always uncontrolled) and large forms where per-keystroke re-render matters.

Q3: Why does React warn "changing an uncontrolled input to be controlled"?
A3: Because `value` changed from `undefined` to a defined value. React decides the mode at the first render, and switching can lose state. Initialize state with `''` or a real default.

Q4: How do you build a component that supports both modes?
A4: Detect `value !== undefined`. If defined, use it and call `onChange`; otherwise keep internal state with `defaultValue` and still call `onChange`. Libraries wrap this in `useControllableState`.

Q5: Does a controlled input hurt performance?
A5: Each keystroke re-renders the owner. For small forms it is negligible. For heavy trees, colocate state in a smaller component, memoize siblings, use `useDeferredValue`, or use an uncontrolled form library.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- The parent must read, validate, reset or sync the value
- You need input formatting/restrictions (uppercase, max length, masks)
- Several widgets depend on the same value (filters, cart)

❌ **Avoid when:**
- A simple one-off form can just read `FormData` on submit
- File inputs (they are always uncontrolled)
- Huge forms where every keystroke re-render hurts (use uncontrolled/react-hook-form)

---

## 📊 Visual Diagram

```
 CONTROLLED                                   UNCONTROLLED
 ┌───────────── Parent ──────────────┐        ┌───────── Child ─────────┐
 │ const [qty, setQty] = useState(1) │        │ const [qty,setQty]=..   │
 └──────┬──────────────────▲─────────┘        │ (parent only sees       │
   value=qty         onChange(new)            │  defaultValue / ref)    │
        ▼                  │                  └─────────────────────────┘
 ┌───────────── Child ───────────────┐
 │ renders {value}; on click →       │
 │ onChange(value + 1)               │
 └───────────────────────────────────┘
 Flow: event → onChange → parent setState → re-render → new value prop → UI
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Controlled | Value owned by parent via props | Parent के props से नियंत्रित value |
| Uncontrolled | Value owned by DOM/inner state | DOM/अंदरूनी state की value |
| `value` | Current value passed to the child | Child को दी गई मौजूदा value |
| `onChange` | Callback reporting a requested change | बदलाव बताने वाला callback |
| `defaultValue` | Initial value for uncontrolled mode | Uncontrolled की शुरुआती value |
| Single source of truth | One place owns the data | डेटा का एक ही मालिक |
| `useControllableState` | Hook supporting both modes | दोनों modes चलाने वाला hook |
| Lifting state up | Moving state to a common parent | State को साझा parent में ले जाना |

---

## ⚡ 3-Line Summary
**English:**
1. Controlled components take `value` and `onChange`, so the parent owns the state and can validate, reset or sync it.
2. Uncontrolled ones keep their own state and are simpler for small forms and file inputs.
3. Never mix modes accidentally: initialize with a defined value and avoid copying props into state.

**Hindi:**
1. Controlled components `value` और `onChange` लेते हैं, इसलिए state parent के पास रहती है और वह validate, reset या sync कर सकता है।
2. Uncontrolled अपनी state खुद रखते हैं और छोटे forms व file inputs के लिए आसान हैं।
3. Modes गलती से मत मिलाओ: defined value से शुरू करो और props को state में copy मत करो।

---

## ➡️ Next Topic
**145. Provider Pattern** — Context Provider से data को पूरे tree में बिना props drilling के कैसे पहुँचाएँ, और उसे सही तरह से design कैसे करें।
