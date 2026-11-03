# 13. Form Validation (required, pattern, min, max)
# हिंदी में: Form Validation — Browser खुद गलत Input रोक देता है

---

## 🔵 Simple Definition (English)
HTML5 form validation lets the **browser itself** check user input before the form is submitted. You add attributes like `required`, `pattern`, `min`, `max`, `minlength`, `maxlength` and `type="email"`. If a value is invalid, the browser blocks submit and shows an error bubble. No JavaScript needed for basic checks.

## 🔵 सरल परिभाषा (Hindi)
HTML5 form validation में **browser खुद** input check करता है, form submit होने से पहले। आप `required`, `pattern`, `min`, `max`, `minlength`, `maxlength` और `type="email"` जैसे attributes लगाते हो। Value गलत हो तो browser submit रोक देता है और error bubble दिखाता है। Basic checks के लिए JavaScript नहीं चाहिए।

---

## 🔴 Problem it Solves
```
BEFORE HTML5:
  - Every form needed custom JavaScript: if (email.indexOf("@") === -1) {...}
  - Each developer wrote different (often buggy) checks
  - JS disabled / failed to load -> zero validation
  - No standard error UI, no accessibility support

WITH HTML5 VALIDATION:
  <input type="email" required>
  - Browser checks it, shows localized message, focuses the bad field
  - Works even before your JS bundle loads (good for Next.js hydration delay)
  - Screen readers announce the error
  - CSS can style :valid / :invalid states

IMPORTANT: client-side validation is for UX only.
  Users can bypass it (DevTools, curl). ALWAYS re-validate on the server.
```

## 🔴 यह क्यों बना? (Hindi)
```
HTML5 से पहले:
  - हर form के लिए custom JavaScript लिखनी पड़ती थी
  - हर developer अलग (और अक्सर buggy) checks लिखता था
  - JS बंद या load नहीं हुई तो validation बिल्कुल नहीं
  - कोई standard error UI या accessibility support नहीं

HTML5 validation के साथ:
  <input type="email" required>
  - Browser खुद check करता है, error message दिखाता है, गलत field पर focus करता है
  - JS bundle load होने से पहले भी काम करता है
  - Screen reader error बोलता है
  - CSS से :valid / :invalid style कर सकते हैं

ज़रूरी: client-side validation सिर्फ UX के लिए है।
  User इसे bypass कर सकता है। Server पर हमेशा दोबारा validate करो।
```

---

## 🟢 How it Works — Step by Step

```
VALIDATION FLOW:
──────────────────────────────────────────────────────────
1. User clicks the submit button (or presses Enter).
2. Browser runs "interactive validation" on every control in the form.
3. Each control is checked against its constraints (its ValidityState).
4. If ANY control is invalid:
     - submit event does NOT fire, request is NOT sent
     - first invalid field gets focus
     - browser shows its default message bubble
5. If all are valid -> submit event fires -> request is sent.

CONSTRAINT ATTRIBUTES:
  required         -> field must not be empty
  type="email"     -> must look like name@domain
  type="url"       -> must be a valid absolute URL
  minlength/maxlength -> text length limits (characters)
  min / max        -> numeric or date range (number, range, date)
  step             -> allowed increments (step="5" -> 0, 5, 10...)
  pattern="regex"  -> text must FULLY match the regular expression
  title            -> hint text, often shown inside the error bubble

CSS HOOKS:
  :valid  :invalid  :required  :optional  :in-range  :out-of-range
  :user-invalid / :user-valid  -> only after the user interacted
                                 (supported in all modern browsers since ~2023;
                                  use :invalid as a fallback)

JS API (Constraint Validation):
  input.validity.valueMissing / typeMismatch / patternMismatch /
                  tooShort / rangeUnderflow / rangeOverflow
  input.setCustomValidity("msg")  -> custom error ("" clears it)
  form.checkValidity() / form.reportValidity()
  <form novalidate>  -> turn OFF built-in bubbles (you show your own)
```

## 🟢 कैसे काम करता है? (Hindi)

```
VALIDATION FLOW:
──────────────────────────────────────────────────────────
1. User submit button दबाता है (या Enter)।
2. Browser form के हर control पर validation चलाता है।
3. हर control अपने constraints (ValidityState) से check होता है।
4. अगर कोई भी invalid है:
     - submit event fire नहीं होता, request नहीं जाती
     - पहली गलत field पर focus आता है
     - browser का default message bubble दिखता है
5. सब valid हैं -> submit event fire -> request जाती है।

CONSTRAINT ATTRIBUTES:
  required         -> field खाली नहीं होनी चाहिए
  type="email"     -> name@domain जैसा दिखना चाहिए
  minlength/maxlength -> text की length limit
  min / max        -> number या date की range
  step             -> allowed steps (step="5" -> 0, 5, 10...)
  pattern="regex"  -> text regex से पूरा match होना चाहिए
  title            -> hint text, error bubble में दिखता है

<form novalidate> से built-in bubbles बंद होते हैं,
फिर आप अपना error UI खुद दिखाते हो।
```

---

## 🟡 Real World Example
**Swiggy / Zomato signup:** The phone field is `type="tel"` with `pattern="[6-9][0-9]{9}"` (10-digit Indian mobile starting with 6-9) and `required`. The pincode field uses `pattern="[0-9]{6}"`. The "Quantity" stepper in a cart uses `type="number" min="1" max="10"`. **Gmail signup** uses `type="email"` and `minlength="8"` for passwords, and inline red borders using `:invalid`. All of this runs instantly with no network call.

## 🟡 Real Example Hindi mein
**Swiggy / Zomato signup:** Phone field `type="tel"` है, `pattern="[6-9][0-9]{9}"` के साथ (6-9 से शुरू होने वाला 10 अंकों का Indian mobile) और `required`। Pincode field में `pattern="[0-9]{6}"`। Cart का "Quantity" `type="number" min="1" max="10"` होता है। **Gmail signup** में `type="email"` और password के लिए `minlength="8"`, और `:invalid` से लाल border। सब कुछ बिना network call के तुरंत होता है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Form Validation Demo</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; background: #f5f5f5; padding: 20px; }

    /* Card wrapper for the form */
    .card { max-width: 420px; margin: 0 auto; background: #fff; padding: 24px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,.1); }
    label { display: block; margin: 14px 0 4px; font-weight: 600; font-size: 14px; }
    input, select { width: 100%; padding: 10px; border: 2px solid #ccc; border-radius: 6px; font-size: 15px; }
    small { color: #666; font-size: 12px; }

    /* Valid / invalid styling.
       :user-invalid only triggers AFTER the user touched the field,
       so the form does not scream red on page load. */
    input:user-valid   { border-color: #2e7d32; }
    input:user-invalid { border-color: #c62828; background: #ffebee; }

    /* Fallback for older browsers: only style invalid fields that are not empty */
    input:not(:placeholder-shown):invalid { border-color: #c62828; }

    button { margin-top: 20px; width: 100%; padding: 12px; background: #e23744; color: #fff; border: 0; border-radius: 6px; font-size: 16px; cursor: pointer; }
    #msg { margin-top: 12px; color: #c62828; font-size: 13px; min-height: 18px; }
  </style>
</head>
<body>
  <div class="card">
    <h2>Create account</h2>

    <!-- The browser validates everything on submit -->
    <form id="signup" action="/signup" method="post">

      <!-- required: cannot be empty. minlength/maxlength: character count -->
      <label for="name">Full name</label>
      <input id="name" name="name" type="text" placeholder="Aditya Ranjan"
             required minlength="3" maxlength="40" autocomplete="name">

      <!-- type=email: must contain @ and a domain -->
      <label for="email">Email</label>
      <input id="email" name="email" type="email" placeholder="you@gmail.com" required>

      <!-- pattern: Indian mobile, 10 digits starting 6-9. Regex must match the WHOLE value.
           title is shown in the error bubble -->
      <label for="phone">Mobile</label>
      <input id="phone" name="phone" type="tel" placeholder="9876543210"
             required pattern="[6-9][0-9]{9}" inputmode="numeric"
             title="Enter a 10-digit mobile number starting with 6, 7, 8 or 9">

      <!-- min / max / step on a number input -->
      <label for="age">Age</label>
      <input id="age" name="age" type="number" min="18" max="100" step="1" required>
      <small>Must be 18 or older</small>

      <!-- min / max on a date input (ISO format YYYY-MM-DD) -->
      <label for="dob">Delivery date</label>
      <input id="dob" name="delivery" type="date" min="2026-01-01" max="2026-12-31">

      <!-- Password with minlength, plus a custom JS check for confirm field -->
      <label for="pw">Password</label>
      <input id="pw" name="pw" type="password" required minlength="8">

      <label for="pw2">Confirm password</label>
      <input id="pw2" name="pw2" type="password" required minlength="8">

      <!-- Required checkbox: must be ticked -->
      <label><input type="checkbox" name="terms" required style="width:auto"> I accept the terms</label>

      <button type="submit">Sign up</button>
      <p id="msg" role="alert"></p>
    </form>
  </div>

  <script>
    // Constraint Validation API: add a custom rule on top of HTML attributes
    const form = document.getElementById('signup');
    const pw = document.getElementById('pw');
    const pw2 = document.getElementById('pw2');

    function checkMatch() {
      // setCustomValidity("text") marks the field invalid; "" clears it
      pw2.setCustomValidity(pw.value !== pw2.value ? 'Passwords do not match' : '');
    }
    pw.addEventListener('input', checkMatch);
    pw2.addEventListener('input', checkMatch);

    form.addEventListener('submit', (e) => {
      e.preventDefault();                 // demo only: do not really post
      document.getElementById('msg').textContent = '';
      alert('All fields valid. Form would be submitted now.');
    });
  </script>
</body>
</html>
```

```css
/* Extra: style required fields with an asterisk using CSS only */
label:has(+ input:required)::after {  /* :has() is supported in all modern browsers (2023+) */
  content: " *";
  color: #c62828;
}
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. In React you keep the HTML attributes. The browser still validates
//    on submit, as long as you do NOT use noValidate.
//    Note camelCase: minLength, maxLength, noValidate.
export default function Signup() {
  const [error, setError] = useState('');

  function onSubmit(e) {
    e.preventDefault();                       // stop page reload
    const form = e.currentTarget;
    if (!form.checkValidity()) {              // run the browser validation manually
      form.reportValidity();                  // show bubbles
      return;
    }
    const data = Object.fromEntries(new FormData(form));
    // send to API (and validate again on the server!)
  }

  return (
    <form onSubmit={onSubmit}>
      <input name="email" type="email" required />
      <input name="phone" type="tel" required pattern="[6-9][0-9]{9}" />
      <input name="age" type="number" min={18} max={100} />   {/* numbers in JSX braces */}
      <button type="submit">Sign up</button>
    </form>
  );
}

// 2. Next.js Server Actions: native attributes give instant client UX,
//    and the server action re-validates (e.g. with Zod) for security.
// 3. Libraries (React Hook Form, Formik) usually set noValidate and use their
//    own rules. Native attributes still help as a no-JS fallback.
// 4. Tailwind: use variants  -> className="invalid:border-red-500 user-invalid:bg-red-50"
//    "peer" + "peer-invalid:block" shows helper text next to an invalid input.
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you validate a form without JavaScript?**
A1: Use HTML5 constraint attributes: `required`, `type="email"/"url"/"number"`, `minlength`, `maxlength`, `min`, `max`, `step` and `pattern`. On submit the browser checks them, blocks the request if something is invalid, focuses the first bad field and shows a message. CSS pseudo-classes `:valid` and `:invalid` let you style the result.

**Q2: Is client-side validation enough? Why or why not?**
A2: No. It is only for user experience. Anyone can disable it with DevTools, remove `required`, or call your API directly with curl or Postman. The server must always validate and sanitize again. Client-side = fast feedback, server-side = actual security and data integrity.

**Q3: How does `pattern` work? Any gotchas?**
A3: `pattern` takes a JavaScript-style regular expression and the value must **fully match** it (the browser implicitly wraps it as `^(?:pattern)$`, so you do not add anchors). It works only on text-like inputs (text, tel, email, url, search, password). It is skipped if the field is empty (combine with `required`). Add a `title` attribute to explain the format to users.

**Q4: How do you show a custom error message or disable the default bubbles?**
A4: For a custom message use `input.setCustomValidity("My message")`; the field then counts as invalid until you call `setCustomValidity("")`. To replace the browser bubbles entirely, add `novalidate` to the `<form>`, listen to the `invalid`/`submit` events, check `input.validity` flags (`valueMissing`, `typeMismatch`, `patternMismatch`, `rangeOverflow`...) and render your own messages with `aria-describedby` and `role="alert"`.

**Q5: What is the difference between `:invalid` and `:user-invalid`?**
A5: `:invalid` matches as soon as the value breaks a rule, even on page load with an empty `required` field, which makes forms look angry too early. `:user-invalid` matches only after the user has interacted with the field (blurred or tried to submit). It is supported in all current evergreen browsers (since about 2023), so use it for nicer UX, with `:invalid` as a fallback for older browsers.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Trusting only client-side validation
```html
<!-- WRONG: server accepts whatever it receives -->
<input name="age" type="number" min="18">
<!-- User edits HTML, sends age=-5 -> bad data in DB -->
```
✅ **Correct way:** Validate again on the server (Zod, Joi, Express-validator, Server Action checks).

❌ **Mistake 2:** Wrong `pattern` expectations
```html
<!-- WRONG: anchors and slashes are not needed, and min on text does nothing -->
<input pattern="/^[0-9]{6}$/" min="6">
```
✅ **Correct way:**
```html
<input type="text" pattern="[0-9]{6}" inputmode="numeric" title="6 digit pincode" required>
```

❌ **Mistake 3:** Using `min`/`max` on text and `minlength` on numbers
```html
<!-- WRONG: ignored by the browser -->
<input type="text" min="3"> <input type="number" minlength="3">
```
✅ **Correct way:** `minlength/maxlength` for text length, `min/max` for number/date/range values.

❌ **Mistake 4:** Putting `required` on a button or relying on `placeholder` as validation
✅ **Correct way:** `required` belongs on form controls (input, select, textarea). A placeholder is only a hint and is not a label or a rule.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| required | Field cannot be empty | खाली नहीं छोड़ सकते |
| pattern | Regex the value must fully match | Regex से match होना ज़रूरी |
| min / max | Lowest / highest number or date | न्यूनतम / अधिकतम मान |
| minlength / maxlength | Text length limits | Text की लंबाई की सीमा |
| ValidityState | Object describing why a field is invalid | Field गलत क्यों है, उसकी जानकारी |
| setCustomValidity | JS method to set a custom error | अपना error message सेट करना |
| novalidate | Form attribute that turns off built-in bubbles | Browser की validation बंद |
| :user-invalid | Invalid state after user interaction | User के छूने के बाद का invalid state |

---

## ⚡ 3-Line Summary
**English:**
1. HTML5 attributes (`required`, `pattern`, `min`, `max`, `minlength`, `type`) let the browser validate forms with no JavaScript.
2. Use `:valid/:invalid/:user-invalid` for styling and the Constraint Validation API (`setCustomValidity`, `checkValidity`) for custom rules.
3. Client validation is only UX; always validate again on the server.

**Hindi:**
1. HTML5 attributes (`required`, `pattern`, `min`, `max`, `minlength`, `type`) से browser बिना JavaScript के form validate करता है।
2. Styling के लिए `:valid/:invalid/:user-invalid` और custom rules के लिए Constraint Validation API use करो।
3. Client validation सिर्फ UX है; server पर हमेशा दोबारा validate करो।

---

## ➡️ Next Topic
**14. HTML Attributes (id, class, name, placeholder, value)** — forms में हमने कई attributes use किए; अब समझते हैं कि attributes सामान्य रूप से क्या होते हैं और `id`, `class`, `name` में क्या फ़र्क है।
