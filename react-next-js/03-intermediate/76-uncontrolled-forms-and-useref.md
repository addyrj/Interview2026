# 76. Uncontrolled Forms + useRef
# हिंदी में: Uncontrolled Forms + useRef — DOM से सीधे value पढ़ना

---

## 🔵 Simple Definition (English)
An **uncontrolled** form field keeps its value in the **DOM**, not in React state. React reads it only when needed (on submit, through a `ref` or `FormData`). **`useRef`** gives you a mutable `{ current }` box that persists across renders **without** causing a re-render, and it is the usual way to get a reference to a DOM node.

## 🔵 सरल परिभाषा (Hindi)
**Uncontrolled** form field अपनी value **DOM** में रखता है, React state में नहीं। React उसे सिर्फ ज़रूरत पड़ने पर पढ़ता है (submit के समय, `ref` या `FormData` से)। **`useRef`** एक mutable `{ current }` box देता है जो render के बीच बना रहता है और **re-render नहीं करवाता**। DOM node का reference लेने का यही आम तरीका है।

---

## 🔴 Problem it Solves
हर keystroke पर state बदलने से component re-render होता है। एक लंबे form में यह हर बार पूरे form को दोबारा बनाता है। कई बार हमें सिर्फ submit के समय value चाहिए, या किसी non-React library को DOM node चाहिए (जैसे focus, scroll, video player)। इसके अलावा **file input** की value को React state से control करना संभव ही नहीं, क्योंकि browser उसे read-only रखता है।

## 🔴 यह क्यों बना? (Hindi)
IRCTC जैसी form में 15 fields हैं। हर keystroke पर पूरा form re-render करना बेकार है। Uncontrolled inputs से DOM खुद value रखता है और submit पर सिर्फ एक बार पढ़ा जाता है। File upload के लिए तो यह ज़रूरी है: Instagram पर profile photo चुनते समय browser ही file पकड़ता है, React नहीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Input को ref दो या name दो (value state में नहीं)
         const nameRef = useRef(null);
         <input ref={nameRef} name="name" defaultValue="" />

Step 2 → User टाइप करता है → value सिर्फ DOM में बदलती है
         (कोई setState नहीं → कोई re-render नहीं)

Step 3 → Submit पर value पढ़ो:
         nameRef.current.value        या     new FormData(form).get('name')

Step 4 → useRef का box "current" में DOM node रखता है
         ref.current बदलने से component re-render नहीं होता

Step 5 → Reset: form.reset() या ref से value खाली करो

KEY: defaultValue सिर्फ शुरुआत के लिए है। बाद में बदलने से input अपने-आप नहीं बदलता।
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Input को ref या name दो, value state में मत रखो
Step 2 → User type करता है → DOM में value बदलती है, re-render नहीं
Step 3 → Submit पर ref.current.value या FormData से पढ़ो
Step 4 → useRef का current बदलने से re-render नहीं होता
Step 5 → reset के लिए form.reset() या ref से खाली करो
KEY: defaultValue सिर्फ शुरू में लागू होता है।
```

---

## 🟡 Real World Example
**IRCTC-style passenger form:** 6 passengers के लिए नाम, उम्र और gender fields हैं। Uncontrolled inputs से typing पूरी तरह smooth रहती है, क्योंकि कोई re-render नहीं होता। Submit पर `FormData` से सारी values एक साथ निकाल ली जाती हैं। Validation में अगर कोई नाम खाली है, तो उसी input पर `ref.focus()` होता है, ताकि user सीधे वहीं पहुंचे।

## 🟡 Real Example Hindi mein
**IRCTC जैसा passenger form:** 6 passengers के नाम, उम्र और gender fields हैं। Uncontrolled inputs से typing smooth रहती है, क्योंकि re-render नहीं होता। Submit पर `FormData` से सारी values एक साथ मिलती हैं। कोई नाम खाली हो तो उसी input पर `focus()` होता है।

---

## 💻 Code Example — Basic

```jsx
import { useRef } from 'react';                        // useRef React से

// ── BASIC: uncontrolled input + ref ──
export default function SearchBox() {
  const inputRef = useRef(null);                       // DOM input का box; शुरू में null

  function handleSubmit(e) {
    e.preventDefault();                                // page reload रोको
    const value = inputRef.current.value;              // DOM से सीधे value पढ़ो (state नहीं)
    console.log('Searching:', value);                  // search करो
    inputRef.current.focus();                          // submit के बाद फिर input पर focus
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        ref={inputRef}                                 // React इस input का DOM node inputRef.current में रखेगा
        defaultValue=""                                // सिर्फ शुरुआती value; बाद में state नहीं बनता
        placeholder="खोजो"
      />
      <button type="submit">Search</button>
    </form>
  );
}
```

## 💻 Code Example — Advanced

```jsx
import { useEffect, useRef, useState } from 'react';

// ── ADVANCED: uncontrolled signup form — FormData, refs, focus, timer ──

export default function SignupForm() {
  const formRef = useRef(null);              // पूरे <form> का DOM node (reset और FormData के लिए)
  const nameRef = useRef(null);              // name input का DOM node (focus के लिए)
  const emailRef = useRef(null);             // email input का DOM node
  const timerRef = useRef(null);             // setTimeout का id: render में नहीं दिखता, सिर्फ store होता है
  const [preview, setPreview] = useState(null); // preview URL: UI पर असर है, इसलिए state में
  const [message, setMessage] = useState('');   // status message

  // Unmount पर pending timer साफ़ करो (memory leak और बाद में setState से बचो)
  useEffect(() => {
    return () => clearTimeout(timerRef.current);
  }, []);

  function handleFile(e) {
    const file = e.target.files[0];          // पहली चुनी गई file (या undefined)
    if (!file) return;                       // कुछ नहीं चुना तो रुक जाओ
    if (preview) URL.revokeObjectURL(preview); // पुराना preview URL हटाओ (memory बचाओ)
    setPreview(URL.createObjectURL(file));     // नया preview URL बनाओ
  }

  function handleSubmit(e) {
    e.preventDefault();                       // reload रोको
    const data = new FormData(formRef.current); // सभी named inputs की values एक साथ, DOM से
    const name = (data.get('name') ?? '').toString().trim(); // string में बदलो और trim करो
    const email = (data.get('email') ?? '').toString();

    if (name.length < 2) {                    // सरल validation
      nameRef.current.focus();                // गलत field पर focus
      setMessage('नाम बहुत छोटा है');
      return;                                 // आगे मत बढ़ो
    }
    if (!email.includes('@')) {
      emailRef.current.focus();
      setMessage('ईमेल सही नहीं है');
      return;
    }

    setMessage('Saving...');
    clearTimeout(timerRef.current);           // पिछला timer (अगर था) रद्द करो
    timerRef.current = setTimeout(() => {     // timer id ref में रखो, ताकि बाद में रद्द कर सकें
      setMessage('Account बन गया!');
      formRef.current.reset();                // सभी uncontrolled inputs DOM स्तर पर खाली
      setPreview(null);                       // preview भी हटाओ
    }, 800);
  }

  return (
    <form ref={formRef} onSubmit={handleSubmit}>
      <input ref={nameRef} name="name" placeholder="नाम" />            {/* uncontrolled: value DOM में */}
      <input ref={emailRef} name="email" type="email" placeholder="ईमेल" />
      <input name="avatar" type="file" accept="image/*" onChange={handleFile} /> {/* file हमेशा uncontrolled */}
      {preview && <img src={preview} alt="preview" width={80} />}     {/* चुनी हुई फ़ोटो का preview */}
      <button type="submit">Sign up</button>
      <p role="status">{message}</p>                                  {/* screen reader को status दिखे */}
    </form>
  );
}
```

---

## 🟠 Real app integration

Next.js (React 19) में `<form action={fn}>` uncontrolled inputs के साथ सबसे साफ़ पैटर्न है। Browser FormData बनाता है, server action उसे पढ़ता है, और सफल submit के बाद React inputs को अपने-आप reset कर देता है।

```jsx
// app/subscribe/actions.js — server पर चलने वाला handler
'use server';                                          // इस file के exports server functions हैं
export async function subscribe(formData) {            // React FormData सीधे यहां देता है
  const email = formData.get('email');                 // string या File (यहां string)
  if (typeof email !== 'string' || !email.includes('@')) {
    return;                                            // invalid: real app में error state लौटाओ
  }
  await addToNewsletter(email);                        // तुम्हारा data layer (illustrative)
}
```

```jsx
// app/subscribe/page.js — Server Component भी हो सकता है, JS के बिना भी काम करता है
import { subscribe } from './actions';                 // server action import

export default function Page() {
  return (
    <form action={subscribe}>                          {/* action server function को FormData देता है */}
      <input name="email" type="email" required />     {/* uncontrolled: कोई state नहीं */}
      <button type="submit">Subscribe</button>         {/* submit पर reset अपने-आप होता है */}
    </form>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Render के दौरान `ref.current` पढ़ना
```jsx
// ❌ Wrong: पहले render में ref.current null है, और ref बदलने से re-render नहीं होता
function Bad() {
  const ref = useRef(null);
  return <p>Length: {ref.current.value.length}</p>; // TypeError on first render
}

// ✅ Right: DOM value सिर्फ event handler में पढ़ो, या जब उसे UI पर दिखाना हो तो state रखो
function Good() {
  const ref = useRef(null);
  function check() {
    alert(ref.current.value.length);                   // event के समय ref.current तैयार है
  }
  return <><input ref={ref} /><button onClick={check}>Check</button></>;
}
```

❌ **Mistake 2:** `defaultValue` बदलने की उम्मीद करना
```jsx
// ❌ Wrong: defaultValue बदलने से input की दिखती value नहीं बदलती
function Greeting({ name }) {
  return <input defaultValue={name} />;   // name बदला, पर input अपनी दर्ज की हुई value रखता है
}

// ✅ Right: बदलना है तो controlled बनाओ (value + onChange) या key बदलकर remount करो
function Greeting({ name }) {
  return <input key={name} defaultValue={name} />; // name बदला → नया input, नई defaultValue
}
```

---

## 🧠 Tricky Interview Question

```jsx
import { useState } from 'react';

function Greeting({ name }) {
  return <input defaultValue={name} />;
}

export default function App() {
  const [name, setName] = useState('Ravi');            // initial name
  return (
    <div>
      <Greeting name={name} />
      <button onClick={() => setName('Sneha')}>Sneha करो</button>
    </div>
  );
}
// Step 1: input में user "Amit" टाइप करता है।
// Step 2: "Sneha करो" button दबाया जाता है।
// Question: Input में अब क्या दिखेगा?
```

**Answer:** Input में `Amit` ही रहेगा, `Sneha` नहीं। `defaultValue` सिर्फ शुरुआती value के लिए है। React `defaultValue` attribute को अपडेट करता है, पर browser का input अपनी दिखती value नहीं बदलता, क्योंकि HTML में value का "dirty" flag तब सेट हो जाता है जब value बदली जाए। User के type करने से यह flag सेट होता है, और React mount के समय खुद `node.value` सेट करता है, इसलिए यह flag पहले से लगा होता है। नतीजा: `defaultValue` बदलने से दिखती value कभी नहीं बदलती, चाहे user ने type किया हो या नहीं। बदलाव चाहिए तो `key={name}` दो (remount) या input को controlled बनाओ।

---

## ⚫ Interview Questions + Answers

**Q1: Uncontrolled input क्या है?**
A1: ऐसा input जिसकी value DOM में रहती है, React state में नहीं। React उसे ref या FormData से submit के समय पढ़ता है। Initial value के लिए `defaultValue` दिया जाता है।

**Q2: `useRef` और `useState` में क्या फर्क है?**
A2: `useState` बदलने पर component re-render होता है और UI update होता है। `useRef` का `current` बदलने पर re-render नहीं होता, इसलिए इसे DOM nodes, timer ids, या ऐसी values के लिए use करो जो UI पर सीधे नहीं दिखतीं।

**Q3: React 19 में `ref` को लेकर क्या बदला?**
A3: `ref` अब एक सामान्य prop है, इसलिए function component को `forwardRef` लपेटने की ज़रूरत नहीं पड़ती। Ref callback अब cleanup function भी return कर सकता है।

**Q4: File input controlled क्यों नहीं हो सकता?**
A4: Browser security की वजह से file input की `value` सिर्फ खाली करने की अनुमति देता है, किसी और value को set करने की नहीं। इसलिए file input हमेशा uncontrolled रहता है, और उसकी file `onChange` में `e.target.files` से पढ़ी जाती है।

**Q5: `FormData` का उपयोग कब करें?**
A5: जब सारे fields एक साथ चाहिए हों, जैसे submit पर पूरा form। `new FormData(form)` सभी named inputs की values देता है। Multiple values (जैसे checkboxes) के लिए `data.getAll('name')` use होता है।

---

## 🔷 When to Use + When Not to Use
✅ **Use uncontrolled + useRef when:**
- File inputs (upload, avatar, documents)
- Submit के समय ही data चाहिए, हर keystroke पर नहीं
- बड़े forms जिनमें re-render का cost ज़्यादा हो
- DOM operations: focus, scroll, select text, media play/pause
- Non-React libraries को DOM node देना

❌ **Avoid when:**
- UI को live बदलना हो (जैसे character count, live validation, dependent dropdown)
- Value को दूसरी jagah पर भी दिखाना हो, तो state बेहतर है
- `ref.current` को render में पढ़ने की कोशिश करना
- `defaultValue` पर भरोसा करके बाद में value बदलने की उम्मीद करना

---

## 📊 Visual Diagram

```
  CONTROLLED (state खुद रखता है)        UNCONTROLLED (DOM रखता है)
  ───────────────────────────────       ───────────────────────────────
  user types                            user types
     │                                     │
     ▼                                     ▼
  onChange → setState                   DOM value बदलती है
     │                                     │  (कोई re-render नहीं)
     ▼                                     │
  re-render → value prop                   │
     │                                     │
     ▼                                     ▼
  DOM sync                              submit पर:
                                        ref.current.value  या  FormData

  useRef box:
  ┌────────────────────────┐
  │ { current: <DOM node> }│ ◄── React यहां DOM node रखता है
  └────────────────────────┘     बदलने से re-render नहीं
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Uncontrolled input | Value DOM में रखने वाला input | Value DOM में रखने वाला input |
| `useRef` | Re-render बिना persist होने वाला mutable box | बिना re-render बने रहने वाला box |
| `ref.current` | Box के अंदर की value (अक्सर DOM node) | Box के अंदर की value |
| `defaultValue` | शुरुआती value, बाद में असर नहीं | शुरुआत की value, बाद में असर नहीं |
| `FormData` | Form की सभी values का browser object | Form की सारी values वाला object |
| Dirty flag | User ने input edit किया या नहीं, इसका flag | User ने input बदला या नहीं, का flag |

---

## ⚡ 3-Line Summary
**English:**
1. Uncontrolled input की value DOM में रहती है, और React उसे submit पर `ref` या `FormData` से पढ़ता है।
2. `useRef` का `current` बदलने से re-render नहीं होता; इसलिए DOM nodes और timer ids उसमें रखो।
3. File inputs हमेशा uncontrolled रहते हैं; बदलाव के लिए `defaultValue` नहीं, `key` या controlled input use करो।

**Hindi:**
1. Uncontrolled input की value DOM में रहती है, और React उसे submit पर `ref` या `FormData` से पढ़ता है।
2. `useRef` का `current` बदलने से re-render नहीं होता; इसलिए DOM nodes और timer ids उसमें रखो।
3. File inputs हमेशा uncontrolled रहते हैं; बदलाव के लिए `defaultValue` नहीं, `key` या controlled input use करो।

---

## ➡️ Next Topic
**77. React Hook Form Library** — uncontrolled performance के साथ declarative validation और form state को संभालने का production-ready तरीका।
