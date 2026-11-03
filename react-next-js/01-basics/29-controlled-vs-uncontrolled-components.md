# 29. Controlled vs Uncontrolled Components
# हिंदी में: Controlled बनाम Uncontrolled Components

---

## 🔵 Simple Definition (English)
A **controlled component** is a form element whose value is stored in React state (`value` + `onChange`), so React is the source of truth. An **uncontrolled component** keeps its value inside the DOM, and you read it only when needed (with a `ref` or `FormData`), using `defaultValue` for the starting value.

## 🔵 सरल परिभाषा (Hindi)
**Controlled component** वह form element है जिसकी value React state में रहती है (`value` + `onChange`), यानी React ही सच्चाई का स्रोत है। **Uncontrolled component** अपनी value DOM के अंदर रखता है, और आप उसे ज़रूरत पर (`ref` या `FormData` से) पढ़ते हैं; शुरुआती value के लिए `defaultValue` इस्तेमाल होती है।

---

## 🔴 Problem it Solves

A form element can have two owners of its value: the DOM (native behavior) and React (your state). If this is not clear, you get bugs: the value does not update, the form cannot be reset from code, validation lags, or React warns about switching from uncontrolled to controlled.

The two patterns give a clear rule. Pick **one owner per input**. Use controlled when the UI must react to every change; use uncontrolled when you just need the final value and want less code and fewer renders.

## 🔴 यह क्यों बना? (Hindi)
Form element की value के दो owner हो सकते हैं: DOM (native व्यवहार) और React (आपकी state)। यह साफ न हो तो bugs आते हैं: value update नहीं होती, form को code से reset नहीं कर पाते, validation पीछे रहती है, या React uncontrolled से controlled में बदलने की warning देता है।

दोनों patterns एक साफ नियम देते हैं: **हर input का एक ही owner चुनो।** जब UI को हर बदलाव पर प्रतिक्रिया देनी हो तब controlled; जब सिर्फ अंतिम value चाहिए और कम code व कम renders चाहिए तब uncontrolled।

---

## 🟢 How it Works — Step by Step

```
CONTROLLED
Step 1 → const [q, setQ] = useState('')
Step 2 → <input value={q} onChange={e => setQ(e.target.value)} />
Step 3 → Each key press: onChange → setQ → re-render → React writes q into the input
Step 4 → React state always equals what the screen shows

UNCONTROLLED
Step 1 → const ref = useRef(null)
Step 2 → <input ref={ref} defaultValue="Pizza" />
Step 3 → Typing is handled by the browser, React is not involved (no re-render)
Step 4 → When needed (submit): ref.current.value  or  new FormData(form)

SPECIAL CASE
<input type="file" /> is ALWAYS uncontrolled (value is read-only for security).

RULES
- Never give both value and defaultValue to the same input.
- value must never be undefined/null on a controlled input (use '' not undefined).
```

## 🟢 कैसे काम करता है? (Hindi)
```
CONTROLLED
Step 1 → const [q, setQ] = useState('')
Step 2 → <input value={q} onChange={e => setQ(e.target.value)} />
Step 3 → हर key press: onChange → setQ → re-render → React q को input में लिखता है
Step 4 → React state हमेशा वही होती है जो screen पर दिखता है

UNCONTROLLED
Step 1 → const ref = useRef(null)
Step 2 → <input ref={ref} defaultValue="Pizza" />
Step 3 → Typing browser संभालता है, React शामिल नहीं (कोई re-render नहीं)
Step 4 → ज़रूरत पर (submit): ref.current.value  या  new FormData(form)

SPECIAL CASE
<input type="file" /> हमेशा uncontrolled होता है (security के कारण value read-only है)।

नियम
- एक ही input को value और defaultValue दोनों मत दो।
- Controlled input की value कभी undefined/null न हो ('' इस्तेमाल करो)।
```

---

## 🟡 Real World Example
**Zomato search vs. feedback form:** The search box is **controlled**: on every letter the app filters restaurants, shows suggestions and a clear (X) button, and the text can be set from code (clicking a recent search fills the box). The "Rate your order" feedback form with a long comment box is fine as **uncontrolled**: nobody needs the text until the user presses Submit. A profile photo upload is always **uncontrolled** (file input).

## 🟡 Real Example Hindi mein
**Zomato search बनाम feedback form:** Search box **controlled** है: हर अक्षर पर app restaurants filter करता है, suggestions और clear (X) button दिखाता है, और text code से भी set हो सकता है (recent search पर click करने से box भर जाता है)। लंबे comment box वाला "Rate your order" feedback form **uncontrolled** हो सकता है: Submit दबाने तक किसी को text नहीं चाहिए। Profile photo upload हमेशा **uncontrolled** है (file input)।

---

## 💻 Code Example — Basic

```jsx
// Basic: the same field written both ways
import { useState, useRef } from 'react';            // state + ref hooks
import { createRoot } from 'react-dom/client';       // React 18/19 root API

function Controlled() {
  const [city, setCity] = useState('');              // React owns the value
  return (
    <div>
      <input value={city} onChange={(e) => setCity(e.target.value)} placeholder="City (controlled)" />
      <p>You typed: {city}</p>                       {/* live preview works because state is current */}
      <button onClick={() => setCity('')}>Clear</button> {/* easy to reset from code */}
    </div>
  );
}

function Uncontrolled() {
  const cityRef = useRef(null);                      // ref points to the real DOM input
  function show() {
    alert(cityRef.current.value);                    // read the value only when needed
  }
  return (
    <div>
      <input ref={cityRef} defaultValue="Delhi" placeholder="City (uncontrolled)" /> {/* defaultValue = initial only */}
      <button onClick={show}>Show value</button>
    </div>
  );
}

createRoot(document.getElementById('root')).render(
  <>
    <Controlled />
    <Uncontrolled />
  </>
);
```

## 💻 Code Example — Advanced

```jsx
// Advanced: uncontrolled form read through FormData (fast, scalable) + a controlled search field with debounce-free filtering
import { useState, useRef } from 'react';            // hooks
import { createRoot } from 'react-dom/client';       // React 18/19 root API

const CITIES = ['Delhi', 'Mumbai', 'Bengaluru', 'Chennai', 'Kolkata', 'Pune', 'Hyderabad'];

// 1) Controlled: filtering while typing needs the value on every key press
function CitySearch() {
  const [q, setQ] = useState('');                    // controlled value
  const results = CITIES.filter((c) => c.toLowerCase().includes(q.toLowerCase())); // derived list
  return (
    <div>
      <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search city" />
      {q && <button onClick={() => setQ('')}>✕</button>} {/* clear button: only possible with state */}
      <ul>{results.map((c) => <li key={c}>{c}</li>)}</ul>
    </div>
  );
}

// 2) Uncontrolled: a big feedback form, values read once on submit (0 renders while typing)
function FeedbackForm() {
  const formRef = useRef(null);                      // lets us reset the form
  const [submitted, setSubmitted] = useState(null);  // only ONE state: the final result

  function handleSubmit(e) {
    e.preventDefault();                              // no page reload
    const data = Object.fromEntries(new FormData(e.currentTarget)); // { rating, comment, subscribe, photo }
    setSubmitted({ ...data, photo: data.photo?.name ?? 'none' }); // File object → show only its name
    formRef.current.reset();                         // DOM reset resets uncontrolled fields to defaultValue
  }

  return (
    <form ref={formRef} onSubmit={handleSubmit}>
      <select name="rating" defaultValue="5">        {/* defaultValue works on select too */}
        {[5, 4, 3, 2, 1].map((n) => <option key={n} value={n}>{n} stars</option>)}
      </select>
      <textarea name="comment" defaultValue="" placeholder="Tell us more" />
      <label><input type="checkbox" name="subscribe" defaultChecked /> Send offers</label> {/* defaultChecked, not checked */}
      <input type="file" name="photo" accept="image/*" /> {/* always uncontrolled */}
      <button type="submit">Send</button>
      {submitted && <pre>{JSON.stringify(submitted, null, 2)}</pre>}
    </form>
  );
}

createRoot(document.getElementById('root')).render(
  <>
    <CitySearch />
    <FeedbackForm />
  </>
);
```

---

## 🟠 Next.js Connection
Server Actions fit the **uncontrolled** style naturally: the form passes `FormData` to the server function, so you do not need `useState` for each field, and the form works before hydration. Use controlled inputs only in Client Components where the UI needs live reactions (search suggestions, live preview). Libraries like React Hook Form are mostly uncontrolled and work well in Next.js Client Components.

```jsx
// app/feedback/actions.js
'use server';                                        // runs on the server

export async function sendFeedback(formData) {
  const rating = Number(formData.get('rating'));     // uncontrolled value arrives in FormData
  const comment = String(formData.get('comment') ?? '');
  // await db.feedback.create({ data: { rating, comment } });
  console.log('feedback', rating, comment.length);   // server log
}
```

```jsx
// app/feedback/page.jsx  (Server Component, no useState at all)
import { sendFeedback } from './actions';

export default function Page() {
  return (
    <form action={sendFeedback}>                     {/* uncontrolled fields + Server Action */}
      <select name="rating" defaultValue="5"><option value="5">5</option><option value="1">1</option></select>
      <textarea name="comment" defaultValue="" />
      <button type="submit">Send</button>
    </form>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Switching from uncontrolled to controlled (value starts as `undefined`)
✅ **Correct:** Always initialize with a defined value such as `''`

```jsx
// Wrong: React warns "changing an uncontrolled input to be controlled"
const [name, setName] = useState();                  // ❌ undefined
<input value={name} onChange={(e) => setName(e.target.value)} />

// Right
const [name, setName] = useState('');                // ✅ always a string
```

❌ **Mistake 2:** Using `value` for an uncontrolled input's starting value
✅ **Correct:** Use `defaultValue` / `defaultChecked`

```jsx
// Wrong: input becomes read-only (controlled without onChange)
<input value="Delhi" />                              // ❌

// Right
<input defaultValue="Delhi" />                       // ✅ user can edit
<input type="checkbox" defaultChecked />             // ✅ for checkboxes
```

❌ **Mistake 3:** Trying to control a file input
✅ **Correct:** Read files from the input ref or `e.target.files`

```jsx
// Wrong: setting value on a file input throws an error
<input type="file" value={file} />                   // ❌ InvalidStateError

// Right
<input type="file" onChange={(e) => setFile(e.target.files[0])} /> // ✅ keep the File object in state if needed
```

---

## 🧠 Tricky Interview Question

```jsx
import { useState } from 'react';

function App() {
  const [text, setText] = useState();                // note: no initial value
  return (
    <input
      value={text}
      onChange={(e) => setText(e.target.value)}
    />
  );
}
// What happens on the first key press?
```
**Answer:** The input works, but React logs a warning in development: "A component is changing an uncontrolled input to be controlled." On the first render `value` is `undefined`, so React treats the input as **uncontrolled**. After the first key press `text` becomes a string, so the same input is suddenly **controlled**. React does not support switching modes during the life of an input because the DOM and React could disagree. Fix: `useState('')`. Similarly, going controlled → uncontrolled (setting the value to `undefined` or `null`) gives the opposite warning.

---

## ⚫ Interview Questions + Answers

Q1: What is a controlled component?
A1: A form element whose value is supplied by React state through `value` and updated through `onChange`. React is the single source of truth, so you can validate, format and reset the value at any time.

Q2: What is an uncontrolled component?
A2: A form element that keeps its own value in the DOM. You set the initial value with `defaultValue` and read the current value with a ref (`ref.current.value`) or `FormData` when needed. It involves less code and no re-render per keystroke.

Q3: Which should you prefer?
A3: Default to controlled when UI depends on the value (live validation, search, dependent fields). Choose uncontrolled for simple forms, big forms, file inputs and Server Actions. Mixing both in one form is fine, but never for the same input.

Q4: How do you reset each type?
A4: Controlled: set the state to its initial value. Uncontrolled: call `form.reset()` (returns to `defaultValue`), or change the input's `key` to remount it.

Q5: Is the `<input type="file">` controlled or uncontrolled?
A5: Always uncontrolled. Its value is read-only because of browser security rules. You read `e.target.files` in `onChange` or from a ref, and you can keep the `File` in state.

---

## 🔷 When to Use + When Not to Use
✅ **Use controlled when:**
- Validating or formatting while typing (phone mask, uppercase)
- Disabling or showing UI based on the value (submit button, character counter)
- Inputs depend on each other or must be set from code

✅ **Use uncontrolled when:**
- You only need values on submit (feedback forms, Server Actions)
- The form is large and per-key renders are costly
- Integrating with non-React code or file inputs

❌ **Avoid:**
- Controlled inputs with no `onChange` (frozen field)
- Mixing `value` and `defaultValue` on one input
- Putting every field of a huge form into separate `useState` calls without measuring

---

## 📊 Visual Diagram

```
 CONTROLLED                              UNCONTROLLED
 keystroke                               keystroke
    │                                       │
    ▼                                       ▼
 onChange(e) ──► setState(v)             browser updates DOM value
    │                │                      (React does nothing)
    │                ▼                         │
    │          React re-renders                │ later: submit / button
    │                │                         ▼
    └── value={state} written back        ref.current.value  /  new FormData(form)

 Source of truth:  React state            Source of truth:  the DOM
 Renders per key:  1                      Renders per key:  0
 Set from code:    easy (setState)        ref.current.value = x  or  form.reset()
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Controlled | Value held in React state | Value React state में |
| Uncontrolled | Value held in the DOM | Value DOM में |
| defaultValue | Initial value of an uncontrolled input | Uncontrolled input की शुरुआती value |
| defaultChecked | Initial checked state for checkbox/radio | Checkbox/radio की शुरुआती checked स्थिति |
| ref | Handle to read the real DOM node | असली DOM node तक पहुँचने का handle |
| FormData | Collects all named fields of a form | Form की सभी named fields इकट्ठा करता है |
| Source of truth | The place that owns the real value | वह जगह जिसके पास असली value है |
| Single owner | Only React or the DOM owns an input, not both | Input का owner React या DOM, दोनों नहीं |

---

## ⚡ 3-Line Summary
**English:**
1. Controlled inputs store their value in React state (`value` + `onChange`); uncontrolled inputs keep it in the DOM (`defaultValue` + ref/FormData).
2. Use controlled for live UI reactions and uncontrolled for simple, large or file-based forms; never switch one input between modes.
3. Server Actions in Next.js fit uncontrolled forms; use controlled only in Client Components that need live feedback.

**Hindi:**
1. Controlled inputs अपनी value React state में रखते हैं (`value` + `onChange`); uncontrolled inputs उसे DOM में रखते हैं (`defaultValue` + ref/FormData)।
2. Live UI प्रतिक्रिया के लिए controlled और सरल, बड़े या file वाले forms के लिए uncontrolled इस्तेमाल करो; किसी input को कभी mode बदलने मत दो।
3. Next.js के Server Actions uncontrolled forms से मेल खाते हैं; controlled सिर्फ वहाँ जहाँ Client Component को live feedback चाहिए।

---

## ➡️ Next Topic
**30. Two-Way Data Binding** — Controlled input में state और UI हमेशा जुड़े दिखते हैं, जो Angular/Vue के two-way binding जैसा लगता है। अगला topic बताता है कि React में यह असल में कैसे चलता है और React इसे one-way क्यों कहता है।
