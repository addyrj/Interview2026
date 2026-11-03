# 28. Forms in React
# हिंदी में: React में Forms — Input, Submit और Validation

---

## 🔵 Simple Definition (English)
A **form** in React collects user input and sends it somewhere. You can handle it in two ways: keep each field in state (**controlled**) and read it on submit, or let the DOM keep the values and read them with `FormData` or a ref (**uncontrolled**). Submit is handled with `onSubmit` plus `e.preventDefault()`, or in React 19 with a form `action`.

## 🔵 सरल परिभाषा (Hindi)
React में **form** user का input इकट्ठा करके कहीं भेजता है। इसे दो तरीकों से संभाल सकते हैं: हर field को state में रखो (**controlled**) और submit पर पढ़ो, या DOM को values रखने दो और `FormData` या ref से पढ़ो (**uncontrolled**)। Submit `onSubmit` और `e.preventDefault()` से संभलता है, या React 19 में form `action` से।

---

## 🔴 Problem it Solves

HTML forms keep their own state in the DOM, and by default submitting reloads the whole page. In a React app you need to validate while typing, disable the button while the request runs, show server errors and keep the user on the page. If React and the DOM both think they own the value, they get out of sync (the classic "I typed but state is empty").

A clear approach to who owns the value (React state or the DOM), and a defined submit flow, solves this.

## 🔴 यह क्यों बना? (Hindi)
HTML forms अपनी state DOM में रखते हैं और default में submit पूरे page को reload कर देता है। React app में आपको typing के समय validate करना, request चलते समय button disable करना, server errors दिखाना और user को उसी page पर रखना होता है। अगर React और DOM दोनों खुद को value का owner समझें, तो वे out of sync हो जाते हैं (क्लासिक "मैंने type किया पर state खाली है")।

यह तय करना कि value का owner कौन है (React state या DOM) और submit का साफ flow होना, यही हल है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Render <form onSubmit={handleSubmit}> with inputs (each with a name)
Step 2 → Decide ownership per field:
         Controlled:   value={state} + onChange={update state}
         Uncontrolled: no value, read at submit with new FormData(e.currentTarget)
Step 3 → User types: onChange fires → setState → re-render → input shows the new value
Step 4 → User presses Enter or clicks a type="submit" button → onSubmit fires
Step 5 → handleSubmit calls e.preventDefault() to stop the page reload
Step 6 → Validate the data (client side), show errors, stop if invalid
Step 7 → Send to the server (fetch / Server Action), keep a "submitting" flag
Step 8 → On success reset or navigate; on failure show the error

React 19 alternative: <form action={fn}> + useActionState + useFormStatus
(fn receives FormData; form fields reset automatically after a successful action)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → <form onSubmit={handleSubmit}> render करो, हर input में name हो
Step 2 → हर field का owner तय करो:
         Controlled:   value={state} + onChange={state update}
         Uncontrolled: value नहीं, submit पर new FormData(e.currentTarget) से पढ़ो
Step 3 → User type करता है: onChange चलता है → setState → re-render → input नई value दिखाता है
Step 4 → User Enter दबाता है या type="submit" button click करता है → onSubmit चलता है
Step 5 → handleSubmit e.preventDefault() call करके page reload रोकता है
Step 6 → Data validate करो (client side), errors दिखाओ, invalid हो तो रुको
Step 7 → Server को भेजो (fetch / Server Action), "submitting" flag रखो
Step 8 → सफल होने पर reset या navigate; fail होने पर error दिखाओ

React 19 विकल्प: <form action={fn}> + useActionState + useFormStatus
(fn को FormData मिलता है; सफल action के बाद form fields अपने आप reset होते हैं)
```

---

## 🟡 Real World Example
**Zomato / Swiggy login with OTP:** The user enters a 10-digit phone number. The button stays disabled until the number is valid. On submit the button shows "Sending OTP..." and cannot be clicked twice. If the server says "number not registered", the error appears under the input and the typed number stays. Another case: the checkout address form validates the PIN code (6 digits) when the user leaves the field, and shows all errors again on submit.

## 🟡 Real Example Hindi mein
**Zomato / Swiggy OTP login:** User 10 अंकों का phone number डालता है। Number valid होने तक button disabled रहता है। Submit पर button "Sending OTP..." दिखाता है और दो बार click नहीं हो सकता। अगर server कहे "number registered नहीं है", तो error input के नीचे दिखती है और डाला हुआ number बना रहता है। दूसरा उदाहरण: checkout address form में PIN code (6 अंक) field छोड़ते समय validate होता है, और submit पर सारी errors फिर दिखती हैं।

---

## 💻 Code Example — Basic

```jsx
// Basic: controlled login form with submit handling
import { useState } from 'react';                    // state hook
import { createRoot } from 'react-dom/client';       // React 18/19 root API

function LoginForm() {
  const [email, setEmail] = useState('');            // field 1 lives in state
  const [password, setPassword] = useState('');      // field 2 lives in state

  function handleSubmit(e) {
    e.preventDefault();                              // stop the browser from reloading the page
    console.log('Submitting', { email, password });  // in real code: send to the server
  }

  return (
    <form onSubmit={handleSubmit}>                   {/* Enter key and submit button both trigger this */}
      <label htmlFor="email">Email</label>           {/* htmlFor (not "for") links label to input */}
      <input
        id="email"
        type="email"
        value={email}                                // React owns the value
        onChange={(e) => setEmail(e.target.value)}   // update state on every keystroke
        required                                     // built-in browser validation still works
      />
      <label htmlFor="password">Password</label>
      <input
        id="password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        minLength={6}
        required
      />
      <button type="submit">Login</button>           {/* type="submit" is the default inside a form */}
    </form>
  );
}

createRoot(document.getElementById('root')).render(<LoginForm />); // mount
```

## 💻 Code Example — Advanced

```jsx
// Advanced: one state object, one generic handler, validation, touched fields, async submit with status
import { useState } from 'react';                    // state hook
import { createRoot } from 'react-dom/client';       // React 18/19 root API

// validation is a pure function: easy to test, no state inside
function validate(v) {
  const errors = {};                                 // collect messages by field name
  if (!/^[6-9]\d{9}$/.test(v.phone)) errors.phone = 'Enter a valid 10-digit mobile number';
  if (!/^\d{6}$/.test(v.pin)) errors.pin = 'PIN code must be 6 digits';
  if (v.address.trim().length < 10) errors.address = 'Address is too short';
  return errors;                                     // empty object = valid
}

function AddressForm() {
  const [values, setValues] = useState({ phone: '', pin: '', address: '' }); // all fields in one object
  const [touched, setTouched] = useState({});        // which fields the user has left (blur)
  const [status, setStatus] = useState('idle');      // idle | submitting | success | error
  const [serverError, setServerError] = useState(''); // message from the server

  const errors = validate(values);                   // DERIVED during render, never stored in state
  const isValid = Object.keys(errors).length === 0;  // derived too

  function handleChange(e) {
    const { name, value } = e.target;                // name attribute decides which key to update
    setValues((v) => ({ ...v, [name]: value }));     // computed property name, immutable update
  }

  function handleBlur(e) {
    const { name } = e.target;                       // mark this field as visited
    setTouched((t) => ({ ...t, [name]: true }));
  }

  async function handleSubmit(e) {
    e.preventDefault();                              // no page reload
    setTouched({ phone: true, pin: true, address: true }); // reveal all errors on submit
    if (!isValid || status === 'submitting') return; // block invalid and double submits
    setStatus('submitting');                         // disable the button, show progress
    setServerError('');
    try {
      const res = await fetch('/api/address', {      // send JSON to a route handler
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values),
      });
      if (!res.ok) throw new Error((await res.json()).message ?? 'Request failed');
      setStatus('success');
    } catch (err) {
      setServerError(err.message);                   // show the server's message
      setStatus('error');                            // keep typed values so the user can retry
    }
  }

  // small helper: show the error only after the field was touched
  const err = (name) => touched[name] && errors[name];

  return (
    <form onSubmit={handleSubmit} noValidate>        {/* noValidate: we show our own messages */}
      {['phone', 'pin'].map((name) => (
        <div key={name}>
          <input
            name={name}                              // used by handleChange
            value={values[name]}
            onChange={handleChange}
            onBlur={handleBlur}
            placeholder={name === 'phone' ? 'Mobile number' : 'PIN code'}
            inputMode="numeric"                      // numeric keyboard on mobile
            aria-invalid={Boolean(err(name))}        // accessibility: marks the invalid field
          />
          {err(name) && <small role="alert" style={{ color: 'crimson' }}>{errors[name]}</small>}
        </div>
      ))}
      <textarea name="address" value={values.address} onChange={handleChange} onBlur={handleBlur} placeholder="Address" />
      {err('address') && <small role="alert" style={{ color: 'crimson' }}>{errors.address}</small>}

      <button type="submit" disabled={status === 'submitting'}>
        {status === 'submitting' ? 'Saving...' : 'Save address'}
      </button>
      {serverError && <p role="alert">{serverError}</p>}
      {status === 'success' && <p>Address saved</p>}
    </form>
  );
}

createRoot(document.getElementById('root')).render(<AddressForm />);
```

---

## 🟠 Next.js Connection
The App Router lets you submit forms to a **Server Action**: a function marked with `'use server'`. The form works even before JavaScript loads (progressive enhancement), and you avoid writing a separate API route. Combine it with `useActionState` (React 19) for validation messages and `useFormStatus` for a pending button. In Next.js 14 (React 18 canary) the hook was called `useFormState` from `react-dom`; it is `useActionState` from `react` in Next.js 15 / React 19 (version-dependent).

```jsx
// app/address/actions.js
'use server';                                        // everything exported here runs only on the server

export async function saveAddress(prevState, formData) {
  const pin = String(formData.get('pin') ?? '');     // read a field by its name attribute
  if (!/^\d{6}$/.test(pin)) {
    return { ok: false, message: 'PIN code must be 6 digits' }; // returned to the client as state
  }
  // await db.address.create({ data: { pin } });     // save to your database here
  return { ok: true, message: 'Saved' };
}
```

```jsx
// app/address/AddressForm.jsx
'use client';                                        // hooks need a Client Component
import { useActionState } from 'react';              // React 19 / Next.js 15
import { useFormStatus } from 'react-dom';           // pending state of the parent form
import { saveAddress } from './actions';

function SubmitButton() {
  const { pending } = useFormStatus();               // must be used in a component INSIDE the form
  return <button disabled={pending}>{pending ? 'Saving...' : 'Save'}</button>;
}

export default function AddressForm() {
  const [state, formAction] = useActionState(saveAddress, { ok: false, message: '' }); // state + action
  return (
    <form action={formAction}>                       {/* no onSubmit, no preventDefault needed */}
      <input name="pin" placeholder="PIN code" />    {/* uncontrolled: FormData reads it */}
      <SubmitButton />
      {state.message && <p>{state.message}</p>}
    </form>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting `e.preventDefault()` in `onSubmit`
✅ **Correct:** Always prevent the default page reload (unless you use a form `action`)

```jsx
// Wrong: page reloads, all state is lost
<form onSubmit={() => sendData()}>...</form>         // ❌

// Right
<form onSubmit={(e) => { e.preventDefault(); sendData(); }}>...</form> // ✅
```

❌ **Mistake 2:** Setting `value` without `onChange` (read-only input)
✅ **Correct:** Pair `value` with `onChange`, or use `defaultValue` for uncontrolled

```jsx
// Wrong: user cannot type; React warns "provided a value prop without an onChange handler"
<input value={name} />                               // ❌ frozen

// Right
<input value={name} onChange={(e) => setName(e.target.value)} />   // ✅ controlled
<input defaultValue="Aman" name="name" />                          // ✅ uncontrolled
```

❌ **Mistake 3:** Mutating a state object on change or using a stale closure
✅ **Correct:** Use the updater function and spread

```jsx
// Wrong: mutates state, no re-render
values[e.target.name] = e.target.value;              // ❌
setValues(values);

// Right
setValues((v) => ({ ...v, [e.target.name]: e.target.value }));   // ✅ new object
```

---

## 🧠 Tricky Interview Question

```jsx
import { useState } from 'react';

function App() {
  const [name, setName] = useState('Aman');
  return <input value={name} />;
}
// What happens when the user tries to type in this input?
```
**Answer:** Nothing changes on screen: the user cannot edit the text. The input is **controlled** (it has `value`) but there is no `onChange`, so React keeps resetting the DOM value back to the state value `'Aman'` after each key press. In development React logs a warning: "You provided a `value` prop to a form field without an `onChange` handler. This will render a read-only field." Fix: add `onChange`, use `defaultValue`, or add `readOnly` if you really want it fixed.

---

## ⚫ Interview Questions + Answers

Q1: How do you handle form submission in React?
A1: Attach `onSubmit` to the `<form>`, call `e.preventDefault()` to stop the page reload, validate the data, then send it with `fetch` or a Server Action. Use a `type="submit"` button so that Enter also submits. In React 19 you can pass a function to `action` instead and receive `FormData`.

Q2: What is the difference between controlled and uncontrolled forms?
A2: In a controlled form, React state is the single source of truth (`value` + `onChange`). In an uncontrolled form, the DOM holds the value and you read it via `FormData` or a ref when needed. Controlled is best for live validation and dependent fields; uncontrolled is simpler and cheaper for large forms.

Q3: How do you handle many inputs without writing many handlers?
A3: Give each input a `name`, keep values in one object, and use a single `handleChange` with `[e.target.name]: e.target.value`. For checkboxes use `e.target.checked`. For big forms use libraries like React Hook Form (uncontrolled, fewer re-renders) or Formik.

Q4: How do you validate forms?
A4: Use HTML attributes (`required`, `pattern`) for simple cases, or a pure validate function that returns errors derived from state. Show errors after a field is touched or on submit. Always **validate again on the server**; client validation is only for user experience.

Q5: What is new about forms in React 19?
A5: `<form action={fn}>` accepts functions (including Server Actions), `useActionState` returns state and a wrapped action, `useFormStatus` gives the `pending` flag to child components, and `useOptimistic` helps with instant UI. Uncontrolled fields reset automatically after a successful action. These APIs are React 19 / Next.js 15 (earlier versions use `useFormState`).

---

## 🔷 When to Use + When Not to Use
✅ **Use controlled inputs when:**
- You need instant validation, formatting (phone mask) or conditional fields
- The UI depends on the value while typing (search suggestions, character counter)
- You must reset or set the value from code

❌ **Prefer uncontrolled (FormData / form libraries) when:**
- The form is large and re-rendering on every key press is slow
- You only need the values on submit
- You use file inputs (they are always uncontrolled) or a Server Action

---

## 📊 Visual Diagram

```
 CONTROLLED                                   UNCONTROLLED
 ┌───────────────┐  type "a"                  ┌───────────────┐ type "a"
 │ <input        │ ───────► onChange          │ <input        │ (DOM keeps it)
 │  value={s} /> │          setS("a")         │  name="phone" │
 └──────▲────────┘             │              └───────┬───────┘
        │       re-render ◄────┘                      │ submit
        └── React state = truth                       ▼
                                              new FormData(form).get("phone")
 submit: use state `s`

 Submit flow:
 user presses Enter → onSubmit → preventDefault → validate → pending=true
      → fetch / Server Action → success (reset/navigate) | error (show message)

 Performance: controlled = 1 render per keystroke for the form component;
 split big forms into field components or use an uncontrolled library.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Controlled input | Value stored in React state | जिसकी value React state में है |
| Uncontrolled input | Value stored in the DOM | जिसकी value DOM में है |
| onSubmit | Event when the form is submitted | Form submit होने पर चलने वाला event |
| preventDefault | Stops the default page reload | Default page reload रोकना |
| FormData | Browser object holding form field values | Form fields की values वाला browser object |
| Validation | Checking the data is acceptable | Data सही है या नहीं जाँचना |
| Server Action | Server function called from a form | Form से बुलाया जाने वाला server function |
| useActionState | React 19 hook for form action state | Form action की state का React 19 hook |

---

## ⚡ 3-Line Summary
**English:**
1. A React form is handled with `onSubmit` + `preventDefault`, and each field is controlled (state) or uncontrolled (FormData).
2. Derive validation errors from state, block double submits, and always validate again on the server.
3. In Next.js and React 19, use `<form action>` with Server Actions, `useActionState` and `useFormStatus`.

**Hindi:**
1. React form `onSubmit` + `preventDefault` से संभलता है, और हर field controlled (state) या uncontrolled (FormData) होती है।
2. Validation errors को state से derive करो, double submit रोको, और server पर हमेशा फिर से validate करो।
3. Next.js और React 19 में Server Actions के साथ `<form action>`, `useActionState` और `useFormStatus` इस्तेमाल करो।

---

## ➡️ Next Topic
**29. Controlled vs Uncontrolled Components** — Forms में हमने दोनों तरीके देखे। अगला topic इनका गहरा फर्क, trade-offs और `ref` से uncontrolled input पढ़ना सिखाता है, जो interview में बार-बार पूछा जाता है।
