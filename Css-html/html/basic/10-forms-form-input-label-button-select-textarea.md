# 10. Forms (form, input, label, button, select, textarea)
# हिंदी में: Forms — User से Data लेना

---

## 🔵 Simple Definition (English)
A **form** (`<form>`) collects input from the user and sends it to a server. It contains controls: `<input>`, `<textarea>`, `<select>`, `<button>`, each ideally paired with a `<label>` that names it.

## 🔵 सरल परिभाषा (Hindi)
**Form** (`<form>`) user से input लेकर server को भेजता है। इसमें controls होते हैं: `<input>`, `<textarea>`, `<select>`, `<button>`, और हर control के साथ उसका नाम बताने वाला `<label>`।

---

## 🔴 Problem it Solves
```
Websites needed a standard way to receive data: login, signup, search, checkout,
comments, uploads.

WITHOUT <form>:
  - You would write JS for every field, key press and request
  - No built-in Enter-to-submit, validation, autofill, password managers
  - Inaccessible: no labels, no focus order

WITH <form>:
  - Browser collects all fields with a name and sends them (GET or POST)
  - Enter key submits, native validation, autofill, "remember password"
  - Labels give bigger click targets and screen-reader names
  - Works even with JS disabled (progressive enhancement)
```

## 🔴 यह क्यों बना? (Hindi)
```
Websites को user से data लेने का standard तरीका चाहिए था: login, signup, search,
checkout, comments, uploads।

<form> के बिना:
  - हर field, key press और request के लिए JS लिखनी पड़ती
  - Enter से submit, validation, autofill, password manager नहीं मिलते
  - Accessible नहीं: labels और focus order नहीं

<form> के साथ:
  - Browser name वाले सभी fields इकट्ठा करके GET या POST से भेजता है
  - Enter से submit, native validation, autofill
  - Label से click area बड़ा और screen reader को नाम मिलता है
  - JS बंद होने पर भी काम करता है
```

---

## 🟢 How it Works — Step by Step

```
FORM ANATOMY:
──────────────────────────────────────────────────────────
<form action="/login" method="post">
  <label for="email">Email</label>            1. label linked to input by for = id
  <input id="email" name="email" type="email" required>
                                              2. name = the KEY sent to the server
  <label for="role">Role</label>
  <select id="role" name="role">              3. dropdown
    <option value="user">User</option>
  </select>

  <label for="msg">Message</label>
  <textarea id="msg" name="msg" rows="4"></textarea>   4. multi-line text

  <button type="submit">Sign in</button>      5. submits the form
</form>

WHAT HAPPENS ON SUBMIT:
  1. Browser runs built-in validation (required, type, pattern...)
  2. If valid: collects every control that has a NAME (and is not disabled)
  3. Encodes as name=value&name2=value2 (default: application/x-www-form-urlencoded)
  4. Sends to `action` URL with `method` (GET -> in URL query, POST -> in body)
  5. Page navigates to the response (unless JS calls event.preventDefault())

THE ELEMENTS:
  <form>      container; action, method, enctype, novalidate, autocomplete
  <input>     void element; behaviour depends on `type` (next topics)
  <label>     for="id" (or wrap the input inside the label). Click label = focus input
  <textarea>  multi-line; rows/cols; initial text goes BETWEEN tags
  <select>    <option value> list; multiple, size; <optgroup label>
  <button>    type="submit" (default!) | "button" | "reset"
  <fieldset> + <legend>   group related controls (e.g., radio group)
  <datalist>  suggestions for an input; <output> shows a result

IMPORTANT ATTRIBUTES: name, id, value, placeholder, required, disabled, readonly,
                     autofocus, autocomplete (e.g. "email", "current-password")

NOTE: id is for label/CSS/JS; NAME is what is sent. A field without name is NOT submitted.
      placeholder is NOT a label.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Submit पर क्या होता है:
  1. Browser पहले built-in validation चलाता है (required, type...)
  2. ठीक हो तो हर उस control का data लेता है जिसका NAME है
  3. name=value&name2=value2 में encode करता है
  4. action URL पर method (GET या POST) से भेजता है
  5. Response page खुलता है (JS में preventDefault() हो तो नहीं)

याद रखो:
  - label का for = input का id; label पर click करने से input focus होता है
  - सिर्फ name वाले fields ही server को जाते हैं (id नहीं)
  - <button> का default type "submit" है; सिर्फ click के लिए type="button" लिखो
  - placeholder, label की जगह नहीं ले सकता
```

---

## 🟡 Real World Example
**Swiggy login/checkout and Gmail sign-in:** Gmail's sign-in is a `<form>` with an email input (`type="email"`, `autocomplete="username"`), a password input, and a "Next" submit button. Pressing Enter submits it, and the browser's password manager recognises the fields. Swiggy's address form uses text inputs, a `<select>` for address type (Home/Work), a `<textarea>` for delivery instructions, and a labelled checkbox "Save as default". Floating labels in these UIs are still real `<label>` elements.

## 🟡 Real Example Hindi mein
**Swiggy login/checkout और Gmail sign-in:** Gmail का sign-in एक `<form>` है जिसमें email input (`type="email"`, `autocomplete="username"`), password input और "Next" submit button है। Enter दबाने पर submit होता है और browser का password manager fields पहचान लेता है। Swiggy के address form में text inputs, address type (Home/Work) के लिए `<select>`, delivery instructions के लिए `<textarea>` और "Save as default" वाला labelled checkbox होता है। इन UIs के floating labels भी असल में `<label>` ही हैं।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Delivery Address Form</title>
  <style>
    * { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; background: #f1f1f6; padding: 20px; }

    form { max-width: 440px; margin: 0 auto; background: #fff; padding: 24px;
           border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,.1); }
    h1 { margin-top: 0; font-size: 22px; }

    .field { margin-bottom: 16px; }                       /* spacing between fields */
    label { display: block; font-weight: 600; margin-bottom: 6px; }   /* label above input */

    /* Shared look for text-like controls */
    input[type="text"], input[type="tel"], input[type="email"], select, textarea {
      width: 100%; padding: 10px 12px; font: inherit;     /* inherit font (forms don't by default) */
      border: 1px solid #bbb; border-radius: 8px; background: #fff;
    }
    textarea { resize: vertical; min-height: 80px; }      /* allow vertical resize only */

    /* Clear focus ring (never remove without replacing) */
    input:focus-visible, select:focus-visible, textarea:focus-visible, button:focus-visible {
      outline: 3px solid #fc8019; outline-offset: 1px;    /* Swiggy orange */
    }

    fieldset { border: 1px solid #ddd; border-radius: 8px; margin: 0 0 16px; padding: 12px; }
    legend { font-weight: 600; padding: 0 6px; }
    .inline label { display: inline-block; font-weight: 400; margin: 0 14px 0 4px; }

    .req { color: #d32f2f; }                              /* required asterisk */
    .actions { display: flex; gap: 10px; }
    button { font: inherit; padding: 12px 18px; border: 0; border-radius: 8px; cursor: pointer; }
    .primary { background: #fc8019; color: #fff; flex: 1; font-weight: 700; }
    .secondary { background: #eee; }
    #result { margin-top: 16px; background: #e8f5e9; padding: 10px; border-radius: 8px; display: none;
              white-space: pre-wrap; font-family: monospace; font-size: 13px; }
  </style>
</head>
<body>

  <!-- action/method decide where/how data goes; we intercept with JS for the demo -->
  <form id="addr" action="/save-address" method="post">
    <h1>Delivery address</h1>

    <div class="field">
      <!-- for="name" connects this label to the input with id="name" -->
      <label for="name">Full name <span class="req" aria-hidden="true">*</span></label>
      <input type="text" id="name" name="fullName" autocomplete="name" required>
    </div>

    <div class="field">
      <label for="phone">Phone</label>
      <input type="tel" id="phone" name="phone" autocomplete="tel" placeholder="98765 43210">
    </div>

    <div class="field">
      <label for="type">Address type</label>
      <select id="type" name="addressType">
        <option value="">-- choose --</option>
        <option value="home">Home</option>
        <option value="work">Work</option>
        <option value="other">Other</option>
      </select>
    </div>

    <div class="field">
      <label for="note">Delivery instructions</label>
      <textarea id="note" name="note" rows="3" placeholder="Ring the bell twice"></textarea>
    </div>

    <!-- fieldset + legend groups related radios for screen readers -->
    <fieldset class="inline">
      <legend>Payment</legend>
      <input type="radio" id="upi" name="pay" value="upi" checked><label for="upi">UPI</label>
      <input type="radio" id="cod" name="pay" value="cod"><label for="cod">Cash</label>
    </fieldset>

    <!-- Checkbox with label wrapping the input: no for/id needed -->
    <div class="field">
      <label style="font-weight:400"><input type="checkbox" name="makeDefault" value="yes"> Save as default address</label>
    </div>

    <div class="actions">
      <button type="reset" class="secondary">Reset</button>
      <button type="submit" class="primary">Save address</button>
    </div>
    <pre id="result"></pre>
  </form>

  <script>
    // Demo only: show what the browser WOULD send, then stop the real submit
    document.getElementById("addr").addEventListener("submit", (e) => {
      e.preventDefault();                                    // stop navigation
      const data = new FormData(e.target);                   // collects fields that have a name
      const out = document.getElementById("result");
      out.style.display = "block";
      out.textContent = JSON.stringify(Object.fromEntries(data), null, 2);
    });
  </script>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Controlled component: React state is the single source of truth
"use client";
import { useState } from "react";

export default function AddressForm() {
  const [form, setForm] = useState({ fullName: "", addressType: "home" });

  const onChange = (e) =>                    // one handler for all fields using name
    setForm({ ...form, [e.target.name]: e.target.value });

  const onSubmit = async (e) => {
    e.preventDefault();                       // stop full page reload
    await fetch("/api/address", { method: "POST", body: JSON.stringify(form) });
  };

  return (
    <form onSubmit={onSubmit} className="space-y-4 max-w-md">
      {/* JSX: htmlFor instead of for; className instead of class */}
      <label htmlFor="fullName" className="block font-semibold">Full name</label>
      <input id="fullName" name="fullName" value={form.fullName} onChange={onChange}
             className="w-full border rounded-lg p-2" required />
      <select name="addressType" value={form.addressType} onChange={onChange}>
        <option value="home">Home</option>
        <option value="work">Work</option>
      </select>
      <button type="submit" className="bg-orange-500 text-white px-4 py-2 rounded-lg">Save</button>
    </form>
  );
}

// 2. Uncontrolled + FormData (less re-rendering):
//    const data = Object.fromEntries(new FormData(e.currentTarget));

// 3. Next.js Server Actions (App Router): <form action={serverAction}> works without client JS.
async function save(formData) { "use server"; const name = formData.get("fullName"); /* DB */ }
// <form action={save}> <input name="fullName" /> <button>Save</button> </form>

// 4. Libraries: React Hook Form (+ Zod) for large forms; Tailwind @tailwindcss/forms plugin
//    for form resets.
```

---

## ⚫ Interview Questions + Answers

**Q1: Why use `<label>` and how do you connect it to an input?**
A1: A label gives the input an **accessible name** (screen readers read it) and enlarges the click target (click label -> focus/toggle input). Connect with `for="id"` matching the input's `id`, or by wrapping the input inside the label. Placeholder text is not a substitute: it disappears when typing and has weak accessibility.

**Q2: What is the difference between `id` and `name` on inputs?**
A2: `id` is a unique identifier for the DOM (label `for`, CSS, JS, anchors). `name` is the **key** under which the value is sent in the form submission and used to group radio buttons. Fields without `name` are not submitted.

**Q3: What is the default `type` of a `<button>` inside a form?**
A3: `submit`. So any button in a form submits it unless you write `type="button"`. This is a classic bug when a "Cancel" or "Show password" button reloads the page. In React, also remember `e.preventDefault()` in `onSubmit`.

**Q4: `<input>` vs `<textarea>` vs `<select>`?**
A4: `<input>` is a void element for single-line values (behaviour depends on `type`). `<textarea>` is for multi-line text (initial value goes between tags, `rows`/`cols`). `<select>` renders a dropdown of `<option>`s; `multiple` allows several selections. Radio/checkbox are inputs; `<datalist>` gives suggestions.

**Q5: Controlled vs uncontrolled forms in React?**
A5: **Controlled**: the input value lives in React state (`value` + `onChange`); easy validation and conditional UI but re-renders on each key. **Uncontrolled**: DOM holds the value; read it via `ref` or `FormData` on submit; fewer re-renders. Libraries like React Hook Form use uncontrolled inputs for performance.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** No label / placeholder as label
```html
<!-- WRONG --> <input placeholder="Email">
<!-- ✅ Correct way --> <label for="e">Email</label><input id="e" name="email" type="email" placeholder="you@x.com">
```

❌ **Mistake 2:** Forgetting `name` so the value is never submitted
```html
<!-- WRONG --> <input id="email" type="email">
<!-- ✅ Correct way --> <input id="email" name="email" type="email">
```

❌ **Mistake 3:** Non-submit button inside a form without `type="button"`
```html
<!-- WRONG: submits the form --> <button onclick="toggle()">Show</button>
<!-- ✅ Correct way --> <button type="button" onclick="toggle()">Show</button>
```

❌ **Mistake 4:** Clickable `<div>` as submit; `outline: none` without a replacement
```css
/* ✅ Correct way */
input:focus-visible { outline: 3px solid #1a73e8; }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `<form>` | Container that submits data | Data भेजने वाला container |
| `<input>` | Single-line / typed control | Input field |
| `<label>` | Text name for a control | Control का नाम |
| `<textarea>` | Multi-line text | Multi-line text box |
| `<select>` | Dropdown | Dropdown list |
| `<button>` | Clickable action control | Button |
| name | Key sent to server | Server को जाने वाला key |
| `<fieldset>/<legend>` | Group of controls + title | Controls का group |
| FormData | JS object of form values | Form values का object |
| Controlled component | React state drives value | React state से चलने वाला input |

---

## ⚡ 3-Line Summary
**English:**
1. `<form>` collects named controls and submits them; each control needs a `<label for>` and a `name`.
2. Core controls: `input`, `textarea`, `select`, `button` (default type is `submit`).
3. In React use `onSubmit` + `preventDefault`, controlled inputs or FormData, and Next.js Server Actions.

**Hindi:**
1. `<form>` named controls का data भेजता है; हर control को `<label for>` और `name` चाहिए।
2. मुख्य controls: `input`, `textarea`, `select`, `button` (default type `submit` है)।
3. React में `onSubmit` + `preventDefault`, controlled inputs या FormData, और Next.js Server Actions use करो।

---

## ➡️ Next Topic
**11. Form Attributes (action, method, enctype)** — form data kahan jaata hai, kaise jaata hai aur kis format mein, yeh ab seekhenge।
