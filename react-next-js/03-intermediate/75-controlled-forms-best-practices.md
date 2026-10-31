# 75. Controlled Forms — Best Practices
# हिंदी में: Controlled Forms — React state से form चलाने के सही तरीके

---

## 🔵 Simple Definition (English)
A **controlled form field** gets its displayed value from React state through the `value` prop, and updates that state through `onChange`. React is the **single source of truth**: the DOM always shows what the state says, and every user keystroke goes through your state first.

## 🔵 सरल परिभाषा (Hindi)
**Controlled form field** अपनी value `value` prop के ज़रिए React state से लेता है, और `onChange` से उस state को अपडेट करता है। React ही **single source of truth** है: DOM वही दिखाता है जो state कहता है, और हर keystroke पहले आपके state से होकर जाता है।

---

## 🔴 Problem it Solves
Forms में कई fields होते हैं: validation, formatting, reset, disabled states, और dependent fields। अगर हर field की value DOM में अलग-अलग रहे और React के state से मेल न खाए, तो bugs आते हैं: reset काम नहीं करता, input में गलत format दिखता है, और submit पर पुराना data जाता है। Controlled forms इस समस्या को एक ही state से हल करते हैं।

## 🔴 यह क्यों बना? (Hindi)
Paytm पर KYC form में PAN, आधार और फ़ोन fields हैं। PAN हमेशा uppercase होना चाहिए, फ़ोन में सिर्फ अंक, और error तुरंत दिखना चाहिए। यह सब तभी संभव है जब React को हर keystroke की value पता हो। Controlled form से format बदलना, validate करना और reset करना आसान और सुरक्षित होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → State बनाओ: const [email, setEmail] = useState('')

Step 2 → Input को value और onChange दो:
         <input value={email} onChange={e => setEmail(e.target.value)} />

Step 3 → User टाइप करता है → browser "input" event देता है

Step 4 → React onChange handler चलाता है → setEmail(नई value)

Step 5 → Component दोबारा render होता है → value prop नया
         → React DOM को नई value पर sync करता है

KEY: DOM की value सिर्फ state के ज़रिए बदलती है। Input कभी अपने आप नहीं बदलता।
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → state बनाओ
Step 2 → input पर value और onChange लगाओ
Step 3 → User type करता है
Step 4 → onChange में setState होता है
Step 5 → Render में नई value DOM तक पहुंचती है
KEY: DOM की value हमेशा state से तय होती है।
```

---

## 🟡 Real World Example
**Paytm KYC form:** PAN field में user "abcde1234f" टाइप करता है। `onChange` उसे uppercase करके state में रखता है, इसलिए input में हमेशा "ABCDE1234F" दिखता है। Phone field सिर्फ digits स्वीकार करता है। Submit button तभी enable होता है जब सारे fields valid हों। यह सारा logic एक state object पर चलता है, और reset बटन पर सब एक साथ खाली हो जाता है।

## 🟡 Real Example Hindi mein
**Paytm KYC form:** PAN field में user "abcde1234f" लिखता है, और `onChange` उसे uppercase करके state में रखता है, तो input में "ABCDE1234F" दिखता है। Phone सिर्फ digits लेता है। Submit तभी enable होता है जब सारे fields valid हों। Reset बटन सब एक साथ खाली करता है, क्योंकि सब state में है।

---

## 💻 Code Example — Basic

```jsx
import { useState } from 'react';

// ── BASIC: एक state object, एक handler, सभी fields ──
export default function CheckoutForm() {
  // सभी fields एक object में: एक जगह से पूरा form नियंत्रित होता है
  const [form, setForm] = useState({ name: '', phone: '', agree: false });

  // एक ही handler सभी inputs के लिए: e.target.name से पता चलता है कौन-सा field है
  function handleChange(e) {
    const { name, value, type, checked } = e.target; // target की ज़रूरी properties निकालो
    setForm(prev => ({
      ...prev,                                       // बाकी fields की पुरानी values रखो
      [name]: type === 'checkbox' ? checked : value, // checkbox → boolean, बाकी → string
    }));
  }

  function handleSubmit(e) {
    e.preventDefault();                              // browser का default page reload रोको
    console.log('Submit:', form);                    // अभी का पूरा state
  }

  return (
    <form onSubmit={handleSubmit}>
      <input name="name" value={form.name} onChange={handleChange} placeholder="नाम" />
      <input
        name="phone"
        value={form.phone}
        onChange={handleChange}
        placeholder="फ़ोन"
        inputMode="numeric"                          // mobile पर number keypad
      />
      <label>
        <input
          type="checkbox"
          name="agree"
          checked={form.agree}                       // checkbox में value नहीं, checked होता है
          onChange={handleChange}
        />
        शर्तें मानता हूँ
      </label>
      <button type="submit" disabled={!form.agree}>Order करो</button> {/* शर्त मानी तभी enable */}
    </form>
  );
}
```

## 💻 Code Example — Advanced

```jsx
import { useEffect, useMemo, useState } from 'react';

// ── ADVANCED: normalize input, derived values, debounced draft save ──

// Pure helper: सिर्फ digits, अधिकतम 10
function normalizePhone(raw) {
  return raw.replace(/\D/g, '').slice(0, 10);       // non-digits हटाओ, फिर 10 तक काटो
}

const INITIAL = { name: '', phone: '', address: '' }; // module scope: reset के लिए एक ही reference

export default function AddressForm({ onSave }) {
  const [form, setForm] = useState(INITIAL);         // single source of truth
  const [submitted, setSubmitted] = useState(false); // error तभी दिखाओ जब user ने submit किया हो

  // Derived value: errors को state में नहीं रखते। हर render में गणना, कभी out-of-sync नहीं
  const errors = useMemo(() => ({
    name: form.name.trim().length < 2 ? 'नाम कम से कम 2 अक्षर' : '',
    phone: form.phone.length === 10 ? '' : '10 अंकों का फ़ोन चाहिए',
  }), [form.name, form.phone]);                      // सिर्फ इन्हीं पर निर्भर
  const isValid = !errors.name && !errors.phone;     // boolean, अलग state नहीं

  // Functional update: हमेशा latest prev पर आधारित
  function update(field, value) {
    setForm(prev => ({ ...prev, [field]: value }));
  }

  // Draft auto-save: typing रुकने के 500ms बाद localStorage में लिखो
  useEffect(() => {
    const id = setTimeout(() => {
      localStorage.setItem('addressDraft', JSON.stringify(form)); // browser में draft
    }, 500);
    return () => clearTimeout(id);                   // नया keystroke आए तो पिछला timer रद्द
  }, [form]);

  function handleSubmit(e) {
    e.preventDefault();                              // reload रोको
    setSubmitted(true);                              // अब errors दिखाओ
    if (isValid) {
      onSave(form);                                  // parent को valid data दो
      setForm(INITIAL);                              // सफल save के बाद खाली
      setSubmitted(false);                           // error flag reset
    }
  }

  return (
    <form onSubmit={handleSubmit} noValidate>        {/* browser की validation बंद, हम खुद करते हैं */}
      <input
        value={form.name}
        onChange={e => update('name', e.target.value)}
        aria-invalid={submitted && !!errors.name}    /* screen reader को बताओ यह field गलत है */
      />
      {submitted && errors.name && <p role="alert">{errors.name}</p>}

      <input
        value={form.phone}
        onChange={e => update('phone', normalizePhone(e.target.value))} // हर keystroke पर normalize
        inputMode="numeric"
      />
      {submitted && errors.phone && <p role="alert">{errors.phone}</p>}

      <textarea value={form.address} onChange={e => update('address', e.target.value)} />
      <button type="submit">Save</button>
    </form>
  );
}
```

---

## 🟠 Real app integration

Next.js 15/16 और React 19 में form submission के लिए **Server Actions** और `useActionState` का चलन है। Controlled inputs client पर रहते हैं, और server error लौटाकर उसी state में दिखाया जाता है।

```jsx
// app/actions.js — Server Action (server पर चलता है)
'use server';                                        // यह file के सभी exports server functions होंगे
export async function saveAddress(prevState, formData) { // useActionState का signature: (prev, formData)
  const name = formData.get('name')?.toString().trim() ?? ''; // FormData से string
  if (name.length < 2) {
    return { ok: false, error: 'नाम कम से कम 2 अक्षर', name }; // error लौटाओ, value वापस दो
  }
  await saveToDatabase({ name });                    // तुम्हारा database layer (illustrative)
  return { ok: true, error: null, name: '' };        // सफल: value खाली
}
```

```jsx
// app/address/AddressForm.js — Client Component
'use client';                                        // controlled state और hooks के लिए
import { useActionState, useEffect, useState } from 'react';
import { useFormStatus } from 'react-dom';           // pending स्थिति के लिए
import { saveAddress } from '../actions';            // Server Action import

function SubmitButton() {
  const { pending } = useFormStatus();               // parent <form> के submit का status
  return <button disabled={pending}>{pending ? 'Saving...' : 'Save'}</button>;
}

export default function AddressForm() {
  const [name, setName] = useState('');              // controlled input की value (client)
  const [state, formAction] = useActionState(saveAddress, { ok: false, error: null, name: '' });

  // React 19 form action के बाद uncontrolled inputs अपने-आप reset होते हैं,
  // पर हमारे controlled input को खुद खाली करना पड़ता है
  useEffect(() => {
    if (state.ok) setName('');                       // सफल submit पर state खाली
  }, [state]);

  return (
    <form action={formAction}>                       {/* action server function को FormData देता है */}
      <input
        name="name"                                  // name attribute: FormData में यह key बनेगी
        value={name}
        onChange={e => setName(e.target.value)}      // controlled: हर keystroke state में
      />
      {state.error && <p role="alert">{state.error}</p>}
      <SubmitButton />
    </form>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** `value` दिया पर `onChange` नहीं, तो input read-only हो जाता है
```jsx
// ❌ Wrong: user type नहीं कर पाएगा, और React warning देगा
<input value={name} />

// ✅ Right: हर बदलाव state में जाए
<input value={name} onChange={e => setName(e.target.value)} />

// ✅ Also right (अगर सिर्फ पढ़ना है): readOnly लिखो
<input value={name} readOnly />
```

❌ **Mistake 2:** Derived value को अलग state में रखना
```jsx
// ❌ Wrong: isValid हमेशा name से बनता है, अलग state रखने से out-of-sync होने का खतरा
const [name, setName] = useState('');
const [isValid, setIsValid] = useState(false);
function handleChange(e) {
  setName(e.target.value);
  setIsValid(e.target.value.length >= 2);            // दो जगह update करना पड़ रहा है
}

// ✅ Right: जो value किसी और से बन सकती है, उसे render में गणना करो
const [name, setName] = useState('');
const isValid = name.length >= 2;                    // हमेशा सही, कोई extra state नहीं
```

---

## 🧠 Tricky Interview Question

```jsx
import { useState } from 'react';

export default function NameField() {
  const [name, setName] = useState('');
  return (
    <input
      value={name.trim()}                            // trim करके दिखाओ
      onChange={e => setName(e.target.value)}        // state में raw value रखो
    />
  );
}
// Question: User "Aditya" टाइप करता है, फिर space दबाता है, फिर "Ranjan" टाइप करता है।
// Input में अंत में क्या दिखेगा?
```

**Answer:** Input में `AdityaRanjan` दिखेगा, यानी space गायब होगा। "Aditya " टाइप करने पर state में raw value `"Aditya "` (trailing space के साथ) जाती है। पर render में `value` `name.trim()` है, यानी `"Aditya"`। React controlled input की DOM value को state-derived value पर वापस सेट कर देता है, इसलिए space तुरंत हट जाता है। फिर "Ranjan" जुड़ने पर `"AdityaRanjan"` बनता है। सही तरीका यह है कि `value={name}` रखो, और trim सिर्फ submit या validation पर करो।

---

## ⚫ Interview Questions + Answers

**Q1: Controlled और uncontrolled input में मुख्य फर्क क्या है?**
A1: Controlled में value React state से आती है और हर बदलाव `onChange` से state में जाता है। Uncontrolled में value DOM में रहती है, और React उसे ref या FormData से कभी-कभी पढ़ता है।

**Q2: Controlled form के फायदे क्या हैं?**
A2: Input की value पर पूरा नियंत्रण मिलता है: formatting, validation, reset, dependent fields और disabled logic आसान होते हैं। Data हमेशा state में होता है, इसलिए submit पर सही value मिलती है।

**Q3: Controlled form का नुकसान क्या है?**
A3: हर keystroke पर component re-render होता है। बड़े forms में यह धीमा हो सकता है। इसके लिए state को छोटे components में बांटो, या React Hook Form जैसे library का उपयोग करो (topic 77)।

**Q4: Derived value को state में क्यों नहीं रखना चाहिए?**
A4: क्योंकि उसे दूसरी state से गणना करके निकाला जा सकता है। अलग state रखने से दो जगह update करना पड़ता है और वे out-of-sync हो सकते हैं। Single source of truth से बचा जा सकता है।

**Q5: React 19 form actions का controlled forms से क्या संबंध है?**
A5: `<form action={fn}>` FormData सीधे server या client function को देता है, और सफल submit के बाद uncontrolled inputs अपने-आप reset हो जाते हैं। Controlled inputs के लिए state को खुद reset करना पड़ता है, जैसे `useEffect` या action के result पर।

---

## 🔷 When to Use + When Not to Use
✅ **Use controlled forms when:**
- Input की value को बदलना, format करना या filter करना हो (uppercase, digits only)
- Fields एक-दूसरे पर निर्भर हों (state से dependent UI)
- Reset, disabled या live validation की ज़रूरत हो
- Data को तुरंत किसी दूसरी component के साथ share करना हो

❌ **Avoid controlled forms when:**
- बहुत बड़ा form है जिसमें हर keystroke पर भारी re-render होता है (React Hook Form या uncontrolled पर जाओ)
- सिर्फ एक simple submit है, जहां `FormData` काफी है
- File input (यह हमेशा uncontrolled होता है)
- Value को state में रखने का कोई फायदा नहीं, जैसे सिर्फ read-only display

---

## 📊 Visual Diagram

```
  ┌──────────────┐  keystroke   ┌──────────────┐  setState   ┌──────────────┐
  │  Browser DOM │ ───────────► │ onChange     │ ──────────► │ React state  │
  │  <input>     │              │ (handler)    │             │ (single      │
  └──────────────┘              └──────────────┘             │  truth)      │
        ▲                                                    └──────┬───────┘
        │                                                           │
        │          value={state}  (React DOM को sync करता है)       │
        └───────────────────────────────────────────────────────────┘

  Derived:  errors = f(state)   ← render में गणना, state नहीं
  Submit:   state → onSave(state)  या  Server Action(formData)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Controlled input | Value state से आने वाला input | State से value लेने वाला input |
| Single source of truth | एक ही जगह जहां data रहता है | Data रखने की एक ही जगह |
| Derived state | दूसरी state से गणना की गई value | दूसरी state से निकाली गई value |
| Normalization | Input को साफ़ और सही format में बदलना | Input को सही format में बदलना |
| Functional update | `setState(prev => ...)` का पैटर्न | `prev` पर आधारित update |
| Server Action | Server पर चलने वाला form handler | Server पर चलने वाला form handler |

---

## ⚡ 3-Line Summary
**English:**
1. Controlled input की value `value` prop से आती है और `onChange` से state में जाती है।
2. Derived values (जैसे errors, isValid) state में नहीं, render में गणना करो।
3. बड़े forms में React Hook Form या uncontrolled inputs पर विचार करो; React 19 में form actions और `useActionState` use करो।

**Hindi:**
1. Controlled input की value `value` prop से आती है और `onChange` से state में जाती है।
2. Derived values (जैसे errors, isValid) state में नहीं, render में गणना करो।
3. बड़े forms में React Hook Form या uncontrolled inputs पर विचार करो; React 19 में form actions और `useActionState` use करो।

---

## ➡️ Next Topic
**76. Uncontrolled Forms + useRef** — DOM को सीधे पढ़ना, `useRef` का उपयोग, और file inputs के लिए uncontrolled approach।
