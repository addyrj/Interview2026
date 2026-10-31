# 78. Form Validation in React
# हिंदी में: Form Validation in React — सही जगह, सही समय पर validation

---

## 🔵 Simple Definition (English)
**Form validation** checks user input against rules (required, format, length, business logic) and shows clear messages before or after submission. In React you can use **native HTML validation**, **hand-written JavaScript checks**, or a **schema library** (Zod, Yup). Client-side validation improves UX, but the **server must always validate again**, because client checks can be bypassed.

## 🔵 सरल परिभाषा (Hindi)
**Form validation** user के input को rules से जांचता है (ज़रूरी है, format, लंबाई, business logic) और submit से पहले या बाद में साफ़ message दिखाता है। React में तीन तरीके हैं: **native HTML validation**, **हाथ से लिखी JavaScript checks**, या **schema library** (Zod, Yup)। Client-side validation से UX बेहतर होता है, पर **server को हमेशा दोबारा validate करना होता है**, क्योंकि client checks को bypass किया जा सकता है।

---

## 🔴 Problem it Solves
Validation के बिना user गलत data भेज देता है: 5 अंक का PIN, बिना @ का email, या खाली नाम। Server पर error आता है, जो user को समझ नहीं आता। अगर validation सिर्फ एक जगह है, तो rules client और server पर अलग-अलग लिखे जाते हैं और बदल जाते हैं। साथ ही error messages अक्सर screen reader के लिए accessible नहीं होते, और user को पता ही नहीं चलता कि गलती कहां है।

## 🔴 यह क्यों बना? (Hindi)
Razorpay checkout पर card number गलत हो तो तुरंत बताना चाहिए, वरना user payment fail होने पर परेशान होता है। Validation का मकसद दो हैं: user को जल्दी सुधार का मौका देना और server पर गंदा data आने से रोकना। इसलिए client पर UX के लिए, और server पर सुरक्षा के लिए, दोनों ज़रूरी हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Rules तय करो (required, format, min/max, custom logic)

Step 2 → कब validate करना है चुनो:
         onSubmit  → submit पर सब fields (सबसे सरल)
         onBlur    → field छोड़ने पर (कम noise)
         onChange  → हर keystroke पर (सबसे तुरंत, पर शोर ज़्यादा)

Step 3 → Errors को state या library के formState में रखो
         (यह derived हो सकता है: schema.safeParse(values))

Step 4 → Error message को सही input से जोड़ो:
         aria-invalid="true" और aria-describedby="error-id"

Step 5 → Submit पर: पहले गलत field पर focus करो, फिर server पर भेजो
         Server भी validate करे → field errors वापस → UI पर दिखाओ

KEY: Client = UX, Server = सुरक्षा और सच। दोनों पर validate करो।
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Rules तय करो
Step 2 → Timing चुनो: submit पर, blur पर, या हर keystroke पर
Step 3 → Errors state या schema से निकालो
Step 4 → Input को aria-invalid और error message से जोड़ो
Step 5 → Submit पर पहले error वाले field पर focus, फिर server validation
KEY: Client UX के लिए, Server सुरक्षा के लिए। दोनों ज़रूरी।
```

---

## 🟡 Real World Example
**Paytm UPI registration:** Mobile number 10 अंक का होना चाहिए, PIN 6 अंक का, और दोनों PIN एक जैसे हों। User PIN टाइप करता है, और "confirm PIN" field blur होने पर mismatch बताया जाता है। Submit पर server फिर जांचता है कि यह number पहले से registered तो नहीं। Error आने पर उसी field पर message दिखता है, और focus उस field पर जाता है।

## 🟡 Real Example Hindi mein
**Paytm UPI registration:** Mobile 10 अंक का होना चाहिए, PIN 6 अंक का, और confirm PIN मिलना चाहिए। Confirm field छोड़ते ही mismatch बताया जाता है। Submit पर server फिर जांचता है कि number पहले से registered तो नहीं। Error उसी field पर दिखता है और focus वहीं जाता है।

---

## 💻 Code Example — Basic

```jsx
import { useState } from 'react';

// ── BASIC: हाथ से लिखी validation, submit पर ──

// Pure function: values लेकर errors object लौटाता है (side effect नहीं)
function validate(values) {
  const errors = {};                                   // खाली errors object
  if (values.name.trim().length < 2) {                 // नाम की लंबाई check (trim के बाद)
    errors.name = 'नाम कम से कम 2 अक्षर का हो';
  }
  if (!/^\d{10}$/.test(values.phone)) {                // exactly 10 अंक (regex)
    errors.phone = '10 अंकों का फ़ोन नंबर डालो';
  }
  return errors;                                       // जिस field में error नहीं, उसकी key नहीं होगी
}

export default function RegisterForm() {
  const [values, setValues] = useState({ name: '', phone: '' }); // input values
  const [errors, setErrors] = useState({});                      // error messages
  const [submitted, setSubmitted] = useState(false);             // error तभी दिखाओ जब submit हुआ हो

  function handleChange(e) {
    const { name, value } = e.target;                  // कौन-सा field, और नई value
    setValues(prev => ({ ...prev, [name]: value }));   // उस field को update करो
  }

  function handleSubmit(e) {
    e.preventDefault();                                // page reload रोको
    setSubmitted(true);                                // अब errors दिखाने की अनुमति
    const found = validate(values);                    // अभी के values पर validation
    setErrors(found);                                  // errors state में
    if (Object.keys(found).length === 0) {             // कोई error नहीं
      console.log('Valid, server को भेजो:', values);
    }
  }

  // सिर्फ तभी दिखाओ जब submit हो चुका हो (पहले से नहीं)
  const showError = field => submitted && errors[field];

  return (
    <form onSubmit={handleSubmit} noValidate>          {/* browser की native popup बंद */}
      <label>
        नाम
        <input
          name="name"
          value={values.name}
          onChange={handleChange}
          aria-invalid={!!showError('name')}            /* screen reader को बताओ यह field गलत है */
          aria-describedby={showError('name') ? 'name-err' : undefined} /* message से जोड़ो */
        />
      </label>
      {showError('name') && <p id="name-err" role="alert">{errors.name}</p>}

      <label>
        फ़ोन
        <input
          name="phone"
          value={values.phone}
          onChange={handleChange}
          inputMode="numeric"
          aria-invalid={!!showError('phone')}
          aria-describedby={showError('phone') ? 'phone-err' : undefined}
        />
      </label>
      {showError('phone') && <p id="phone-err" role="alert">{errors.phone}</p>}

      <button type="submit">Register</button>
    </form>
  );
}
```

## 💻 Code Example — Advanced

```jsx
import { useState } from 'react';
import { z } from 'zod';                               // schema library (zod@3 के साथ tested)

// ── ADVANCED: Zod schema, blur-time validation, focus first error, server errors ──

// Schema: client और server दोनों पर यही file import होगी (single source of truth)
const schema = z
  .object({
    name: z.string().trim().min(2, 'नाम कम से कम 2 अक्षर'),        // trim के बाद check
    pin: z.string().regex(/^\d{6}$/, 'PIN ठीक 6 अंक का हो'),        // exactly 6 digits
    confirmPin: z.string(),                                          // मिलान ऊपर refine में
  })
  .refine(d => d.pin === d.confirmPin, {                             // cross-field rule
    message: 'PIN मेल नहीं खाते',                                    // यह message
    path: ['confirmPin'],                                            // error इसी field पर जाए
  });

// Fake server: असली app में Server Action होगा
async function serverRegister(values) {
  await new Promise(r => setTimeout(r, 300));                        // network delay
  if (values.name === 'admin') return { ok: false, field: 'name', message: 'यह नाम उपलब्ध नहीं' };
  return { ok: true };
}

export default function UpiRegister() {
  const [values, setValues] = useState({ name: '', pin: '', confirmPin: '' });
  const [errors, setErrors] = useState({});                          // field => message
  const [touched, setTouched] = useState({});                        // कौन-सा field छुआ गया (blur)
  const [pending, setPending] = useState(false);                     // server call चल रही है?

  // Schema से सारे errors निकालो (derived, किसी और state से sync नहीं)
  function runSchema(next) {
    const result = schema.safeParse(next);                           // throw नहीं करता
    if (result.success) return {};                                   // कोई error नहीं
    const map = {};                                                  // field => पहला message
    for (const issue of result.error.issues) {
      const key = issue.path[0];                                     // कौन-सा field
      if (!map[key]) map[key] = issue.message;                       // पहला error ही दिखाओ
    }
    return map;
  }

  function handleChange(e) {
    const { name, value } = e.target;
    const next = { ...values, [name]: value };                       // नई values
    setValues(next);
    if (touched[name]) setErrors(runSchema(next));                   // छुए field पर live अपडेट
  }

  function handleBlur(e) {
    const { name } = e.target;
    setTouched(t => ({ ...t, [name]: true }));                       // field छुआ गया
    setErrors(runSchema(values));                                    // blur पर validate
  }

  async function handleSubmit(e) {
    e.preventDefault();
    const found = runSchema(values);                                 // submit पर सब fields
    setErrors(found);
    setTouched({ name: true, pin: true, confirmPin: true });         // अब सारे errors दिखें
    const firstBad = Object.keys(found)[0];                          // पहला गलत field
    if (firstBad) {
      document.querySelector(`[name="${firstBad}"]`)?.focus();       // उस पर focus (a11y)
      return;
    }
    setPending(true);
    const res = await serverRegister(values);                        // server की validation भी
    setPending(false);
    if (!res.ok) setErrors(prev => ({ ...prev, [res.field]: res.message })); // server error उसी field पर
  }

  const err = field => (touched[field] ? errors[field] : undefined); // सिर्फ छुए fields के errors

  return (
    <form onSubmit={handleSubmit} noValidate>
      {['name', 'pin', 'confirmPin'].map(field => (
        <div key={field}>
          <input
            name={field}
            value={values[field]}
            onChange={handleChange}
            onBlur={handleBlur}
            aria-invalid={!!err(field)}
            aria-describedby={err(field) ? `${field}-err` : undefined}
            type={field === 'name' ? 'text' : 'password'}
            inputMode={field === 'name' ? 'text' : 'numeric'}
          />
          {err(field) && <p id={`${field}-err`} role="alert">{err(field)}</p>}
        </div>
      ))}
      <button type="submit" disabled={pending}>{pending ? 'Checking...' : 'Register'}</button>
    </form>
  );
}
```

---

## 🟠 Real app integration

Next.js में सबसे अच्छा pattern यह है कि **एक Zod schema** client form और Server Action दोनों में चले। Server Action में `safeParse` से फिर से जांच होती है, और errors को `useActionState` के state से form पर वापस दिखाया जाता है।

```jsx
// lib/schemas.js — single source of truth
import { z } from 'zod';
export const registerSchema = z.object({
  email: z.string().trim().email('ईमेल सही नहीं है'),   // email format
  password: z.string().min(8, 'कम से कम 8 अक्षर'),     // password लंबाई
});
```

```jsx
// app/register/actions.js — server पर दोबारा validation
'use server';
import { registerSchema } from '@/lib/schemas';        // वही schema
export async function registerAction(prevState, formData) {
  // FormData से raw values (client पर भरोसा नहीं)
  const parsed = registerSchema.safeParse({
    email: formData.get('email'),
    password: formData.get('password'),
  });
  if (!parsed.success) {
    // field errors वापस भेजो: UI उन्हें उसी input के पास दिखाएगा
    return { errors: parsed.error.flatten().fieldErrors };
  }
  await createUser(parsed.data);                        // तुम्हारा data layer (illustrative)
  return { errors: {} };                                // सफल
}
```

```jsx
// app/register/RegisterForm.js — Client Component
'use client';
import { useActionState } from 'react';
import { registerAction } from './actions';

export default function RegisterForm() {
  const [state, formAction, pending] = useActionState(registerAction, { errors: {} }); // React 19: तीसरा value pending
  return (
    <form action={formAction}>
      <input name="email" type="email" aria-invalid={!!state.errors.email} />
      {state.errors.email && <p role="alert">{state.errors.email[0]}</p>} {/* पहला message */}
      <input name="password" type="password" aria-invalid={!!state.errors.password} />
      {state.errors.password && <p role="alert">{state.errors.password[0]}</p>}
      <button disabled={pending}>{pending ? 'Wait...' : 'Register'}</button>
    </form>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** सिर्फ client validation पर भरोसा करना
```jsx
// ❌ Wrong: browser DevTools या curl से कोई भी गलत data भेज सकता है
function submit(values) {
  if (values.price > 0) saveProduct(values); // server ने कभी check नहीं किया
}

// ✅ Right: client पर UX के लिए, और server पर सुरक्षा के लिए, दोनों
// server action / API route में:
const parsed = productSchema.safeParse(body);   // फिर से validate
if (!parsed.success) return badRequest(parsed.error);
```

❌ **Mistake 2:** पहले से ही सारे fields में error दिखाना (user को डराना)
```jsx
// ❌ Wrong: पेज खुलते ही लाल errors दिखते हैं, user ने कुछ लिखा भी नहीं
const errors = validate(values);                        // हर render पर
{errors.name && <p role="alert">{errors.name}</p>}      // खाली form पर भी दिखेगा

// ✅ Right: error सिर्फ तभी दिखाओ जब field छुआ गया हो या form submit हुआ हो
const showName = (touched.name || submitted) && errors.name;
{showName && <p role="alert">{errors.name}</p>}
```

---

## 🧠 Tricky Interview Question

```js
import { z } from 'zod';

const ageSchema = z.coerce.number().optional();     // age optional है

console.log(ageSchema.safeParse('').success);        // (A)
console.log(ageSchema.safeParse(undefined).success); // (B)
console.log(ageSchema.safeParse('').data);           // (C)
```

**Answer:** Output होगा: (A) `true`, (B) `true`, (C) `0`। `z.coerce.number()` खाली string `''` को `Number('')` से `0` में बदल देता है। `0` एक valid number है, इसलिए `optional()` को इसकी ज़रूरत ही नहीं, और validation पास हो जाता है। लोग सोचते हैं कि खाली input "optional" है, पर coerce उसे `0` बना देता है। `undefined` के लिए `optional()` काम करता है। Fix: `z.preprocess(v => (v === '' ? undefined : v), z.coerce.number().optional())` लिखो, ताकि खाली string `undefined` बने और `optional` सही काम करे।

---

## ⚫ Interview Questions + Answers

**Q1: Client और server validation दोनों क्यों ज़रूरी हैं?**
A1: Client validation तुरंत feedback देकर UX बेहतर करता है। Server validation सुरक्षा और data integrity की गारंटी है, क्योंकि client code को किसी भी तरीके से bypass किया जा सकता है।

**Q2: Validation कब करें: onChange, onBlur या onSubmit?**
A2: Submit पर सब check करना सबसे सरल है। onBlur पर validate करना अच्छा balance है: user field छोड़ते ही गलती जानता है, पर हर keystroke पर शोर नहीं होता। onChange तभी use करो जब तुरंत feedback ज़रूरी हो, जैसे password strength।

**Q3: Accessibility के लिए validation errors कैसे दिखाएं?**
A3: Input पर `aria-invalid` लगाओ, `aria-describedby` से error message को input से जोड़ो, error को `role="alert"` या live region में दिखाओ, और submit पर पहले गलत field पर focus करो।

**Q4: `required` attribute और schema validation में क्या फर्क है?**
A4: `required` सिर्फ खाली होने की जांच करता है, और spaces वाली string को valid मानता है। Schema library में trim, format, cross-field rules (जैसे दोनों PIN मिलें) और custom messages आसानी से लिखे जाते हैं।

**Q5: Server validation के errors को React form पर कैसे लौटाएं?**
A5: Server action या API से structured errors लौटाओ (जैसे `fieldErrors`)। React 19 में `useActionState` से state में errors आते हैं, और उन्हें उसी input के पास दिखाते हो। React Hook Form में `setError` से यही किया जाता है।

---

## 🔷 When to Use + When Not to Use
✅ **Use validation when:**
- Data गलत होने पर पैसे, सुरक्षा या database पर असर पड़ता हो
- User को तुरंत साफ़ message देकर सुधार का मौका देना हो
- Rules client और server दोनों पर एक जैसे चाहिए (Zod schema)
- Cross-field rules हों, जैसे password confirm, date range

❌ **Avoid / do not rely when:**
- सिर्फ client पर validation और server पर कोई check नहीं (सुरक्षा का छेद)
- खाली form पर सारे errors दिखाना (user को डराता है)
- Validation को हर keystroke पर भारी काम बनाना (debounce या blur use करो)
- Native validation और custom validation दोनों एक साथ चलाना, जिससे दो तरह की popups दिखें (`noValidate` लगाओ)

---

## 📊 Visual Diagram

```
  User input
     │
     ▼
  ┌─────────────────────────────┐
  │ CLIENT (UX)                 │
  │  rules / Zod schema         │──── error ──► aria-invalid + message (उसी field पर)
  │  onBlur / onSubmit          │
  └──────────────┬──────────────┘
                 │ valid
                 ▼
  ┌─────────────────────────────┐
  │ SERVER (सुरक्षा और सच)      │
  │  safeParse(same schema)     │──── error ──► fieldErrors वापस ──► UI
  │  DB uniqueness, auth checks │
  └──────────────┬──────────────┘
                 │ ok
                 ▼
         Data saved ✅

  Submit पर: पहले गलत field पर focus ──► फिर server call
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Validation | Input को rules से जांचना | Input को rules से जांचना |
| Schema | Data का structure और rules का set (जैसे Zod) | Data के rules का set |
| `safeParse` | Zod का method जो throw किए बिना result लौटाता है | बिना throw result देने वाला method |
| `aria-invalid` | Screen reader को बताता है कि field गलत है | Screen reader को field गलत बताने वाला attribute |
| `aria-describedby` | Input को उसके error message से जोड़ता है | Input को error message से जोड़ने वाला attribute |
| Cross-field rule | दो fields के बीच का rule (PIN मिलान) | दो fields के बीच का rule |
| Single source of truth | Client और server पर एक ही schema | Client-server पर एक ही schema |

---

## ⚡ 3-Line Summary
**English:**
1. Validation client पर UX के लिए और server पर सुरक्षा के लिए ज़रूरी है; server हमेशा फिर से check करे।
2. Errors को सही समय (blur या submit) पर दिखाओ, और `aria-invalid` व `aria-describedby` से accessible बनाओ।
3. Zod जैसा एक schema client और Server Action दोनों पर use करो, और server errors को उसी field पर वापस दिखाओ।

**Hindi:**
1. Validation client पर UX के लिए और server पर सुरक्षा के लिए ज़रूरी है; server हमेशा फिर से check करे।
2. Errors को सही समय (blur या submit) पर दिखाओ, और `aria-invalid` व `aria-describedby` से accessible बनाओ।
3. Zod जैसा एक schema client और Server Action दोनों पर use करो, और server errors को उसी field पर वापस दिखाओ।

---

## ➡️ Next Topic
**79. Forms with Next.js Server Actions** — `useActionState`, `useFormStatus`, progressive enhancement और server-side mutations को एक साथ समझना।
