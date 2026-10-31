# 77. React Hook Form Library
# हिंदी में: React Hook Form — Forms संभालने की performant library

---

## 🔵 Simple Definition (English)
**React Hook Form (RHF)** is a library that manages form state, validation and submission while keeping inputs mostly **uncontrolled** under the hood. It uses `register` to connect inputs, `handleSubmit` to run validation before your handler, and a **proxied `formState`** so components re-render only for the form state they actually read.

## 🔵 सरल परिभाषा (Hindi)
**React Hook Form (RHF)** एक library है जो form state, validation और submission संभालती है, और अंदर से inputs को ज़्यादातर **uncontrolled** रखती है। यह `register` से inputs जोड़ती है, `handleSubmit` से पहले validation चलाती है, और **proxy वाला `formState`** देती है, ताकि component सिर्फ उसी form state के बदलने पर re-render हो जो वह सच में पढ़ता है।

---

## 🔴 Problem it Solves
Controlled forms (topic 75) में हर field के लिए `useState`, `onChange`, error state और submit flag हाथ से लिखने पड़ते हैं। 15 fields का form हो तो हर keystroke पर पूरा form re-render होता है। Validation के rules भी बिखर जाते हैं। RHF यह सब एक जगह और कम code में देता है।

## 🔴 यह क्यों बना? (Hindi)
Naukri या Shaadi.com जैसे sites पर profile form में दर्जनों fields होते हैं। हर field पर अलग state रखना और सबकी errors हाथ से संभालना बोझ है। RHF से form की performance अच्छी रहती है (कम re-renders), validation rules declarative होते हैं, और schema library (Zod) से client और server दोनों पर एक ही rules लागू होते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → useForm({ defaultValues, mode, resolver }) call करो
         → इससे register, handleSubmit, formState, control आदि मिलते हैं

Step 2 → Input में {...register('email', rules)} लगाओ
         → RHF input का ref और onChange/onBlur/name जोड़ देता है
         → value DOM में रहती है (uncontrolled)

Step 3 → User टाइप करता है → RHF internal store में value रखता है
         → Re-render सिर्फ तब, जब वह formState का subscribed हिस्सा बदले (जैसे errors)

Step 4 → handleSubmit(onValid) submit पर:
         a) सारे rules / resolver चलाता है
         b) valid → onValid(data) call होता है
         c) invalid → formState.errors भरता है, onValid नहीं चलता

Step 5 → formState.isSubmitting से loading UI दिखाओ; reset(), setError() भी उपलब्ध

KEY: register = uncontrolled wiring. formState = proxied (सिर्फ पढ़े गए हिस्से पर re-render)।
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → useForm() से register, handleSubmit, formState लो
Step 2 → inputs पर {...register('field', rules)} लगाओ
Step 3 → Typing पर value RHF के अंदर रहती है; re-render सिर्फ ज़रूरत पर
Step 4 → handleSubmit सारे rules चलाता है; valid हो तो onValid, नहीं तो errors
Step 5 → isSubmitting से loading दिखाओ; reset और setError भी हैं
KEY: register uncontrolled wiring है; formState proxy है।
```

---

## 🟡 Real World Example
**Naukri-style job application form:** 12 fields हैं: नाम, फ़ोन, अनुभव, skills, resume upload, और salary। RHF के साथ हर field का validation एक जगह लिखा है। Resume (file) के लिए `register` काम करता है, और custom "Skills" dropdown के लिए `Controller`। Submit पर loading spinner `isSubmitting` से दिखता है, और server ने अगर यह फ़ोन पहले से दर्ज पाया, तो `setError` से उसी field पर error दिखता है।

## 🟡 Real Example Hindi mein
**Naukri जैसा job application form:** 12 fields हैं। हर field का validation एक जगह लिखा है। Resume file के लिए `register` काम करता है, और custom "Skills" dropdown के लिए `Controller`। Submit पर `isSubmitting` से spinner दिखता है, और server ने फ़ोन पहले से दर्ज पाया तो `setError` से उसी field पर error आता है।

---

## 💻 Code Example — Basic

```jsx
import { useForm } from 'react-hook-form';          // library का main hook

// ── BASIC: register + handleSubmit + errors ──
export default function LoginForm() {
  const {
    register,                                        // input को RHF से जोड़ने वाला function
    handleSubmit,                                    // submit wrapper: पहले validation, फिर onValid
    formState: { errors, isSubmitting },             // errors और submit status (proxied)
  } = useForm({
    defaultValues: { email: '', password: '' },     // शुरुआती values
  });

  // सिर्फ valid data पर call होता है; data में सभी fields की values होती हैं
  async function onValid(data) {
    await new Promise(r => setTimeout(r, 500));     // fake API call (500ms)
    console.log('Login:', data);                    // { email, password }
  }

  return (
    <form onSubmit={handleSubmit(onValid)}>          {/* handleSubmit(onValid) event को संभालता है */}
      <input
        placeholder="ईमेल"
        {...register('email', {                      // "email" नाम से field register करो
          required: 'ईमेल ज़रूरी है',                // खाली हो तो यह message
          pattern: { value: /\S+@\S+\.\S+/, message: 'ईमेल सही नहीं है' }, // format
        })}
      />
      {errors.email && <p role="alert">{errors.email.message}</p>} {/* error message */}

      <input
        type="password"
        placeholder="पासवर्ड"
        {...register('password', {
          required: 'पासवर्ड ज़रूरी है',
          minLength: { value: 8, message: 'कम से कम 8 अक्षर' }, // लंबाई check
        })}
      />
      {errors.password && <p role="alert">{errors.password.message}</p>}

      <button type="submit" disabled={isSubmitting}>  {/* submit चल रहा हो तो disable */}
        {isSubmitting ? 'Login हो रहा है...' : 'Login'}
      </button>
    </form>
  );
}
```

## 💻 Code Example — Advanced

```jsx
import { useForm, Controller } from 'react-hook-form';  // Controller: custom components के लिए
import { zodResolver } from '@hookform/resolvers/zod';  // Zod schema को RHF से जोड़ने वाला adapter
import { z } from 'zod';                                 // schema library

// ── ADVANCED: Zod schema, Controller, server error, loading ──

// Schema: एक जगह पर सारे rules (client और server दोनों पर same)
const schema = z.object({
  name: z.string().trim().min(2, 'नाम कम से कम 2 अक्षर'),   // trim के बाद लंबाई check
  phone: z.string().regex(/^\d{10}$/, '10 अंकों का फ़ोन'),  // exactly 10 digits
  city: z.string().min(1, 'शहर चुनो'),                       // खाली string नहीं होना चाहिए
  agree: z.literal(true, { errorMap: () => ({ message: 'शर्तें मानो' }) }), // सिर्फ true
});

// Custom component: plain select जो value/onChange लेता है (RHF से सीधे नहीं जुड़ता)
function CitySelect({ value, onChange, onBlur }) {
  return (
    <select value={value} onChange={onChange} onBlur={onBlur}>
      <option value="">शहर चुनो</option>
      <option value="delhi">Delhi</option>
      <option value="mumbai">Mumbai</option>
      <option value="bengaluru">Bengaluru</option>
    </select>
  );
}

// Fake server call: असली app में fetch/Server Action होगा
async function submitToServer(data) {
  await new Promise(r => setTimeout(r, 300));           // network delay
  if (data.phone === '9999999999') return { error: 'phone' }; // duplicate phone demo
  return { ok: true };
}

export default function JobForm() {
  const {
    register,                                           // सामान्य inputs के लिए
    handleSubmit,                                       // submit wrapper
    control,                                            // Controller को चाहिए
    setError,                                           // server error को field पर डालने के लिए
    reset,                                              // सफल submit पर खाली करने के लिए
    formState: { errors, isSubmitting },                // errors और loading
  } = useForm({
    resolver: zodResolver(schema),                      // Zod rules अब RHF validation हैं
    mode: 'onBlur',                                     // field छोड़ने पर validate करो (पहले नहीं)
    defaultValues: { name: '', phone: '', city: '', agree: false }, // सभी fields की शुरुआत
  });

  async function onValid(data) {
    const res = await submitToServer(data);            // server call
    if (res.error === 'phone') {
      setError('phone', { type: 'server', message: 'यह फ़ोन पहले से दर्ज है' }); // उसी field पर error
      return;                                          // reset मत करो, user सुधार सके
    }
    reset();                                           // सफल: सारे fields default पर
  }

  return (
    <form onSubmit={handleSubmit(onValid)} noValidate> {/* native validation बंद, Zod संभालेगा */}
      <input {...register('name')} placeholder="नाम" />
      {errors.name && <p role="alert">{errors.name.message}</p>}

      <input {...register('phone')} inputMode="numeric" placeholder="फ़ोन" />
      {errors.phone && <p role="alert">{errors.phone.message}</p>}

      {/* Controller: custom component को RHF की value और onChange देता है */}
      <Controller
        name="city"
        control={control}                              // उसी form का control
        render={({ field: { value, onChange, onBlur } }) => (
          <CitySelect value={value} onChange={onChange} onBlur={onBlur} />
        )}
      />
      {errors.city && <p role="alert">{errors.city.message}</p>}

      <label>
        <input type="checkbox" {...register('agree')} /> शर्तें मानता हूँ
      </label>
      {errors.agree && <p role="alert">{errors.agree.message}</p>}

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'भेजा जा रहा है...' : 'Apply करो'}
      </button>
    </form>
  );
}
```

---

## 🟠 Real app integration

Next.js में RHF client पर रहता है, और **वही Zod schema** server action में भी चलता है। Client पर UX के लिए validation होता है, पर भरोसा server पर ही होता है।

```jsx
// lib/schemas.js — एक schema, दो जगह उपयोग
import { z } from 'zod';
export const applySchema = z.object({
  name: z.string().trim().min(2, 'नाम कम से कम 2 अक्षर'), // rules
  phone: z.string().regex(/^\d{10}$/, '10 अंकों का फ़ोन'),
});
```

```jsx
// app/apply/actions.js — Server Action: client पर भरोसा नहीं, फिर से validate करो
'use server';
import { applySchema } from '@/lib/schemas';           // वही schema
export async function applyAction(values) {
  const parsed = applySchema.safeParse(values);        // server पर validation
  if (!parsed.success) return { ok: false, errors: parsed.error.flatten().fieldErrors };
  await saveApplication(parsed.data);                  // तुम्हारा data layer (illustrative)
  return { ok: true };
}
```

```jsx
// app/apply/ApplyForm.js — Client Component में RHF
'use client';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { applySchema } from '@/lib/schemas';
import { applyAction } from './actions';

export default function ApplyForm() {
  const { register, handleSubmit, setError, formState: { errors, isSubmitting } } = useForm({
    resolver: zodResolver(applySchema),                // client validation (UX)
  });
  async function onValid(values) {
    const res = await applyAction(values);             // server action call
    if (!res.ok) {
      // server की field errors को उसी field पर दिखाओ
      Object.entries(res.errors).forEach(([field, msgs]) =>
        setError(field, { message: msgs[0] })
      );
    }
  }
  return (
    <form onSubmit={handleSubmit(onValid)}>
      <input {...register('name')} />{errors.name && <p>{errors.name.message}</p>}
      <input {...register('phone')} />{errors.phone && <p>{errors.phone.message}</p>}
      <button disabled={isSubmitting}>Apply</button>
    </form>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** `register` के साथ `value` prop भी देना
```jsx
// ❌ Wrong: RHF value खुद संभालता है; दोनों मिलाने से conflict होता है
<input value={email} {...register('email')} />

// ✅ Right: सिर्फ register। Value RHF की है, state में मत रखो।
<input {...register('email')} />
```

❌ **Mistake 2:** Custom component पर `register` लगाना
```jsx
// ❌ Wrong: CitySelect में ref या onChange सही नहीं जुड़ते; value नहीं पहुंचेगी
<CitySelect {...register('city')} />

// ✅ Right: Controller से value और onChange दो
<Controller name="city" control={control}
  render={({ field }) => <CitySelect value={field.value} onChange={field.onChange} />} />
```

---

## 🧠 Tricky Interview Question

```jsx
import { useForm } from 'react-hook-form';

export default function NameForm() {
  const { register, handleSubmit } = useForm({ defaultValues: { name: '' } });

  return (
    <form onSubmit={handleSubmit(d => console.log('OK', JSON.stringify(d)))}>
      <input {...register('name', { required: 'Naam chahiye' })} />
      <button>Go</button>
    </form>
  );
}
// User input में सिर्फ तीन spaces टाइप करता है ("   ") और Go दबाता है।
// Console में क्या छपेगा? क्या error दिखेगा?
```

**Answer:** Console में `OK {"name":"   "}` छपेगा, और कोई error नहीं दिखेगा। `required` rule सिर्फ यह देखता है कि value खाली string है या नहीं। Spaces से बनी string खाली नहीं है, इसलिए rule पास हो जाता है। यह HTML की `required` attribute के व्यवहार जैसा ही है। Fix यह है कि `validate` rule लिखो, जैसे `validate: v => v.trim() !== '' || 'Naam chahiye'`, या Zod में `z.string().trim().min(1)` use करो, जो trim के बाद लंबाई देखता है।

---

## ⚫ Interview Questions + Answers

**Q1: React Hook Form का मुख्य फायदा क्या है?**
A1: कम re-renders। Inputs uncontrolled wiring से जुड़े रहते हैं, और `formState` proxied है, इसलिए सिर्फ वही state बदलने पर re-render होता है जो component पढ़ता है। इससे बड़े forms तेज़ रहते हैं।

**Q2: `register` क्या करता है?**
A2: यह input को form से जोड़ता है: `name`, `ref`, `onChange`, `onBlur` देता है, और validation rules लागू करता है। Value DOM में रहती है, state में नहीं।

**Q3: `Controller` कब चाहिए?**
A3: जब component native input न हो, जैसे custom select, date picker या rich text editor, जो `value` और `onChange` से चलता है। `Controller` उसे RHF की value और onChange देता है।

**Q4: `mode` option क्या तय करता है?**
A4: यह तय करता है कि validation कब चले: `onSubmit` (default), `onBlur`, `onChange`, `onTouched`, या `all`। Submit के बाद `reValidateMode` (default `onChange`) से दोबारा validation होता है।

**Q5: Server errors को form field पर कैसे दिखाएं?**
A5: `setError('field', { type: 'server', message: '...' })` से। इससे error उसी input के `errors.field` में आता है, और form submit होने से रोका नहीं जाता, जब तक तुम खुद reset न करो।

---

## 🔷 When to Use + When Not to Use
✅ **Use React Hook Form when:**
- Forms में 5+ fields हों, या validation complex हो
- Performance मायने रखती हो (बड़े forms, हर keystroke पर heavy UI)
- Zod/Yup schema से client और server पर एक जैसे rules चाहिए
- Loading, server errors और reset जैसी form states की ज़रूरत हो

❌ **Avoid when:**
- सिर्फ एक या दो fields हैं, तो plain state या `FormData` काफी है
- Form की हर value को हर keystroke पर UI में live दिखाना है (फिर भी RHF `watch` चलता है, पर सोच-समझकर)
- Library का बोझ किसी छोटी page के लिए बेमतलब लगे
- Form पहले से React 19 `<form action>` और `useActionState` से अच्छी तरह चल रहा है

---

## 📊 Visual Diagram

```
  useForm({ resolver, mode, defaultValues })
        │
        ├── register('name', rules) ──► <input>  (ref + name, uncontrolled)
        ├── Controller (control)    ──► custom <CitySelect>  (value/onChange)
        │
        ├── formState (Proxy)  ──► errors, isSubmitting  (सिर्फ पढ़े गए हिस्से पर re-render)
        │
        └── handleSubmit(onValid)
                 │
                 ├── resolver / rules चलाओ
                 │      ├── invalid ──► errors भरो, onValid नहीं
                 │      └── valid   ──► onValid(data)
                 │                         │
                 │                         ├── server error ──► setError(field)
                 │                         └── success      ──► reset()
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `useForm` | Form की मुख्य hook, सब APIs देती है | Form की मुख्य hook |
| `register` | Input को RHF से जोड़ने वाला function | Input को RHF से जोड़ने वाला function |
| `handleSubmit` | Validation के बाद handler चलाने वाला wrapper | Validation के बाद handler चलाने वाला wrapper |
| `formState` | Proxied form status (errors, isSubmitting) | Proxy वाला form status |
| `Controller` | Custom components के लिए RHF bridge | Custom components के लिए bridge |
| `resolver` | बाहरी schema (Zod, Yup) को RHF से जोड़ने वाला adapter | Schema को RHF से जोड़ने वाला adapter |
| `setError` | Field पर manual error डालना | Field पर manual error डालना |

---

## ⚡ 3-Line Summary
**English:**
1. React Hook Form inputs को uncontrolled wiring से जोड़ता है, इसलिए form तेज़ रहता है।
2. `register` से inputs, `handleSubmit` से submit, और `formState` से errors व loading मिलते हैं।
3. Custom components के लिए `Controller`, और client-server पर एक जैसी validation के लिए Zod resolver use करो।

**Hindi:**
1. React Hook Form inputs को uncontrolled wiring से जोड़ता है, इसलिए form तेज़ रहता है।
2. `register` से inputs, `handleSubmit` से submit, और `formState` से errors व loading मिलते हैं।
3. Custom components के लिए `Controller`, और client-server पर एक जैसी validation के लिए Zod resolver use करो।

---

## ➡️ Next Topic
**78. Form Validation in React** — native HTML validation, schema validation, field errors की accessibility, और server-side validation का सही संतुलन।
