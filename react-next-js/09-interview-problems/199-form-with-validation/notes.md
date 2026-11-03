# 199. Build Form with Validation
# हिंदी में: Validation वाला Form बनाओ

Code: [App.jsx](./App.jsx) (complete working implementation, exports `validate` and a default `App`)

---

## 🔵 Simple Definition (English)
A **validated form** is a form whose inputs are controlled by React state, and whose values are checked by rules (required, email format, password length) before submit. Errors are shown next to the field that has the problem.

## 🔵 सरल परिभाषा (Hindi)
**Validated form** वह form है जिसके inputs React state से control होते हैं, और submit से पहले rules (required, email format, password length) से जाँचे जाते हैं। Error उसी field के पास दिखता है जिसमें गलती है।

---

## 🔴 Problem it Solves

Without validation, bad data reaches the server: an empty name, `abc@` as email, a short password. The user finds out only after a failed request. Without care, validation also annoys users: red errors appear while they are still typing the first letter. A good form validates on every change internally, but shows an error only after the user has left the field (blur) or tried to submit.

## 🔴 यह क्यों बना? (Hindi)
Validation के बिना गलत data server तक पहुँचता है: खाली name, `abc@` जैसा email, छोटा password। User को request fail होने के बाद पता चलता है। गलत तरीके से validation करने पर user परेशान भी होता है: पहला अक्षर लिखते ही लाल error दिखने लगता है। अच्छा form अंदर हर change पर validate करता है, लेकिन error तभी दिखाता है जब user field छोड़ दे (blur) या submit करने की कोशिश करे।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Keep all field values in ONE state object: { name, email, password, confirm }
Step 2 → onChange updates a single key: setValues(v => ({ ...v, [name]: value }))
Step 3 → A pure function validate(values) returns an errors object ({} means valid)
Step 4 → errors is DERIVED on each render (no separate state, so it can never go stale)
Step 5 → "touched" state records which fields the user has left (onBlur)
Step 6 → Show errors[name] only if touched[name] is true
Step 7 → On submit: preventDefault, mark ALL fields touched, stop if invalid
Step 8 → If valid: disable the button, call the API, then show success
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → सारी field values एक ही state object में रखो: { name, email, password, confirm }
Step 2 → onChange सिर्फ एक key बदलता है: setValues(v => ({ ...v, [name]: value }))
Step 3 → Pure function validate(values) errors object लौटाता है ({} का मतलब valid)
Step 4 → errors हर render में DERIVE होता है (अलग state नहीं, इसलिए पुराना/stale नहीं हो सकता)
Step 5 → "touched" state याद रखती है कि user ने कौन सी fields छोड़ दीं (onBlur)
Step 6 → errors[name] तभी दिखाओ जब touched[name] true हो
Step 7 → Submit पर: preventDefault, सारी fields touched करो, invalid हो तो रुक जाओ
Step 8 → Valid हो तो button disable करो, API call करो, फिर success दिखाओ
```

---

## 🟡 Real World Example
**Swiggy / Zomato signup:** You type your email and tab to the next field. Only then a message like "Enter a valid email" appears under the email. While you are typing the password, you see nothing. When you press "Create account" with empty fields, all errors appear at once and the button does not send the request. After the API accepts the data, the button shows "Saving..." and then a welcome screen.

## 🟡 Real Example Hindi mein
**Swiggy / Zomato signup:** आप email लिखकर अगली field पर जाते हैं। तभी email के नीचे "Enter a valid email" जैसा message आता है। Password लिखते समय कुछ नहीं दिखता। खाली fields के साथ "Create account" दबाने पर सारे errors एक साथ दिखते हैं और request नहीं जाती। API data accept कर ले तो बटन पर "Saving..." दिखता है और फिर welcome screen।

---

## 💻 Code Example — Basic

```jsx
// Basic: one field (email) with validation on blur
import { useState } from 'react';                        // state hook
import { createRoot } from 'react-dom/client';            // React 18/19 root API

function EmailForm() {
  const [email, setEmail] = useState('');                 // controlled input value
  const [touched, setTouched] = useState(false);          // has the user left the field?

  const error = !email.trim()                             // derive the error, do not store it
    ? 'Email is required'
    : !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
      ? 'Enter a valid email'
      : '';

  const onSubmit = (e) => {
    e.preventDefault();                                   // stop the browser page reload
    setTouched(true);                                     // reveal the error if any
    if (!error) alert('Submitted ' + email);              // only valid data goes forward
  };

  return (
    <form onSubmit={onSubmit} noValidate>                 {/* noValidate: we show our own messages */}
      <input
        value={email}                                     // value comes from state
        onChange={(e) => setEmail(e.target.value)}        // state follows typing
        onBlur={() => setTouched(true)}                   // show error after leaving field
        aria-invalid={touched && Boolean(error)}          // screen readers hear the invalid state
      />
      {touched && error && <span role="alert">{error}</span>} {/* error only when touched */}
      <button type="submit">Save</button>
    </form>
  );
}

createRoot(document.getElementById('root')).render(<EmailForm />); // mount
```

## 💻 Code Example — Advanced

The full working version is in [App.jsx](./App.jsx). Its core parts:

```jsx
// Advanced: multi-field signup with pure validate(), touched map, submit state, accessibility
import { useState } from 'react';

// Pure validator: easy to unit test without rendering anything
export function validate(v) {
  const e = {};                                             // collects messages by field name
  if (!v.name.trim()) e.name = 'Name is required';
  if (!v.email.trim()) e.email = 'Email is required';
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.email)) e.email = 'Enter a valid email';
  if (v.password.length < 8) e.password = 'Password must be at least 8 characters';
  else if (!/\d/.test(v.password)) e.password = 'Password needs at least one number';
  if (v.confirm !== v.password) e.confirm = 'Passwords do not match'; // cross-field rule
  return e;                                                 // {} means valid
}

export default function App() {
  const [values, setValues] = useState({ name: '', email: '', password: '', confirm: '' });
  const [touched, setTouched] = useState({});               // { email: true } after blur
  const [submitting, setSubmitting] = useState(false);      // disables the button during the request
  const [done, setDone] = useState(false);                  // success screen flag

  const errors = validate(values);                          // derived each render (cheap)
  const isValid = Object.keys(errors).length === 0;

  const onChange = (e) => setValues((v) => ({ ...v, [e.target.name]: e.target.value }));
  const onBlur = (e) => setTouched((t) => ({ ...t, [e.target.name]: true }));

  const onSubmit = async (e) => {
    e.preventDefault();
    setTouched({ name: true, email: true, password: true, confirm: true }); // reveal everything
    if (!isValid) return;                                   // block invalid submit
    setSubmitting(true);
    await new Promise((r) => setTimeout(r, 500));           // replace with a real fetch
    setSubmitting(false);
    setDone(true);
  };

  if (done) return <p role="status">Welcome, {values.name}!</p>;
  // ... the field() helper renders label + input + <span role="alert"> (see App.jsx)
}
```

Verified by script: `validate` returns `{}` for good data, and submitting the empty form shows "Name is required".

---

## 🟠 Next.js Connection

In the App Router, the form is a Client Component (it uses state), but the submit can go to a **Server Action**. Always validate again on the server, because client validation can be bypassed.

```jsx
// app/signup/actions.js (server code)
'use server';                                              // this module runs only on the server

export async function signup(prevState, formData) {
  const email = String(formData.get('email') ?? '');       // read the raw value
  const password = String(formData.get('password') ?? '');
  const errors = {};
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) errors.email = 'Enter a valid email';
  if (password.length < 8) errors.password = 'Password must be at least 8 characters';
  if (Object.keys(errors).length) return { errors };       // send errors back, no DB call
  // await db.user.create(...)                             // real work only after server validation
  return { errors: {}, ok: true };
}
```

```jsx
// app/signup/page.jsx
'use client';                                              // hooks need a Client Component
import { useActionState } from 'react';                    // React 19 (useFormState in older Next 14)
import { signup } from './actions';

export default function Page() {
  const [state, action, pending] = useActionState(signup, { errors: {} }); // state from the server
  return (
    <form action={action}>
      <input name="email" />
      <span role="alert">{state.errors?.email}</span>
      <input name="password" type="password" />
      <span role="alert">{state.errors?.password}</span>
      <button disabled={pending}>Sign up</button>
    </form>
  );
}
```

`useActionState` is React 19 / Next.js 15; Next.js 14 uses `useFormState` from `react-dom` (version-dependent). Libraries like React Hook Form with Zod can share one schema between client and server.

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Storing `errors` in separate state and updating it by hand
✅ **Correct:** Derive errors from values on every render

```jsx
// Wrong: errors can go stale if you forget a setErrors call
const [errors, setErrors] = useState({});
const onChange = (e) => { setValues({ ...values, [e.target.name]: e.target.value }); }; // errors not updated

// Right: always in sync because it is computed
const errors = validate(values);
```

❌ **Mistake 2:** Showing errors immediately on the first keystroke
✅ **Correct:** Show errors only for touched fields (and all fields after submit)

```jsx
// Wrong: user sees "Enter a valid email" after typing "a"
<span>{errors.email}</span>

// Right: wait for blur or submit
<span>{touched.email && errors.email}</span>
```

❌ **Mistake 3:** Forgetting `e.preventDefault()` or letting the user submit twice
✅ **Correct:** Prevent the default reload and disable the button while submitting

```jsx
// Wrong: page reloads, state is lost
const onSubmit = () => save(values);

// Right
const onSubmit = async (e) => { e.preventDefault(); setSubmitting(true); await save(values); setSubmitting(false); };
// <button disabled={submitting}>
```

---

## 🧠 Tricky Interview Question

```jsx
import { useState } from 'react';

function Form() {
  const [values, setValues] = useState({ email: '' });
  const [errors, setErrors] = useState({});

  const onChange = (e) => {
    setValues({ email: e.target.value });                 // update value
    if (!values.email.includes('@')) setErrors({ email: 'Invalid' }); // validate
  };
  return <input value={values.email} onChange={onChange} />;
}
```
What is wrong when the user types `a@` one character at a time?

**Answer:** The validation reads `values.email`, which is the value from the **previous** render (state is a snapshot; `setValues` does not change the variable in the current call). So the error lags one keystroke behind: after typing `@` the check still sees `a` and flags it invalid, and the error is stored separately so it may remain stale. Fix: validate the new value (`const next = e.target.value`), or better, derive `errors = validate(values)` during render.

---

## ⚫ Interview Questions + Answers

Q1: Controlled vs uncontrolled inputs in forms?
A1: A controlled input gets its `value` from React state and updates it in `onChange`, so React is the single source of truth and validation is easy. An uncontrolled input keeps its value in the DOM and you read it with a ref or `FormData`. Uncontrolled is lighter for big forms and works well with Server Actions.

Q2: When should you show validation errors?
A2: Not on first render and not on the first keystroke. Show them after blur (touched) and for all fields after a submit attempt. This avoids shouting at the user while they are still typing.

Q3: Why derive `errors` instead of storing it in state?
A3: Errors are a function of values, so storing them duplicates state and can go out of sync. A computed value is always correct and removes whole classes of bugs. If validation is expensive, wrap it in `useMemo`.

Q4: Is client-side validation enough?
A4: No. Anyone can bypass the browser with curl. Client validation is for user experience; the server must validate again (in an API route or Server Action) and be the real gatekeeper.

Q5: How do you make a form accessible?
A5: Use `<label>` for each input, `aria-invalid` on bad fields, `aria-describedby` pointing to the error element, `role="alert"` on error text so screen readers announce it, and a real `<button type="submit">` so Enter works.

---

## 🔷 When to Use + When Not to Use
✅ **Use a hand-written controlled form when:**
- The form is small (3 to 8 fields) and rules are simple
- You need to show that you understand state, events and derived data (interviews)
- You want full control over when errors appear

❌ **Avoid it when:**
- The form is large or dynamic (use React Hook Form, Formik or TanStack Form)
- You need schema validation shared with the server (use Zod or Yup resolvers)
- A plain HTML form with a Server Action and native `required` is enough

---

## 📊 Visual Diagram

```
  user types ──► onChange ──► values (state)
                                 │
                                 ▼ every render
                       errors = validate(values)      (derived, not state)
                                 │
  user leaves field ─► onBlur ─► touched (state)
                                 │
                                 ▼
                  show errors[name] only if touched[name]

  submit ─► preventDefault ─► touch ALL fields ─► isValid?
                                          ├─ no  → stop, errors visible
                                          └─ yes → submitting=true → API → done=true

  Re-renders: every keystroke re-renders the form (fine for small forms;
  validate() is O(fields) so the cost is negligible)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Controlled input | Value comes from React state | जिसकी value React state से आती है |
| Derived state | Value computed from other state | दूसरी state से निकाली गई value |
| Touched | User has visited and left the field | User field पर आकर छोड़ चुका है |
| Blur | Input loses focus | Input का focus हटना |
| Validation | Checking data against rules | Data को rules से जाँचना |
| Server Action | Server function called from a form | Form से बुलाया जाने वाला server function |
| aria-invalid | Marks a field as invalid for screen readers | Field गलत है, यह बताने वाला attribute |
| Pure function | Same input gives same output, no side effects | समान input पर समान output, कोई side effect नहीं |

---

## ⚡ 3-Line Summary
**English:**
1. Keep values in state, derive errors with a pure `validate()` function, and track `touched` fields.
2. Show errors after blur or submit, block invalid submits, and disable the button while saving.
3. Always validate again on the server (Server Action or API); client checks are only for user experience.

**Hindi:**
1. Values को state में रखो, pure `validate()` function से errors निकालो, और `touched` fields को track करो।
2. Errors blur या submit के बाद दिखाओ, invalid submit रोको, और saving के समय button disable करो।
3. Server पर (Server Action या API) दोबारा validate ज़रूर करो; client की जाँच सिर्फ user experience के लिए है।

---

## ➡️ Next Topic
**200. Dark Mode Toggle** — theme को state, localStorage और CSS variables से कैसे manage करें, और Next.js में flash of wrong theme कैसे रोकें।
