# 30. Two-Way Data Binding
# हिंदी में: Two-Way Data Binding — Data और UI का दोतरफा जुड़ाव

---

## 🔵 Simple Definition (English)
**Two-way data binding** means that when the data changes the UI updates, and when the user changes the UI the data updates, automatically. React has **no built-in two-way binding**. It uses one-way data flow, and you build the second direction yourself with `value` (data → UI) and `onChange` (UI → data).

## 🔵 सरल परिभाषा (Hindi)
**Two-way data binding** का मतलब है कि data बदलने पर UI अपने आप बदले, और user के UI बदलने पर data अपने आप बदले। React में **built-in two-way binding नहीं है**। वह one-way data flow इस्तेमाल करता है, और दूसरी दिशा आप खुद `value` (data → UI) और `onChange` (UI → data) से बनाते हैं।

---

## 🔴 Problem it Solves

Frameworks like AngularJS (1.x) used automatic two-way binding (`ng-model`). It looked easy for forms, but in big apps any component could change the shared data from anywhere, and it was hard to find out who changed what and when. Debugging cascades of updates became painful, and performance suffered (dirty checking).

React chose **explicit, one-way flow**: data goes down, events go up. For form inputs, you wire both directions by hand, so every change passes through a handler where you can validate, transform or reject it.

```jsx
// Angular-style (conceptual): <input [(ngModel)]="name">   ← automatic, hidden
// React: both directions are visible code
<input value={name} onChange={(e) => setName(e.target.value)} />
```

## 🔴 यह क्यों बना? (Hindi)
AngularJS (1.x) जैसे frameworks automatic two-way binding (`ng-model`) इस्तेमाल करते थे। Forms के लिए यह आसान लगता था, पर बड़े apps में shared data को कोई भी component कहीं से भी बदल सकता था, और पता करना मुश्किल था कि किसने क्या कब बदला। Updates की श्रृंखला debug करना दर्दनाक हो गया, और performance भी गिरती थी (dirty checking)।

React ने **साफ, one-way flow** चुना: data नीचे, events ऊपर। Form inputs के लिए दोनों दिशाएँ आप हाथ से जोड़ते हैं, इसलिए हर बदलाव एक handler से गुज़रता है जहाँ आप validate, transform या reject कर सकते हैं।

---

## 🟢 How it Works — Step by Step

```
Direction 1 (data → UI):  <input value={name} />
Direction 2 (UI → data):  onChange={e => setName(e.target.value)}

Step 1 → State holds the value:               const [name, setName] = useState('')
Step 2 → Render: input shows `name`           (data → UI)
Step 3 → User types "A" → browser fires an input event
Step 4 → React calls onChange with the synthetic event
Step 5 → Handler reads e.target.value and calls setName("A")   (UI → data)
Step 6 → React re-renders; input shows "A" because value={name}
Step 7 → Any other component using `name` re-renders with "A" too (live preview)

Result: looks like two-way binding, but the loop is explicit:
        state → UI → event → handler → state → UI
Because the handler is yours, you can change the value in between (trim, uppercase, limit length).
```

## 🟢 कैसे काम करता है? (Hindi)
```
दिशा 1 (data → UI):  <input value={name} />
दिशा 2 (UI → data):  onChange={e => setName(e.target.value)}

Step 1 → State value रखती है:                 const [name, setName] = useState('')
Step 2 → Render: input `name` दिखाता है        (data → UI)
Step 3 → User "A" लिखता है → browser input event चलाता है
Step 4 → React synthetic event के साथ onChange call करता है
Step 5 → Handler e.target.value पढ़कर setName("A") करता है   (UI → data)
Step 6 → React re-render करता है; value={name} होने से input "A" दिखाता है
Step 7 → `name` इस्तेमाल करने वाले दूसरे components भी "A" के साथ re-render होते हैं (live preview)

नतीजा: दिखता two-way binding जैसा है, पर loop साफ है:
        state → UI → event → handler → state → UI
Handler आपका है, इसलिए बीच में value बदल सकते हैं (trim, uppercase, length limit)।
```

---

## 🟡 Real World Example
**Amazon checkout coupon box and order summary:** The user types a coupon code in an input. The input shows what they type (UI → state), and the code is shown in uppercase in the "Apply" button label and a live "Code: SAVE20" preview in the order summary (state → UI). The handler converts the text to uppercase and removes spaces before saving, which would not be possible if the DOM changed the data directly. Another case is a Flipkart filter price slider and a number input that show the same value and update each other.

## 🟡 Real Example Hindi mein
**Amazon checkout coupon box और order summary:** User input में coupon code लिखता है। Input वही दिखाता है जो वह लिखता है (UI → state), और code "Apply" button के label और order summary के live "Code: SAVE20" preview में बड़े अक्षरों में दिखता है (state → UI)। Handler save करने से पहले text को uppercase करता है और spaces हटाता है, जो तब संभव नहीं होता अगर DOM सीधे data बदलता। दूसरा उदाहरण Flipkart का price slider और number input है, जो एक ही value दिखाते हैं और एक-दूसरे को update करते हैं।

---

## 💻 Code Example — Basic

```jsx
// Basic: "two-way" binding built from value + onChange
import { useState } from 'react';                    // state hook
import { createRoot } from 'react-dom/client';       // React 18/19 root API

function CouponBox() {
  const [code, setCode] = useState('');              // single source of truth

  return (
    <div>
      <input
        value={code}                                 // direction 1: state → input
        onChange={(e) => setCode(e.target.value)}    // direction 2: input → state
        placeholder="Coupon code"
      />
      <p>Preview: {code}</p>                         {/* another view of the same state updates live */}
      <button onClick={() => setCode('')}>Clear</button> {/* changing state from code updates the input */}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<CouponBox />); // mount
```

## 💻 Code Example — Advanced

```jsx
// Advanced: a reusable useBinding hook, transform in the handler, and two controls bound to ONE state
import { useState, useCallback } from 'react';       // hooks
import { createRoot } from 'react-dom/client';       // React 18/19 root API

// Custom hook: returns { value, onChange } so you can spread it into an input like a "v-model"
function useBinding(initial = '', transform = (v) => v) {
  const [value, setValue] = useState(initial);       // the state
  const onChange = useCallback(
    (e) => setValue(transform(e.target.value)),      // apply the transform BEFORE saving
    [transform]                                      // transform must be stable (defined outside components)
  );
  return { value, onChange, set: setValue };         // set lets code update the value too
}

const toCoupon = (v) => v.toUpperCase().replace(/\s/g, '').slice(0, 10); // uppercase, no spaces, max 10 chars
const toNumber = (v) => v.replace(/\D/g, '');        // keep digits only

function Checkout() {
  const coupon = useBinding('', toCoupon);           // bound text value with a transform
  const [price, setPrice] = useState(500);           // ONE state shared by two controls

  return (
    <div>
      <input {...coupon} placeholder="Coupon" />     {/* spreads value + onChange (extra "set" key is ignored? see note) */}
      <p>Code: {coupon.value || '-'}</p>

      <h4>Max price: ₹{price}</h4>
      {/* two different controls bound to the same state: they stay in sync automatically */}
      <input type="range" min="0" max="5000" step="100" value={price} onChange={(e) => setPrice(Number(e.target.value))} />
      <input
        value={price}
        inputMode="numeric"
        onChange={(e) => setPrice(Number(toNumber(e.target.value)))}
      />
    </div>
  );
}

createRoot(document.getElementById('root')).render(<Checkout />);
// NOTE: <input {...coupon}> also passes the "set" prop to the DOM and React warns about an unknown prop.
// In real code return only { value, onChange } for spreading, and expose "set" via a separate property
// (or destructure it before spreading): const { set, ...bind } = coupon; <input {...bind} />
```

---

## 🟠 Next.js Connection
Binding works the same in Next.js, but only in **Client Components** because it needs state and `onChange`. A neat Next.js variant is binding an input to the **URL**: `searchParams` becomes the state. The input updates the URL (UI → URL), and the server page reads the URL (URL → UI), which makes searches shareable and refresh-safe.

```jsx
// app/search/SearchBox.jsx
'use client';                                        // needs hooks
import { useRouter, useSearchParams } from 'next/navigation'; // App Router hooks
import { useState } from 'react';

export default function SearchBox() {
  const router = useRouter();                        // to change the URL
  const params = useSearchParams();                  // read the current URL
  const [q, setQ] = useState(params.get('q') ?? ''); // start from the URL value

  function submit(e) {
    e.preventDefault();                              // no full page reload
    router.push(`/search?q=${encodeURIComponent(q)}`); // UI → URL
  }

  return (
    <form onSubmit={submit}>
      <input value={q} onChange={(e) => setQ(e.target.value)} /> {/* two-way with local state */}
      <button>Search</button>
    </form>
  );
}
```

```jsx
// app/search/page.jsx (Server Component) reads the URL and renders results on the server
export default async function Page({ searchParams }) {
  const { q = '' } = await searchParams;             // Next.js 15+: Promise (Next.js 14: plain object)
  return <h2>Results for: {q}</h2>;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Binding only one direction (`value` without `onChange`)
✅ **Correct:** Always wire both directions

```jsx
// Wrong: data → UI only, the user cannot change it
<input value={name} />                               // ❌ read-only

// Right
<input value={name} onChange={(e) => setName(e.target.value)} /> // ✅
```

❌ **Mistake 2:** Using the wrong event property for the input type
✅ **Correct:** Text uses `e.target.value`, checkboxes use `e.target.checked`

```jsx
// Wrong: value of a checkbox is the static string "on", so the state is always "on"
<input type="checkbox" checked={agree} onChange={(e) => setAgree(e.target.value)} /> // ❌

// Right
<input type="checkbox" checked={agree} onChange={(e) => setAgree(e.target.checked)} /> // ✅ boolean
```

❌ **Mistake 3:** Trying to share one value by mutating it from two places
✅ **Correct:** Keep one state and let every control read and write it

```jsx
// Wrong: two copies drift apart
const [sliderValue, setSliderValue] = useState(10);
const [inputValue, setInputValue] = useState(10);    // ❌ duplicated

// Right: one source of truth
const [value, setValue] = useState(10);              // ✅ both controls use value/setValue
```

---

## 🧠 Tricky Interview Question

```jsx
import { useState } from 'react';

function App() {
  const [text, setText] = useState('');
  return (
    <input
      value={text}
      onChange={(e) => setText(e.target.value.trim())}  // trim on every change
    />
  );
}
// The user tries to type "hello world". What ends up in the input?
```
**Answer:** `helloworld`. Every time the user types a space at the end, `e.target.value` is `"hello "`, `.trim()` makes it `"hello"`, and React writes `"hello"` back into the input, so the space disappears and the user can never type a space between words (then `w` is appended to `hello`). This shows the power of the explicit handler (it can transform input) and the danger. Trim at **submit** time, not on every keystroke. For masks (phone, card number) transform carefully and keep the caret position in mind.

---

## ⚫ Interview Questions + Answers

Q1: Does React support two-way data binding?
A1: Not built-in. React has one-way data flow (parent to child through props). For form inputs you imitate two-way binding with controlled components: `value` pulls the state into the input, and `onChange` pushes the user's changes back to state.

Q2: Why did React choose one-way flow?
A2: It makes data changes predictable and traceable: state is changed only through setters, in known places. Two-way automatic binding makes it hard to know what changed a value and can create update cycles. One-way flow also makes debugging and performance reasoning simpler.

Q3: What is the difference between React's approach and Angular's `ngModel` or Vue's `v-model`?
A3: In Angular/Vue, a directive keeps the model and the input in sync for you. In React you write the handler yourself (or a custom hook), which is more code but gives full control to validate or transform the value. Vue's `v-model` is sugar for `:value` + `@input`; React's pattern is the same idea but explicit.

Q4: How would you build a reusable binding helper?
A4: Create a custom hook such as `useInput(initial)` that returns `{ value, onChange }` and spread it onto inputs, or use a form library. Keep the returned object limited to valid DOM props.

Q5: How does a child component update parent state in this model?
A5: The parent passes a callback prop (`onChange`, `setValue`). The child calls it with the new value. This "data down, events up" pattern is the component-level version of the same two-way loop.

---

## 🔷 When to Use + When Not to Use
✅ **Use this value + onChange pattern when:**
- Several UI parts must show or edit the same value (input + slider + preview)
- You need to validate, format or limit input as the user types
- The value must be changed from code (reset, autofill, suggestions)

❌ **Avoid (use uncontrolled / refs) when:**
- You only need the value once on submit
- A huge form re-renders slowly on every keystroke
- The element is a file input (cannot be bound)

---

## 📊 Visual Diagram

```
          ┌────────────────────── React "two-way" loop ───────────────────────┐
          │                                                                   │
   ┌──────▼───────┐     render      ┌───────────────┐   user types   ┌────────┴───────┐
   │ state: name  │ ──────────────► │ <input        │ ─────────────► │ onChange(e)    │
   │  "Aman"      │  value={name}   │  value=Aman/> │   "Amani"      │ setName(...)   │
   └──────────────┘  (data → UI)    └───────────────┘                └────────┬───────┘
          ▲                                                    (UI → data)    │
          └────────────────────────────────────────────────────────────────────┘
                     handler can validate / transform in the middle

 Angular/Vue:  model ⇄ input (framework syncs automatically, hidden)
 React:        model → input (value), input → model (onChange), both visible in your code

 Performance: every keystroke = one state update + one render of the owner component.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Two-way binding | Data and UI update each other automatically | Data और UI एक-दूसरे को अपने आप update करें |
| One-way data flow | Data moves parent → child only | Data सिर्फ parent से child की ओर |
| value | Prop that sets the input from state | State से input सेट करने वाला prop |
| onChange | Event that sends input changes to state | Input के बदलाव state तक भेजने वाला event |
| ngModel / v-model | Angular / Vue two-way binding directives | Angular / Vue के two-way binding directives |
| Source of truth | One place that owns the value | वह एक जगह जो value की owner है |
| Transform | Change the input before saving it | Save से पहले input बदलना |
| Custom hook | Reusable function using hooks (useInput) | Hooks वाला reusable function |

---

## ⚡ 3-Line Summary
**English:**
1. React is one-way; "two-way binding" is built manually with `value` (state → UI) and `onChange` (UI → state).
2. The explicit handler lets you validate or transform input, but only trim or format at the right moment (not every keystroke).
3. In Next.js do it in Client Components, or bind inputs to the URL with `searchParams` for shareable state.

**Hindi:**
1. React one-way है; "two-way binding" हाथ से `value` (state → UI) और `onChange` (UI → state) से बनती है।
2. साफ handler से input को validate या transform कर सकते हैं, पर trim या format सही समय पर करो (हर keystroke पर नहीं)।
3. Next.js में यह Client Components में करो, या shareable state के लिए inputs को `searchParams` के ज़रिए URL से bind करो।

---

## ➡️ Next Topic
**31. React Fragments (<> </>)** — JSX में एक component को एक ही root element लौटाना होता है। अगला topic बताता है कि फालतू `div` डाले बिना कई elements कैसे return करें।
