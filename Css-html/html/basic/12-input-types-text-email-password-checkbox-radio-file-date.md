# 12. Input Types (text, email, password, checkbox, radio, file, date)
# हिंदी में: Input Types — हर काम के लिए सही Input

---

## 🔵 Simple Definition (English)
The `<input>` element changes behaviour entirely based on its **`type`** attribute: `text`, `email`, `password`, `checkbox`, `radio`, `file`, `date` and more. The right type gives you the correct keyboard on mobile, built-in validation, pickers and better accessibility with no JavaScript.

## 🔵 सरल परिभाषा (Hindi)
`<input>` element का पूरा behaviour उसके **`type`** attribute से बदल जाता है: `text`, `email`, `password`, `checkbox`, `radio`, `file`, `date` और भी बहुत। सही type से mobile पर सही keyboard, built-in validation, pickers और बेहतर accessibility बिना JavaScript के मिलती है।

---

## 🔴 Problem it Solves
```
BEFORE HTML5 everything was type="text" (+ JavaScript):
  - Email: custom regex and custom error messages
  - Date: hand-built calendar widgets with jQuery plugins
  - Password: must manually mask characters
  - Mobile users got a normal keyboard for phone numbers and emails

WITH SPECIFIC TYPES:
  type="email"    validates format, shows "@" keyboard on phones
  type="tel"      numeric dial pad
  type="date"     native calendar picker (OS-localised)
  type="password" masked text, password-manager support
  type="file"     OS file picker
  radio/checkbox  proper single/multi choice with group behaviour
```

## 🔴 यह क्यों बना? (Hindi)
```
HTML5 से पहले सब कुछ type="text" था (+ JavaScript):
  - Email के लिए अपना regex और error messages
  - Date के लिए jQuery के calendar plugins
  - Password को हाथ से mask करना
  - Phone number/email के लिए mobile पर सामान्य keyboard

सही type के साथ:
  type="email"    format validate, phone पर "@" वाला keyboard
  type="tel"      numeric dial pad
  type="date"     native calendar picker
  type="password" masked text, password manager support
  type="file"     OS का file picker
  radio/checkbox  एक/कई विकल्प चुनने का सही behaviour
```

---

## 🟢 How it Works — Step by Step

```
THE MAIN TYPES:
──────────────────────────────────────────────────────────
type        Value sent / notes
text        default; single-line string. Attrs: maxlength, minlength, pattern, placeholder
email       validates "a@b.c" shape; `multiple` allows comma-separated emails; mobile @ keyboard
password    masked; use autocomplete="current-password" / "new-password"
tel         no format validation (formats vary); phone keypad. Use pattern if needed
number      numeric; min, max, step; spinner arrows. Beware: not for ZIP/OTP/phone/card numbers
            (use type="text" inputmode="numeric" instead)
url         validates absolute URL
search      like text; clear (x) button in some browsers; semantic for search boxes
checkbox    zero, one or many on/off choices. Sent ONLY when checked: name=value
              attrs: checked, value (default "on"), indeterminate (JS only)
radio       choose EXACTLY ONE of a group. Same `name` = same group. Always give each a value
              Group radios in <fieldset><legend>
file        choose files. attrs: accept=".pdf,image/*", multiple, capture. Needs
              method="post" + enctype="multipart/form-data" in a form. Read via input.files
date        yyyy-mm-dd value regardless of display locale; min, max, step
              related: time, datetime-local, month, week
range       slider (min, max, step); value is a string
color       color picker, value "#rrggbb"
hidden      invisible; carries data (e.g. CSRF token, record id)
submit / reset / button / image  button-like inputs (prefer <button>)

COMMON ATTRIBUTES (work on most types):
  name  value  required  disabled  readonly  autofocus  autocomplete  placeholder  list (datalist)
  `inputmode` = which virtual keyboard (numeric, decimal, tel, email, search...)

VALUE FORMATS (JS):
  input.value       always a STRING (even for number/range/date)
  input.valueAsNumber / valueAsDate    typed access
  checkbox/radio:   input.checked (boolean), input.value (the value attribute)
  file:             input.files -> FileList of File objects (name, size, type)

PITFALLS:
  - Unchecked checkbox is NOT submitted at all
  - Radio buttons without a shared name are not mutually exclusive
  - type="date" UI differs per browser/OS; old Safari desktop (<14.1) lacks a picker, so
    design for the text-field fallback; always validate on the SERVER too
  - You cannot set file input value programmatically (security); only clear it
  - type="password" does not encrypt anything: use HTTPS
```

## 🟢 कैसे काम करता है? (Hindi)
```
मुख्य types:
  text      साधारण single-line text
  email     email format check, mobile पर @ वाला keyboard
  password  अक्षर छुपे रहते हैं; autocomplete="current-password"
  number    min/max/step; पर phone, OTP, pin code के लिए नहीं (type="text" inputmode="numeric")
  checkbox  कई विकल्प चुन सकते हो; चुना हुआ ही submit होता है
  radio     समूह में से सिर्फ एक; समूह के लिए सबका name एक जैसा
  file      file चुनना; accept, multiple; form में enctype="multipart/form-data" चाहिए
  date      calendar picker; value हमेशा yyyy-mm-dd
  range     slider; color  रंग चुनना; hidden  छुपा data

JS में:
  input.value हमेशा string होती है
  checkbox/radio में input.checked (true/false)
  file में input.files (File objects की list)
```

---

## 🟡 Real World Example
**Zomato / Swiggy / Gmail forms:** Gmail's compose "To" field is an email-like input, the sign-in password uses `type="password"`. Zomato's table-booking page uses `type="date"` and `type="time"` for the booking slot, radio buttons for "Veg / Non-veg" and a stepper for guests (`type="number"`). Swiggy's "Save address" uses checkboxes ("Make default") and the OTP screen uses `type="text" inputmode="numeric" autocomplete="one-time-code"`, which lets phones auto-fill the SMS code. Instagram's profile picture upload uses `type="file" accept="image/*"`.

## 🟡 Real Example Hindi mein
**Zomato / Swiggy / Gmail forms:** Gmail के compose में "To" field email जैसा input है, sign-in password `type="password"` है। Zomato की table-booking page पर slot के लिए `type="date"` और `type="time"`, "Veg / Non-veg" के लिए radio buttons, और guests के लिए `type="number"` stepper है। Swiggy का "Save address" checkbox ("Make default") इस्तेमाल करता है, और OTP screen `type="text" inputmode="numeric" autocomplete="one-time-code"` इस्तेमाल करती है जिससे phone SMS code खुद भर देता है। Instagram का profile picture upload `type="file" accept="image/*"` है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Input Types Playground</title>
  <style>
    * { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; background: #f4f4f4; padding: 20px; }
    form { max-width: 520px; margin: 0 auto; background: #fff; padding: 24px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,.1); }
    h1 { margin-top: 0; font-size: 22px; }
    .field { margin-bottom: 16px; }
    label.top { display: block; font-weight: 600; margin-bottom: 6px; }
    input[type=text], input[type=email], input[type=password], input[type=tel],
    input[type=number], input[type=date], input[type=file] {
      width: 100%; padding: 10px 12px; font: inherit; border: 1px solid #bbb; border-radius: 8px;
    }
    input:focus-visible { outline: 3px solid #e23744; outline-offset: 1px; }   /* visible focus */

    /* Validation styling: only after user typed (:user-invalid is newer; :invalid:not(:placeholder-shown) works everywhere) */
    input:invalid:not(:placeholder-shown) { border-color: #d32f2f; background: #fff5f5; }
    input:valid:not(:placeholder-shown)   { border-color: #2e7d32; }

    fieldset { border: 1px solid #ddd; border-radius: 8px; padding: 10px 14px; margin: 0 0 16px; }
    legend { font-weight: 600; padding: 0 6px; }
    .opt { display: inline-flex; align-items: center; gap: 6px; margin-right: 16px; }
    input[type=checkbox], input[type=radio] { width: 18px; height: 18px; accent-color: #e23744; } /* modern tint */
    input[type=range] { width: 100%; accent-color: #e23744; }
    button { width: 100%; padding: 12px; font: inherit; font-weight: 700; border: 0; border-radius: 8px; background: #e23744; color: #fff; cursor: pointer; }
    pre { background: #111; color: #9f9; padding: 12px; border-radius: 8px; white-space: pre-wrap; font-size: 13px; }
  </style>
</head>
<body>
  <form id="f" action="/book" method="post" enctype="multipart/form-data">  <!-- multipart because of the file input -->
    <h1>Table booking</h1>

    <div class="field">
      <label class="top" for="name">Name (text)</label>
      <input type="text" id="name" name="name" placeholder=" " required minlength="2" maxlength="40" autocomplete="name">
    </div>

    <div class="field">
      <label class="top" for="email">Email</label>
      <!-- type=email validates the format; placeholder=" " enables :placeholder-shown trick -->
      <input type="email" id="email" name="email" placeholder=" " required autocomplete="email">
    </div>

    <div class="field">
      <label class="top" for="pw">Password</label>
      <input type="password" id="pw" name="password" placeholder=" " required minlength="8" autocomplete="new-password">
    </div>

    <div class="field">
      <label class="top" for="tel">Phone (tel)</label>
      <!-- tel shows dial pad; pattern = 10 digits (Indian mobile) -->
      <input type="tel" id="tel" name="phone" placeholder=" " pattern="[6-9][0-9]{9}" inputmode="numeric" title="10-digit Indian mobile number">
    </div>

    <div class="field">
      <label class="top" for="guests">Guests (number)</label>
      <input type="number" id="guests" name="guests" min="1" max="10" step="1" value="2">
    </div>

    <div class="field">
      <label class="top" for="date">Date</label>
      <!-- value format is always yyyy-mm-dd; min blocks past dates -->
      <input type="date" id="date" name="date" required>
    </div>

    <!-- radio group: same name = pick ONE -->
    <fieldset>
      <legend>Seating</legend>
      <label class="opt"><input type="radio" name="seat" value="indoor" checked> Indoor</label>
      <label class="opt"><input type="radio" name="seat" value="outdoor"> Outdoor</label>
    </fieldset>

    <!-- checkboxes: pick any; same name collects an array of values -->
    <fieldset>
      <legend>Extras</legend>
      <label class="opt"><input type="checkbox" name="extras" value="birthday"> Birthday cake</label>
      <label class="opt"><input type="checkbox" name="extras" value="highchair"> High chair</label>
    </fieldset>

    <div class="field">
      <label class="top" for="photo">Photo (file)</label>
      <input type="file" id="photo" name="photo" accept="image/*">
    </div>

    <div class="field">
      <label class="top" for="vol">Music volume: <output id="volOut">50</output></label>
      <input type="range" id="vol" name="volume" min="0" max="100" value="50">
    </div>

    <input type="hidden" name="source" value="web">   <!-- hidden carries extra data -->

    <button type="submit">Book table</button>
    <pre id="out" hidden></pre>
  </form>

  <script>
    // Set the minimum date to today, so past dates cannot be picked
    const dateEl = document.getElementById("date");
    dateEl.min = new Date().toISOString().split("T")[0];

    // Live range value
    document.getElementById("vol").addEventListener("input", e =>
      document.getElementById("volOut").textContent = e.target.value);

    // Demo submit: show what will be sent (no real server needed)
    document.getElementById("f").addEventListener("submit", e => {
      e.preventDefault();                                  // only runs if native validation passed
      const fd = new FormData(e.target);
      const obj = {};
      for (const [k, v] of fd) {
        const val = v instanceof File ? `File(${v.name || "none"}, ${v.size} bytes)` : v;
        obj[k] = k in obj ? [].concat(obj[k], val) : val;  // repeated names (checkbox) become arrays
      }
      const out = document.getElementById("out");
      out.hidden = false;
      out.textContent = JSON.stringify(obj, null, 2);
    });
  </script>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
"use client";
import { useState } from "react";

export default function BookingForm() {
  const [form, setForm] = useState({
    name: "", email: "", guests: 2, seat: "indoor", extras: [], agree: false,
  });

  // One handler that understands different input types
  const onChange = (e) => {
    const { name, type, value, checked, files } = e.target;
    if (type === "checkbox" && name === "extras") {
      // multi checkbox group -> array
      setForm(f => ({ ...f, extras: checked ? [...f.extras, value] : f.extras.filter(x => x !== value) }));
    } else if (type === "checkbox") {
      setForm(f => ({ ...f, [name]: checked }));                 // single checkbox -> boolean (use `checked`)
    } else if (type === "file") {
      setForm(f => ({ ...f, [name]: files[0] }));                // File object
    } else if (type === "number") {
      setForm(f => ({ ...f, [name]: Number(value) }));           // value is a string: convert
    } else {
      setForm(f => ({ ...f, [name]: value }));                   // text, email, date, radio...
    }
  };

  return (
    <form onSubmit={(e) => { e.preventDefault(); console.log(form); }} className="space-y-4">
      <input name="email" type="email" value={form.email} onChange={onChange} required />
      <input name="guests" type="number" min={1} max={10} value={form.guests} onChange={onChange} />

      {/* radio: `checked` is derived from state */}
      <label><input type="radio" name="seat" value="indoor"
                    checked={form.seat === "indoor"} onChange={onChange} /> Indoor</label>

      {/* checkbox uses `checked`, not `value` for its state */}
      <label><input type="checkbox" name="agree" checked={form.agree} onChange={onChange} /> I agree</label>

      {/* file inputs are ALWAYS uncontrolled in React (cannot set value) */}
      <input type="file" name="photo" accept="image/*" onChange={onChange} />
      <button type="submit">Book</button>
    </form>
  );
}

// Notes:
// - JSX attributes: defaultChecked / defaultValue for uncontrolled; htmlFor on labels
// - Tailwind: accent-red-500 on checkbox/radio, @tailwindcss/forms plugin to normalise inputs
// - Libraries: React Hook Form register("email") works with every input type; Zod validates
```

---

## ⚫ Interview Questions + Answers

**Q1: Why use `type="email"` instead of `type="text"`?**
A1: It gives **built-in format validation** (CSS `:invalid` + blocks submit), the right **mobile keyboard** (@ and .), autofill hints, and `multiple` support. It is only a *client-side* convenience: the server must still validate because anyone can bypass the browser.

**Q2: Difference between checkbox and radio?**
A2: **Radio**: choose exactly **one** of a group; inputs sharing the same `name` are mutually exclusive; once selected, you cannot unselect by clicking again. **Checkbox**: independent on/off; many can be selected; each can be toggled. A checked checkbox submits `name=value`; an unchecked one submits **nothing**.

**Q3: How do you handle file uploads in HTML?**
A3: Use `<input type="file" name="photo" accept="image/*">` (add `multiple` for several). In a native form set `method="post"` and `enctype="multipart/form-data"`. In JS read `input.files[0]` (a `File` with name, size, type), validate size/type, and send with `FormData`. You cannot preset a value for security reasons.

**Q4: What is the value format of `type="date"` and what are its limitations?**
A4: `value` is always an ISO string `yyyy-mm-dd`, regardless of how the browser displays it locally. Limitations: picker UI differs by browser/OS, styling is limited, time zones are not included (use `datetime-local` for date+time, no timezone), and for complex needs (ranges, disabled days) teams use a date-picker library. Use `min`/`max` for allowed ranges.

**Q5: Why shouldn't you use `type="number"` for phone numbers, OTPs or card numbers?**
A5: Number inputs allow only numeric values, drop leading zeros, show spinner arrows, change value on mouse wheel/arrow keys, and accept `e`, `+`, `-`. Identifiers are **strings, not quantities**. Use `type="text"` (or `tel`) with `inputmode="numeric"`, `pattern` and `autocomplete="one-time-code"` for OTPs.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** `type="text"` for everything
```html
<!-- WRONG --> <input type="text" name="email">
<!-- ✅ Correct way --> <input type="email" name="email" autocomplete="email">
```

❌ **Mistake 2:** Radio buttons with different (or missing) names
```html
<!-- WRONG: both can be selected --> <input type="radio" name="a"> <input type="radio" name="b">
<!-- ✅ Correct way --> <input type="radio" name="seat" value="indoor"> <input type="radio" name="seat" value="outdoor">
```

❌ **Mistake 3:** Number type for OTP / phone / pincode
```html
<!-- WRONG --> <input type="number" name="otp">
<!-- ✅ Correct way -->
<input type="text" name="otp" inputmode="numeric" pattern="[0-9]{6}" maxlength="6" autocomplete="one-time-code">
```

❌ **Mistake 4:** Trusting client validation; expecting `value` of checkbox to be true/false
```js
// WRONG: checkbox.value is the string "on" (or its value attr)
if (box.value) { /* always truthy */ }
// ✅ Correct way
if (box.checked) { /* real state */ }
// And ALWAYS re-validate on the server.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| type | Decides input behaviour | Input का प्रकार |
| email / tel / url | Typed text with validation/keyboard | Format और keyboard वाले inputs |
| password | Masked input | छुपे अक्षरों वाला input |
| checkbox | Independent on/off | कई चुनने वाला box |
| radio | Pick one in a group | समूह में से एक |
| file | File chooser | File चुनने वाला |
| date | Date picker (yyyy-mm-dd) | तारीख चुनना |
| inputmode | Virtual keyboard hint | Keyboard का संकेत |
| accept | Allowed file types | अनुमत file types |
| accent-color | Tint for native controls | Native controls का रंग |

---

## ⚡ 3-Line Summary
**English:**
1. `type` changes input behaviour: text, email, password, tel, number, date, checkbox, radio, file, range, hidden.
2. Right type = free validation, correct mobile keyboard and pickers; but always validate again on the server.
3. Radios share one `name`, unchecked checkboxes send nothing, files need multipart; use text + `inputmode` for OTP/phone, not number.

**Hindi:**
1. `type` से input का behaviour बदलता है: text, email, password, tel, number, date, checkbox, radio, file, range, hidden।
2. सही type से free validation, सही mobile keyboard और pickers मिलते हैं; फिर भी server पर दोबारा validate करो।
3. Radios का `name` एक ही, unchecked checkbox कुछ नहीं भेजता, files को multipart चाहिए; OTP/phone के लिए number नहीं, text + `inputmode`।

---

## ➡️ Next Topic
**13. Form Validation (required, pattern, min, max)** — ab seekhenge ki browser ki built-in validation kaise kaam karti hai aur custom error messages kaise dete hain।
